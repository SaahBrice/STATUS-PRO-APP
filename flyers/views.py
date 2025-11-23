from django.shortcuts import render
from .session_utils import get_or_create_session

def home(request):
    """Landing page view"""
    # Initialize session
    user_session = get_or_create_session(request)
    
    context = {
        'session_key': request.session.session_key
    }
    
    return render(request, 'home.html', context)
