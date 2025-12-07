// src/components/RegisterForm.tsx
import React, { useState } from "react";
import {
  createUserWithEmailAndPassword,
  updateProfile,
  signOut,
} from "firebase/auth"; // Import signOut
import { auth } from "../firebaseConfig";
import { getFriendlyMessage } from "../utils/authHelper.ts";

interface RegisterFormProps {
  onSwitchToLogin: () => void;
  onRegisterSuccess: () => void; // New prop
}

const RegisterForm: React.FC<RegisterFormProps> = ({
  onSwitchToLogin,
  onRegisterSuccess,
}) => {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!fullName.trim()) {
      setError(getFriendlyMessage("missing-name"));
      setLoading(false);
      return;
    }
    if (password !== confirmPassword) {
      setError(getFriendlyMessage("passwords-do-not-match"));
      setLoading(false);
      return;
    }

    try {
      // 1. Create User
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        password
      );

      // 2. Update Profile Name
      await updateProfile(userCredential.user, {
        displayName: fullName,
      });

      // 3. FORCE LOGOUT IMMEDIATELY
      // This prevents the App from switching to Home page automatically
      await signOut(auth);

      // 4. Trigger Success Flow
      onRegisterSuccess();
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
        Create Account
      </h2>
      <p style={{ marginBottom: "30px", color: "#666", fontSize: "14px" }}>
        Sign up to start summarizing
      </p>

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
        onSubmit={handleRegister}
        style={{ display: "flex", flexDirection: "column", gap: "15px" }}
      >
        <input
          type="text"
          placeholder="Full Name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
          style={inputStyle}
        />
        <input
          type="email"
          placeholder="Email address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={inputStyle}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={inputStyle}
        />
        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          style={inputStyle}
        />

        <button type="submit" disabled={loading} style={buttonStyle}>
          {loading ? "Creating Account..." : "Sign Up"}
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
          Already have an account?{" "}
          <span
            onClick={onSwitchToLogin}
            style={{ color: "#4f46e5", fontWeight: 600, cursor: "pointer" }}
          >
            Login
          </span>
        </p>
      </div>
    </>
  );
};

// Simple styles objects to keep code clean
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

export default RegisterForm;
