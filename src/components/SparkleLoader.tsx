import React from 'react'
import { Sparkles } from 'lucide-react'

interface SparkleLoaderProps {
  className?: string
  size?: 'small' | 'medium' | 'large'
}

export default function SparkleLoader({ className = '', size = 'medium' }: SparkleLoaderProps) {
  const sizeClasses = {
    small: 'w-6 h-6',
    medium: 'w-20 h-20',
    large: 'w-32 h-32'
  }

  const sparkleSize = {
    small: 'w-3 h-3',
    medium: 'w-6 h-6',
    large: 'w-8 h-8'
  }

  return (
    <div className={`pulse-container ${sizeClasses[size]} ${className}`}>
      {/* Central sparkle */}
      <Sparkles className={`text-primary central-sparkle ${sparkleSize[size]}`} />

      {/* Concentric pulse rings */}
      <div className="pulse-ring pulse-ring-1"></div>
      <div className="pulse-ring pulse-ring-2"></div>
      <div className="pulse-ring pulse-ring-3"></div>
    </div>
  )
}// Force deployment trigger Tue Sep 23 14:06:08 EDT 2025
