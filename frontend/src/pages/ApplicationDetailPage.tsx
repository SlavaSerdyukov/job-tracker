import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch, getErrorMessage } from "../api/client";
import {
  ApplicationEventOut,
  ApplicationOut,
  ApplicationStatus,
} from "../types/api";

const STATUSES: ApplicationStatus[] = [
  "applied",
  "screening",
  "interview",
  "offer",
  "accepted",
  "rejected",
];

export function ApplicationDetailPage(): JSX.Element {
  const queryClient = useQueryClient();
  const { id } = useParams();
  const [note, setNote] = useState("");
  const [statusValue, setStatusValue] = useState<ApplicationStatus>("applied");
  const [actionError, setActionError] = useState("");

  const appId = useMemo(() => Number(id), [id]);

  const detailQuery = useQuery({
    queryKey: ["application", appId],
    queryFn: async (): Promise<ApplicationOut> => {
      return apiFetch<ApplicationOut>(`/v1/applications/${appId}`);
    },
    enabled: Number.isFinite(appId),
  });

  const timelineQuery = useQuery({
    queryKey: ["timeline", appId],
    queryFn: async (): Promise<ApplicationEventOut[]> => {
      return apiFetch<ApplicationEventOut[]>(
        `/v1/applications/${appId}/timeline`,
      );
    },
    enabled: Number.isFinite(appId),
  });

  const updateStatusMutation = useMutation({
    mutationFn: async (): Promise<ApplicationOut> => {
      return apiFetch<ApplicationOut>(`/v1/applications/${appId}`, {
        method: "PATCH",
        body: { status: statusValue },
      });
    },
    onSuccess: () => {
      setActionError("");
      void queryClient.invalidateQueries({ queryKey: ["application", appId] });
      void queryClient.invalidateQueries({ queryKey: ["applications"] });
      void queryClient.invalidateQueries({ queryKey: ["timeline", appId] });
    },
    onError: (error) => {
      setActionError(getErrorMessage(error));
    },
  });

  const noteMutation = useMutation({
    mutationFn: async (): Promise<ApplicationEventOut> => {
      return apiFetch<ApplicationEventOut>(`/v1/applications/${appId}/notes`, {
        method: "POST",
        body: { note: note.trim() },
      });
    },
    onSuccess: () => {
      setActionError("");
      setNote("");
      void queryClient.invalidateQueries({ queryKey: ["timeline", appId] });
    },
    onError: (error) => {
      setActionError(getErrorMessage(error));
    },
  });

  const onNoteSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (note.trim() === "") {
      setActionError("note is required");
      return;
    }
    noteMutation.mutate();
  };

  const application = detailQuery.data;
  const timelineItems = timelineQuery.data ?? [];

  useEffect(() => {
    if (application) {
      setStatusValue(application.status);
    }
  }, [application]);

  if (!Number.isFinite(appId)) {
    return (
      <section className="card">
        <h1>Application</h1>
        <p className="error">Invalid application id</p>
      </section>
    );
  }

  return (
    <div>
      <section className="card">
        <div className="row">
          <h1>Application #{appId}</h1>
          <Link to="/">Back</Link>
        </div>

        {detailQuery.isLoading ? <p>Loading...</p> : null}
        {detailQuery.isError ? (
          <p className="error">{getErrorMessage(detailQuery.error)}</p>
        ) : null}

        {application ? (
          <div className="grid">
            <div>
              <strong>Company</strong>
              <p>{application.company_name}</p>
            </div>
            <div>
              <strong>Position</strong>
              <p>{application.position}</p>
            </div>
            <div>
              <strong>Status</strong>
              <p>{application.status}</p>
            </div>
            <div>
              <strong>Recruiter Email</strong>
              <p>{application.recruiter_email ?? "-"}</p>
            </div>
            <div>
              <strong>Recruiter Name</strong>
              <p>{application.recruiter_name ?? "-"}</p>
            </div>
            <div>
              <strong>Follow Up</strong>
              <p>{application.follow_up_at ?? "-"}</p>
            </div>
          </div>
        ) : null}

        <div className="row">
          <label>
            Update status
            <select
              value={statusValue}
              onChange={(event) => {
                setStatusValue(event.target.value as ApplicationStatus);
              }}
            >
              {STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={() => updateStatusMutation.mutate()}
            disabled={updateStatusMutation.isPending}
          >
            {updateStatusMutation.isPending ? "Updating..." : "Update"}
          </button>
        </div>

        {actionError !== "" ? <p className="error">{actionError}</p> : null}
      </section>

      <section className="card">
        <h2>Add note</h2>
        <form onSubmit={onNoteSubmit}>
          <label>
            note
            <textarea
              value={note}
              onChange={(event) => setNote(event.target.value)}
              rows={4}
            />
          </label>
          <button type="submit" disabled={noteMutation.isPending}>
            {noteMutation.isPending ? "Saving..." : "Add note"}
          </button>
        </form>
      </section>

      <section className="card">
        <h2>Timeline</h2>

        {timelineQuery.isLoading ? <p>Loading...</p> : null}
        {timelineQuery.isError ? (
          <p className="error">{getErrorMessage(timelineQuery.error)}</p>
        ) : null}

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>created_at</th>
                <th>event_type</th>
                <th>from_status</th>
                <th>to_status</th>
                <th>note</th>
              </tr>
            </thead>
            <tbody>
              {timelineItems.length === 0 ? (
                <tr>
                  <td colSpan={5}>No data</td>
                </tr>
              ) : (
                timelineItems.map((event) => (
                  <tr key={event.id}>
                    <td>{event.created_at}</td>
                    <td>{event.event_type}</td>
                    <td>{event.from_status ?? "-"}</td>
                    <td>{event.to_status ?? "-"}</td>
                    <td>{event.note ?? "-"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
