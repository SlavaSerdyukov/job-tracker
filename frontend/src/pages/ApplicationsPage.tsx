import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch, getErrorMessage } from "../api/client";
import {
  ApplicationOut,
  ApplicationStatus,
  PaginatedApplications,
} from "../types/api";

const STATUSES: ApplicationStatus[] = [
  "applied",
  "screening",
  "interview",
  "offer",
  "accepted",
  "rejected",
];

interface CreateForm {
  company_name: string;
  position: string;
  status: ApplicationStatus;
  recruiter_email: string;
  recruiter_name: string;
  job_url: string;
  salary_range: string;
  location: string;
}

const INITIAL_FORM: CreateForm = {
  company_name: "",
  position: "",
  status: "applied",
  recruiter_email: "",
  recruiter_name: "",
  job_url: "",
  salary_range: "",
  location: "",
};

function buildCreatePayload(form: CreateForm): Record<string, unknown> {
  const payload: Record<string, unknown> = {
    company_name: form.company_name.trim(),
    position: form.position.trim(),
    status: form.status,
  };

  const optionalFields: Array<
    keyof Omit<CreateForm, "company_name" | "position" | "status">
  > = [
    "recruiter_email",
    "recruiter_name",
    "job_url",
    "salary_range",
    "location",
  ];

  for (const field of optionalFields) {
    const value = form[field].trim();
    if (value !== "") {
      payload[field] = value;
    }
  }

  return payload;
}

