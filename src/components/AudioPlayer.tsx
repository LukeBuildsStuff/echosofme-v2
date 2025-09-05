import React, { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Play, Pause, Volume2, VolumeX } from 'lucide-react';

interface AudioPlayerProps {
  audioUrl: string;
  onComplete?: () => void;
  className?: string;
  compact?: boolean;
}

export default function AudioPlayer({ 
  audioUrl, 
  onComplete, 
  className = '',
  compact = false 
}: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const audio = new Audio(audioUrl);
    audioRef.current = audio;
    
    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
      setIsLoading(false);
    };
    
    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };
    
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
      onComplete?.();
    };
    
    const handleError = () => {
      setError('Failed to load audio');
      setIsLoading(false);
    };

    const handleCanPlayThrough = () => {
      setIsLoading(false);
    };

    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);
    audio.addEventListener('canplaythrough', handleCanPlayThrough);
    
    audio.volume = volume;
    audio.muted = isMuted;
    
    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
      audio.removeEventListener('canplaythrough', handleCanPlayThrough);
      audio.pause();
      audio.src = '';
    };
  }, [audioUrl, volume, isMuted, onComplete]);

  const togglePlayPause = async () => {
    if (!audioRef.current || error) return;
    
    try {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        await audioRef.current.play();
        setIsPlaying(true);
      }
    } catch (err) {
      console.error('Audio playback failed:', err);
      setError('Playback failed');
    }
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!audioRef.current || !progressRef.current) return;
    
    const rect = progressRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const newTime = percentage * duration;
    
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
    }
  };

  const formatTime = (seconds: number): string => {
    if (!isFinite(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (error) {
    return (
      <div className={`flex items-center text-red-500 text-sm ${className}`}>
        <VolumeX className="w-4 h-4 mr-2" />
        <span>Audio unavailable</span>
      </div>
    );
  }

  if (compact) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <Button
          onClick={togglePlayPause}
          disabled={isLoading}
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0 hover:bg-gray-100"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
          ) : isPlaying ? (
            <Pause className="w-4 h-4" />
          ) : (
            <Play className="w-4 h-4" />
          )}
        </Button>
        
        <div className="flex-1 min-w-0">
          <div 
            ref={progressRef}
            onClick={handleProgressClick}
            className="h-1 bg-gray-200 rounded-full cursor-pointer group"
          >
            <div 
              className="h-full bg-blue-500 rounded-full transition-all duration-150 group-hover:bg-blue-600"
              style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
            />
          </div>
        </div>
        
        <span className="text-xs text-gray-500 tabular-nums min-w-0">
          {formatTime(currentTime)}
        </span>
      </div>
    );
  }

  return (
    <div className={`bg-white border rounded-lg p-4 shadow-sm ${className}`}>
      <div className="flex items-center space-x-4">
        <Button
          onClick={togglePlayPause}
          disabled={isLoading}
          variant="ghost"
          size="sm"
          className="h-10 w-10 p-0 hover:bg-gray-100"
        >
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
          ) : isPlaying ? (
            <Pause className="w-5 h-5" />
          ) : (
            <Play className="w-5 h-5" />
          )}
        </Button>
        
        <div className="flex-1 space-y-2">
          <div 
            ref={progressRef}
            onClick={handleProgressClick}
            className="h-2 bg-gray-200 rounded-full cursor-pointer group"
          >
            <div 
              className="h-full bg-blue-500 rounded-full transition-all duration-150 group-hover:bg-blue-600"
              style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
            />
          </div>
          
          <div className="flex justify-between text-sm text-gray-500 tabular-nums">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>
        
        <Button
          onClick={toggleMute}
          variant="ghost"
          size="sm"
          className="h-10 w-10 p-0 hover:bg-gray-100"
        >
          {isMuted ? (
            <VolumeX className="w-4 h-4" />
          ) : (
            <Volume2 className="w-4 h-4" />
          )}
        </Button>
      </div>
    </div>
  );
}