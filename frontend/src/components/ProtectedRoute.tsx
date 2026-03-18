import { Navigate } from "react-router-dom";

import { getToken } from "../auth/token";

interface Props {
  children: JSX.Element;
}

export function ProtectedRoute({ children }: Props): JSX.Element {
  const token = getToken();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
