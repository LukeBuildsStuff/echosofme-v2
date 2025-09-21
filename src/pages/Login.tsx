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
                        className="w-full inline-flex justify-center items-center py-2.5 px-4 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
                      >
                        <svg className="w-4 h-4 me-2" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 18 19">
                          <path fillRule="evenodd" d="M8.842 18.083a8.8 8.8 0 0 1-8.65-8.948 8.841 8.841 0 0 1 8.8-8.652h.153a8.464 8.464 0 0 1 5.7 2.257l-2.193 2.038A5.27 5.27 0 0 0 9.09 3.4a5.882 5.882 0 0 0-.2 11.76h.124a5.091 5.091 0 0 0 5.248-4.057L14.3 11H9V8h8.34c.066.543.095 1.09.088 1.636-.086 5.053-3.463 8.449-8.4 8.449l-.186-.002Z" clipRule="evenodd"/>
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