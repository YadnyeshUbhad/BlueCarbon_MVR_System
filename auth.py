"""
Authentication utilities and decorators for secure access control
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request
from db import verify_user


def login_required(roles=None):
    """
    Decorator to require login and optionally specific roles
    @roles: list of allowed roles, or None for any authenticated user
    """
    if roles is None:
        roles = []
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                # Determine which login page to redirect to based on the route
                if request.endpoint and 'admin' in request.endpoint:
                    return redirect(url_for('admin.login'))
                elif request.endpoint and 'ngo' in request.endpoint:
                    return redirect(url_for('ngo.ngo_login'))
                elif request.endpoint and 'industry' in request.endpoint:
                    return redirect(url_for('industry.industry_login'))
                else:
                    return redirect(url_for('public_landing_page'))
            
            if roles and session.get('user_role') not in roles:
                flash('Access denied. Insufficient privileges.', 'error')
                return redirect(url_for('public_landing_page'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def authenticate_user(email, password, role):
    """
    Authenticate user with email, password, and role
    Returns user data if successful, None otherwise
    """
    return verify_user(email, password, role)


def login_user(user_data):
    """
    Log in a user by setting session variables
    """
    session['user_id'] = user_data['id']
    session['user_email'] = user_data['email']
    session['user_role'] = user_data['role']
    session['user_name'] = user_data['name']
    session['user_organization'] = user_data['organization']


def logout_user():
    """
    Log out the current user by clearing session
    """
    session.clear()


def get_current_user():
    """
    Get current user info from session
    """
    if 'user_id' not in session:
        return None
    
    return {
        'id': session['user_id'],
        'email': session['user_email'],
        'role': session['user_role'],
        'name': session['user_name'],
        'organization': session['user_organization']
    }


def is_authenticated():
    """
    Check if user is authenticated
    """
    return 'user_id' in session


def has_role(role):
    """
    Check if current user has specific role
    """
    return session.get('user_role') == role


def has_any_role(roles):
    """
    Check if current user has any of the specified roles
    """
    return session.get('user_role') in roles if roles else False