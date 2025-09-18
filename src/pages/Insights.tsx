import React, { useState, useEffect, useRef } from 'react';
import Layout from '../components/Layout/Layout';
import { useAuth } from '../contexts/SupabaseAuthContext';
import { getEleanorApiUrl, isEleanorEnabled } from '../utils/apiConfig';

interface InsightsData {
  total_reflections: number;
  insights: {
    message?: string;
    personal_summary?: string;
    core_values?: Array<{
      value: string;
      strength: number;
      description: string;
    }>;
    reflection_dna?: Array<string>;
    streak_calendar?: {
      current_streak: number;
      longest_streak: number;
      total_active_days: number;
      calendar_data: Array<{
        date: string;
        count: number;
        intensity: number;
      }>;
    };
    growth_journey?: {
      reflection_depth_change: string;
      focus_evolution: string;
      emotional_growth: string;
    };
    reflection_style?: {
      avg_word_count: number;
      depth_level: string;
      consistency: string;
    };
  };
}

const Insights: React.FC = () => {
  const { user } = useAuth();
  const [insights, setInsights] = useState<InsightsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const calendarRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (user?.email) {
      loadInsights();
    }
  }, [user?.email]);

  // Auto-scroll calendar to the end (most recent dates) when calendar data loads
  useEffect(() => {
    if (insights?.insights?.streak_calendar?.calendar_data && calendarRef.current) {
      // Small delay to ensure the DOM is fully rendered
      setTimeout(() => {
        if (calendarRef.current) {
          calendarRef.current.scrollLeft = calendarRef.current.scrollWidth;
        }
      }, 100);
    }
  }, [insights?.insights?.streak_calendar?.calendar_data]);

  const loadInsights = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check if Eleanor API is enabled
      if (!isEleanorEnabled()) {
        setError('Eleanor AI insights are not available in this environment. Insights require the Eleanor AI service to be running.');
        return;
      }

      const apiUrl = getEleanorApiUrl();
      const response = await fetch(`${apiUrl}/insights/${user?.email}`);

      if (response.ok) {
        const data = await response.json();
        setInsights(data);
      } else {
        // Try to parse error response as JSON, fallback to text
        let errorMessage = `Failed to load insights: ${response.statusText}`;
        try {
          const contentType = response.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
          } else {
            const errorText = await response.text();
            if (errorText && errorText.length < 200) {
              errorMessage = errorText;
            }
          }
        } catch (parseError) {
          console.error('Error parsing error response:', parseError);
        }
        throw new Error(errorMessage);
      }
    } catch (err) {
      console.error('Error loading insights:', err);
      if (err instanceof Error && err.message.includes('Eleanor API is disabled')) {
        setError('Eleanor AI insights are not available in this environment. Insights require the Eleanor AI service to be running.');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to load insights');
      }
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'philosophy_values': 'bg-blue-100 text-blue-800',
      'family_parenting': 'bg-green-100 text-green-800',
      'career': 'bg-purple-100 text-purple-800',
      'personal_history': 'bg-yellow-100 text-yellow-800',
      'hobbies': 'bg-orange-100 text-orange-800',
      'friendships_social': 'bg-pink-100 text-pink-800',
      'education': 'bg-indigo-100 text-indigo-800',
      'daily_life': 'bg-cyan-100 text-cyan-800',
      'romantic_love': 'bg-red-100 text-red-800',
      'life_milestones': 'bg-emerald-100 text-emerald-800',
      'marriage_partnerships': 'bg-teal-100 text-teal-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  const formatCategoryName = (category: string) => {
    return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getGrowthTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving': return 'text-green-600';
      case 'stable': return 'text-blue-600';
      default: return 'text-orange-600';
    }
  };

  const getGrowthTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return (
          <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        );
      case 'stable':
        return (
          <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5 12a1 1 0 102 0V6.414l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L5 6.414V12zM15 8a1 1 0 10-2 0v5.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L15 13.586V8z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  if (loading) {
    return (
      <Layout hideFooter={true}>
        <div className="min-h-screen bg-gray-50 pt-20">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-center min-h-96">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-gray-600">Analyzing your reflections...</p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    const isEleanorDisabled = error.includes('Eleanor AI insights are not available');

    return (
      <Layout hideFooter={true}>
        <div className="min-h-screen bg-gray-50 pt-20">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <div className={`border rounded-lg p-6 max-w-2xl mx-auto mt-20 ${
              isEleanorDisabled
                ? 'bg-blue-50 border-blue-200'
                : 'bg-red-50 border-red-200'
            }`}>
              <div className="flex">
                {isEleanorDisabled ? (
                  <svg className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                )}
                <div className="ml-3">
                  <h3 className={`text-sm font-medium ${
                    isEleanorDisabled ? 'text-blue-800' : 'text-red-800'
                  }`}>
                    {isEleanorDisabled ? 'AI Insights Not Available' : 'Error Loading Insights'}
                  </h3>
                  <p className={`text-sm mt-1 ${
                    isEleanorDisabled ? 'text-blue-700' : 'text-red-700'
                  }`}>
                    {error}
                  </p>
                  {isEleanorDisabled && (
                    <div className="mt-3 text-sm text-blue-700">
                      <p className="mb-2">While AI insights aren't available, you can still:</p>
                      <ul className="list-disc list-inside space-y-1">
                        <li>View and create reflections</li>
                        <li>Export your data for analysis</li>
                        <li>Browse your reflection history</li>
                      </ul>
                    </div>
                  )}
                  {!isEleanorDisabled && (
                    <button
                      onClick={loadInsights}
                      className="mt-3 text-sm bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded-md transition-colors"
                    >
                      Try Again
                    </button>
                  )}
                  <div className="mt-4 flex gap-3">
                    <a
                      href="/reflections"
                      className={`text-sm px-3 py-1 rounded-md transition-colors ${
                        isEleanorDisabled
                          ? 'bg-blue-100 hover:bg-blue-200 text-blue-800'
                          : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
                      }`}
                    >
                      View Reflections
                    </a>
                    <a
                      href="/dashboard"
                      className={`text-sm px-3 py-1 rounded-md transition-colors ${
                        isEleanorDisabled
                          ? 'bg-blue-100 hover:bg-blue-200 text-blue-800'
                          : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
                      }`}
                    >
                      Dashboard
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (!insights || insights.total_reflections === 0) {
    return (
      <Layout hideFooter={true}>
        <div className="min-h-screen bg-gray-50 pt-20">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <div className="text-center mt-20">
              <svg className="mx-auto h-24 w-24 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <h3 className="mt-6 text-lg font-medium text-gray-900">No Insights Yet</h3>
              <p className="mt-2 text-gray-500 max-w-md mx-auto">
                Start reflecting to see personalized insights about your thoughts, patterns, and growth over time.
              </p>
              <div className="mt-6">
                <a
                  href="/reflections"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary/90 transition-colors"
                >
                  Start Reflecting
                </a>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  const { personal_summary, core_values, reflection_dna, streak_calendar, growth_journey, reflection_style } = insights.insights;

  return (
    <Layout hideFooter={true}>
      <div className="min-h-screen bg-gray-50 pt-20">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="md:flex md:items-center md:justify-between mb-8">
            <div className="min-w-0 flex-1">
              <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
                Personal Insights
              </h2>
              <div className="mt-1 flex flex-col sm:mt-0 sm:flex-row sm:flex-wrap sm:space-x-6">
                <div className="mt-2 flex items-center text-sm text-gray-500">
                  <svg className="mr-1.5 h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Based on {insights.total_reflections} reflections
                </div>
              </div>
            </div>
          </div>

          {/* Personal Summary */}
          {personal_summary && (
            <div className="bg-white overflow-hidden shadow rounded-lg mb-8">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-start">
                  <svg className="w-8 h-8 text-primary mr-4 mt-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h3 className="text-lg leading-6 font-medium text-gray-900 mb-2">
                      Your Reflection Journey
                    </h3>
                    <p className="text-gray-700 text-base leading-relaxed">
                      {personal_summary}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Core Values */}
          {core_values && core_values.length > 0 && (
            <div className="bg-white overflow-hidden shadow rounded-lg mb-8">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-6">
                  Your Core Values
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {core_values.map((value, index) => {
                    const maxStrength = Math.max(...core_values.map(v => v.strength));
                    const strengthPercent = (value.strength / maxStrength) * 100;
                    const isTopValue = index < 3;

                    return (
                      <div key={value.value} className={`border-2 rounded-lg p-4 ${isTopValue ? 'border-primary bg-primary/5' : 'border-gray-200'}`}>
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="text-lg font-semibold text-gray-900">{value.value}</h4>
                          <span className={`text-sm font-medium px-2 py-1 rounded-full ${isTopValue ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600'}`}>
                            {value.strength}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                          <div
                            className={`h-2 rounded-full ${isTopValue ? 'bg-primary' : 'bg-gray-400'}`}
                            style={{ width: `${strengthPercent}%` }}
                          ></div>
                        </div>
                        <p className="text-sm text-gray-600">
                          {value.description}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Streak Calendar */}
          {streak_calendar && (
            <div className="bg-white overflow-hidden shadow rounded-lg mb-8">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-6">
                  Your Reflection Journey
                </h3>

                {/* Streak Stats */}
                <div className="flex flex-wrap gap-6 mb-6">
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">🔥</span>
                    <div>
                      <div className="text-sm text-gray-600">Current Streak</div>
                      <div className="text-2xl font-bold text-gray-900">{streak_calendar.current_streak}</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">🏆</span>
                    <div>
                      <div className="text-sm text-gray-600">Best Streak</div>
                      <div className="text-2xl font-bold text-gray-900">{streak_calendar.longest_streak}</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">📅</span>
                    <div>
                      <div className="text-sm text-gray-600">Active Days</div>
                      <div className="text-2xl font-bold text-gray-900">{streak_calendar.total_active_days}</div>
                    </div>
                  </div>
                </div>

                {/* Heatmap Calendar */}
                <div ref={calendarRef} className="overflow-x-auto">
                  <div className="min-w-max">
                    {/* Create weeks structure and track months */}
                    {(() => {
                      if (!streak_calendar.calendar_data.length) return null;

                      // Group days by week and track month positions
                      const weeks = [];
                      const monthPositions = [];
                      let currentWeek = [];
                      const startDate = new Date(streak_calendar.calendar_data[0].date);
                      const endDate = new Date(streak_calendar.calendar_data[streak_calendar.calendar_data.length - 1].date);

                      // Start from the first Sunday of the year containing the start date
                      const yearStart = new Date(startDate.getFullYear(), 0, 1);
                      const firstSunday = new Date(yearStart);
                      firstSunday.setDate(yearStart.getDate() - yearStart.getDay());

                      const currentDate = new Date(firstSunday);
                      let currentMonth = null;
                      let weekIndex = 0;

                      // Build calendar data by iterating through all days
                      while (currentDate <= endDate) {
                        const dateStr = currentDate.toISOString().slice(0, 10);
                        const dayData = streak_calendar.calendar_data.find(d => d.date === dateStr);
                        const isToday = dateStr === new Date().toISOString().slice(0, 10);

                        // Check if we've entered a new month
                        const monthKey = `${currentDate.getFullYear()}-${currentDate.getMonth()}`;
                        if (monthKey !== currentMonth && currentDate.getDate() <= 7) { // Only on first week of month
                          currentMonth = monthKey;
                          const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                          const monthName = monthNames[currentDate.getMonth()];
                          const yearSuffix = currentDate.getFullYear() !== new Date().getFullYear() ?
                            ` '${currentDate.getFullYear().toString().slice(-2)}` : '';

                          monthPositions.push({
                            name: `${monthName}${yearSuffix}`,
                            weekIndex: weekIndex,
                            isCurrentMonth: currentDate.getMonth() === new Date().getMonth() &&
                                          currentDate.getFullYear() === new Date().getFullYear()
                          });
                        }

                        // Color based on intensity
                        let colorClass = 'bg-gray-100';
                        if (dayData?.intensity === 1) colorClass = 'bg-green-200';
                        else if (dayData?.intensity === 2) colorClass = 'bg-green-300';
                        else if (dayData?.intensity === 3) colorClass = 'bg-green-400';
                        else if (dayData?.intensity >= 4) colorClass = 'bg-green-600';

                        currentWeek.push({
                          date: dateStr,
                          count: dayData?.count || 0,
                          colorClass,
                          isToday,
                          dayOfWeek: currentDate.getDay()
                        });

                        // If Saturday (end of week), push the week
                        if (currentDate.getDay() === 6) {
                          weeks.push([...currentWeek]);
                          currentWeek = [];
                          weekIndex++;
                        }

                        currentDate.setDate(currentDate.getDate() + 1);
                      }

                      // Add any remaining days to the last week
                      if (currentWeek.length > 0) {
                        weeks.push(currentWeek);
                      }

                      return (
                        <div>
                          <div className="flex gap-1">
                            {/* Weekday labels */}
                            <div className="flex flex-col gap-1 mr-2 text-xs text-gray-500">
                              <div className="h-3"></div> {/* spacer for alignment */}
                              <div className="h-3 flex items-center">Sun</div>
                              <div className="h-3"></div>
                              <div className="h-3 flex items-center">Tue</div>
                              <div className="h-3"></div>
                              <div className="h-3 flex items-center">Thu</div>
                              <div className="h-3"></div>
                            </div>

                            {/* Calendar grid */}
                            <div className="flex gap-1">
                              {weeks.map((week, weekIndex) => (
                                <div key={weekIndex} className="flex flex-col gap-1">
                                  {/* Ensure we have 7 slots for each week */}
                                  {[0, 1, 2, 3, 4, 5, 6].map(dayOfWeek => {
                                    const dayData = week.find(d => d.dayOfWeek === dayOfWeek);

                                    if (!dayData) {
                                      return <div key={dayOfWeek} className="w-3 h-3"></div>;
                                    }

                                    return (
                                      <div
                                        key={dayData.date}
                                        className={`w-3 h-3 rounded-sm ${dayData.colorClass} ${dayData.isToday ? 'ring-2 ring-primary' : ''}`}
                                        title={`${new Date(dayData.date).toLocaleDateString()}: ${dayData.count} reflection${dayData.count !== 1 ? 's' : ''}`}
                                      />
                                    );
                                  })}
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Month labels positioned under actual weeks */}
                          <div className="ml-12 mt-2 relative">
                            {monthPositions.map((month, index) => (
                              <div
                                key={index}
                                className={`absolute text-xs ${month.isCurrentMonth ? 'font-semibold text-gray-700' : 'text-gray-500'}`}
                                style={{
                                  left: `${month.weekIndex * 16}px`, // 12px width + 4px gap = 16px per week
                                  transform: 'translateX(-50%)'
                                }}
                              >
                                {month.name}
                              </div>
                            ))}
                          </div>

                          {/* Legend */}
                          <div className="flex items-center justify-between mt-8 text-xs text-gray-500">
                            <span>Less</span>
                            <div className="flex items-center gap-1">
                              <div className="w-3 h-3 bg-gray-100 rounded-sm"></div>
                              <div className="w-3 h-3 bg-green-200 rounded-sm"></div>
                              <div className="w-3 h-3 bg-green-300 rounded-sm"></div>
                              <div className="w-3 h-3 bg-green-400 rounded-sm"></div>
                              <div className="w-3 h-3 bg-green-600 rounded-sm"></div>
                            </div>
                            <span>More</span>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Reflection DNA - Your Unique Patterns */}
          {reflection_dna && reflection_dna.length > 0 && (
            <div className="bg-white overflow-hidden shadow rounded-lg mb-8">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-6">
                  Your Reflection DNA
                </h3>
                <p className="text-sm text-gray-600 mb-6">
                  The unique patterns that make up your inner world, discovered through your reflections.
                </p>
                <div className="grid grid-cols-1 gap-4">
                  {reflection_dna.map((insight, index) => (
                    <div
                      key={index}
                      className="border-l-4 border-primary bg-primary/5 p-4 rounded-r-lg hover:bg-primary/10 transition-colors"
                    >
                      <p className="text-gray-800 font-medium leading-relaxed">
                        {insight}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Growth Journey & Reflection Style */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Growth Journey */}
            {growth_journey && (
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-6">
                    Your Growth Journey
                  </h3>
                  <div className="space-y-4">
                    {growth_journey.reflection_depth_change && (
                      <div className="flex items-start">
                        <svg className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">Depth Evolution</h4>
                          <p className="text-sm text-gray-600 mt-1">{growth_journey.reflection_depth_change}</p>
                        </div>
                      </div>
                    )}

                    {growth_journey.focus_evolution && (
                      <div className="flex items-start">
                        <svg className="w-5 h-5 text-blue-600 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                        </svg>
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">Focus Shift</h4>
                          <p className="text-sm text-gray-600 mt-1">{growth_journey.focus_evolution}</p>
                        </div>
                      </div>
                    )}

                    {growth_journey.emotional_growth && (
                      <div className="flex items-start">
                        <svg className="w-5 h-5 text-purple-600 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                        </svg>
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">Emotional Growth</h4>
                          <p className="text-sm text-gray-600 mt-1">{growth_journey.emotional_growth}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Reflection Style */}
            {reflection_style && (
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-6">
                    Your Reflection Style
                  </h3>
                  <div className="space-y-4">
                    <div className="bg-gray-50 px-4 py-3 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">Average Length</span>
                        <span className="text-lg font-semibold text-gray-900">{reflection_style.avg_word_count} words</span>
                      </div>
                    </div>

                    <div className="bg-gray-50 px-4 py-3 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">Depth Level</span>
                        <span className={`text-sm font-medium px-2 py-1 rounded-full ${
                          reflection_style.depth_level.includes('deep') ? 'bg-blue-100 text-blue-800' :
                          reflection_style.depth_level.includes('moderate') ? 'bg-green-100 text-green-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {reflection_style.depth_level}
                        </span>
                      </div>
                    </div>

                    <div className="bg-gray-50 px-4 py-3 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">Consistency</span>
                        <span className={`text-sm font-medium px-2 py-1 rounded-full ${
                          reflection_style.consistency.includes('consistent') ? 'bg-green-100 text-green-800' :
                          reflection_style.consistency.includes('moderate') ? 'bg-yellow-100 text-yellow-800' :
                          'bg-orange-100 text-orange-800'
                        }`}>
                          {reflection_style.consistency}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Insights;