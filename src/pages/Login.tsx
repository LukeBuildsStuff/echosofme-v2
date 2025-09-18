import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import type { CredentialResponse } from '@react-oauth/google';
import Layout from '../components/Layout/Layout';
import { useAuth } from '../contexts/SupabaseAuthContext';
import GoogleAuth from '../components/GoogleAuth';

const Login: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    isSignUp: false,
    displayName: '',
    rememberMe: false,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  const { login, signup, loginWithGoogle } = useAuth();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    try {
      setError('');
      setLoading(true);
      
      // Decode the JWT token to get user information
      if (credentialResponse.credential) {
        const payload = JSON.parse(atob(credentialResponse.credential.split('.')[1]));
        
        const { email, name, sub: googleId } = payload;
        
        console.log('🔍 Google login successful for:', email);
        
        await loginWithGoogle(email, name, googleId);
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Google login failed:', error);
      setError('Google login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleError = () => {
    console.error('Google login error');
    setError('Google login failed. Please check your internet connection and try again.');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setError('');
    setLoading(true);

    try {
      const normalizedEmail = formData.email.toLowerCase().trim();

      if (formData.isSignUp) {
        // New user signup
        await signup(normalizedEmail, formData.password, formData.displayName);
      } else {
        // Existing user login
        await login(normalizedEmail, formData.password);
      }

      navigate('/dashboard');
    } catch (error) {
      console.error('Authentication failed:', error);
      setError('Login failed. Please check your information and try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setFormData({
      ...formData,
      isSignUp: !formData.isSignUp,
      displayName: '',
    });
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.checked,
    });
  };

  return (
    <Layout>
      {/* Banner Section */}
      <div className="relative z-10 pt-[120px] pb-[110px] bg-primary">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap -mx-4">
            <div className="w-full px-4">
              <div className="mx-auto max-w-[400px] text-center">
                <h2 className="mb-5 text-3xl font-bold leading-tight text-white sm:text-4xl sm:leading-tight md:text-5xl md:leading-tight">
                  {formData.isSignUp ? 'Join Echos of Me' : 'Welcome Back'}
                </h2>
                <p className="mb-5 text-base text-white/80">
                  {formData.isSignUp 
                    ? 'Start your journey of self-reflection and create your AI companion.'
                    : 'Continue your journey with Eleanor and explore your memories.'
                  }
                </p>

                <ul className="flex items-center justify-center gap-[10px]">
                  <li>
                    <Link
                      to="/"
                      className="flex items-center gap-[10px] text-base font-medium text-white hover:text-white/70"
                    >
                      Home
                    </Link>
                  </li>
                  <li>
                    <span className="flex items-center gap-[10px] text-base font-medium text-white/60">
                      <span> / </span>
                      {formData.isSignUp ? 'Sign Up' : 'Sign In'}
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Forms Section */}
      <section className="bg-[#F4F7FF] py-14 lg:py-20 dark:bg-dark">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap -mx-4">
            <div className="w-full px-4">
              <div className="relative mx-auto max-w-[525px] overflow-hidden rounded-lg bg-white dark:bg-dark-2 py-14 px-8 text-center sm:px-12 md:px-[60px]">
                <div className="mb-10 text-center">
                  <Link
                    to="/"
                    className="mx-auto inline-block max-w-[160px]"
                  >
                    <span className="text-2xl font-bold text-primary">
                      Echos of Me
                    </span>
                  </Link>
                </div>
                
                <form onSubmit={handleSubmit}>
                  {error && (
                    <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                      {error}
                    </div>
                  )}
                  
                  {formData.isSignUp && (
                    <div className="mb-[22px]">
                      <input
                        type="text"
                        name="displayName"
                        placeholder="Your Name"
                        value={formData.displayName}
                        onChange={handleChange}
                        required={formData.isSignUp}
                        className="w-full px-5 py-3 text-base transition bg-transparent border rounded-md outline-none border-stroke dark:border-dark-3 text-body-color dark:text-dark-6 placeholder:text-dark-6 focus:border-primary dark:focus:border-primary focus-visible:shadow-none"
                      />
                    </div>
                  )}
                  
                  <div className="mb-[22px]">
                    <input
                      type="email"
                      name="email"
                      placeholder="Email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="w-full px-5 py-3 text-base transition bg-transparent border rounded-md outline-none border-stroke dark:border-dark-3 text-body-color dark:text-dark-6 placeholder:text-dark-6 focus:border-primary dark:focus:border-primary focus-visible:shadow-none"
                    />
                  </div>
                  
                  <div className="mb-[22px]">
                    <input
                      type="password"
                      name="password"
                      placeholder="Password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      className="w-full px-5 py-3 text-base transition bg-transparent border rounded-md outline-none border-stroke dark:border-dark-3 text-body-color dark:text-dark-6 placeholder:text-dark-6 focus:border-primary dark:focus:border-primary focus-visible:shadow-none"
                    />
                  </div>

                  {!formData.isSignUp && (
                    <div className="mb-[22px] flex items-center">
                      <input
                        type="checkbox"
                        name="rememberMe"
                        id="rememberMe"
                        checked={formData.rememberMe}
                        onChange={handleCheckboxChange}
                        className="mr-2 h-4 w-4 text-primary border-gray-300 rounded focus:ring-primary"
                      />
                      <label 
                        htmlFor="rememberMe"
                        className="text-sm text-body-color dark:text-dark-6"
                      >
                        Remember me for 30 days
                      </label>
                    </div>
                  )}
                  
                  <div className="mb-6">
                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full px-5 py-3 text-base text-white transition duration-300 ease-in-out border rounded-md cursor-pointer border-primary bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? (
                        <div className="flex items-center justify-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          {formData.isSignUp ? 'Creating Account...' : 'Signing In...'}
                        </div>
                      ) : (
                        formData.isSignUp ? 'Create Account' : 'Sign In'
                      )}
                    </button>
                  </div>

                  <div className="mb-6">
                    <div className="flex items-center justify-center mb-4">
                      <div className="border-t border-gray-300 flex-1"></div>
                      <span className="px-3 text-sm text-gray-500">or</span>
                      <div className="border-t border-gray-300 flex-1"></div>
                    </div>
                    
                    <div className="flex justify-center">
                      <GoogleAuth
                        onSuccess={handleGoogleSuccess}
                        onError={handleGoogleError}
                      />
                    </div>
                  </div>
                </form>


                <div className="mb-4">
                  {!formData.isSignUp && (
                    <Link
                      to="/reset-password"
                      className="inline-block mb-2 text-base text-dark dark:text-white hover:text-primary dark:hover:text-primary"
                    >
                      Forgot Password?
                    </Link>
                  )}
                </div>
                
                <p className="text-base text-body-secondary">
                  {formData.isSignUp ? 'Already have an account?' : "Don't have an account?"}
                  <button
                    onClick={toggleMode}
                    className="text-primary hover:underline ml-1"
                  >
                    {formData.isSignUp ? 'Sign In' : 'Sign Up'}
                  </button>
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Login;