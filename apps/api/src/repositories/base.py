from datetime import datetime, timezone
from typing import Any
from google.cloud.firestore_v1.base_query import FieldFilter
from src.core.errors import ApiError
from src.firebase.client import get_db

class FirestoreRepository:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    @property
    def collection(self):
        return get_db().collection(self.collection_name)

    def list(self, filters: dict[str, Any] | None = None) -> list[dict]:
        q = self.collection
        for key, value in (filters or {}).items():
            if key in ('limit', 'offset'):
                continue
            q = q.where(filter=FieldFilter(key, '==', value))
        result = []
        for snap in q.stream():
            result.append({'id': snap.id, **(snap.to_dict() or {})})
        return result

    def get(self, document_id: str) -> dict:
        snap = self.collection.document(document_id).get()
        if not snap.exists:
            raise ApiError('Registro no encontrado', 404, 'NOT_FOUND')
        return {'id': snap.id, **(snap.to_dict() or {})}

    def create(self, data: dict) -> dict:
        now = datetime.now(timezone.utc)
        doc = self.collection.document()
        doc.set({**data, 'created_at': now, 'updated_at': now})
        return self.get(doc.id)

    def update(self, document_id: str, data: dict) -> dict:
        self.get(document_id)
        # No aceptar id ni campos de auditoria desde peticiones.
        doc = self.collection.document(document_id)
        doc.update({**data, 'updated_at': datetime.now(timezone.utc)})
        return self.get(document_id)

    def delete(self, document_id: str):
        self.get(document_id)
        self.collection.document(document_id).delete()

    def exists_by_field(self, field: str, value: Any, exclude_id: str | None = None) -> bool:
        q = self.collection.where(filter=FieldFilter(field, '==', value)).limit(3)
        return any(snap.id != exclude_id for snap in q.stream())
