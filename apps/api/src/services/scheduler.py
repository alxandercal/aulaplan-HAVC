"""Planificador determinista: sin Gemini, sin LLM, sin servicios externos.

Las restricciones HARD (colisiones, capacidad, tipo de aula, disponibilidad y
carga maxima) son inviolables. Si no hay solucion no guarda horario parcial.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import Any
from src.core.errors import ApiError

DAYS = ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY')
HARD_TYPES = {'TEACHER_UNAVAILABLE', 'ROOM_UNAVAILABLE', 'GROUP_UNAVAILABLE'}
SOFT_TYPES = {'TEACHER_PREFERRED_DAY'}


def _interval_overlap(a: dict, b: dict) -> bool:
    return (a['day'] == b['day'] and a['start_time'] < b['end_time']
            and b['start_time'] < a['end_time'])


def _invalid(message: str, details: Any = None) -> ApiError:
    return ApiError(message, 422, 'SCHEDULE_VALIDATION_ERROR', details)


def _index(rows: list[dict]) -> dict[str, dict]:
    return {str(row['id']): row for row in rows}


@dataclass
class SchedulingInput:
    period_id: str
    teachers: list[dict]
    subjects: list[dict]
    groups: list[dict]
    rooms: list[dict]
    blocks: list[dict]
    offerings: list[dict]
    availability: list[dict]
    constraints: list[dict]


def generate_schedule(data: SchedulingInput, max_nodes: int = 50000) -> dict:
    if not 100 <= max_nodes <= 200000:
        raise _invalid('max_nodes debe estar entre 100 y 200000')

    teachers = _index([r for r in data.teachers if r.get('active', True)])
    subjects = _index([r for r in data.subjects if r.get('active', True)])
    groups = _index([r for r in data.groups if r.get('active', True) and r.get('academic_period_id') == data.period_id])
    rooms = _index([r for r in data.rooms if r.get('active', True)])
    blocks = _index([r for r in data.blocks if r.get('active', True)])
    offerings = [r for r in data.offerings if r.get('active', True) and r.get('academic_period_id') == data.period_id]

    if not offerings:
        raise _invalid('No hay ofertas academicas activas en el periodo')
    if not blocks or not rooms:
        raise _invalid('Captura bloques horarios y salones antes de generar')

    for block in blocks.values():
        if block.get('day') not in DAYS or str(block.get('start_time', '')) >= str(block.get('end_time', '')):
            raise _invalid('Bloque horario invalido', {'id': block['id']})
    sorted_blocks = sorted(blocks.values(), key=lambda b: (DAYS.index(b['day']), b['start_time'], str(b['id'])))
    available = {(r['teacher_id'], r['time_block_id']): r for r in data.availability if 'teacher_id' in r and 'time_block_id' in r}
    active_constraints = [r for r in data.constraints if r.get('active', True)]
    for c in active_constraints:
        supported = HARD_TYPES if c.get('priority') == 'HARD' else SOFT_TYPES if c.get('priority') == 'SOFT' else set()
        if c.get('type') not in supported:
            raise _invalid('Tipo de restriccion no implementado: ' + str(c.get('type')), {'id': c.get('id'), 'priority': c.get('priority')})
        if c.get('type') in HARD_TYPES and c.get('target_type') != c['type'].split('_')[0]:
            raise _invalid('target_type invalido para restriccion', {'id': c.get('id')})
        if c.get('type') in SOFT_TYPES and c.get('target_type') != 'TEACHER':
            raise _invalid('target_type invalido para restriccion', {'id': c.get('id')})

    tasks: list[dict] = []
    weekly_required_by_teacher = defaultdict(int)
    for offer in offerings:
        ref = {key: obj.get(offer.get(key + '_id')) for key, obj in [
            ('teacher', teachers), ('subject', subjects), ('group', groups)
        ]}
        if any(value is None for value in ref.values()):
            raise _invalid('Oferta con profesor, materia o grupo ausente/inactivo/fuera de periodo', {'offering_id': offer['id']})
        teacher = ref['teacher']
        subject = ref['subject']
        group = ref['group']
        count = int(subject.get('weekly_blocks', 0))
        if count < 1 or count > 10:
            raise _invalid('weekly_blocks invalido', {'subject_id': subject['id']})
        weekly_required_by_teacher[teacher['id']] += count
        matching_rooms = [r for r in rooms.values() if int(r.get('capacity', 0)) >= int(group.get('student_count', 0))
                          and r.get('type') == subject.get('required_room_type', 'CLASSROOM')]
        if not matching_rooms:
            raise _invalid('No hay salon con tipo y capacidad suficientes', {'offering_id': offer['id']})
        for i in range(count):
            tasks.append({'offer': offer, 'teacher': teacher, 'subject': subject, 'group': group,
                          'rooms': matching_rooms, 'lesson': i})
    for teacher_id, required in weekly_required_by_teacher.items():
        if required > int(teachers[teacher_id].get('max_weekly_blocks', 16)):
            raise _invalid('Carga semanal del profesor excedida', {'teacher_id': teacher_id, 'required': required})
    if len(tasks) > 250:
        raise _invalid('El limite actual es 250 sesiones por generacion')

    def forbidden(task: dict, block: dict, room: dict) -> bool:
        avail = available.get((task['teacher']['id'], block['id']))
        if avail is not None and not avail.get('available', True):
            return True
        for c in active_constraints:
            if c.get('priority') != 'HARD':
                continue
            target = c['type'].split('_')[0].lower()
            selected = task.get(target) if target != 'room' else room
            if selected is None or c.get('target_id') != selected['id']:
                continue
            params = c.get('params') or {}
            if not isinstance(params, dict):
                raise _invalid('params debe ser objeto', {'id': c.get('id')})
            if (params.get('time_block_id') and params['time_block_id'] == block['id']) or (
                    params.get('day') and params['day'] == block['day']):
                return True
        return False

    def preference(task: dict, block: dict) -> int:
        item = available.get((task['teacher']['id'], block['id']))
        score = int(item.get('preference_weight', 0)) if item else 0
        for c in active_constraints:
            if (c.get('priority') == 'SOFT' and c.get('type') == 'TEACHER_PREFERRED_DAY'
                    and c.get('target_id') == task['teacher']['id']
                    and (c.get('params') or {}).get('day') == block['day']):
                score += int(c.get('weight', 0))
        return score

    # Primero las ofertas mas restringidas, desempate estable para reproducibilidad.
    def candidate_options(task: dict) -> list[tuple[dict, dict, int]]:
        result = []
        for block in sorted_blocks:
            for room in sorted(task['rooms'], key=lambda r: r['id']):
                if not forbidden(task, block, room):
                    result.append((block, room, preference(task, block)))
        return sorted(result, key=lambda tup: (-tup[2], DAYS.index(tup[0]['day']), tup[0]['start_time'], tup[1]['id']))

    for task in tasks:
        task['options'] = candidate_options(task)
        if not task['options']:
            raise _invalid('Oferta sin bloque y salon compatibles', {'offering_id': task['offer']['id']})
    tasks.sort(key=lambda task: (len(task['options']), task['offer']['id'], task['lesson']))
    assigned: list[tuple[dict, dict, dict, int]] = []
    count_per_teacher_day: dict[tuple[str, str], int] = defaultdict(int)
    count_per_teacher_week: dict[str, int] = defaultdict(int)
    explored = 0
    exhausted = False

    def search(i: int) -> bool:
        nonlocal explored, exhausted
        if i == len(tasks):
            return True
        task = tasks[i]
        teacher_id, group_id = task['teacher']['id'], task['group']['id']
        if count_per_teacher_week[teacher_id] >= int(task['teacher'].get('max_weekly_blocks', 16)):
            return False
        for block, room, points in task['options']:
            explored += 1
            if explored > max_nodes:
                exhausted = True
                return False
            day_key = (teacher_id, block['day'])
            if count_per_teacher_day[day_key] >= int(task['teacher'].get('max_daily_blocks', 4)):
                continue
            conflict = False
            for existing_task, existing_block, existing_room, _ in assigned:
                if _interval_overlap(block, existing_block) and (
                    teacher_id == existing_task['teacher']['id'] or
                    group_id == existing_task['group']['id'] or
                    room['id'] == existing_room['id']
                ):
                    conflict = True
                    break
            if conflict:
                continue
            assigned.append((task, block, room, points))
            count_per_teacher_day[day_key] += 1
            count_per_teacher_week[teacher_id] += 1
            if search(i + 1):
                return True
            assigned.pop()
            count_per_teacher_day[day_key] -= 1
            count_per_teacher_week[teacher_id] -= 1
            if exhausted:
                return False
        return False

    if not search(0):
        raise ApiError(
            'Se alcanzo max_nodes sin solucion' if exhausted else 'No existe horario que respete las restricciones actuales',
            422, 'SEARCH_LIMIT_REACHED' if exhausted else 'SCHEDULE_UNFEASIBLE',
            {'explored_nodes': explored, 'required_sessions': len(tasks)},
        )
    entries = []
    for task, block, room, _ in assigned:
        entries.append({
            'offering_id': task['offer']['id'], 'subject_id': task['subject']['id'],
            'subject_name': task['subject'].get('name', ''),
            'teacher_id': task['teacher']['id'], 'teacher_name': task['teacher'].get('name', ''),
            'group_id': task['group']['id'], 'group_name': task['group'].get('name', ''),
            'room_id': room['id'], 'room_name': room.get('name', ''),
            'time_block_id': block['id'], 'day': block['day'],
            'start_time': block['start_time'], 'end_time': block['end_time'],
        })
    entries.sort(key=lambda r: (DAYS.index(r['day']), r['start_time'], r['group_name'], r['subject_name']))
    return {
        'entries': entries,
        'score': sum(points for *_, points in assigned),
        'metrics': {'sessions': len(entries), 'explored_nodes': explored, 'hard_conflicts': 0},
        'engine': 'DETERMINISTIC_V1',
    }
