from typing import Any, Literal
from pydantic import BaseModel, EmailStr, Field

class AcademicPeriodCreate(BaseModel):
  code: str = Field(min_length=2, max_length=30)
  name: str = Field(min_length=2, max_length=120)
  start_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
  end_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
  active: bool = True

class AcademicPeriodUpdate(AcademicPeriodCreate):
  pass

class TeacherCreate(BaseModel):
  code: str = Field(min_length=2, max_length=30)
  name: str = Field(min_length=2, max_length=120)
  email: EmailStr
  max_daily_blocks: int = Field(default=4, ge=1, le=8)
  max_weekly_blocks: int = Field(default=16, ge=1, le=40)
  active: bool = True

class TeacherUpdate(TeacherCreate):
  pass

class SubjectCreate(BaseModel):
  code: str = Field(min_length=2, max_length=30)
  name: str = Field(min_length=2, max_length=120)
  weekly_blocks: int = Field(ge=1, le=10)
  required_room_type: str = 'CLASSROOM'
  active: bool = True

class SubjectUpdate(SubjectCreate):
  pass

class GroupCreate(BaseModel):
  code: str = Field(min_length=2, max_length=30)
  name: str = Field(min_length=2, max_length=120)
  student_count: int = Field(ge=1, le=500)
  academic_period_id: str = Field(min_length=1)
  active: bool = True

class GroupUpdate(GroupCreate):
  pass

class RoomCreate(BaseModel):
  code: str = Field(min_length=2, max_length=30)
  name: str = Field(min_length=2, max_length=120)
  capacity: int = Field(ge=1, le=1000)
  type: str = 'CLASSROOM'
  building: str = ''
  active: bool = True

class RoomUpdate(RoomCreate):
  pass

class TimeBlockCreate(BaseModel):
    day: Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
    start_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    order: int = Field(ge=1, le=30)
    active: bool = True


class TimeBlockUpdate(TimeBlockCreate):
    pass


class OfferingCreate(BaseModel):
    academic_period_id: str = Field(min_length=1)
    subject_id: str = Field(min_length=1)
    group_id: str = Field(min_length=1)
    teacher_id: str = Field(min_length=1)
    active: bool = True


class OfferingUpdate(OfferingCreate):
    pass


class AvailabilityCreate(BaseModel):
    teacher_id: str = Field(min_length=1)
    time_block_id: str = Field(min_length=1)
    available: bool = True
    preference_weight: int = Field(default=0, ge=-100, le=100)


class AvailabilityUpdate(AvailabilityCreate):
    pass


class ConstraintCreate(BaseModel):
    type: str = Field(min_length=2, max_length=80)
    priority: Literal["HARD", "SOFT"]
    target_type: str = Field(min_length=2, max_length=40)
    target_id: str = Field(min_length=1)
    weight: int = Field(default=0, ge=-1000, le=1000)
    params: dict[str, Any] = Field(default_factory=dict)
    active: bool = True


class ConstraintUpdate(ConstraintCreate):
    pass