from functools import wraps
from flask import g, request
from firebase_admin import auth
from src.core.errors import ApiError
from src.repositories.base import FirestoreRepository
from src.firebase.client import ensure_firebase

users_repository = FirestoreRepository('users')

def authenticate_request():
    if request.method == 'OPTIONS' or request.path == '/health':
        return
    authorization = request.headers.get('Authorization', '')
    if not authorization.startswith('Bearer '):
        raise ApiError('Autenticacion requerida', 401, 'UNAUTHENTICATED')
    token = authorization[7:].strip()
    if not token:
        raise ApiError('Token requerido', 401, 'UNAUTHENTICATED')
    try:
        ensure_firebase()
        decoded = auth.verify_id_token(token, check_revoked=True)
    except Exception as exc:
        raise ApiError('Token invalido o expirado', 401, 'UNAUTHENTICATED') from exc
    uid = decoded['uid']
    try:
        profile = users_repository.get(uid)
    except ApiError as exc:
        raise ApiError('Perfil no autorizado', 403, 'PROFILE_NOT_FOUND') from exc
    if not profile.get('active', True):
        raise ApiError('Usuario inactivo', 403, 'INACTIVE_USER')
    g.current_user = {
        'uid': uid, 'email': decoded.get('email', ''),
        'display_name': profile.get('display_name', ''),
        'role': profile.get('role', 'VIEWER'), 'active': True,
    }

def require_roles(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            if user is None or user.get('role') not in roles:
                raise ApiError('Permisos insuficientes', 403, 'FORBIDDEN')
            return fn(*args, **kwargs)
        return wrapper
    return decorator
