import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";

import { apiFetch, getErrorMessage } from "../api/client";
import { setToken } from "../auth/token";
import { TokenOut } from "../types/api";

export function RegisterPage(): JSX.Element {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const registerMutation = useMutation({
    mutationFn: async (): Promise<TokenOut> => {
      return apiFetch<TokenOut>("/v1/auth/register", {
        method: "POST",
        body: {
          email: email.trim(),
          password,
        },
        auth: false,
      });
    },
    onSuccess: (token) => {
      setToken(token.access_token);
      navigate("/", { replace: true });
    },
  });

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    registerMutation.reset();
    registerMutation.mutate();
  };

  return (
    <div className="auth-page card">
      <h1>Register</h1>
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

        {registerMutation.isError ? (
          <p className="error">{getErrorMessage(registerMutation.error)}</p>
        ) : null}

        <button type="submit" disabled={registerMutation.isPending}>
          {registerMutation.isPending ? "Loading..." : "Register"}
        </button>
      </form>

      <p className="muted">
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
}
