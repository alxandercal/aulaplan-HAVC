"""Bootstrap ADMIN interactivo SOLO en Auth/Firestore emulators."""
import argparse
import getpass
import os
from _bootstrap import setup
setup()
from firebase_admin import auth
from src.firebase.client import ensure_firebase, get_db


def main():
    parser = argparse.ArgumentParser(description='Crear ADMIN para entorno de emuladores')
    parser.add_argument('--email', required=True)
    parser.add_argument('--name', default='Administrador')
    args = parser.parse_args()
    if not os.getenv('FIREBASE_AUTH_EMULATOR_HOST') or not os.getenv('FIRESTORE_EMULATOR_HOST'):
        raise SystemExit('Por seguridad, crea_admin solo funciona con emuladores. Consulta docs/INSTALACION.md para produccion.')
    password = getpass.getpass('Contraseña del ADMIN (minimo 8 caracteres): ')
    if len(password) < 8:
        raise SystemExit('La contraseña debe contener al menos 8 caracteres.')
    ensure_firebase()
    try:
        user = auth.get_user_by_email(args.email)
        print('Usuario existente; no se modificara su contraseña.')
    except auth.UserNotFoundError:
        user = auth.create_user(email=args.email, password=password, display_name=args.name, email_verified=True)
    profile = {
        'email': user.email, 'display_name': user.display_name or args.name,
        'role': 'ADMIN', 'active': True,
    }
    get_db().collection('users').document(user.uid).set(profile, merge=True)
    print(f'Administrador listo: {user.email} (uid={user.uid})')


if __name__ == '__main__':
    main()
