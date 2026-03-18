import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { clearToken } from "../auth/token";

export function AppLayout(): JSX.Element {
  const navigate = useNavigate();

  const onLogout = () => {
    clearToken();
    navigate("/login", { replace: true });
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <nav className="nav-links">
          <NavLink to="/">Applications</NavLink>
          <NavLink to="/analytics">Analytics</NavLink>
        </nav>
        <button type="button" onClick={onLogout}>
          Logout
        </button>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
