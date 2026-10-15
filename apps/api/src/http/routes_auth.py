from flask import Blueprint, g, jsonify, request
from firebase_admin import auth
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from src.auth.security import require_roles
from src.core.errors import ApiError
from src.firebase.client import ensure_firebase
from src.http.responses import to_jsonable
from src.repositories.base import FirestoreRepository

users_bp = Blueprint('users', __name__)
repo = FirestoreRepository('users')

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=120)
    role: Literal['ADMIN', 'COORDINATOR', 'VIEWER'] = 'VIEWER'

class UserUpdate(BaseModel):
    display_name: str = Field(min_length=2, max_length=120)
    role: Literal['ADMIN', 'COORDINATOR', 'VIEWER']
    active: bool

@users_bp.get('/auth/me')
def me():
    return jsonify(g.current_user)

@users_bp.get('/users')
@require_roles('ADMIN')
def list_users():
    result = repo.list()
    return jsonify(to_jsonable([{'uid': r['id'], **{k:v for k,v in r.items() if k != 'id'}} for r in result]))

@users_bp.post('/users')
@require_roles('ADMIN')
def create_user():
    data = UserCreate.model_validate(request.get_json(silent=True) or {})
    ensure_firebase()
    try:
        user = auth.create_user(email=data.email, password=data.password, display_name=data.display_name)
    except Exception as exc:
        raise ApiError('No fue posible crear usuario en Firebase Auth (correo duplicado o datos invalidos)', 409, 'USER_CREATION_FAILED') from exc
    profile = {'email': data.email, 'display_name': data.display_name, 'role': data.role, 'active': True}
    try:
        repo.collection.document(user.uid).set(profile)
    except Exception:
        auth.delete_user(user.uid)
        raise
    return jsonify({'uid': user.uid, **profile}), 201

@users_bp.put('/users/<uid>')
@require_roles('ADMIN')
def update_user(uid):
    data = UserUpdate.model_validate(request.get_json(silent=True) or {})
    if uid == g.current_user['uid'] and (not data.active or data.role != 'ADMIN'):
        raise ApiError('No puedes desactivar ni quitar tu propio rol ADMIN', 409, 'SELF_ROLE_CHANGE')
    repo.update(uid, data.model_dump())
    return jsonify(to_jsonable({'uid': uid, **repo.get(uid)}))
