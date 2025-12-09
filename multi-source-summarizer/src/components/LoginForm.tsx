// src/components/LoginForm.tsx
import React, { useState } from "react";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebaseConfig";
import { getFriendlyMessage } from "../utils/authHelper.ts";

interface LoginFormProps {
  onSwitchToRegister: () => void;
  successMessage?: string | null; // Receive success message
}

const LoginForm: React.FC<LoginFormProps> = ({
  onSwitchToRegister,
  successMessage,
}) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (err: any) {
      setError(getFriendlyMessage(err.code));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <h2
        style={{
          fontSize: "26px",
          marginBottom: "10px",
          fontWeight: 700,
          color: "#1a1a1a",
        }}
      >
        Welcome Back
      </h2>
      <p style={{ marginBottom: "30px", color: "#666", fontSize: "14px" }}>
        Enter your credentials to access your account
      </p>

      {/* SUCCESS MESSAGE (Green Toast) */}
      {successMessage && (
        <div
          style={{
            background: "#dcfce7",
            color: "#166534",
            padding: "10px",
            borderRadius: "8px",
            marginBottom: "15px",
            fontSize: "14px",
            border: "1px solid #bbf7d0",
          }}
        >
          {successMessage}
        </div>
      )}

      {/* ERROR MESSAGE (Red Toast) */}
      {error && (
        <div
          style={{
            background: "#fee2e2",
            color: "#dc2626",
            padding: "10px",
            borderRadius: "8px",
            marginBottom: "15px",
            fontSize: "14px",
            border: "1px solid #fecaca",
          }}
        >
          {error}
        </div>
      )}

      <form
        onSubmit={handleLogin}
        style={{ display: "flex", flexDirection: "column", gap: "15px" }}
      >
        <input
          type="email"
          data-testid="email-input"
          placeholder="Email address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={inputStyle}
        />
        <input
          type="password"
          placeholder="Password"
          data-testid="password-input"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={inputStyle}
        />

        <button
          type="submit"
          data-testid="login-btn"
          disabled={loading}
          style={buttonStyle}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>

      <div
        style={{
          marginTop: "25px",
          borderTop: "1px solid #f0f0f0",
          paddingTop: "20px",
        }}
      >
        <p style={{ fontSize: "14px", color: "#666" }}>
          Don't have an account?{" "}
          <span
            onClick={onSwitchToRegister}
            style={{ color: "#4f46e5", fontWeight: 600, cursor: "pointer" }}
          >
            Register
          </span>
        </p>
      </div>
    </>
  );
};

const inputStyle = {
  padding: "14px",
  borderRadius: "8px",
  border: "1px solid #e1e4e8",
  fontSize: "15px",
  outline: "none",
};
const buttonStyle = {
  marginTop: "10px",
  padding: "14px",
  background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
  color: "white",
  border: "none",
  borderRadius: "8px",
  fontSize: "16px",
  fontWeight: 600,
  cursor: "pointer",
};

export default LoginForm;
