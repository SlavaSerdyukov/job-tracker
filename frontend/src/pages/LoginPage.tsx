import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";

import { apiFetch, getErrorMessage } from "../api/client";
import { setToken } from "../auth/token";
import { TokenOut } from "../types/api";

export function LoginPage(): JSX.Element {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const loginMutation = useMutation({
    mutationFn: async (): Promise<TokenOut> => {
      const form = new URLSearchParams();
      form.set("username", email.trim());
      form.set("password", password);

      return apiFetch<TokenOut>("/v1/auth/login", {
        method: "POST",
        body: form,
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        auth: false,
        handleUnauthorized: false,
      });
    },
    onSuccess: (token) => {
      setToken(token.access_token);
      navigate("/", { replace: true });
    },
  });

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    loginMutation.reset();
    loginMutation.mutate();
  };

  return (
    <div className="auth-page card">
      <h1>Login</h1>
      <form onSubmit={onSubmit}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>

        {loginMutation.isError ? (
          <p className="error">{getErrorMessage(loginMutation.error)}</p>
        ) : null}

        <button type="submit" disabled={loginMutation.isPending}>
          {loginMutation.isPending ? "Loading..." : "Login"}
        </button>
      </form>

      <p className="muted">
        No account? <Link to="/register">Register</Link>
      </p>
    </div>
  );
}
