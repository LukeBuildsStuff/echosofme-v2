import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout/Layout';
import { useAuth } from '../contexts/SupabaseAuthContext';

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

  const handleGoogleLogin = async () => {
    try {
      setError('');
      setLoading(true);

      console.log('🔍 Starting Google OAuth login');

      await loginWithGoogle();
      // Supabase will handle the redirect after successful authentication
    } catch (error) {
      console.error('Google login failed:', error);
      setError('Google login failed. Please try again.');
      setLoading(false);
    }
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
                      <button
                        type="button"
                        onClick={handleGoogleLogin}
                        disabled={loading}
                        className="w-full inline-flex justify-center items-center py-2.5 px-4 text-sm font-medium text-dark dark:text-white focus:outline-none bg-white dark:bg-dark-2 rounded-lg border border-stroke dark:border-dark-3 hover:bg-gray-50 dark:hover:bg-dark hover:border-primary dark:hover:border-primary focus:ring-4 focus:ring-primary/20 transition-colors duration-200"
                      >
                        <svg className="w-4 h-4 me-2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        Sign in with Google
                      </button>
                    </div>
                  </div>
                </form>


                <div className="mb-4">
                  {!formData.isSignUp && (
                    <Link
                      to="/reset-password"
                      className="inline-block mb-2 text-base text-primary hover:text-primary/80 dark:text-primary dark:hover:text-primary/80 transition-colors duration-200"
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