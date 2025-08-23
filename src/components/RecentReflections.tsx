import React from 'react';
import { useEcho } from '../contexts/EchoContext';

interface RecentReflectionsProps {
  limit?: number;
}

const RecentReflections: React.FC<RecentReflectionsProps> = ({ limit = 5 }) => {
  const { reflections } = useEcho();
  
  const recentReflections = reflections
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, limit);

  if (recentReflections.length === 0) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-lg transition-shadow duration-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Reflections</h3>
        <div className="text-center py-8">
          <div className="text-4xl mb-2">📝</div>
          <p className="text-gray-600 mb-4">No reflections yet</p>
          <p className="text-sm text-gray-500">Start training your Echo by sharing your first reflection!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-lg transition-shadow duration-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Reflections</h3>
      <div className="space-y-4">
        {recentReflections.map((reflection) => (
          <div key={reflection.id} className="border-l-4 border-primary/30 pl-4 py-2 hover:bg-gray-50 transition-colors duration-200 cursor-pointer rounded-r-lg">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 mb-1">
                  {reflection.question}
                </p>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {reflection.response.length > 120 
                    ? `${reflection.response.substring(0, 120)}...` 
                    : reflection.response}
                </p>
                <div className="flex items-center mt-2 space-x-4 text-xs text-gray-500">
                  <span>{reflection.wordCount} words</span>
                  <span>{Math.round(reflection.qualityScore * 100)}% quality</span>
                  <span>{new Date(reflection.createdAt).toLocaleDateString()}</span>
                </div>
              </div>
              
              {/* Category Badge */}
              <span className="ml-3 px-2 py-1 text-xs font-medium bg-primary/10 text-primary rounded-full hover:bg-primary/20 transition-colors duration-200 cursor-pointer">
                {reflection.category}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      {reflections.length > limit && (
        <div className="mt-4 pt-4 border-t border-gray-200 text-center">
          <p className="text-sm text-gray-600">
            Showing {limit} of {reflections.length} reflections
          </p>
        </div>
      )}
    </div>
  );
};

export default RecentReflections;