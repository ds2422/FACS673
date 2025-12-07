// src/components/Auth.tsx
import React, { useState } from "react";
import LoginForm from "./LoginForm";
import RegisterForm from "./RegisterForm";

const Auth: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleRegisterSuccess = () => {
    setSuccessMessage("Account created successfully! Please log in.");
    setIsLogin(true); // Switch to Login view
  };

  const handleSwitchToRegister = () => {
    setSuccessMessage(null); // Clear messages when switching
    setIsLogin(false);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "#f5f7fa",
        padding: "20px",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "400px",
          background: "white",
          padding: "40px",
          borderRadius: "16px",
          boxShadow: "0 10px 40px rgba(0,0,0,0.08)",
          textAlign: "center",
        }}
      >
        {isLogin ? (
          <LoginForm
            onSwitchToRegister={handleSwitchToRegister}
            successMessage={successMessage} // Pass message to Login
          />
        ) : (
          <RegisterForm
            onSwitchToLogin={() => setIsLogin(true)}
            onRegisterSuccess={handleRegisterSuccess} // Pass success handler
          />
        )}
      </div>
    </div>
  );
};

export default Auth;
