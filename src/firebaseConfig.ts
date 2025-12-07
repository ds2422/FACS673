// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyB1HR6F5tOaSCM9VHPlDE13o0DXLF5lYSM",
  authDomain: "contentsummary-61846.firebaseapp.com",
  projectId: "contentsummary-61846",
  storageBucket: "contentsummary-61846.firebasestorage.app",
  messagingSenderId: "1015854757814",
  appId: "1:1015854757814:web:59b0a2ff4e3c05d282b317",
  measurementId: "G-C0E54S3RVK"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);