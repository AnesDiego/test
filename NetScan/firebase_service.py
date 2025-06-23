import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
import json
import os
from flask import request
import uuid
import hashlib

class FirebaseService:
    def __init__(self, config):
        """Initialize Firebase service"""
        self.config = config
        self.db = None
        self.initialized = False
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK with robust error handling"""
        try:
            # Force load environment variables
            from dotenv import load_dotenv
            load_dotenv()
            
            # Check Firebase project ID from multiple sources
            project_id = (
                getattr(self.config, 'FIREBASE_PROJECT_ID', None) or 
                os.environ.get('FIREBASE_PROJECT_ID') or
                os.getenv('FIREBASE_PROJECT_ID')
            )
            
            print(f"🔍 Checking Firebase config - Project ID: {project_id}")
            
            if not project_id or project_id == 'your-firebase-project-id':
                print("⚠️  FIREBASE_PROJECT_ID not configured - running without analytics")
                return
            
            # Prevent duplicate initialization
            if not firebase_admin._apps:
                # Check for service account file
                service_account_path = 'firebase-service-account.json'
                if not os.path.exists(service_account_path):
                    print(f"⚠️  Firebase service account file not found: {service_account_path}")
                    print("📋 Please download the service account JSON from Firebase Console")
                    return
                
                # Initialize Firebase Admin SDK
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': project_id
                })
                print(f"🔥 Firebase initialized with project: {project_id}")
            
            # Initialize Firestore client
            self.db = firestore.client()
            self.initialized = True
            print("✅ Firestore client initialized successfully")
            
        except Exception as e:
            print(f"❌ Firebase initialization failed: {str(e)}")
            print("🔄 Application will continue without Firebase analytics")
            self.db = None
            self.initialized = False
    
    def is_ready(self):
        """Check if Firebase service is ready"""
        return self.initialized and self.db is not None
    
    def _hash_ip(self, ip_address):
        """Create a secure hash of IP address for privacy"""
        if not ip_address:
            return None
        return hashlib.sha256(f"{ip_address}:netscan_salt".encode()).hexdigest()[:16]
    
    def track_user_visit(self, request_obj):
        """Track user visit privately for admin analytics"""
        try:
            if not self.is_ready():
                return None
            
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            # Extract anonymized user information
            user_info = {
                'session_id': session_id,
                'timestamp': datetime.now(timezone.utc),
                'ip_hash': self._hash_ip(request_obj.remote_addr),
                'user_agent': (request_obj.headers.get('User-Agent', '') or '')[:200],
                'referer': (request_obj.headers.get('Referer', '') or '')[:200],
                'language': (request_obj.headers.get('Accept-Language', '') or '')[:50],
                'page_url': (request_obj.url or '')[:200],
                'method': request_obj.method or 'GET',
                'country': None  # Can be populated later with IP geolocation
            }
            
            # Store user visit in Firestore
            doc_ref = self.db.collection('user_analytics').document(session_id)
            doc_ref.set(user_info)
            
            # Update daily statistics
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            daily_ref = self.db.collection('daily_stats').document(today)
            
            # Use transaction to ensure atomic updates
            @firestore.transactional
            def update_daily_stats(transaction, daily_ref):
                doc = daily_ref.get(transaction=transaction)
                if doc.exists:
                    transaction.update(daily_ref, {
                        'unique_visitors': firestore.Increment(1),
                        'total_visits': firestore.Increment(1),
                        'last_updated': datetime.now(timezone.utc)
                    })
                else:
                    transaction.set(daily_ref, {
                        'date': today,
                        'unique_visitors': 1,
                        'total_visits': 1,
                        'last_updated': datetime.now(timezone.utc),
                        'total_scans': 0
                    })
            
            transaction = self.db.transaction()
            update_daily_stats(transaction, daily_ref)
            
            print(f"📊 User visit tracked: {session_id[:8]}...")
            return session_id
            
        except Exception as e:
            print(f"⚠️  Error tracking user visit: {str(e)}")
            return None
    
    def get_user_stats(self, admin_key):
        """Get comprehensive user statistics (admin only)"""
        try:
            # Validate admin access
            admin_secret = getattr(self.config, 'ADMIN_SECRET_KEY', None)
            if not admin_secret or admin_key != admin_secret:
                return {'error': 'Unauthorized access', 'code': 401}
            
            if not self.is_ready():
                return {'error': 'Firebase analytics not available', 'code': 503}
            
            # Get total unique visits count
            analytics_ref = self.db.collection('user_analytics')
            total_docs = 0
            for _ in analytics_ref.stream():
                total_docs += 1
            
            # Get daily statistics for the last 30 days
            daily_stats_ref = (self.db.collection('daily_stats')
                            .order_by('date', direction=firestore.Query.DESCENDING)
                            .limit(30))
            
            daily_stats = []
            current_month_visitors = 0
            current_month_visits = 0
            current_month_scans = 0
            current_month = datetime.now(timezone.utc).strftime('%Y-%m')
            
            for doc in daily_stats_ref.stream():
                data = doc.to_dict()
                date_str = data.get('date', '')
                
                daily_entry = {
                    'date': date_str,
                    'unique_visitors': data.get('unique_visitors', 0),
                    'total_visits': data.get('total_visits', 0),
                    'total_scans': data.get('total_scans', 0)
                }
                daily_stats.append(daily_entry)
                
                # Calculate current month totals
                if date_str.startswith(current_month):
                    current_month_visitors += daily_entry['unique_visitors']
                    current_month_visits += daily_entry['total_visits']
                    current_month_scans += daily_entry['total_scans']
            
            # Get recent activity (last 100 visits for geographic analysis)
            recent_limit = 100
            recent_visits_ref = (self.db.collection('user_analytics')
                               .order_by('timestamp', direction=firestore.Query.DESCENDING)
                               .limit(recent_limit))
            
            countries = {}
            user_agents = {}
            recent_count = 0
            
            for doc in recent_visits_ref.stream():
                data = doc.to_dict()
                recent_count += 1
                
                # Count countries
                country = data.get('country', 'Unknown')
                countries[country] = countries.get(country, 0) + 1
                
                # Analyze user agents for browser stats
                user_agent = data.get('user_agent', '')
                if 'Chrome' in user_agent:
                    browser = 'Chrome'
                elif 'Firefox' in user_agent:
                    browser = 'Firefox'
                elif 'Safari' in user_agent:
                    browser = 'Safari'
                elif 'Edge' in user_agent:
                    browser = 'Edge'
                else:
                    browser = 'Other'
                
                user_agents[browser] = user_agents.get(browser, 0) + 1
            
            # Get scan events stats (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc).replace(day=max(1, datetime.now(timezone.utc).day-30))
            scan_events_ref = (self.db.collection('scan_events')
                             .where('timestamp', '>=', thirty_days_ago))
            
            scan_types = {}
            total_scan_events = 0
            
            for doc in scan_events_ref.stream():
                data = doc.to_dict()
                total_scan_events += 1
                scan_type = data.get('scan_type', 'unknown')
                scan_types[scan_type] = scan_types.get(scan_type, 0) + 1
            
            # Sort statistics
            top_countries = dict(sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10])
            top_browsers = dict(sorted(user_agents.items(), key=lambda x: x[1], reverse=True)[:5])
            scan_type_stats = dict(sorted(scan_types.items(), key=lambda x: x[1], reverse=True))
            
            return {
                'success': True,
                'total_all_time_visits': total_docs,
                'current_month_visitors': current_month_visitors,
                'current_month_visits': current_month_visits,
                'current_month_scans': current_month_scans,
                'daily_stats': daily_stats,
                'top_countries_recent': top_countries,
                'browser_stats': top_browsers,
                'scan_type_stats': scan_type_stats,
                'total_scan_events_30d': total_scan_events,
                'recent_activity_analyzed': recent_count,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'firebase_status': 'connected'
            }
            
        except Exception as e:
            print(f"❌ Error getting user stats: {str(e)}")
            return {
                'error': f'Analytics error: {str(e)}',
                'code': 500,
                'firebase_status': 'error'
            }
    
    def track_scan_event(self, ip_address, scan_type, country=None, session_id=None):
        """Track scanning events for comprehensive analytics"""
        try:
            if not self.is_ready():
                return False
            
            event_data = {
                'timestamp': datetime.now(timezone.utc),
                'ip_hash': self._hash_ip(ip_address),
                'scan_type': scan_type or 'unknown',
                'country': country,
                'session_id': session_id,
            }
            
            # Store scan event
            self.db.collection('scan_events').add(event_data)
            
            # Update daily scan counter
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            daily_ref = self.db.collection('daily_stats').document(today)
            
            # Use transaction for atomic updates
            @firestore.transactional
            def update_scan_stats(transaction, daily_ref, scan_type):
                doc = daily_ref.get(transaction=transaction)
                if doc.exists:
                    transaction.update(daily_ref, {
                        'total_scans': firestore.Increment(1),
                        f'scans_{scan_type}': firestore.Increment(1),
                        'last_scan': datetime.now(timezone.utc)
                    })
                else:
                    transaction.set(daily_ref, {
                        'date': today,
                        'unique_visitors': 0,
                        'total_visits': 0,
                        'total_scans': 1,
                        f'scans_{scan_type}': 1,
                        'last_scan': datetime.now(timezone.utc),
                        'last_updated': datetime.now(timezone.utc)
                    })
            
            transaction = self.db.transaction()
            update_scan_stats(transaction, daily_ref, scan_type)
            
            print(f"🔍 Scan event tracked: {scan_type}")
            return True
            
        except Exception as e:
            print(f"⚠️  Error tracking scan event: {str(e)}")
            return False
    
    def health_check(self):
        """Perform Firebase health check"""
        try:
            if not self.is_ready():
                return {
                    'status': 'disconnected',
                    'firebase_initialized': self.initialized,
                    'firestore_client': self.db is not None
                }
            
            # Test Firestore connection
            test_ref = self.db.collection('_health_check').document('test')
            test_ref.set({
                'timestamp': datetime.now(timezone.utc),
                'status': 'healthy'
            })
            
            # Try to read it back
            doc = test_ref.get()
            if doc.exists:
                # Clean up test document
                test_ref.delete()
                return {
                    'status': 'healthy',
                    'firebase_initialized': True,
                    'firestore_client': True,
                    'connection_test': 'passed'
                }
            else:
                return {
                    'status': 'error',
                    'firebase_initialized': True,
                    'firestore_client': True,
                    'connection_test': 'failed'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'firebase_initialized': self.initialized,
                'firestore_client': self.db is not None,
                'error': str(e)
            }

# Global Firebase service instance
firebase_service = None

def init_firebase(config):
    """Initialize Firebase service with configuration"""
    global firebase_service
    try:
        firebase_service = FirebaseService(config)
        print("🚀 Firebase service initialization completed")
        return firebase_service
    except Exception as e:
        print(f"❌ Failed to initialize Firebase service: {str(e)}")
        return None

def get_firebase_service():
    """Get the global Firebase service instance"""
    return firebase_service