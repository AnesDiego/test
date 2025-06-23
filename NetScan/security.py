from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta
import time
from collections import defaultdict
import hashlib

class SecurityMiddleware:
    def __init__(self, app=None):
        self.app = app
        self.rate_limits = defaultdict(list)
        self.blocked_ips = set()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware with Flask app"""
        self.app = app
        
        @app.before_request
        def before_request():
            # Security headers
            g.start_time = time.time()
            
            # Block malicious IPs
            if request.remote_addr in self.blocked_ips:
                return jsonify({'error': 'Access denied'}), 403
            
            # Basic rate limiting
            if not self.check_rate_limit(request.remote_addr):
                return jsonify({'error': 'Rate limit exceeded'}), 429
        
        @app.after_request
        def after_request(response):
            # Add security headers
            if hasattr(app.config, 'SECURITY_HEADERS'):
                for header, value in app.config.SECURITY_HEADERS.items():
                    response.headers[header] = value
            
            # CORS headers for API endpoints
            if request.endpoint and request.endpoint.startswith('api'):
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            
            return response
    
    def check_rate_limit(self, ip_address, limit=100, window=3600):
        """Check if IP is within rate limit"""
        now = time.time()
        
        # Clean old entries
        self.rate_limits[ip_address] = [
            timestamp for timestamp in self.rate_limits[ip_address]
            if now - timestamp < window
        ]
        
        # Check limit
        if len(self.rate_limits[ip_address]) >= limit:
            # Block IP if repeatedly exceeding limits
            if len(self.rate_limits[ip_address]) > limit * 2:
                self.blocked_ips.add(ip_address)
            return False
        
        # Add current request
        self.rate_limits[ip_address].append(now)
        return True
    
    def require_admin_key(self, f):
        """Decorator to require admin key for sensitive endpoints"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
            
            if not admin_key or admin_key != self.app.config.get('ADMIN_SECRET_KEY'):
                return jsonify({'error': 'Admin access required'}), 401
            
            return f(*args, **kwargs)
        return decorated_function

def validate_ip_input(ip_input):
    """Validate IP address input to prevent injection attacks"""
    import ipaddress
    import re
    
    # Remove whitespace
    ip_input = ip_input.strip()
    
    # Check for basic patterns that might indicate malicious input
    dangerous_patterns = [
        r'[;&|`$()<>]',  # Shell injection
        r'script|javascript|vbscript',  # Script injection
        r'<|>',  # HTML injection
        r'union|select|drop|delete|insert|update',  # SQL injection
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, ip_input, re.IGNORECASE):
            raise ValueError("Invalid input detected")
    
    # Validate IP format
    try:
        ipaddress.ip_address(ip_input)
        return ip_input
    except ValueError:
        # Try to validate as hostname
        if re.match(r'^[a-zA-Z0-9.-]+$', ip_input) and len(ip_input) <= 253:
            return ip_input
        else:
            raise ValueError("Invalid IP address or hostname format")

def sanitize_output(data):
    """Sanitize output data to prevent XSS"""
    if isinstance(data, dict):
        return {key: sanitize_output(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_output(item) for item in data]
    elif isinstance(data, str):
        # Basic HTML escaping
        return (data.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
    else:
        return data
