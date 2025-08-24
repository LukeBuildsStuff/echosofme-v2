import React from 'react';

interface EleanorNotificationProps {
  message: string;
  onDismiss: () => void;
  onClick: () => void;
}

const EleanorNotification: React.FC<EleanorNotificationProps> = ({
  message,
  onDismiss,
  onClick
}) => {
  return (
    <div className="fixed top-4 right-4 z-50 animate-slide-in-top">
      <div 
        className="bg-white dark:bg-dark-2 rounded-lg shadow-lg border border-gray-200 dark:border-dark-3 p-4 max-w-sm cursor-pointer hover:shadow-xl transition-all duration-200"
        onClick={onClick}
      >
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center shadow-sm">
              <span className="text-white text-sm font-medium">E</span>
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-900 dark:text-white">Eleanor</p>
              <button 
                onClick={(e) => { 
                  e.stopPropagation(); 
                  onDismiss(); 
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 ml-2 p-1"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-3">
              {message}
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">Just now</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EleanorNotification;