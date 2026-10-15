from src.repositories.base import FirestoreRepository
from src.schemas.catalogs import (
  AcademicPeriodCreate, AcademicPeriodUpdate,
  AvailabilityCreate, AvailabilityUpdate,
  ConstraintCreate, ConstraintUpdate,
  GroupCreate, GroupUpdate,
  OfferingCreate, OfferingUpdate,
  RoomCreate, RoomUpdate,
  SubjectCreate, SubjectUpdate,
  TeacherCreate, TeacherUpdate,
  TimeBlockCreate, TimeBlockUpdate
)
from src.services.crud import CrudService

academic_periods_service = CrudService(FirestoreRepository('academic_periods'), AcademicPeriodCreate, AcademicPeriodUpdate, ('code',))
teachers_service = CrudService(FirestoreRepository('teachers'), TeacherCreate, TeacherUpdate, ('code', 'email'))
subjects_service = CrudService(FirestoreRepository('subjects'), SubjectCreate, SubjectUpdate, ('code',))
groups_service = CrudService(FirestoreRepository('groups'), GroupCreate, GroupUpdate, ('code',))
rooms_service = CrudService(FirestoreRepository('rooms'), RoomCreate, RoomUpdate, ('code',))
time_blocks_service = CrudService(FirestoreRepository('time_blocks'), TimeBlockCreate, TimeBlockUpdate)
offerings_service = CrudService(FirestoreRepository('course_offerings'), OfferingCreate, OfferingUpdate)
availability_service = CrudService(FirestoreRepository('teacher_availability'), AvailabilityCreate, AvailabilityUpdate)
constraints_service = CrudService(FirestoreRepository('constraints'), ConstraintCreate, ConstraintUpdate)
