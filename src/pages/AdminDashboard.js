import React, { useState } from 'react';
import { mockTimetables, mockAnalytics } from '../data/mockData';
import TimetableCard from '../components/TimetableCard';
import AnalyticsChart from '../components/AnalyticsChart';
import { useNavigate } from 'react-router-dom';

const AdminDashboard = () => {
  const [timetables, setTimetables] = useState(mockTimetables);
  const [selectedTimetable, setSelectedTimetable] = useState(mockTimetables[0]);
  const navigate = useNavigate();

  const generateNewTimetable = () => {
    // Create a new mock timetable
    const newTimetable = {
      id: `opt${timetables.length + 1}`,
      name: `Option ${timetables.length + 1}`,
      status: 'pending',
      paretoScore: 0.75 + Math.random() * 0.2, // Random score between 0.75-0.95
      objectives: {
        workload: 0.7 + Math.random() * 0.2,
        utilization: 0.7 + Math.random() * 0.2,
        preferences: 0.7 + Math.random() * 0.2
      },
      conflicts: 0,
      timetable: [
        { day: 'Monday', time: '9-11', subject: 'Mathematics', room: 'A101', faculty: 'Dr. Smith', students: 45 },
        { day: 'Monday', time: '11-1', subject: 'Physics', room: 'B203', faculty: 'Dr. Johnson', students: 38 },
        { day: 'Monday', time: '2-4', subject: 'Computer Science', room: 'C305', faculty: 'Dr. Williams', students: 52 },
        { day: 'Tuesday', time: '9-11', subject: 'Chemistry', room: 'D401', faculty: 'Dr. Brown', students: 40 },
        { day: 'Tuesday', time: '11-1', subject: 'Mathematics', room: 'A101', faculty: 'Dr. Smith', students: 45 },
        { day: 'Wednesday', time: '9-11', subject: 'Physics', room: 'B203', faculty: 'Dr. Johnson', students: 38 },
        { day: 'Wednesday', time: '2-4', subject: 'Computer Science', room: 'C305', faculty: 'Dr. Williams', students: 52 },
        { day: 'Thursday', time: '9-11', subject: 'Chemistry', room: 'D401', faculty: 'Dr. Brown', students: 40 },
        { day: 'Thursday', time: '11-1', subject: 'Mathematics', room: 'A101', faculty: 'Dr. Smith', students: 45 },
        { day: 'Friday', time: '9-11', subject: 'Physics', room: 'B203', faculty: 'Dr. Johnson', students: 38 },
      ]
    };
    
    setTimetables([...timetables, newTimetable]);
    setSelectedTimetable(newTimetable);
  };

  const approveTimetable = (id) => {
    setTimetables(timetables.map(t => 
      t.id === id ? { ...t, status: 'approved' } : t
    ));
  };

  const rescheduleTimetable = (id) => {
    alert(`Rescheduling timetable ${id}. This would trigger the AI rescheduling process.`);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Admin Dashboard</h1>
        <div className="flex space-x-3">
          <button 
            onClick={generateNewTimetable}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 flex items-center"
          >
            <span className="mr-2">🔄</span> Generate New
          </button>
          <button 
            onClick={() => navigate('/admin/generator')}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 flex items-center"
          >
            <span className="mr-2">🤖</span> AI Generator
          </button>
          <button 
            onClick={() => navigate('/admin/editor')}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center"
          >
            <span className="mr-2">✏️</span> Editor
          </button>
        </div>
      </div>
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">Timetable Proposals</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {timetables.map((timetable) => (
            <TimetableCard
              key={timetable.id}
              timetable={timetable}
              onSelect={setSelectedTimetable}
              isSelected={selectedTimetable.id === timetable.id}
              onApprove={approveTimetable}
              onReschedule={rescheduleTimetable}
            />
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">System Overview</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-700">24</div>
              <div className="text-gray-600">Total Faculty</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-700">18</div>
              <div className="text-gray-600">Available Rooms</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-700">342</div>
              <div className="text-gray-600">Total Students</div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-yellow-700">12</div>
              <div className="text-gray-600">Pending Requests</div>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">Recent Activity</h2>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="bg-blue-100 p-2 rounded-full mr-3">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div>
                <p className="font-medium">Timetable approved</p>
                <p className="text-sm text-gray-500">Admin approved Option 2 timetable</p>
                <p className="text-xs text-gray-400">2 hours ago</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="bg-yellow-100 p-2 rounded-full mr-3">
                <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
              </div>
              <div>
                <p className="font-medium">Faculty unavailable</p>
                <p className="text-sm text-gray-500">Dr. Johnson reported unavailable for Friday</p>
                <p className="text-xs text-gray-400">5 hours ago</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="bg-green-100 p-2 rounded-full mr-3">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <div>
                <p className="font-medium">New room added</p>
                <p className="text-sm text-gray-500">Room C205 added to system</p>
                <p className="text-xs text-gray-400">Yesterday</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <AnalyticsChart 
          type="bar"
          title="Faculty Workload Distribution" 
          data={mockAnalytics.facultyWorkload} 
          dataKey="hours"
          additionalDataKey="maxHours"
        />
        <AnalyticsChart 
          type="bar"
          title="Room Utilization Rate" 
          data={mockAnalytics.roomUtilization} 
          dataKey="utilization"
        />
      </div>
    </div>
  );
};

export default AdminDashboard;