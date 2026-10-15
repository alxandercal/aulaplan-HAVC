"""Versiones: DRAFT -> PUBLISHED. Una publicacion por periodo (puntero transaccional)."""
from datetime import datetime, timezone
from flask import Blueprint, g, jsonify, request
from pydantic import BaseModel, Field
from firebase_admin import firestore
from src.auth.security import require_roles
from src.core.errors import ApiError
from src.http.responses import to_jsonable
from src.firebase.client import get_db
from src.repositories.base import FirestoreRepository
from src.services.scheduler import SchedulingInput, generate_schedule

schedules_bp = Blueprint('schedules', __name__)
repo = FirestoreRepository('schedules')
periods = FirestoreRepository('academic_periods')

class GenerateRequest(BaseModel):
    academic_period_id: str = Field(min_length=1)
    max_nodes: int = Field(default=50000, ge=100, le=200000)

@schedules_bp.get('/schedules')
def list_schedules():
    filters = {}
    if request.args.get('academic_period_id'):
        filters['academic_period_id'] = request.args['academic_period_id']
    rows = repo.list(filters)
    return jsonify(to_jsonable(sorted(rows, key=lambda r: (r.get('created_at', ''), r.get('id', '')), reverse=True)))

@schedules_bp.get('/schedules/<schedule_id>')
def get_schedule(schedule_id):
    return jsonify(to_jsonable(repo.get(schedule_id)))

@schedules_bp.post('/schedules/generate')
@require_roles('ADMIN', 'COORDINATOR')
def generate():
    payload = GenerateRequest.model_validate(request.get_json(silent=True) or {})
    period = periods.get(payload.academic_period_id)
    if not period.get('active', True):
        raise ApiError('Periodo academico inactivo', 422, 'INACTIVE_PERIOD')
    def rows(name):
        return FirestoreRepository(name).list()
    input_data = SchedulingInput(
        period_id=payload.academic_period_id,
        teachers=rows('teachers'), subjects=rows('subjects'),
        groups=rows('groups'), rooms=rows('rooms'), blocks=rows('time_blocks'),
        offerings=rows('course_offerings'), availability=rows('teacher_availability'),
        constraints=rows('constraints'),
    )
    result = generate_schedule(input_data, payload.max_nodes)
    db = get_db()
    period_ref = db.collection('academic_periods').document(payload.academic_period_id)
    schedule_ref = db.collection('schedules').document()
    now = datetime.now(timezone.utc)
    transaction = db.transaction()

    @firestore.transactional
    def save_version(tx):
        # Asegura consecutivo de versiones incluso con peticiones concurrentes.
        snapshot = period_ref.get(transaction=tx)
        if not snapshot.exists or not (snapshot.to_dict() or {}).get('active', True):
            raise ApiError('Periodo inexistente o inactivo', 422, 'INACTIVE_PERIOD')
        version = int((snapshot.to_dict() or {}).get('schedule_sequence', 0)) + 1
        tx.update(period_ref, {'schedule_sequence': version, 'updated_at': now})
        tx.set(schedule_ref, {
            **result, 'academic_period_id': payload.academic_period_id,
            'version': version, 'status': 'DRAFT',
            'created_by': g.current_user['uid'],
            'created_at': now, 'updated_at': now,
        })
        return version
    save_version(transaction)
    return jsonify(to_jsonable(repo.get(schedule_ref.id))), 201

@schedules_bp.post('/schedules/<schedule_id>/publish')
@require_roles('ADMIN', 'COORDINATOR')
def publish(schedule_id):
    db = get_db()
    doc = db.collection('schedules').document(schedule_id)
    transaction = db.transaction()

    @firestore.transactional
    def update(tx):
        target = doc.get(transaction=tx)
        if not target.exists:
            raise ApiError('Horario no encontrado', 404, 'NOT_FOUND')
        data = target.to_dict() or {}
        if not data.get('entries') or data.get('status') not in ('DRAFT', 'PUBLISHED'):
            raise ApiError('Version no publicable', 409, 'INVALID_STATUS')
        period_ref = db.collection('academic_periods').document(data['academic_period_id'])
        period = period_ref.get(transaction=tx)
        if not period.exists or not (period.to_dict() or {}).get('active', True):
            raise ApiError('Periodo inexistente o inactivo', 422, 'INACTIVE_PERIOD')
        previous_id = (period.to_dict() or {}).get('published_schedule_id')
        previous_ref = db.collection('schedules').document(previous_id) if previous_id else None
        # Todas las lecturas antes de escribir, como requiere Firestore transaction.
        previous = previous_ref.get(transaction=tx) if previous_ref and previous_id != schedule_id else None
        now = datetime.now(timezone.utc)
        if previous and previous.exists:
            tx.update(previous_ref, {'status': 'ARCHIVED', 'updated_at': now})
        tx.update(doc, {'status': 'PUBLISHED', 'published_at': now, 'updated_at': now})
        tx.update(period_ref, {'published_schedule_id': schedule_id, 'updated_at': now})
    update(transaction)
    return jsonify(to_jsonable(repo.get(schedule_id)))
