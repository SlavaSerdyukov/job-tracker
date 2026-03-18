import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { apiFetch, getErrorMessage } from "../api/client";
import {
  ApplicationsFunnelOut,
  ApplicationsSummaryOut,
  RecruiterPerformanceOut,
  StatusDurationOut,
} from "../types/api";

const COLORS = [
  "#2563eb",
  "#16a34a",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
];

export function AnalyticsPage(): JSX.Element {
  const summaryQuery = useQuery({
    queryKey: ["analytics", "summary"],
    queryFn: async (): Promise<ApplicationsSummaryOut> => {
      return apiFetch<ApplicationsSummaryOut>(
        "/v1/applications/analytics/summary",
      );
    },
  });

  const funnelQuery = useQuery({
    queryKey: ["analytics", "funnel"],
    queryFn: async (): Promise<ApplicationsFunnelOut> => {
      return apiFetch<ApplicationsFunnelOut>(
        "/v1/applications/analytics/funnel",
      );
    },
  });

  const recruiterQuery = useQuery({
    queryKey: ["analytics", "recruiter-performance"],
    queryFn: async (): Promise<RecruiterPerformanceOut> => {
      return apiFetch<RecruiterPerformanceOut>(
        "/v1/applications/analytics/recruiter-performance",
      );
    },
  });

  const statusDurationQuery = useQuery({
    queryKey: ["analytics", "status-duration"],
    queryFn: async (): Promise<StatusDurationOut> => {
      return apiFetch<StatusDurationOut>(
        "/v1/applications/analytics/status-duration",
      );
    },
  });

  const summaryData =
    summaryQuery.data?.by_status.filter((item) => item.count > 0) ?? [];
  const funnelData = funnelQuery.data?.steps ?? [];
  const recruiterData = recruiterQuery.data?.recruiters.slice(0, 10) ?? [];
  const statusDurationData =
    statusDurationQuery.data?.metrics
      .filter((item) => item.avg_days !== null)
      .map((item) => ({
        status: item.status,
        avg_days: item.avg_days as number,
      })) ?? [];

  return (
    <div>
      <section className="card">
        <h1>Analytics</h1>
      </section>

      <section className="card">
        <h2>Summary</h2>
        {summaryQuery.isLoading ? <p>Loading...</p> : null}
        {summaryQuery.isError ? (
          <p className="error">{getErrorMessage(summaryQuery.error)}</p>
        ) : null}
        {!summaryQuery.isLoading && !summaryQuery.isError ? (
          summaryData.length === 0 ? (
            <p>No data</p>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={summaryData}
                  dataKey="count"
                  nameKey="status"
                  outerRadius={110}
                >
                  {summaryData.map((item, index) => (
                    <Cell
                      key={`${item.status}-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )
        ) : null}
      </section>

      <section className="card">
        <h2>Funnel</h2>
        {funnelQuery.isLoading ? <p>Loading...</p> : null}
        {funnelQuery.isError ? (
          <p className="error">{getErrorMessage(funnelQuery.error)}</p>
        ) : null}
        {!funnelQuery.isLoading && !funnelQuery.isError ? (
          funnelData.length === 0 ? (
            <p>No data</p>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={funnelData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="step" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#2563eb" />
              </BarChart>
            </ResponsiveContainer>
          )
        ) : null}
      </section>

      <section className="card">
        <h2>Status duration</h2>
        {statusDurationQuery.isLoading ? <p>Loading...</p> : null}
        {statusDurationQuery.isError ? (
          <p className="error">{getErrorMessage(statusDurationQuery.error)}</p>
        ) : null}
        {!statusDurationQuery.isLoading && !statusDurationQuery.isError ? (
          statusDurationData.length === 0 ? (
            <p>No data</p>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={statusDurationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="status" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="avg_days" fill="#16a34a" />
              </BarChart>
            </ResponsiveContainer>
          )
        ) : null}
      </section>

      <section className="card">
        <h2>Recruiter performance</h2>
        {recruiterQuery.isLoading ? <p>Loading...</p> : null}
        {recruiterQuery.isError ? (
          <p className="error">{getErrorMessage(recruiterQuery.error)}</p>
        ) : null}
        {!recruiterQuery.isLoading && !recruiterQuery.isError ? (
          recruiterData.length === 0 ? (
            <p>No data</p>
          ) : (
            <ResponsiveContainer width="100%" height={380}>
              <BarChart data={recruiterData} margin={{ bottom: 50 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="recruiter_email" angle={-20} textAnchor="end" interval={0} height={80} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#f59e0b" />
              </BarChart>
            </ResponsiveContainer>
          )
        ) : null}
      </section>
    </div>
  );
}
