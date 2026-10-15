"""Carga demo idempotente; solo emuladores para proteger datos reales."""
import os
from _bootstrap import setup
setup()
from src.firebase.client import get_db


def main():
    if not os.getenv('FIRESTORE_EMULATOR_HOST'):
        raise SystemExit('Seed demo bloqueado en produccion: falta FIRESTORE_EMULATOR_HOST')
    db = get_db()

    def create(name, key, payload):
        ref = db.collection(name).document(key)
        if not ref.get().exists:
            ref.set(payload)
            return True
        return False

    counts = {}
    def put(collection, doc_id, doc):
        counts[collection] = counts.get(collection, 0) + int(create(collection, doc_id, doc))

    put('academic_periods', '2026-B', {
        'code': '2026-B', 'name': 'Agosto - Diciembre 2026',
        'start_date': '2026-08-01', 'end_date': '2026-12-15', 'active': True,
    })
    for code, name, email, daily, weekly in [
        ('DOC-001', 'Andrea Morales', 'andrea@example.test', 4, 16),
        ('DOC-002', 'Luis Romero', 'luis@example.test', 4, 16),
    ]:
        put('teachers', code, {'code': code, 'name': name, 'email': email, 'active': True, 'max_daily_blocks': daily, 'max_weekly_blocks': weekly})
    for code, name, count, kind in [
        ('MAT-001', 'Programacion', 3, 'COMPUTER_LAB'),
        ('MAT-002', 'Redes', 2, 'CLASSROOM'),
        ('MAT-003', 'Bases de datos', 2, 'COMPUTER_LAB'),
    ]:
        put('subjects', code, {'code': code, 'name': name, 'weekly_blocks': count, 'required_room_type': kind, 'active': True})
    for code, size in [('GRP-A', 28), ('GRP-B', 25)]:
        put('groups', code, {'code': code, 'name': 'Grupo ' + code[-1], 'student_count': size, 'academic_period_id': '2026-B', 'active': True})
    for code, name, size, kind in [
        ('A-101', 'Aula 101', 40, 'CLASSROOM'),
        ('A-102', 'Aula 102', 35, 'CLASSROOM'),
        ('LAB-01', 'Laboratorio de computo 1', 32, 'COMPUTER_LAB'),
        ('LAB-02', 'Laboratorio de computo 2', 30, 'COMPUTER_LAB'),
    ]:
        put('rooms', code, {'code': code, 'name': name, 'capacity': size, 'type': kind, 'building': 'Edificio A', 'active': True})
    days = ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY')
    slots = [('08:00', '09:30'), ('09:30', '11:00'), ('11:00', '12:30'), ('12:30', '14:00')]
    for day in days:
        for order, (start, end) in enumerate(slots, 1):
            put('time_blocks', f'{day[:3]}-{order:02}', {
                'day': day, 'start_time': start, 'end_time': end, 'order': order, 'active': True,
            })
    for code, subject, group, teacher in [
        ('OF-001', 'MAT-001', 'GRP-A', 'DOC-001'),
        ('OF-002', 'MAT-002', 'GRP-A', 'DOC-002'),
        ('OF-003', 'MAT-003', 'GRP-B', 'DOC-002'),
        ('OF-004', 'MAT-001', 'GRP-B', 'DOC-001'),
    ]:
        put('course_offerings', code, {'academic_period_id': '2026-B', 'subject_id': subject, 'group_id': group, 'teacher_id': teacher, 'active': True})
    put('teacher_availability', 'AV-001', {'teacher_id': 'DOC-001', 'time_block_id': 'MON-01', 'available': False, 'preference_weight': 0})
    put('teacher_availability', 'AV-002', {'teacher_id': 'DOC-002', 'time_block_id': 'TUE-01', 'available': True, 'preference_weight': 10})
    print('Seed ejecutado (nuevos por colección):', counts)
    print('Periodo demo: 2026-B; ofertas: OF-001 a OF-004; 10 sesiones semanales.')


if __name__ == '__main__':
    main()
