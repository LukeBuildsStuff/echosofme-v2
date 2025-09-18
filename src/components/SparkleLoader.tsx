import React from 'react'
import { Sparkles } from 'lucide-react'

interface SparkleLoaderProps {
  className?: string
}

export default function SparkleLoader({ className = '' }: SparkleLoaderProps) {
  return (
    <div className={`pulse-container ${className}`}>
      {/* Central sparkle */}
      <Sparkles className="text-primary central-sparkle" />

      {/* Concentric pulse rings */}
      <div className="pulse-ring pulse-ring-1"></div>
      <div className="pulse-ring pulse-ring-2"></div>
      <div className="pulse-ring pulse-ring-3"></div>
    </div>
  )
}