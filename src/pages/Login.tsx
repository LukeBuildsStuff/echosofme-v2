import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout/Layout';
import { useAuth } from '../contexts/AuthContext';

const Login: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    isSignUp: false,
    displayName: '',
  });
  
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Create user object
    const user = {
      id: Date.now().toString(),
      email: formData.email,
      displayName: formData.isSignUp ? formData.displayName : formData.email.split('@')[0],
      profile: {
        displayName: formData.isSignUp ? formData.displayName : formData.email.split('@')[0],
        relationship: 'Friendly',
        meetingStatus: 'First time meeting',
        purpose: 'Personal growth and reflection',
        knowledgeLevel: 'Learning together',
        introduction: '',
      }
    };

    // Use AuthContext login method
    try {
      login(user);
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed. Please try again.');
    }
  };

  const toggleMode = () => {
    setFormData({
      ...formData,
      isSignUp: !formData.isSignUp,
      displayName: '',
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
                  
                  <div className="mb-9">
                    <button
                      type="submit"
                      className="w-full px-5 py-3 text-base text-white transition duration-300 ease-in-out border rounded-md cursor-pointer border-primary bg-primary hover:bg-primary/90"
                    >
                      {formData.isSignUp ? 'Create Account' : 'Sign In'}
                    </button>
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