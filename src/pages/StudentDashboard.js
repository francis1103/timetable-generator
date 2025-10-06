import React, { useState } from 'react';
import { mockTimetables, mockUsers } from '../data/mockData';

const StudentDashboard = () => {
  const [preferences, setPreferences] = useState(mockUsers.student.preferences);
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: 'New timetable available',
      message: 'Option 3 timetable has been generated',
      date: '2023-05-15',
      read: false
    },
    {
      id: 2,
      title: 'Preference updated',
      message: 'Your preference for morning classes has been saved',
      date: '2023-05-10',
      read: true
    },
    {
      id: 3,
      title: 'Room change',
      message: 'CS201 class moved from A101 to B203',
      date: '2023-05-05',
      read: true
    }
  ]);

  const studentTimetable = mockTimetables[0].timetable;

  const handlePreferenceChange = (e) => {
    const { name, value, type, checked } = e.target;
    setPreferences(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleDayToggle = (day) => {
    setPreferences(prev => {
      const newDays = prev.preferredDays.includes(day)
        ? prev.preferredDays.filter(d => d !== day)
        : [...prev.preferredDays, day];
      return { ...prev, preferredDays: newDays };
    });
  };

  const markAsRead = (id) => {
    setNotifications(notifications.map(notif => 
      notif.id === id ? { ...notif, read: true } : notif
    ));
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Student Dashboard</h1>
        <div className="text-sm text-gray-500">
          {mockUsers.student.name} | {mockUsers.student.department}, Year {mockUsers.student.year}
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">My Timetable</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white">
            <thead>
              <tr>
                <th className="py-2 px-4 border-b">Time</th>
                {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].map(day => (
                  <th key={day} className="py-2 px-4 border-b">{day}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {['9-11', '11-1', '2-4', '4-6'].map(time => (
                <tr key={time}>
                  <td className="py-3 px-4 border-b font-medium">{time}</td>
                  {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].map(day => {
                    const slot = studentTimetable.find(
                      s => s.day === day && s.time === time
                    );
                    return (
                      <td key={`${day}-${time}`} className="py-3 px-4 border-b">
                        {slot ? (
                          <div className="bg-blue-50 p-2 rounded">
                            <div className="font-medium">{slot.subject}</div>
                            <div className="text-sm text-gray-600">{slot.room}</div>
                          </div>
                        ) : (
                          <div className="h-16"></div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">Schedule Preferences</h2>
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="morningClasses"
                name="morningClasses"
                checked={preferences.morningClasses}
                onChange={handlePreferenceChange}
                className="h-5 w-5 text-indigo-600 rounded"
              />
              <label htmlFor="morningClasses" className="ml-2 text-gray-700">
                Prefer morning classes
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="noBackToBack"
                name="noBackToBack"
                checked={preferences.noBackToBack}
                onChange={handlePreferenceChange}
                className="h-5 w-5 text-indigo-600 rounded"
              />
              <label htmlFor="noBackToBack" className="ml-2 text-gray-700">
                No back-to-back classes
              </label>
            </div>
            
            <div>
              <p className="text-gray-700 mb-2">Preferred days:</p>
              <div className="flex flex-wrap gap-2">
                {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].map(day => (
                  <button
                    key={day}
                    type="button"
                    onClick={() => handleDayToggle(day)}
                    className={`px-3 py-1 rounded-full text-sm ${
                      preferences.preferredDays.includes(day)
                        ? 'bg-indigo-500 text-white'
                        : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    {day}
                  </button>
                ))}
              </div>
            </div>
            
            <div>
              <p className="text-gray-700 mb-2">Electives:</p>
              <div className="flex flex-wrap gap-2">
                {mockUsers.student.electives.map(elective => (
                  <span key={elective} className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                    {elective}
                  </span>
                ))}
              </div>
            </div>
            
            <button className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700">
              Save Preferences
            </button>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">Notifications</h2>
          <div className="space-y-4">
            {notifications.map(notification => (
              <div 
                key={notification.id} 
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  notification.read ? 'bg-gray-50' : 'bg-blue-50'
                }`}
                onClick={() => markAsRead(notification.id)}
              >
                <div className="flex justify-between">
                  <p className="font-medium">{notification.title}</p>
                  {!notification.read && (
                    <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  )}
                </div>
                <p className="text-sm text-gray-600">{notification.message}</p>
                <p className="text-xs text-gray-500 mt-1">{notification.date}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">Request Changes</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-gray-700 mb-2">Request Type</label>
            <select className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option>Reschedule class</option>
              <option>Change room</option>
              <option>Swap with another student</option>
              <option>Other</option>
            </select>
          </div>
          
          <div>
            <label className="block text-gray-700 mb-2">Details</label>
            <textarea 
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" 
              rows="3"
              placeholder="Please provide details about your request..."
            ></textarea>
          </div>
          
          <button className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700">
            Submit Request
          </button>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;