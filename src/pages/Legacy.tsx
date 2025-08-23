import React, { useState } from 'react';
import Layout from '../components/Layout/Layout';
import { useEcho, type Reflection } from '../contexts/EchoContext';

const Legacy: React.FC = () => {
  const { reflections, stats, updateReflection, deleteReflection } = useEcho();
  const [editingReflection, setEditingReflection] = useState<Reflection | null>(null);
  const [editText, setEditText] = useState('');
  const [isDeleting, setIsDeleting] = useState<string | null>(null);

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    if (diffDays <= 30) return `${Math.ceil((diffDays - 1) / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  // Get category color
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'philosophy_values': 'primary',
      'family_parenting': 'green-500',
      'career': 'blue-500',
      'personal_history': 'purple-500',
      'hobbies': 'orange-500',
      'friendships_social': 'pink-500',
      'education': 'indigo-500',
      'daily_life': 'yellow-500',
      'romantic_love': 'red-500',
      'life_milestones': 'emerald-500',
      'marriage_partnerships': 'teal-500'
    };
    return colors[category] || 'gray-500';
  };

  // Sort reflections by date (newest first)
  const sortedReflections = [...reflections].sort((a, b) => 
    new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );

  // Handle edit reflection
  const handleEditClick = (reflection: Reflection) => {
    setEditingReflection(reflection);
    setEditText(reflection.response);
  };

  const handleSaveEdit = async () => {
    if (!editingReflection) return;
    
    try {
      await updateReflection(editingReflection.id, {
        response: editText,
        wordCount: editText.split(' ').length
      });
      setEditingReflection(null);
      setEditText('');
    } catch (error) {
      alert('Failed to update reflection. Please try again.');
    }
  };

  const handleCancelEdit = () => {
    setEditingReflection(null);
    setEditText('');
  };

  // Handle delete reflection
  const handleDeleteClick = async (reflectionId: string) => {
    if (!confirm('Are you sure you want to delete this reflection? This action cannot be undone.')) {
      return;
    }

    setIsDeleting(reflectionId);
    try {
      await deleteReflection(reflectionId);
    } catch (error) {
      alert('Failed to delete reflection. Please try again.');
    } finally {
      setIsDeleting(null);
    }
  };

  return (
    <Layout hideFooter={true}>
      <div className="pt-20 min-h-screen bg-gray-50">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Your Legacy Timeline</h1>
            <p className="text-gray-600">
              A beautiful chronicle of your {stats.totalReflections} reflections and memories across {stats.categoriesCovered.length} life areas.
            </p>
          </div>

          {reflections.length > 0 ? (
            <div className="relative">
              <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>
              
              {/* Real Timeline Items */}
              <div className="space-y-8">
                {sortedReflections.map((reflection) => {
                  const categoryColor = getCategoryColor(reflection.category);
                  const displayCategory = reflection.category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                  
                  return (
                    <div key={reflection.id} className="relative flex items-start space-x-6">
                      <div className={`flex-shrink-0 w-4 h-4 bg-${categoryColor} rounded-full mt-1`}></div>
                      <div className="bg-white rounded-lg p-6 shadow-sm border flex-1 hover:shadow-lg transition-shadow duration-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className={`text-sm font-medium text-${categoryColor}`}>
                            {displayCategory}
                          </span>
                          <span className="text-sm text-gray-500">
                            {formatDate(reflection.createdAt)}
                          </span>
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-2">
                          {reflection.question}
                        </h3>
                        <p className="text-gray-600 text-sm">
                          {reflection.response.length > 200 
                            ? `${reflection.response.substring(0, 200)}...` 
                            : reflection.response
                          }
                        </p>
                        <div className="mt-3 flex items-center justify-between">
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span>{reflection.wordCount} words</span>
                            <span>Quality: {Math.round(reflection.qualityScore * 100)}%</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleEditClick(reflection)}
                              className="text-gray-400 hover:text-blue-600 text-sm transition-colors hover:scale-110 transform duration-200"
                              title="Edit reflection"
                            >
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                              </svg>
                            </button>
                            <button
                              onClick={() => handleDeleteClick(reflection.id)}
                              disabled={isDeleting === reflection.id}
                              className="text-gray-400 hover:text-red-600 text-sm transition-colors disabled:opacity-50 hover:scale-110 transform duration-200"
                              title="Delete reflection"
                            >
                              {isDeleting === reflection.id ? (
                                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                              ) : (
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                                </svg>
                              )}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="mt-12 text-center">
              <div className="bg-white rounded-lg p-8 shadow-sm border">
                <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0118 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                </svg>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Your Legacy Awaits</h3>
                <p className="text-gray-600 mb-6">Start creating your digital legacy by chatting with Eleanor or writing your first reflection.</p>
                <div className="flex justify-center space-x-4">
                  <button className="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary/90 hover:scale-105 transition-all duration-200">
                    Chat with Eleanor
                  </button>
                  <button className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-50 hover:scale-105 transition-all duration-200">
                    Write Reflection
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Edit Modal */}
      {editingReflection && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Edit Reflection
              </h3>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Question: {editingReflection.question}
                </label>
                <textarea
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={8}
                  placeholder="Share your thoughts..."
                />
                <div className="mt-2 text-sm text-gray-500">
                  {editText.split(' ').length} words
                </div>
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={handleCancelEdit}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 hover:scale-105 transition-all duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveEdit}
                  disabled={!editText.trim()}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 transition-all duration-200"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};

export default Legacy;