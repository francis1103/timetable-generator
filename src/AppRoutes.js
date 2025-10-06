import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import FacultyDashboard from './pages/FacultyDashboard';
import StudentDashboard from './pages/StudentDashboard';
import TimetableGenerator from './pages/TimetableGenerator';
import TimetableEditor from './pages/TimetableEditor';
import AgentValidationPage from './pages/AgentValidation';
import Sidebar from './components/Sidebar';

const AppRoutes = () => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }
  
  if (!user) {
    return <Login />;
  }

  return (
    <>
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-6">
        <Routes>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/generator" element={<TimetableGenerator />} />
          <Route path="/admin/editor" element={<TimetableEditor />} />
          <Route path="/admin/agents" element={<AgentValidationPage />} />
          <Route path="/faculty" element={<FacultyDashboard />} />
          <Route path="/student" element={<StudentDashboard />} />
          <Route path="*" element={<Navigate to={`/${user.role}`} replace />} />
        </Routes>
      </main>
    </>
  );
};

export default AppRoutes;