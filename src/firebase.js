// src/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCI78xOkS2L9cKjNcmORgYGCd6TZbRA8eE",
  authDomain: "timetable-manager-943bf.firebaseapp.com",
  projectId: "timetable-manager-943bf",
  storageBucket: "timetable-manager-943bf.firebasestorage.app",
  messagingSenderId: "927122863163",
  appId: "1:927122863163:web:5841b6a9c5344a5dcb581e",
  measurementId: "G-0K2RRRLBEC"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export { auth, db };