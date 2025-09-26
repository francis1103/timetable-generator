import React, { useState } from 'react';
import { mockTimetables } from '../data/mockData';
import { useNavigate } from 'react-router-dom';

const TimetableGenerator = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [generatedTimetables, setGeneratedTimetables] = useState([]);
  const [algorithm, setAlgorithm] = useState('nsga2');
  const navigate = useNavigate();

  const generateTimetables = () => {
    setIsGenerating(true);
    setProgress(0);
    
    // Simulate AI generation process
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          
          // Create 3 new mock timetables
          const newTimetables = [
            {
              id: `gen${Date.now()}-1`,
              name: 'Generated Option 1',
              status: 'pending',
              paretoScore: 0.88 + Math.random() * 0.1,
              objectives: {
                workload: 0.85 + Math.random() * 0.1,
                utilization: 0.85 + Math.random() * 0.1,
                preferences: 0.85 + Math.random() * 0.1
              },
              conflicts: 0,
              algorithm: algorithm,
              timetable: generateRandomTimetable()
            },
            {
              id: `gen${Date.now()}-2`,
              name: 'Generated Option 2',
              status: 'pending',
              paretoScore: 0.82 + Math.random() * 0.1,
              objectives: {
                workload: 0.80 + Math.random() * 0.1,
                utilization: 0.80 + Math.random() * 0.1,
                preferences: 0.80 + Math.random() * 0.1
              },
              conflicts: 0,
              algorithm: algorithm,
              timetable: generateRandomTimetable()
            },
            {
              id: `gen${Date.now()}-3`,
              name: 'Generated Option 3',
              status: 'pending',
              paretoScore: 0.78 + Math.random() * 0.1,
              objectives: {
                workload: 0.75 + Math.random() * 0.1,
                utilization: 0.75 + Math.random() * 0.1,
                preferences: 0.75 + Math.random() * 0.1
              },
              conflicts: 0,
              algorithm: algorithm,
              timetable: generateRandomTimetable()
            }
          ];
          
          setGeneratedTimetables(newTimetables);
          setIsGenerating(false);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const generateRandomTimetable = () => {
    const subjects = ['Mathematics', 'Physics', 'Chemistry', 'Computer Science', 'Biology'];
    const faculty = ['Dr. Smith', 'Dr. Johnson', 'Dr. Williams', 'Dr. Brown', 'Dr. Davis'];
    const rooms = ['A101', 'B203', 'C305', 'D401', 'E502'];
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const times = ['9-11', '11-1', '2-4', '4-6'];
    
    const timetable = [];
    
    // Generate 10 random class slots
    for (let i = 0; i < 10; i++) {
      const subject = subjects[Math.floor(Math.random() * subjects.length)];
      const prof = faculty[Math.floor(Math.random() * faculty.length)];
      const room = rooms[Math.floor(Math.random() * rooms.length)];
      const day = days[Math.floor(Math.random() * days.length)];
      const time = times[Math.floor(Math.random() * times.length)];
      const students = 30 + Math.floor(Math.random() * 30);
      
      // Avoid duplicates
      if (!timetable.some(slot => slot.day === day && slot.time === time)) {
        timetable.push({ day, time, subject, faculty: prof, room, students });
      }
    }
    
    return timetable;
  };

  const viewTimetable = (timetable) => {
    // In a real app, this would navigate to the editor with the timetable data
    alert(`Viewing timetable: ${timetable.name}`);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">AI Timetable Generator</h1>
        <button 
          onClick={() => navigate('/admin')}
          className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          Back to Dashboard
        </button>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">Algorithm Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-gray-700 mb-2">Select Algorithm</label>
            <select 
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="nsga2">NSGA-II (Multi-Objective)</option>
              <option value="conflict">Conflict Graph Based</option>
              <option value="hybrid">Hybrid Approach</option>
            </select>
          </div>
          
          <div>
            <label className="block text-gray-700 mb-2">Optimization Objectives</label>
            <div className="space-y-2">
              <div className="flex items-center">
                <input type="checkbox" id="workload" className="mr-2" defaultChecked />
                <label htmlFor="workload">Faculty Workload Balance</label>
              </div>
              <div className="flex items-center">
                <input type="checkbox" id="utilization" className="mr-2" defaultChecked />
                <label htmlFor="utilization">Room Utilization</label>
              </div>
              <div className="flex items-center">
                <input type="checkbox" id="preferences" className="mr-2" defaultChecked />
                <label htmlFor="preferences">Student Preferences</label>
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-6">
          <p className="text-gray-600 mb-6">
            Our AI-powered generator will create 3 Pareto-optimal timetable options based on the selected algorithm and objectives. 
            The system uses conflict graphs to ensure clash-free scheduling while optimizing for multiple objectives.
          </p>
          
          <div className="flex items-center space-x-4">
            <button 
              onClick={generateTimetables}
              disabled={isGenerating}
              className={`px-6 py-3 rounded-lg font-medium ${
                isGenerating 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
            >
              {isGenerating ? 'Generating...' : 'Generate Timetables'}
            </button>
            
            {isGenerating && (
              <div className="flex-1">
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    className="bg-indigo-600 h-2.5 rounded-full" 
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {algorithm === 'nsga2' ? 'Running NSGA-II algorithm...' : 
                   algorithm === 'conflict' ? 'Building conflict graph...' : 
                   'Running hybrid algorithm...'} {progress}%
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {generatedTimetables.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">Generated Timetables</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {generatedTimetables.map((timetable) => (
              <div key={timetable.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold">{timetable.name}</h3>
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">
                    {timetable.status}
                  </span>
                </div>
                
                <div className="mb-3">
                  <div className="text-sm text-gray-600 mb-1">Pareto Score</div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-indigo-600 h-2 rounded-full" 
                      style={{ width: `${timetable.paretoScore * 100}%` }}
                    ></div>
                  </div>
                  <div className="text-right text-xs text-gray-500 mt-1">
                    {Math.round(timetable.paretoScore * 100)}%
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-1 mb-3 text-xs">
                  <div className="bg-blue-50 p-1 rounded text-center">
                    <div>Workload</div>
                    <div>{Math.round(timetable.objectives.workload * 100)}%</div>
                  </div>
                  <div className="bg-green-50 p-1 rounded text-center">
                    <div>Utilization</div>
                    <div>{Math.round(timetable.objectives.utilization * 100)}%</div>
                  </div>
                  <div className="bg-purple-50 p-1 rounded text-center">
                    <div>Preferences</div>
                    <div>{Math.round(timetable.objectives.preferences * 100)}%</div>
                  </div>
                </div>
                
                <div className="text-sm text-gray-600 mb-4">
                  <div className="flex justify-between">
                    <span>Algorithm:</span>
                    <span className="font-medium">{timetable.algorithm.toUpperCase()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Classes:</span>
                    <span>{timetable.timetable.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Conflicts:</span>
                    <span className="text-green-600">{timetable.conflicts}</span>
                  </div>
                </div>
                
                <button 
                  onClick={() => viewTimetable(timetable)}
                  className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700"
                >
                  View Details
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TimetableGenerator;