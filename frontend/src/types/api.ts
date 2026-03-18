export type ApplicationStatus =
  | "applied"
  | "screening"
  | "interview"
  | "offer"
  | "accepted"
  | "rejected";

export type ApplicationEventType =
  | "status_change"
  | "follow_up"
  | "note"
  | "contact";

export interface TokenOut {
  access_token: string;
  token_type: string;
}

export interface ApplicationOut {
  id: number;
  company_name: string;
  position: string;
  status: ApplicationStatus;
  recruiter_name: string | null;
  recruiter_email: string | null;
  job_url: string | null;
  salary_range: string | null;
  location: string | null;
  follow_up_at: string | null;
  status_updated_at: string | null;
  created_at: string;
}

export interface PaginatedApplications {
  items: ApplicationOut[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApplicationEventOut {
  id: number;
  application_id: number;
  event_type: ApplicationEventType;
  from_status: ApplicationStatus | null;
  to_status: ApplicationStatus | null;
  note: string | null;
  created_at: string;
}

export interface StatusCountOut {
  status: ApplicationStatus;
  count: number;
}

export interface ApplicationsSummaryOut {
  total: number;
  by_status: StatusCountOut[];
}

export interface ApplicationsFunnelOut {
  steps: Array<{
    step: ApplicationStatus;
    count: number;
  }>;
}

export interface RecruiterPerformanceOut {
  recruiters: Array<{
    recruiter_email: string;
    count: number;
  }>;
}

export interface StatusDurationOut {
  metrics: Array<{
    status: ApplicationStatus;
    avg_days: number | null;
  }>;
}
