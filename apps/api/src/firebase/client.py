
"""Inicialización centralizada de Firebase Admin SDK."""

import os
from functools import lru_cache

import firebase_admin
from firebase_admin import credentials, firestore
from google.auth.credentials import AnonymousCredentials


class EmulatorCredentials(credentials.Base):
    """Credenciales exclusivas para los emuladores."""

    def __init__(self, project_id: str):
        self.project_id = project_id

    def get_credential(self):
        return AnonymousCredentials()

    def get_project_id(self):
        return self.project_id


@lru_cache(maxsize=1)
def ensure_firebase():
    project_id = os.getenv("FIREBASE_PROJECT_ID")

    if not project_id:
        raise RuntimeError("Falta FIREBASE_PROJECT_ID")

    auth_host = os.getenv("FIREBASE_AUTH_EMULATOR_HOST")
    firestore_host = os.getenv("FIRESTORE_EMULATOR_HOST")

    if bool(auth_host) != bool(firestore_host):
        raise RuntimeError(
            "Configura ambos emuladores o ninguno."
        )

    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    if auth_host and firestore_host:
        credential = EmulatorCredentials(project_id)
    else:
        credential = credentials.ApplicationDefault()

    return firebase_admin.initialize_app(
        credential=credential,
        options={"projectId": project_id},
    )


@lru_cache(maxsize=1)
def get_db():
    ensure_firebase()
    return firestore.client()
 