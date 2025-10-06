import React from 'react';

const TimetableCard = ({ timetable, onSelect, isSelected, onApprove, onReschedule }) => {
  return (
    <div 
      className={`bg-white rounded-lg shadow p-4 cursor-pointer transition-all ${
        isSelected ? 'ring-2 ring-indigo-500' : 'hover:shadow-md'
      }`}
      onClick={() => onSelect(timetable)}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-lg font-semibold">{timetable.name}</h3>
        <span className={`px-2 py-1 rounded text-xs ${
          timetable.status === 'approved' ? 'bg-green-100 text-green-800' : 
          timetable.status === 'rejected' ? 'bg-red-100 text-red-800' : 
          'bg-yellow-100 text-yellow-800'
        }`}>
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
      
      <div className="grid grid-cols-3 gap-2 mb-3 text-xs">
        <div className="bg-blue-50 p-1 rounded text-center">
          <div className="font-medium">Workload</div>
          <div>{Math.round(timetable.objectives.workload * 100)}%</div>
        </div>
        <div className="bg-green-50 p-1 rounded text-center">
          <div className="font-medium">Utilization</div>
          <div>{Math.round(timetable.objectives.utilization * 100)}%</div>
        </div>
        <div className="bg-purple-50 p-1 rounded text-center">
          <div className="font-medium">Preferences</div>
          <div>{Math.round(timetable.objectives.preferences * 100)}%</div>
        </div>
      </div>
      
      <div className="flex justify-between space-x-2">
        <button 
          onClick={(e) => {
            e.stopPropagation();
            onApprove(timetable.id);
          }}
          className="flex-1 text-sm bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700"
        >
          Approve
        </button>
        <button 
          onClick={(e) => {
            e.stopPropagation();
            onReschedule(timetable.id);
          }}
          className="flex-1 text-sm border border-gray-300 px-3 py-1 rounded hover:bg-gray-100"
        >
          Reschedule
        </button>
      </div>
    </div>
  );
};

export default TimetableCard;