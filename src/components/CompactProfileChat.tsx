import React from 'react';

interface CompactProfileChatProps {
  onExpand: () => void;
  isCompleted: boolean;
}

const CompactProfileChat: React.FC<CompactProfileChatProps> = ({ onExpand, isCompleted }) => {
  if (isCompleted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="text-green-600 text-2xl mr-3">✅</div>
            <div>
              <h3 className="text-sm font-semibold text-green-800">Profile Complete</h3>
              <p className="text-xs text-green-600">Your comprehensive profile has been saved</p>
            </div>
          </div>
          <button
            onClick={onExpand}
            className="text-green-600 hover:text-green-700 text-sm font-medium px-3 py-1 rounded-md hover:bg-green-100 transition-colors"
          >
            View Details
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 hover:bg-blue-100 transition-colors cursor-pointer" onClick={onExpand}>
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className="text-blue-600 text-2xl mr-3">🤖</div>
          <div>
            <h3 className="text-sm font-semibold text-blue-800">Complete Your Profile</h3>
            <p className="text-xs text-blue-600">Chat with our assistant to build your comprehensive profile</p>
          </div>
        </div>
        <div className="text-blue-600">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>
  );
};

export default CompactProfileChat;