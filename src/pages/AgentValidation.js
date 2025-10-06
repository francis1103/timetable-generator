import React, { useState } from 'react';
import { mockAgents } from '../data/mockData';
import AgentValidation from '../components/AgentValidation';
import { useNavigate } from 'react-router-dom';

const AgentValidationPage = () => {
  const [agents, setAgents] = useState(mockAgents);
  const navigate = useNavigate();

  const handleValidation = (agentType) => {
    // Simulate agent negotiation
    if (agentType === 'admin') {
      alert('Admin has given final approval. Timetable will be published.');
      // In a real app, this would save to Firestore and notify users
    } else {
      const updatedAgents = { ...agents };
      
      // Simulate agent response
      if (agentType === 'student') {
        updatedAgents.student = {
          ...updatedAgents.student,
          response: "Thank you for addressing my concern. I'm now satisfied with the schedule.",
          accepted: true,
          reason: ""
        };
      } else if (agentType === 'faculty') {
        updatedAgents.faculty = {
          ...updatedAgents.faculty,
          response: "I've reviewed the changes and they work for me.",
          accepted: true,
          reason: ""
        };
      }
      
      setAgents(updatedAgents);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Agent Validation</h1>
        <button 
          onClick={() => navigate('/admin')}
          className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          Back to Dashboard
        </button>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AgentValidation agents={agents} onValidate={handleValidation} />
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">Agent Negotiation Process</h2>
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-medium mb-2">Multi-Agent System</h3>
              <p className="text-sm text-gray-600">
                Our system uses LangChain agents to simulate stakeholder negotiation. 
                Each agent represents a different perspective in the timetable scheduling process.
              </p>
            </div>
            
            <div className="p-4 bg-green-50 rounded-lg">
              <h3 className="font-medium mb-2">Faculty Agent</h3>
              <p className="text-sm text-gray-600">
                Evaluates schedules based on workload balance, teaching preferences, 
                and research time availability.
              </p>
            </div>
            
            <div className="p-4 bg-purple-50 rounded-lg">
              <h3 className="font-medium mb-2">Student Agent</h3>
              <p className="text-sm text-gray-600">
                Assesses schedules based on class preferences, gap times between classes, 
                and overall learning experience.
              </p>
            </div>
            
            <div className="p-4 bg-yellow-50 rounded-lg">
              <h3 className="font-medium mb-2">Room Agent</h3>
              <p className="text-sm text-gray-600">
                Ensures optimal room utilization, appropriate room sizes for class enrollments, 
                and equipment availability.
              </p>
            </div>
            
            <div className="p-4 bg-red-50 rounded-lg">
              <h3 className="font-medium mb-2">Admin Agent</h3>
              <p className="text-sm text-gray-600">
                Provides final approval based on institutional constraints, policies, 
                and overall stakeholder satisfaction.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentValidationPage;