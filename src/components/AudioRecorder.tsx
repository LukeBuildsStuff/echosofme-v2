import React, { useState, useRef, useCallback } from 'react';
import { Button } from './ui/button';

interface AudioRecorderProps {
  onRecordingComplete: (audioBlob: Blob) => void;
  onRecordingStart?: () => void;
  onRecordingStop?: () => void;
  maxDuration?: number; // in seconds
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onRecordingComplete,
  onRecordingStart,
  onRecordingStop,
  maxDuration = 300 // 5 minutes default
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioURL, setAudioURL] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' });
        const url = URL.createObjectURL(audioBlob);
        setAudioURL(url);
        onRecordingComplete(audioBlob);
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          const newTime = prev + 1;
          if (newTime >= maxDuration) {
            stopRecording();
          }
          return newTime;
        });
      }, 1000);

      onRecordingStart?.();
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Unable to access microphone. Please check permissions and try again.');
    }
  }, [maxDuration, onRecordingComplete, onRecordingStart]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      
      onRecordingStop?.();
    }
  }, [isRecording, onRecordingStop]);

  const playRecording = useCallback(() => {
    if (audioURL && audioPlayerRef.current) {
      setIsPlaying(true);
      audioPlayerRef.current.play();
    }
  }, [audioURL]);

  const pauseRecording = useCallback(() => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      setIsPlaying(false);
    }
  }, []);

  const resetRecording = useCallback(() => {
    if (audioURL) {
      URL.revokeObjectURL(audioURL);
      setAudioURL(null);
    }
    setRecordingTime(0);
    setIsPlaying(false);
    chunksRef.current = [];
  }, [audioURL]);

  const formatTime = useCallback((seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, []);

  const formatMaxTime = useCallback((seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, []);

  return (
    <div className="space-y-4">
      {/* Recording Status */}
      <div className="text-center">
        {isRecording && (
          <div className="flex items-center justify-center space-x-2 text-red-600">
            <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse"></div>
            <span className="font-medium">Recording...</span>
          </div>
        )}
        
        <div className="text-2xl font-mono mt-2">
          {formatTime(recordingTime)} / {formatMaxTime(maxDuration)}
        </div>
        
        {recordingTime > 60 && (
          <p className="text-sm text-green-600 mt-1">
            Great! You have enough audio for voice cloning.
          </p>
        )}
      </div>

      {/* Recording Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-1000"
          style={{ width: `${(recordingTime / maxDuration) * 100}%` }}
        ></div>
      </div>

      {/* Control Buttons */}
      <div className="flex justify-center space-x-4">
        {!isRecording && !audioURL && (
          <Button
            onClick={startRecording}
            className="bg-red-600 hover:bg-red-700 text-white px-8 py-3"
          >
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
            </svg>
            Start Recording
          </Button>
        )}

        {isRecording && (
          <Button
            onClick={stopRecording}
            className="bg-gray-600 hover:bg-gray-700 text-white px-8 py-3"
          >
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
            </svg>
            Stop Recording
          </Button>
        )}

        {audioURL && (
          <>
            <Button
              onClick={isPlaying ? pauseRecording : playRecording}
              variant="outline"
              className="px-6 py-3"
            >
              {isPlaying ? (
                <>
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  Pause
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                  </svg>
                  Play Preview
                </>
              )}
            </Button>
            
            <Button
              onClick={resetRecording}
              variant="outline"
              className="px-6 py-3 text-red-600 border-red-600 hover:bg-red-50"
            >
              Record Again
            </Button>
          </>
        )}
      </div>

      {/* Hidden audio player for playback */}
      {audioURL && (
        <audio
          ref={audioPlayerRef}
          src={audioURL}
          onEnded={() => setIsPlaying(false)}
          className="hidden"
        />
      )}

      {/* Recording Guidelines */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">Recording Tips:</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Speak naturally and clearly</li>
          <li>• Record in a quiet environment</li>
          <li>• Minimum 1 minute recommended for good quality</li>
          <li>• 2-5 minutes ideal for best results</li>
          <li>• Try reading a paragraph or talking about yourself</li>
        </ul>
      </div>
    </div>
  );
};

export default AudioRecorder;