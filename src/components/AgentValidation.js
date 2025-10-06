import React from 'react';

const AgentValidation = ({ agents, onValidate }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4 text-gray-700">Agent Validation</h2>
      <div className="space-y-4">
        {Object.entries(agents).map(([agentType, agentData]) => (
          <div key={agentType} className="border rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold capitalize">{agentType} Agent</h3>
              <span className={`px-2 py-1 rounded text-xs ${
                agentData.accepted ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {agentData.accepted ? 'Accepted' : 'Rejected'}
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-3">{agentData.response}</p>
            {!agentData.accepted && agentData.reason && (
              <div className="text-sm text-red-600 mb-3">
                <span className="font-medium">Reason:</span> {agentData.reason}
              </div>
            )}
            <button 
              onClick={() => onValidate(agentType)}
              className="text-sm bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700"
            >
              Re-negotiate
            </button>
          </div>
        ))}
        
        <div className="flex justify-end space-x-3 pt-4">
          <button className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
            Generate New Option
          </button>
          <button 
            onClick={() => onValidate('admin')}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            Final Approval
          </button>
        </div>
      </div>
    </div>
  );
};

export default AgentValidation;