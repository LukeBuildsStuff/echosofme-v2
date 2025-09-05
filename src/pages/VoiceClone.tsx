import React from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout/Layout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';

const VoiceClone: React.FC = () => {
  const navigate = useNavigate();
  // Voice cloning coming soon page

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50 pt-20">
        <div className="max-w-4xl mx-auto py-12 px-4">
          <div className="max-w-2xl mx-auto text-center space-y-8">
            {/* Coming Soon Header */}
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-12 rounded-2xl text-white">
              <div className="w-20 h-20 mx-auto mb-6 bg-white/20 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                </svg>
              </div>
              <h1 className="text-4xl font-bold mb-4">Voice Cloning</h1>
              <div className="inline-block bg-white/20 backdrop-blur-sm px-6 py-2 rounded-full">
                <span className="text-xl font-semibold">Coming Soon</span>
              </div>
            </div>

            {/* What to Expect */}
            <Card className="text-left">
              <CardHeader>
                <CardTitle className="text-xl">What's Coming</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold text-sm mt-0.5">1</div>
                  <div>
                    <h3 className="font-medium text-gray-900">Record Your Voice</h3>
                    <p className="text-gray-600 text-sm">Upload a few minutes of your speech to create a personalized voice model</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold text-sm mt-0.5">2</div>
                  <div>
                    <h3 className="font-medium text-gray-900">AI Processing</h3>
                    <p className="text-gray-600 text-sm">Advanced AI analyzes your unique voice patterns and characteristics</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold text-sm mt-0.5">3</div>
                  <div>
                    <h3 className="font-medium text-gray-900">Your Digital Voice</h3>
                    <p className="text-gray-600 text-sm">Eleanor and your Echo memories can speak in your own voice</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Current Status */}
            <Card>
              <CardContent className="pt-6">
                <div className="text-center space-y-4">
                  <div className="w-16 h-16 bg-yellow-100 text-yellow-600 rounded-full flex items-center justify-center mx-auto">
                    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold">Feature In Development</h3>
                  <p className="text-gray-600">
                    We're working hard to bring you personalized voice cloning. In the meantime, you can enjoy chatting with Eleanor using our built-in voices!
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="flex justify-center space-x-4">
              <Button
                onClick={() => navigate('/eleanor-chat')}
                className="bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 px-8"
              >
                Try Eleanor Chat
              </Button>
              <Button
                onClick={() => navigate('/dashboard')}
                variant="outline"
                className="px-8"
              >
                Back to Dashboard
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default VoiceClone;