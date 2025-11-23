from .models import UserSession
from django.utils import timezone





def get_or_create_session(request):
    """
    Ensures a session exists and tracks it in the database
    """
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    
    # Get or create UserSession
    user_session, created = UserSession.objects.get_or_create(
        session_key=session_key,
        defaults={'products_count': 0}
    )
    
    return user_session


def update_session_activity(request):
    """
    Updates the last activity timestamp for the session
    """
    if request.session.session_key:
        UserSession.objects.filter(
            session_key=request.session.session_key
        ).update(last_activity=timezone.now())


def get_session_products(request):
    """
    Retrieves all products associated with the current session
    """
    from .models import Product
    
    if not request.session.session_key:
        return Product.objects.none()
    
    return Product.objects.filter(
        session_key=request.session.session_key
    ).order_by('-created_at')


def cleanup_old_sessions(days=7):
    """
    Removes sessions and associated data older than specified days
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import Product
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # Get old sessions
    old_sessions = UserSession.objects.filter(last_activity__lt=cutoff_date)
    session_keys = list(old_sessions.values_list('session_key', flat=True))
    
    # Delete associated products (cascade will handle designs)
    Product.objects.filter(session_key__in=session_keys).delete()
    
    # Delete sessions
    old_sessions.delete()
