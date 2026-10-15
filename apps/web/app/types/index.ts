export type Role = 'ADMIN' | 'COORDINATOR' | 'VIEWER'

export interface UserProfile {
  uid: string
  email: string
  display_name: string
  role: Role
  active: boolean
}

export interface CatalogRecord {
  id: string
  [key: string]: unknown
}

export interface CatalogField {
  key: string
  label: string
  type?: 'text' | 'number' | 'email' | 'select' | 'checkbox' | 'json'
  required?: boolean
  options?: Array<{ label: string; value: string }>
  reference?: string
  defaultValue?: string | number | boolean | Record<string, unknown>
}

export interface ScheduleEntry {
  offering_id: string
  subject_id: string
  subject_name: string
  teacher_id: string
  teacher_name: string
  group_id: string
  group_name: string
  room_id: string
  room_name: string
  time_block_id: string
  day: string
  start_time: string
  end_time: string
}

export interface ScheduleVersion {
  id: string
  academic_period_id: string
  version: number
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED'
  score: number
  entries: ScheduleEntry[]
  engine: string
  metrics: { sessions: number; explored_nodes: number; hard_conflicts: number }
  created_at: string
}

export interface ApiErrorInfo {
  error?: string
  message?: string
  details?: Array<{ field: string; message: string }> | Record<string, unknown>
}
