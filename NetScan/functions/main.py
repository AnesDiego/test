import os
import sys

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# This is the entry point for Firebase Functions
def netscan_app(request):
    """HTTP Cloud Function entry point"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()
