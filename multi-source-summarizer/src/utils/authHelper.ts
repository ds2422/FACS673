// src/utils/authHelpers.ts

export const getFriendlyMessage = (code: string): string => {
  switch (code) {
    case "auth/invalid-email":
      return "Please enter a valid email address.";
    case "auth/missing-password":
      return "Please enter your password.";
    case "auth/weak-password":
      return "Password must be at least 6 characters.";
    case "auth/email-already-in-use":
      return "This email is already registered. Try logging in.";
    case "auth/user-not-found":
    case "auth/invalid-credential":
      return "Invalid email or password.";
    case "auth/wrong-password":
      return "Incorrect password. Please try again.";
    case "passwords-do-not-match":
      return "Passwords do not match.";
    case "missing-name":
      return "Please enter your full name.";
    default:
      return "Something went wrong. Please try again.";
  }
};