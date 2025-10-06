import React, { useState } from 'react';
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";

import { v4 as uuidv4 } from 'uuid';
import { mockTimetables } from '../data/mockData';
import { useNavigate } from 'react-router-dom';

const TimetableEditor = () => {
  const [timetable, setTimetable] = useState(mockTimetables[0].timetable);
  const [subjects, setSubjects] = useState([
    { id: uuidv4(), name: 'Mathematics', faculty: 'Dr. Smith', duration: 2 },
    { id: uuidv4(), name: 'Physics', faculty: 'Dr. Johnson', duration: 2 },
    { id: uuidv4(), name: 'Chemistry', faculty: 'Dr. Brown', duration: 2 },
    { id: uuidv4(), name: 'Computer Science', faculty: 'Dr. Williams', duration: 2 },
    { id: uuidv4(), name: 'Biology', faculty: 'Dr. Davis', duration: 2 },
  ]);
  
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const times = ['9-11', '11-1', '2-4', '4-6'];
  const rooms = ['A101', 'B203', 'C305', 'D401', 'E502'];
  const navigate = useNavigate();

  const handleDragEnd = (result) => {
    if (!result.destination) return;
    
    const { source, destination } = result;
    
    // Moving from subjects list to timetable
    if (source.droppableId === 'subjects' && destination.droppableId.startsWith('timetable-')) {
      const [day, time] = destination.droppableId.split('-').slice(1);
      const subject = subjects[source.index];
      
      // Remove from subjects list
      const newSubjects = [...subjects];
      newSubjects.splice(source.index, 1);
      setSubjects(newSubjects);
      
      // Add to timetable
      const newTimetable = [...timetable];
      const existingIndex = newTimetable.findIndex(slot => slot.day === day && slot.time === time);
      
      if (existingIndex >= 0) {
        // Replace existing slot
        newTimetable[existingIndex] = {
          ...newTimetable[existingIndex],
          subject: subject.name,
          faculty: subject.faculty,
          room: rooms[Math.floor(Math.random() * rooms.length)],
          students: 30 + Math.floor(Math.random() * 30)
        };
      } else {
        // Add new slot
        newTimetable.push({
          day,
          time,
          subject: subject.name,
          faculty: subject.faculty,
          room: rooms[Math.floor(Math.random() * rooms.length)],
          students: 30 + Math.floor(Math.random() * 30)
        });
      }
      
      setTimetable(newTimetable);
    }
    
    // Moving within timetable
    else if (source.droppableId.startsWith('timetable-') && destination.droppableId.startsWith('timetable-')) {
      const [sourceDay, sourceTime] = source.droppableId.split('-').slice(1);
      const [destDay, destTime] = destination.droppableId.split('-').slice(1);
      
      const sourceIndex = timetable.findIndex(slot => slot.day === sourceDay && slot.time === sourceTime);
      const destIndex = timetable.findIndex(slot => slot.day === destDay && slot.time === destTime);
      
      if (sourceIndex >= 0 && destIndex >= 0) {
        const newTimetable = [...timetable];
        const temp = { ...newTimetable[sourceIndex] };
        
        // Swap day and time
        newTimetable[sourceIndex] = { ...newTimetable[destIndex], day: sourceDay, time: sourceTime };
        newTimetable[destIndex] = { ...temp, day: destDay, time: destTime };
        
        setTimetable(newTimetable);
      }
    }
    
    // Moving from timetable back to subjects
    else if (source.droppableId.startsWith('timetable-') && destination.droppableId === 'subjects') {
      const [day, time] = source.droppableId.split('-').slice(1);
      const sourceIndex = timetable.findIndex(slot => slot.day === day && slot.time === time);
      
      if (sourceIndex >= 0) {
        const slot = timetable[sourceIndex];
        
        // Remove from timetable
        const newTimetable = [...timetable];
        newTimetable.splice(sourceIndex, 1);
        setTimetable(newTimetable);
        
        // Add back to subjects
        setSubjects([
          ...subjects,
          { 
            id: uuidv4(), 
            name: slot.subject, 
            faculty: slot.faculty, 
            duration: 2 
          }
        ]);
      }
    }
  };

  const saveTimetable = () => {
    alert('Timetable saved successfully!');
    // In a real app, this would save to Firestore
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Timetable Editor</h1>
        <div className="flex space-x-3">
          <button 
            onClick={() => navigate('/admin')}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Back to Dashboard
          </button>
          <button 
            onClick={saveTimetable}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            Save Timetable
          </button>
        </div>
      </div>
      
      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <div className="bg-white p-4 rounded-lg shadow mb-4">
              <h2 className="text-lg font-semibold mb-3 text-gray-700">Available Subjects</h2>
              <Droppable droppableId="subjects">
                {(provided) => (
                  <div 
                    {...provided.droppableProps} 
                    ref={provided.innerRef}
                    className="space-y-2 min-h-[200px]"
                  >
                    {subjects.map((subject, index) => (
                      <Draggable key={subject.id} draggableId={subject.id} index={index}>
                        {(provided) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className="bg-blue-50 p-3 rounded-lg border border-blue-200 cursor-move"
                          >
                            <div className="font-medium">{subject.name}</div>
                            <div className="text-sm text-gray-600">{subject.faculty}</div>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-3 text-gray-700">Conflict Detection</h2>
              <div className="space-y-2">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
                  <span className="text-sm">No conflicts detected</span>
                </div>
                <div className="text-xs text-gray-500">
                  Conflicts will appear here if any are detected during scheduling.
                </div>
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-3">
            <div className="bg-white p-4 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-3 text-gray-700">Weekly Timetable</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="py-2 px-3 border-b">Time</th>
                      {days.map(day => (
                        <th key={day} className="py-2 px-3 border-b">{day}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {times.map(time => (
                      <tr key={time}>
                        <td className="py-2 px-3 border-b font-medium">{time}</td>
                        {days.map(day => {
                          const slot = timetable.find(s => s.day === day && s.time === time);
                          return (
                            <td key={`${day}-${time}`} className="py-2 px-3 border-b">
                              <Droppable droppableId={`timetable-${day}-${time}`}>
                                {(provided) => (
                                  <div
                                    {...provided.droppableProps}
                                    ref={provided.innerRef}
                                    className="min-h-[60px]"
                                  >
                                    {slot && (
                                      <Draggable 
                                        draggableId={`${day}-${time}-${slot.subject}`} 
                                        index={0}
                                      >
                                        {(provided) => (
                                          <div
                                            ref={provided.innerRef}
                                            {...provided.draggableProps}
                                            {...provided.dragHandleProps}
                                            className="bg-green-50 p-2 rounded border border-green-200 cursor-move"
                                          >
                                            <div className="font-medium">{slot.subject}</div>
                                            <div className="text-xs text-gray-600">{slot.faculty} | {slot.room}</div>
                                            <div className="text-xs text-gray-500">{slot.students} students</div>
                                          </div>
                                        )}
                                      </Draggable>
                                    )}
                                    {provided.placeholder}
                                  </div>
                                )}
                              </Droppable>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </DragDropContext>
    </div>
  );
};

export default TimetableEditor;