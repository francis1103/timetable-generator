import React, { useState } from 'react';
import { mockTimetables, mockAnalytics, mockUsers } from '../data/mockData';
import AnalyticsChart from '../components/AnalyticsChart';

const FacultyDashboard = () => {
  const [availability, setAvailability] = useState(mockUsers.faculty.availability);
  const [requests, setRequests] = useState([
    {
      id: 1,
      student: 'John Doe',
      type: 'Reschedule',
      details: 'Request to move Friday class to Thursday due to personal commitment',
      status: 'pending',
      date: '2023-05-15'
    },
    {
      id: 2,
      student: 'Sarah Johnson',
      type: 'Room Change',
      details: 'Request larger room for CS101 as enrollment has increased',
      status: 'approved',
      date: '2023-05-10'
    }
  ]);

  const toggleAvailability = (day) => {
    setAvailability({
      ...availability,
      [day]: !availability[day]
    });
  };

  const facultySchedule = mockTimetables[0].timetable.filter(
    slot => slot.faculty === 'Dr. Smith'
  );

  const handleRequestAction = (id, action) => {
    setRequests(requests.map(req => 
      req.id === id ? { ...req, status: action } : req
    ));
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Faculty Dashboard</h1>
        <div className="text-sm text-gray-500">
          Dr. Smith | Computer Science
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow lg:col-span-2">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">My Schedule</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white">
              <thead>
                <tr>
                  <th className="py-2 px-4 border-b">Day</th>
                  <th className="py-2 px-4 border-b">Time</th>
                  <th className="py-2 px-4 border-b">Subject</th>
                  <th className="py-2 px-4 border-b">Room</th>
                  <th className="py-2 px-4 border-b">Students</th>
                </tr>
              </thead>
              <tbody>
                {facultySchedule.map((slot, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="py-3 px-4 border-b">{slot.day}</td>
                    <td className="py-3 px-4 border-b">{slot.time}</td>
                    <td className="py-3 px-4 border-b font-medium">{slot.subject}</td>
                    <td className="py-3 px-4 border-b">{slot.room}</td>
                    <td className="py-3 px-4 border-b">{slot.students}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">Workload Summary</h2>
          <div className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-3xl font-bold text-blue-700">12</div>
              <div className="text-gray-600">Hours this week</div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-3xl font-bold text-green-700">3</div>
              <div className="text-gray-600">Subjects assigned</div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-3xl font-bold text-purple-700">85%</div>
              <div className="text-gray-600">Preferred schedule match</div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">Set Availability</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(availability).map(([day, available]) => (
              <div 
                key={day} 
                className={`p-4 rounded-lg cursor-pointer transition-colors duration-200 ${
                  available ? 'bg-green-100 border-2 border-green-500' : 'bg-red-100 border-2 border-red-500'
                }`}
                onClick={() => toggleAvailability(day)}
              >
                <div className="font-medium">{day}</div>
                <div className="text-sm mt-1">
                  {available ? 'Available' : 'Unavailable'}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">Workload Analytics</h2>
          <AnalyticsChart 
            type="bar"
            title="Faculty Workload Comparison" 
            data={mockAnalytics.facultyWorkload} 
            dataKey="hours"
            additionalDataKey="maxHours"
          />
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">Student Requests</h2>
        <div className="space-y-4">
          {requests.map(request => (
            <div key={request.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <div className="flex items-center">
                  <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                    request.status === 'pending' ? 'bg-yellow-500' : 
                    request.status === 'approved' ? 'bg-green-500' : 'bg-red-500'
                  }`}></span>
                  <p className="font-medium">{request.type} Request</p>
                </div>
                <p className="text-sm text-gray-500">{request.student} - {request.details}</p>
                <p className="text-xs text-gray-400">Submitted: {request.date}</p>
              </div>
              <div className="flex space-x-2">
                {request.status === 'pending' && (
                  <>
                    <button 
                      onClick={() => handleRequestAction(request.id, 'approved')}
                      className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                    >
                      Approve
                    </button>
                    <button 
                      onClick={() => handleRequestAction(request.id, 'rejected')}
                      className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                    >
                      Decline
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FacultyDashboard;