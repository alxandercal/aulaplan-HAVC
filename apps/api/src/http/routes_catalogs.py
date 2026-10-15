from flask import Blueprint, jsonify, request
from src.auth.security import require_roles
from src.core.errors import ApiError
from src.http.responses import to_jsonable
from src.services.catalogs import (
    academic_periods_service, availability_service, constraints_service,
    groups_service, offerings_service, rooms_service, subjects_service,
    teachers_service, time_blocks_service,
)

catalogs_bp = Blueprint('catalogs', __name__)
SERVICES = {
    'academic-periods': academic_periods_service,
    'teachers': teachers_service,
    'subjects': subjects_service,
    'groups': groups_service,
    'rooms': rooms_service,
    'time-blocks': time_blocks_service,
    'offerings': offerings_service,
    'availability': availability_service,
    'constraints': constraints_service,
}

def get_service(resource):
    service = SERVICES.get(resource)
    if service is None:
        raise ApiError('Recurso no encontrado', 404, 'NOT_FOUND')
    return service

@catalogs_bp.get('/<resource>')
def list_records(resource):
    service = get_service(resource)
    allowed = set(service.create_schema.model_fields)
    filters = {k: v for k, v in request.args.items() if k in allowed}
    return jsonify(to_jsonable(service.list(filters)))

@catalogs_bp.get('/<resource>/<document_id>')
def get_record(resource, document_id):
    return jsonify(to_jsonable(get_service(resource).get(document_id)))

@catalogs_bp.post('/<resource>')
@require_roles('ADMIN', 'COORDINATOR')
def create_record(resource):
    return jsonify(to_jsonable(get_service(resource).create(request.get_json(silent=True) or {}))), 201

@catalogs_bp.put('/<resource>/<document_id>')
@require_roles('ADMIN', 'COORDINATOR')
def update_record(resource, document_id):
    return jsonify(to_jsonable(get_service(resource).update(document_id, request.get_json(silent=True) or {})))

@catalogs_bp.delete('/<resource>/<document_id>')
@require_roles('ADMIN', 'COORDINATOR')
def delete_record(resource, document_id):
    get_service(resource).delete(document_id)
    return '', 204
