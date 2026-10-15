from typing import Type
from pydantic import BaseModel
from src.core.errors import ApiError
from src.repositories.base import FirestoreRepository

class CrudService:
    def __init__(self, repository: FirestoreRepository, create_schema: Type[BaseModel], update_schema: Type[BaseModel], unique_fields: tuple[str, ...] = ()):
        self.repository = repository
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.unique_fields = unique_fields

    def list(self, filters=None):
        return self.repository.list(filters)

    def get(self, document_id):
        return self.repository.get(document_id)

    def create(self, raw):
        data = self.create_schema.model_validate(raw).model_dump()
        self._assert_unique(data)
        self._assert_references(data)
        self._assert_business_rules(data)
        return self.repository.create(data)

    def update(self, document_id, raw):
        data = self.update_schema.model_validate(raw).model_dump()
        self._assert_unique(data, document_id)
        self._assert_references(data)
        self._assert_business_rules(data, document_id)
        return self.repository.update(document_id, data)

    def delete(self, document_id):
        # Evitar borrar catalogos referenciados por configuraciones y horarios.
        checks = {
            'academic_periods': [('groups', 'academic_period_id'), ('course_offerings', 'academic_period_id'), ('schedules', 'academic_period_id')],
            'teachers': [('course_offerings', 'teacher_id'), ('teacher_availability', 'teacher_id')],
            'subjects': [('course_offerings', 'subject_id')],
            'groups': [('course_offerings', 'group_id')],
            'rooms': [('schedules', 'room_id')],
            'time_blocks': [('teacher_availability', 'time_block_id')],
        }
        for collection, field in checks.get(self.repository.collection_name, []):
            if FirestoreRepository(collection).exists_by_field(field, document_id):
                raise ApiError('Registro vinculado; no puede eliminarse', 409, 'REFERENCE_IN_USE')
        nested_key = {
            'teachers': 'teacher_id', 'subjects': 'subject_id', 'groups': 'group_id',
            'rooms': 'room_id', 'time_blocks': 'time_block_id',
            'course_offerings': 'offering_id',
        }.get(self.repository.collection_name)
        if nested_key:
            for schedule in FirestoreRepository('schedules').list():
                if any(entry.get(nested_key) == document_id for entry in schedule.get('entries', [])):
                    raise ApiError('Registro utilizado por un horario; no puede eliminarse', 409, 'REFERENCE_IN_USE')
        self.repository.delete(document_id)

    def _assert_unique(self, data, exclude_id=None):
        for field in self.unique_fields:
            if field in data and self.repository.exists_by_field(field, data[field], exclude_id):
                raise ApiError(f'El campo {field} ya existe', 409, 'DUPLICATE_VALUE')

    def _assert_references(self, data):
        mapping = {
            'academic_period_id': 'academic_periods',
            'teacher_id': 'teachers', 'subject_id': 'subjects',
            'group_id': 'groups', 'room_id': 'rooms', 'time_block_id': 'time_blocks',
        }
        # Generaciones guardan sus propios datos; estos campos son FKs en los catalogos.
        for key, collection in mapping.items():
            if key in data and data[key]:
                try:
                    FirestoreRepository(collection).get(data[key])
                except ApiError as exc:
                    raise ApiError(f'Referencia invalida: {key}', 422, 'INVALID_REFERENCE', {'field': key, 'id': data[key]}) from exc

    def _assert_business_rules(self, data: dict, exclude_id: str | None = None) -> None:
        name = self.repository.collection_name
        if name == 'academic_periods' and data['start_date'] > data['end_date']:
            raise ApiError('La fecha de inicio debe ser anterior al fin', 422, 'INVALID_DATES')
        if name == 'time_blocks' and data['start_time'] >= data['end_time']:
            raise ApiError('La hora de inicio debe ser menor a fin', 422, 'INVALID_TIMES')
        if name == 'course_offerings':
            group = FirestoreRepository('groups').get(data['group_id'])
            if group.get('academic_period_id') != data['academic_period_id']:
                raise ApiError('El grupo debe pertenecer al periodo de la oferta', 422, 'PERIOD_MISMATCH')
            for row in self.repository.list({'academic_period_id': data['academic_period_id']}):
                if row['id'] != exclude_id and all(row.get(k) == data[k] for k in ('subject_id', 'group_id', 'teacher_id')):
                    raise ApiError('Ya existe esta oferta academica', 409, 'DUPLICATE_OFFERING')
        if name == 'teacher_availability':
            for row in self.repository.list({'teacher_id': data['teacher_id']}):
                if row['id'] != exclude_id and row.get('time_block_id') == data['time_block_id']:
                    raise ApiError('Ya existe disponibilidad para ese profesor y bloque', 409, 'DUPLICATE_AVAILABILITY')
        if name == 'constraints':
            allowed = {
                'TEACHER_UNAVAILABLE': ('HARD', 'TEACHER', 'teachers'),
                'ROOM_UNAVAILABLE': ('HARD', 'ROOM', 'rooms'),
                'GROUP_UNAVAILABLE': ('HARD', 'GROUP', 'groups'),
                'TEACHER_PREFERRED_DAY': ('SOFT', 'TEACHER', 'teachers'),
            }
            expected = allowed.get(data['type'])
            if expected is None:
                raise ApiError('Tipo de restriccion no admitido', 422, 'INVALID_CONSTRAINT')
            priority, target_type, collection = expected
            if (data['priority'], data['target_type']) != (priority, target_type):
                raise ApiError('Prioridad y entidad no coinciden con el tipo', 422, 'INVALID_CONSTRAINT')
            try:
                FirestoreRepository(collection).get(data['target_id'])
            except ApiError as exc:
                raise ApiError('La entidad referida por la restriccion no existe', 422, 'INVALID_REFERENCE') from exc
            params = data.get('params') or {}
            if not isinstance(params, dict):
                raise ApiError('params debe ser un objeto', 422, 'INVALID_CONSTRAINT')
            if any(k not in ('day', 'time_block_id') for k in params):
                raise ApiError('Parametro de restriccion desconocido', 422, 'INVALID_CONSTRAINT')
            day = params.get('day')
            if day is not None and day not in ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'):
                raise ApiError('Dia de restriccion invalido', 422, 'INVALID_CONSTRAINT')
            if params.get('time_block_id'):
                self._get_block(params['time_block_id'])
            if data['type'] == 'TEACHER_PREFERRED_DAY' and not day:
                raise ApiError('La preferencia requiere params.day', 422, 'INVALID_CONSTRAINT')
            if not day and not params.get('time_block_id'):
                raise ApiError('La restriccion requiere day o time_block_id', 422, 'INVALID_CONSTRAINT')

    @staticmethod
    def _get_block(block_id: str) -> None:
        try:
            FirestoreRepository('time_blocks').get(block_id)
        except ApiError as exc:
            raise ApiError('Bloque indicado en restriccion inexistente', 422, 'INVALID_REFERENCE') from exc
