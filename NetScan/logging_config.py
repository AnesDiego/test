import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json

def setup_logging(app):
    """Configure application logging"""
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Main application log
    app_handler = RotatingFileHandler(
        'logs/netscan.log', 
        maxBytes=10240000,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.INFO)
    app_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    app_handler.setFormatter(app_formatter)
    
    # Error log
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10240000,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(app_formatter)
    
    # Security log for suspicious activities
    security_handler = RotatingFileHandler(
        'logs/security.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    security_handler.setLevel(logging.WARNING)
    security_formatter = logging.Formatter(
        '%(asctime)s SECURITY %(levelname)s: %(message)s'
    )
    security_handler.setFormatter(security_formatter)
    
    # Analytics log for user tracking
    analytics_handler = RotatingFileHandler(
        'logs/analytics.log',
        maxBytes=10240000,  # 10MB
        backupCount=30  # Keep more analytics data
    )
    analytics_handler.setLevel(logging.INFO)
    analytics_formatter = logging.Formatter(
        '%(asctime)s ANALYTICS: %(message)s'
    )
    analytics_handler.setFormatter(analytics_formatter)
    
    # Configure app logger
    app.logger.addHandler(app_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)
    
    # Create separate loggers
    security_logger = logging.getLogger('security')
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.WARNING)
    
    analytics_logger = logging.getLogger('analytics')
    analytics_logger.addHandler(analytics_handler)
    analytics_logger.setLevel(logging.INFO)
    
    return {
        'app': app.logger,
        'security': security_logger,
        'analytics': analytics_logger
    }

def log_user_activity(request, action, details=None):
    """Log user activity for analytics"""
    analytics_logger = logging.getLogger('analytics')
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'action': action,
        'url': request.url,
        'method': request.method,
        'details': details
    }
    
    analytics_logger.info(json.dumps(log_data))

def log_security_event(request, event_type, description, severity='WARNING'):
    """Log security events"""
    security_logger = logging.getLogger('security')
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'event_type': event_type,
        'description': description,
        'severity': severity,
        'url': request.url
    }
    
    if severity == 'CRITICAL':
        security_logger.critical(json.dumps(log_data))
    elif severity == 'ERROR':
        security_logger.error(json.dumps(log_data))
    else:
        security_logger.warning(json.dumps(log_data))

def monitor_performance(func):
    """Decorator to monitor function performance"""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log slow requests (> 5 seconds)
            if execution_time > 5:
                app_logger = logging.getLogger('flask.app')
                app_logger.warning(
                    f'Slow request: {func.__name__} took {execution_time:.2f}s'
                )
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            app_logger = logging.getLogger('flask.app')
            app_logger.error(
                f'Error in {func.__name__} after {execution_time:.2f}s: {str(e)}'
            )
            raise
    
    return wrapper
