import React from 'react';
import { GoogleLogin, type CredentialResponse } from '@react-oauth/google';

interface GoogleAuthProps {
  onSuccess: (credentialResponse: CredentialResponse) => void;
  onError: () => void;
}

const GoogleAuth: React.FC<GoogleAuthProps> = ({ onSuccess, onError }) => {
  return (
    <div className="w-full">
      <GoogleLogin
        onSuccess={onSuccess}
        onError={onError}
        useOneTap={false}
        theme="outline"
        size="large"
        width="100%"
        text="signin_with"
        shape="rectangular"
      />
    </div>
  );
};

export default GoogleAuth;