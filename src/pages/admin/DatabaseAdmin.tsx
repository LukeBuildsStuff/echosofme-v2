import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout/Layout';
import { useAuth } from '../../contexts/SupabaseAuthContext';
import { getEleanorApiUrl } from '../../utils/apiConfig';
import SparkleLoader from '../../components/SparkleLoader';

interface Question {
  id: number;
  question_text: string;
  category: string;
  subcategory: string;
  difficulty_level: number;
  question_type: string;
  usage_count?: number;
}

interface Response {
  id: number;
  user_id: number;
  question_id: number;
  response_text: string;
  word_count: number;
  created_at: string;
  question_text_snapshot?: string;
  category_snapshot?: string;
  user_email?: string;
}

interface EditQuestion {
  id: number;
  question_text: string;
  category: string;
}

interface PaginatedResponse<T> {
  total: number;
  limit: number;
  offset: number;
  data: T[];
}

interface QuestionsResponse extends PaginatedResponse<Question> {
  questions: Question[];
}

interface ResponsesResponse extends PaginatedResponse<Response> {
  responses: Response[];
}

interface DuplicateGroup {
  id: number;
  question_text: string;
  category: string;
}

const DatabaseAdmin: React.FC = () => {
  const { user, session } = useAuth();
  const navigate = useNavigate();

  // Security check
  if (user?.email !== 'lukemoeller@yahoo.com') {
    navigate('/dashboard');
    return null;
  }

  const [activeTab, setActiveTab] = useState<'questions' | 'responses' | 'duplicates'>('questions');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Questions state
  const [questionsData, setQuestionsData] = useState<QuestionsResponse | null>(null);
  const [questionSearch, setQuestionSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [questionPage, setQuestionPage] = useState(1);

  // Responses state
  const [responsesData, setResponsesData] = useState<ResponsesResponse | null>(null);
  const [responseSearch, setResponseSearch] = useState('');
  const [userFilter, setUserFilter] = useState('all');
  const [responsePage, setResponsePage] = useState(1);
  const [usersList, setUsersList] = useState<Array<{email: string, response_count: number}>>([]);

  // Duplicates state
  const [duplicates, setDuplicates] = useState<DuplicateGroup[][]>([]);
  const [duplicatesLoaded, setDuplicatesLoaded] = useState(false);

  // Edit modal state
  const [editingQuestion, setEditingQuestion] = useState<EditQuestion | null>(null);
  const [editingResponse, setEditingResponse] = useState<Response | null>(null);

  const itemsPerPage = 50;

  // Load questions with pagination
  const loadQuestions = useCallback(async (page: number = 1, search: string = '', category: string = 'all') => {
    setLoading(true);
    setError(null);

    try {
      const offset = (page - 1) * itemsPerPage;
      const params = new URLSearchParams({
        limit: itemsPerPage.toString(),
        offset: offset.toString(),
      });

      if (search) params.append('search', search);
      if (category !== 'all') params.append('category', category);

      const response = await fetch(`/api/admin/questions?${params}`, {
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        const data = await response.json();
        setQuestionsData(data);
      } else {
        throw new Error('Failed to load questions');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load questions');
    } finally {
      setLoading(false);
    }
  }, [session?.access_token]);

  // Load responses with pagination
  const loadResponses = useCallback(async (page: number = 1, search: string = '', userFilter: string = 'all') => {
    setLoading(true);
    setError(null);

    try {
      const offset = (page - 1) * itemsPerPage;
      const params = new URLSearchParams({
        limit: itemsPerPage.toString(),
        offset: offset.toString(),
      });

      if (search) params.append('search', search);
      if (userFilter !== 'all') params.append('user_filter', userFilter);

      const response = await fetch(`/api/admin/responses?${params}`, {
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        const data = await response.json();
        setResponsesData(data);
      } else {
        throw new Error('Failed to load responses');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load responses');
    } finally {
      setLoading(false);
    }
  }, [session?.access_token]);

  // Load duplicates (only when tab is active)
  const loadDuplicates = useCallback(async () => {
    if (duplicatesLoaded) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/admin/duplicates`, {
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        const data = await response.json();
        setDuplicates(data.duplicate_groups || []);
        setDuplicatesLoaded(true);
      } else {
        throw new Error('Failed to load duplicates');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load duplicates');
    } finally {
      setLoading(false);
    }
  }, [duplicatesLoaded, session?.access_token]);

  // Fetch users who have responses
  const fetchUsers = useCallback(async () => {
    try {
      const response = await fetch(`/api/admin/users`, {
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUsersList(data.users || []);
      } else {
        console.error('Failed to fetch users:', response.statusText);
      }
    } catch (err) {
      console.error('Error fetching users:', err);
    }
  }, [session?.access_token]);

  // Handle tab changes with lazy loading
  const handleTabChange = (tab: 'questions' | 'responses' | 'duplicates') => {
    setActiveTab(tab);
    setError(null);

    if (tab === 'questions' && !questionsData) {
      loadQuestions(1, questionSearch, categoryFilter);
    } else if (tab === 'responses') {
      if (usersList.length === 0) {
        fetchUsers();
      }
      if (!responsesData) {
        loadResponses(1, responseSearch, userFilter);
      }
    } else if (tab === 'duplicates' && !duplicatesLoaded) {
      loadDuplicates();
    }
  };

  // Load initial data for questions tab
  useEffect(() => {
    if (activeTab === 'questions') {
      loadQuestions(questionPage, questionSearch, categoryFilter);
    }
  }, [activeTab, questionPage, loadQuestions, questionSearch, categoryFilter]);

  // Handle search with debouncing
  useEffect(() => {
    if (activeTab === 'questions') {
      const timer = setTimeout(() => {
        setQuestionPage(1);
        loadQuestions(1, questionSearch, categoryFilter);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [questionSearch, categoryFilter, activeTab, loadQuestions]);

  useEffect(() => {
    if (activeTab === 'responses') {
      const timer = setTimeout(() => {
        setResponsePage(1);
        loadResponses(1, responseSearch, userFilter);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [responseSearch, userFilter, activeTab, loadResponses]);

  // Edit and delete functions
  const updateQuestion = async (id: number, updates: { question_text?: string; category?: string }) => {
    try {
      const response = await fetch(`/api/admin/questions/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates),
      });

      if (response.ok) {
        setEditingQuestion(null);
        loadQuestions(questionPage, questionSearch, categoryFilter);
      } else {
        throw new Error('Failed to update question');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update question');
    }
  };

  const deleteQuestion = async (id: number) => {
    if (!confirm('Are you sure you want to delete this question? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`/api/admin/questions/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        loadQuestions(questionPage, questionSearch, categoryFilter);
      } else {
        throw new Error('Failed to delete question');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete question');
    }
  };

  const deleteResponse = async (id: number) => {
    if (!confirm('Are you sure you want to delete this response? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`/api/admin/responses?id=${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        loadResponses(responsePage, responseSearch, userFilter);
      } else {
        throw new Error('Failed to delete response');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete response');
    }
  };

  // Pagination helpers
  const renderPagination = (currentPage: number, total: number, onPageChange: (page: number) => void) => {
    const totalPages = Math.ceil(total / itemsPerPage);
    if (totalPages <= 1) return null;

    return (
      <div className="flex justify-center items-center space-x-2 mt-6">
        <button
          onClick={() => onPageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
          className="px-3 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>

        <span className="text-sm text-gray-600">
          Page {currentPage} of {totalPages} ({total} total)
        </span>

        <button
          onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage === totalPages}
          className="px-3 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    );
  };

  if (loading && !questionsData && !responsesData) {
    return (
      <Layout hideFooter={true}>
        <div className="min-h-screen bg-gray-50 pt-20">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-center py-20">
              <SparkleLoader />
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout hideFooter={true}>
      <div className="min-h-screen bg-gray-50 pt-20">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Database Admin</h1>
            <p className="text-gray-600">Manage questions and responses</p>
          </div>

          {/* Error display */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="text-red-800">{error}</div>
            </div>
          )}

          {/* Tabs */}
          <div className="mb-6">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex">
                <button
                  onClick={() => handleTabChange('questions')}
                  className={`py-2 px-4 border-b-2 font-medium text-sm ${
                    activeTab === 'questions'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Questions {questionsData ? `(${questionsData.total})` : ''}
                </button>
                <button
                  onClick={() => handleTabChange('responses')}
                  className={`py-2 px-4 border-b-2 font-medium text-sm ${
                    activeTab === 'responses'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Responses {responsesData ? `(${responsesData.total})` : ''}
                </button>
                <button
                  onClick={() => handleTabChange('duplicates')}
                  className={`py-2 px-4 border-b-2 font-medium text-sm ${
                    activeTab === 'duplicates'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Duplicates {duplicatesLoaded ? `(${duplicates.length} groups)` : ''}
                </button>
              </nav>
            </div>
          </div>

          {/* Questions Tab */}
          {activeTab === 'questions' && (
            <div>
              {/* Search and filters */}
              <div className="mb-6 bg-white p-4 rounded-lg shadow">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Search Questions
                    </label>
                    <input
                      type="text"
                      value={questionSearch}
                      onChange={(e) => setQuestionSearch(e.target.value)}
                      placeholder="Search by question text or ID..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Filter by Category
                    </label>
                    <select
                      value={categoryFilter}
                      onChange={(e) => setCategoryFilter(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="all">All Categories</option>
                      <option value="personal_history">Personal History</option>
                      <option value="relationships">Relationships</option>
                      <option value="goals_aspirations">Goals & Aspirations</option>
                      <option value="values_beliefs">Values & Beliefs</option>
                      <option value="experiences_memories">Experiences & Memories</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Questions Table */}
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <SparkleLoader />
                </div>
              ) : questionsData && questionsData.questions ? (
                <>
                  <div className="bg-white rounded-lg shadow overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            ID
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Question
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Category
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Usage
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {questionsData.questions.map((question) => (
                          <tr key={question.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {question.id}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900 max-w-md">
                              <div className="truncate">{question.question_text}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {question.category}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {question.usage_count || 0}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                              <button
                                onClick={() => setEditingQuestion({
                                  id: question.id,
                                  question_text: question.question_text,
                                  category: question.category
                                })}
                                className="text-primary hover:text-primary-dark"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => deleteQuestion(question.id)}
                                className="text-red-600 hover:text-red-900"
                              >
                                Delete
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {renderPagination(questionPage, questionsData.total, setQuestionPage)}
                </>
              ) : (
                <div className="text-center py-8 text-gray-500">No questions found</div>
              )}
            </div>
          )}

          {/* Responses Tab */}
          {activeTab === 'responses' && (
            <div>
              {/* Search and filters */}
              <div className="mb-6 bg-white p-4 rounded-lg shadow">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Search Responses
                    </label>
                    <input
                      type="text"
                      value={responseSearch}
                      onChange={(e) => setResponseSearch(e.target.value)}
                      placeholder="Search by response text, ID, or question..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Filter by User
                    </label>
                    <select
                      value={userFilter}
                      onChange={(e) => setUserFilter(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="all">All Users</option>
                      {usersList.map(user => (
                        <option key={user.email} value={user.email}>
                          {user.email} ({user.response_count} responses)
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Load responses when tab becomes active */}
              {!responsesData && !loading && (
                <div className="text-center py-8">
                  <button
                    onClick={() => loadResponses(1, responseSearch, userFilter)}
                    className="bg-primary text-white px-4 py-2 rounded hover:bg-primary-dark"
                  >
                    Load Responses
                  </button>
                </div>
              )}

              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <SparkleLoader />
                </div>
              ) : responsesData && responsesData.responses ? (
                <>
                  <div className="bg-white rounded-lg shadow overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            ID
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            User
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Response
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Words
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Date
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {responsesData.responses.map((response) => (
                          <tr key={response.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {response.id}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {response.user_email}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900 max-w-md">
                              <div className="truncate">{response.response_text}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {response.word_count}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {new Date(response.created_at).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <button
                                onClick={() => deleteResponse(response.id)}
                                className="text-red-600 hover:text-red-900"
                              >
                                Delete
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {renderPagination(responsePage, responsesData.total, setResponsePage)}
                </>
              ) : responsesData && responsesData.responses?.length === 0 ? (
                <div className="text-center py-8 text-gray-500">No responses found</div>
              ) : null}
            </div>
          )}

          {/* Duplicates Tab */}
          {activeTab === 'duplicates' && (
            <div>
              {!duplicatesLoaded && !loading && (
                <div className="text-center py-8">
                  <button
                    onClick={loadDuplicates}
                    className="bg-primary text-white px-4 py-2 rounded hover:bg-primary-dark"
                  >
                    Load Duplicates
                  </button>
                </div>
              )}

              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <SparkleLoader />
                </div>
              ) : duplicatesLoaded && (
                <div>
                  <p className="text-gray-600 mb-4">Found {duplicates.length} groups of potential duplicate questions.</p>

                  <div className="space-y-6">
                    {duplicates.map((group, groupIndex) => (
                      <div key={groupIndex} className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">
                          Duplicate Group {groupIndex + 1}
                        </h3>
                        <div className="space-y-3">
                          {group.map((question, index) => (
                            <div key={question.id} className="border rounded p-3 bg-gray-50">
                              <div className="flex justify-between items-start">
                                <div>
                                  <div className="text-sm text-gray-600">ID: {question.id}</div>
                                  <div className="text-gray-900">{question.question_text}</div>
                                  <div className="text-sm text-gray-600">Category: {question.category}</div>
                                </div>
                                <button
                                  onClick={() => deleteQuestion(question.id)}
                                  className="text-red-600 hover:text-red-900 text-sm"
                                >
                                  Delete
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Edit Question Modal */}
          {editingQuestion && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4">
                <h3 className="text-lg font-semibold mb-4">Edit Question</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Question Text
                    </label>
                    <textarea
                      value={editingQuestion.question_text}
                      onChange={(e) => setEditingQuestion({
                        ...editingQuestion,
                        question_text: e.target.value
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      rows={3}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category
                    </label>
                    <select
                      value={editingQuestion.category}
                      onChange={(e) => setEditingQuestion({
                        ...editingQuestion,
                        category: e.target.value
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="personal_history">Personal History</option>
                      <option value="relationships">Relationships</option>
                      <option value="goals_aspirations">Goals & Aspirations</option>
                      <option value="values_beliefs">Values & Beliefs</option>
                      <option value="experiences_memories">Experiences & Memories</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    onClick={() => setEditingQuestion(null)}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => updateQuestion(editingQuestion.id, {
                      question_text: editingQuestion.question_text,
                      category: editingQuestion.category
                    })}
                    className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default DatabaseAdmin;