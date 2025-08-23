import React from 'react';
import { useEcho } from '../contexts/EchoContext';

interface TrainingProgressProps {
  showMilestones?: boolean;
  compact?: boolean;
}

const TrainingProgress: React.FC<TrainingProgressProps> = ({ 
  showMilestones = true, 
  compact = false 
}) => {
  const { stats, getCompletionPercentage, getNextMilestone, personality } = useEcho();
  
  const completionPercentage = getCompletionPercentage();
  const nextMilestone = getNextMilestone();
  const isComplete = completionPercentage >= 100;

  const getProgressColor = (percentage: number): string => {
    if (percentage >= 100) return 'bg-emerald-500';
    if (percentage >= 80) return 'bg-blue-500';
    if (percentage >= 60) return 'bg-indigo-500';
    if (percentage >= 40) return 'bg-purple-500';
    if (percentage >= 20) return 'bg-pink-500';
    return 'bg-gray-400';
  };

  const getReadinessStatus = (): { label: string; color: string; description: string } => {
    if (isComplete) {
      return {
        label: 'Echo Complete',
        color: 'text-emerald-600',
        description: 'Your digital legacy is ready to share!'
      };
    }
    if (completionPercentage >= 80) {
      return {
        label: 'Nearly Ready',
        color: 'text-blue-600',
        description: 'Your Echo is almost complete and very knowledgeable about you.'
      };
    }
    if (completionPercentage >= 60) {
      return {
        label: 'Advanced Training',
        color: 'text-indigo-600',
        description: 'Your Echo has a strong understanding of your perspectives.'
      };
    }
    if (completionPercentage >= 40) {
      return {
        label: 'Good Progress',
        color: 'text-purple-600',
        description: 'Your Echo is learning your communication style and values.'
      };
    }
    if (completionPercentage >= 20) {
      return {
        label: 'Getting Started',
        color: 'text-pink-600',
        description: 'Your Echo is beginning to understand your voice.'
      };
    }
    return {
      label: 'Early Training',
      color: 'text-gray-600',
      description: 'Your Echo is just beginning to learn from your reflections.'
    };
  };

  const status = getReadinessStatus();

  if (compact) {
    return (
      <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200 hover:shadow-lg transition-shadow duration-200 cursor-pointer">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Echo Training</span>
          <span className={`text-sm font-semibold ${status.color}`}>
            {Math.round(completionPercentage)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(completionPercentage)}`}
            style={{ width: `${completionPercentage}%` }}
          ></div>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {stats.totalReflections} / 2500 reflections
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg p-6 shadow-lg border border-gray-200 hover:shadow-xl transition-shadow duration-300">
      {/* Header */}
      <div className="text-center mb-6">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          {personality.name}
        </h3>
        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${status.color} bg-opacity-10`}>
          <div className={`w-2 h-2 rounded-full mr-2 ${getProgressColor(completionPercentage)}`}></div>
          {status.label}
        </div>
        <p className="text-gray-600 mt-2">{status.description}</p>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Training Progress</span>
          <span className="text-2xl font-bold text-primary">
            {Math.round(completionPercentage)}%
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${getProgressColor(completionPercentage)}`}
            style={{ width: `${completionPercentage}%` }}
          >
            <div className="h-full bg-gradient-to-r from-transparent to-white/20"></div>
          </div>
        </div>
        
        <div className="flex justify-between text-sm text-gray-500 mt-2">
          <span>{stats.totalReflections} reflections</span>
          <span>Target: 2,500</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200 cursor-pointer">
          <div className="text-xl font-bold text-gray-900">{stats.categoriesCovered.length}</div>
          <div className="text-sm text-gray-600">Categories Explored</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200 cursor-pointer">
          <div className="text-xl font-bold text-gray-900">{stats.currentStreak}</div>
          <div className="text-sm text-gray-600">Day Streak</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200 cursor-pointer">
          <div className="text-xl font-bold text-gray-900">{Math.round(stats.averageWordCount)}</div>
          <div className="text-sm text-gray-600">Avg Words</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200 cursor-pointer">
          <div className="text-xl font-bold text-gray-900">{Math.round(stats.averageQualityScore * 100)}%</div>
          <div className="text-sm text-gray-600">Quality Score</div>
        </div>
      </div>

      {/* Next Milestone */}
      {showMilestones && nextMilestone && (
        <div className="bg-gradient-to-r from-primary/10 to-secondary/10 rounded-lg p-4 hover:from-primary/15 hover:to-secondary/15 transition-all duration-200 cursor-pointer">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Next Milestone</span>
            <span className="text-sm text-primary font-semibold">
              {nextMilestone.target - stats.totalReflections} reflections to go
            </span>
          </div>
          <div className="text-sm text-gray-600 mb-2">{nextMilestone.description}</div>
          
          {/* Milestone Progress */}
          <div className="w-full bg-white/60 rounded-full h-2">
            <div
              className="h-2 bg-primary rounded-full transition-all duration-500"
              style={{ width: `${Math.min((stats.totalReflections / nextMilestone.target) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Personality Traits */}
      {personality.dominantTraits.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Emerging Traits</h4>
          <div className="flex flex-wrap gap-2">
            {personality.dominantTraits.map((trait, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary hover:bg-primary/20 transition-colors duration-200 cursor-pointer"
              >
                {trait}
              </span>
            ))}
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Communication Style: {personality.communicationStyle}
          </p>
        </div>
      )}
    </div>
  );
};

export default TrainingProgress;