export function ApplicationsPage(): JSX.Element {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState("");
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [form, setForm] = useState<CreateForm>(INITIAL_FORM);
  const [actionError, setActionError] = useState("");

  const applicationsQuery = useQuery({
    queryKey: ["applications", statusFilter, query, page],
    queryFn: async (): Promise<PaginatedApplications> => {
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("page_size", "20");
      params.set("sort", "-created_at");

      if (statusFilter !== "") {
        params.set("status", statusFilter);
      }
      if (query.trim() !== "") {
        params.set("q", query.trim());
      }

      return apiFetch<PaginatedApplications>(
        `/v1/applications?${params.toString()}`,
      );
    },
    placeholderData: (previous) => previous,
  });

  const createMutation = useMutation({
    mutationFn: async (): Promise<ApplicationOut> => {
      const payload = buildCreatePayload(form);
      return apiFetch<ApplicationOut>("/v1/applications", {
        method: "POST",
        body: payload,
      });
    },
    onSuccess: () => {
      setForm(INITIAL_FORM);
      setActionError("");
      setPage(1);
      void queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
    onError: (error) => {
      setActionError(getErrorMessage(error));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number): Promise<void> => {
      await apiFetch<void>(`/v1/applications/${id}`, {
        method: "DELETE",
      });
    },
    onSuccess: () => {
      setActionError("");
      void queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
    onError: (error) => {
      setActionError(getErrorMessage(error));
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: async (payload: {
      id: number;
      status: ApplicationStatus;
    }): Promise<ApplicationOut> => {
      return apiFetch<ApplicationOut>(`/v1/applications/${payload.id}`, {
        method: "PATCH",
        body: { status: payload.status },
      });
    },
    onSuccess: () => {
      setActionError("");
      void queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
    onError: (error) => {
      setActionError(getErrorMessage(error));
    },
  });

  const updateFollowUpMutation = useMutation({
    mutationFn: async (payload: {
      id: number;
      follow_up_at: string | null;
    }): Promise<ApplicationOut> => {
      return apiFetch<ApplicationOut>(`/v1/applications/${payload.id}`, {
        method: "PATCH",
        body: { follow_up_at: payload.follow_up_at },
      });
    },
    onSuccess: () => {
      setActionError("");
      void queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
    onError: (error) => {
      setActionError(getErrorMessage(error));
    },
  });

  const onCreateSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setActionError("");

    if (form.company_name.trim() === "" || form.position.trim() === "") {
      setActionError("company_name and position are required");
      return;
    }

    createMutation.mutate();
  };

  const onDelete = (id: number) => {
    const approved = window.confirm("Delete application?");
    if (!approved) {
      return;
    }
    deleteMutation.mutate(id);
  };

  const onSetFollowUp = (id: number, current: string | null) => {
    const value = window.prompt(
      "Enter ISO datetime. Leave empty to clear.",
      current ?? "",
    );

    if (value === null) {
      return;
    }

    const nextValue = value.trim() === "" ? null : value.trim();
    updateFollowUpMutation.mutate({
      id,
      follow_up_at: nextValue,
    });
  };

  const total = applicationsQuery.data?.total ?? 0;
  const pageSize = applicationsQuery.data?.page_size ?? 20;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const items = applicationsQuery.data?.items ?? [];

  return (
    <div>
      <section className="card">
        <h1>Applications</h1>

        <div className="row">
          <label>
            Status
            <select
              value={statusFilter}
              onChange={(event) => {
                setStatusFilter(event.target.value);
                setPage(1);
              }}
            >
              <option value="">All</option>
              {STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>

          <label>
            Search q
            <input
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                setPage(1);
              }}
              placeholder="company, position, recruiter email"
            />
          </label>
        </div>

        {applicationsQuery.isLoading ? <p>Loading...</p> : null}
        {applicationsQuery.isError ? (
          <p className="error">{getErrorMessage(applicationsQuery.error)}</p>
        ) : null}

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Company</th>
                <th>Position</th>
                <th>Status</th>
                <th>Recruiter</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan={6}>No data</td>
                </tr>
              ) : (
                items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.company_name}</td>
                    <td>{item.position}</td>
                    <td>
                      <select
                        value={item.status}
                        onChange={(event) => {
                          updateStatusMutation.mutate({
                            id: item.id,
                            status: event.target.value as ApplicationStatus,
                          });
                        }}
                      >
                        {STATUSES.map((status) => (
                          <option key={status} value={status}>
                            {status}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td>{item.recruiter_email ?? "-"}</td>
                    <td>
                      <div className="actions">
                        <Link to={`/applications/${item.id}`}>Open</Link>
                        <button
                          type="button"
                          onClick={() => {
                            onSetFollowUp(item.id, item.follow_up_at);
                          }}
                        >
                          Set follow-up
                        </button>
                        <button
                          type="button"
                          onClick={() => onDelete(item.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="row">
          <button
            type="button"
            onClick={() => setPage((current) => Math.max(1, current - 1))}
            disabled={page <= 1}
          >
            Prev
          </button>
          <span>
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            onClick={() => setPage((current) => current + 1)}
            disabled={page >= totalPages}
          >
            Next
          </button>
        </div>
      </section>

      <section className="card">
        <h2>Create application</h2>

        {actionError !== "" ? <p className="error">{actionError}</p> : null}

        <form onSubmit={onCreateSubmit}>
          <div className="grid">
            <label>
              company_name
              <input
                value={form.company_name}
                onChange={(event) => {
                  setForm((current) => ({
                    ...current,
                    company_name: event.target.value,
                  }));
                }}
                required
              />
            </label>

            <label>
              position
              <input
                value={form.position}
                onChange={(event) => {
                  setForm((current) => ({
                    ...current,
                    position: event.target.value,
                  }));
                }}
                required
              />
            </label>

            <label>
              status
              <select
                value={form.status}
                onChange={(event) => {
                  setForm((current) => ({
                    ...current,
                    status: event.target.value as ApplicationStatus,
                  }));
                }}
              >
                {STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>

            <label>
              recruiter_email
              <input
                value={form.recruiter_email}
                onChange={(event) => {
                  setForm((current) => ({
                    ...current,
                    recruiter_email: event.target.value,
                  }));
                }}
              />
            </label>

            <label>
              recruiter_name
              <input
                value={form.recruiter_name}
                onChange={(event) => {
                  setForm((current) => ({
                    ...current,
                    recruiter_name: event.target.value,
                  }));
                }}
              />
            </label>

            <label>
              job_url
              <input
                value={form.job_url}
                onChange={(event) => {
                  setForm((current) => ({
                    ...current,
                    job_url: event.target.value,
                  }));
                }}
              />
            </label>

            <label>
              salary_range
              <input
                value={form.salary_range}
                onChange={(event) => {
                  setForm((current) => ({
                    ...current,
                    salary_range: event.target.value,
                  }));
                }}
              />
            </label>

            <label>
              location
              <input
                value={form.location}
                onChange={(event) => {
                  setForm((current) => ({
                    ...current,
                    location: event.target.value,
                  }));
                }}
              />
            </label>
          </div>

          <button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? "Creating..." : "Create"}
          </button>
        </form>
      </section>
    </div>
  );
}
