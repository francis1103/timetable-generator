import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Sidebar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  const getNavItems = () => {
    switch(user.role) {
      case 'admin':
        return [
          { name: 'Dashboard', path: '/admin', icon: '📊' },
          { name: 'Timetable Generator', path: '/admin/generator', icon: '🔄' },
          { name: 'Timetable Editor', path: '/admin/editor', icon: '✏️' },
          { name: 'Analytics', path: '/admin/analytics', icon: '📈' },
          { name: 'Agent Validation', path: '/admin/agents', icon: '🤖' },
          { name: 'User Management', path: '/admin/users', icon: '👥' },
        ];
      case 'faculty':
        return [
          { name: 'My Schedule', path: '/faculty', icon: '📅' },
          { name: 'Workload', path: '/faculty/workload', icon: '⏱️' },
          { name: 'Availability', path: '/faculty/availability', icon: '✅' },
          { name: 'Student Requests', path: '/faculty/requests', icon: '📝' },
        ];
      case 'student':
        return [
          { name: 'My Timetable', path: '/student', icon: '📅' },
          { name: 'Preferences', path: '/student/preferences', icon: '⚙️' },
          { name: 'Notifications', path: '/student/notifications', icon: '🔔' },
          { name: 'Request Changes', path: '/student/requests', icon: '✉️' },
        ];
      default:
        return [];
    }
  };

  return (
    <div className="w-64 bg-gray-800 text-white flex flex-col h-full">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-xl font-semibold">Smart Timetable</h2>
        <p className="text-gray-400 text-sm mt-1">{user?.displayName}</p>
        <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
      </div>
      
      <nav className="flex-1 mt-4">
        {getNavItems().map((item) => (
          <a
            key={item.path}
            href={item.path}
            className="flex items-center px-4 py-3 hover:bg-gray-700 transition-colors duration-200"
          >
            <span className="mr-3 text-lg">{item.icon}</span>
            {item.name}
          </a>
        ))}
      </nav>
      
      <button
        onClick={handleLogout}
        className="w-full p-4 text-left hover:bg-gray-700 transition-colors duration-200 border-t border-gray-700 flex items-center"
      >
        <span className="mr-3">🚪</span>
        Logout
      </button>
    </div>
  );
};

export default Sidebar;