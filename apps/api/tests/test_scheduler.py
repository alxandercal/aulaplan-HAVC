import pytest
from src.core.errors import ApiError
from src.services.scheduler import SchedulingInput, generate_schedule, _interval_overlap


def sample():
    return SchedulingInput(
        period_id='P1',
        teachers=[{'id': 'T1', 'name': 'Ana', 'active': True, 'max_daily_blocks': 4, 'max_weekly_blocks': 10},
                  {'id': 'T2', 'name': 'Juan', 'active': True, 'max_daily_blocks': 4, 'max_weekly_blocks': 10}],
        subjects=[{'id': 'S1', 'name': 'Programación', 'active': True, 'weekly_blocks': 2, 'required_room_type': 'LAB'},
                  {'id': 'S2', 'name': 'Redes', 'active': True, 'weekly_blocks': 1, 'required_room_type': 'LAB'}],
        groups=[{'id': 'G1', 'name': 'A', 'active': True, 'student_count': 25, 'academic_period_id': 'P1'},
                {'id': 'G2', 'name': 'B', 'active': True, 'student_count': 25, 'academic_period_id': 'P1'}],
        rooms=[{'id': 'R1', 'type': 'LAB', 'name': 'Lab', 'capacity': 35, 'active': True}],
        blocks=[{'id': 'MON-01', 'day': 'MONDAY', 'start_time': '08:00', 'end_time': '09:30', 'active': True},
                {'id': 'MON-02', 'day': 'MONDAY', 'start_time': '09:30', 'end_time': '11:00', 'active': True},
                {'id': 'TUE-01', 'day': 'TUESDAY', 'start_time': '08:00', 'end_time': '09:30', 'active': True}],
        offerings=[{'id': 'O1', 'academic_period_id': 'P1', 'subject_id': 'S1', 'teacher_id': 'T1', 'group_id': 'G1'},
                   {'id': 'O2', 'academic_period_id': 'P1', 'subject_id': 'S2', 'teacher_id': 'T2', 'group_id': 'G2'}],
        availability=[], constraints=[],
    )


def test_complete_schedule_no_collisions():
    result = generate_schedule(sample())
    assert len(result['entries']) == 3
    assert result['metrics']['hard_conflicts'] == 0
    assert result['engine'] == 'DETERMINISTIC_V1'
    entries = result['entries']
    for i, a in enumerate(entries):
        for b in entries[i + 1:]:
            assert not (_interval_overlap(a, b) and (a['room_id'] == b['room_id'] or a['group_id'] == b['group_id'] or a['teacher_id'] == b['teacher_id']))


def test_unavailability_honored():
    data = sample()
    data.availability.append({'teacher_id': 'T1', 'time_block_id': 'MON-01', 'available': False})
    entries = generate_schedule(data)['entries']
    assert all(not (e['teacher_id'] == 'T1' and e['time_block_id'] == 'MON-01') for e in entries)


def test_teacher_restriction_day_honored():
    data = sample()
    data.constraints.append({'id': 'C1', 'type': 'TEACHER_UNAVAILABLE', 'priority': 'HARD',
                             'target_type': 'TEACHER', 'target_id': 'T1', 'params': {'day': 'MONDAY'}, 'active': True})
    with pytest.raises(ApiError) as ex:
        generate_schedule(data)
    assert ex.value.code == 'SCHEDULE_UNFEASIBLE'


def test_invalid_subject_without_suitable_room():
    data = sample()
    data.rooms[0]['capacity'] = 10
    with pytest.raises(ApiError) as ex:
        generate_schedule(data)
    assert ex.value.status_code == 422


def test_invalid_unknown_hard_rule_fails_closed():
    data = sample()
    data.constraints.append({'id': 'C', 'type': 'MAGIC', 'priority': 'HARD', 'active': True})
    with pytest.raises(ApiError) as ex:
        generate_schedule(data)
    assert ex.value.code == 'SCHEDULE_VALIDATION_ERROR'


def test_weekly_capacity_rejected():
    data = sample()
    data.teachers[0]['max_weekly_blocks'] = 1
    with pytest.raises(ApiError) as ex:
        generate_schedule(data)
    assert 'semanal' in ex.value.message


def test_empty_period_rejected():
    data = sample()
    data.offerings = []
    with pytest.raises(ApiError):
        generate_schedule(data)


def test_invalid_limit_rejected():
    with pytest.raises(ApiError):
        generate_schedule(sample(), max_nodes=10)


def test_scores_teacher_preferences():
    data = sample()
    data.availability.append({'teacher_id': 'T1', 'time_block_id': 'MON-01', 'available': True, 'preference_weight': 15})
    first = generate_schedule(data)
    assert first['score'] >= 15


def test_group_collisions_avoided_even_if_different_teacher():
    data = sample()
    data.offerings[1]['group_id'] = 'G1'
    entries = generate_schedule(data)['entries']
    for i, a in enumerate(entries):
        for b in entries[i + 1:]:
            assert not (_interval_overlap(a, b) and a['group_id'] == b['group_id'])
