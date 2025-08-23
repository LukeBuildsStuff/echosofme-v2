import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout/Layout';

const ResetPassword: React.FC = () => {
  const [step, setStep] = useState<'email' | 'verify' | 'newPassword' | 'success'>('email');
  const [formData, setFormData] = useState({
    email: '',
    verificationCode: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<string[]>([]);
  const [generatedCode, setGeneratedCode] = useState('');
  const navigate = useNavigate();

  const validateEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const validatePassword = (password: string) => {
    const errors: string[] = [];
    if (password.length < 8) errors.push('At least 8 characters');
    if (!/[A-Z]/.test(password)) errors.push('One uppercase letter');
    if (!/[a-z]/.test(password)) errors.push('One lowercase letter');
    if (!/[0-9]/.test(password)) errors.push('One number');
    return errors;
  };

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateEmail(formData.email)) {
      setErrors(['Please enter a valid email address']);
      return;
    }

    // Simulate sending email with verification code
    const code = Math.floor(100000 + Math.random() * 900000).toString();
    setGeneratedCode(code);
    setErrors([]);
    setStep('verify');
  };

  const handleVerifySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.verificationCode !== generatedCode) {
      setErrors(['Invalid verification code']);
      return;
    }

    setErrors([]);
    setStep('newPassword');
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const passwordErrors = validatePassword(formData.newPassword);
    
    if (passwordErrors.length > 0) {
      setErrors(['Password must have:', ...passwordErrors]);
      return;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setErrors(['Passwords do not match']);
      return;
    }

    // Simulate updating password (in real app, this would be secure)
    // For demo purposes, just show success
    setErrors([]);
    setStep('success');
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const getPasswordStrength = (password: string) => {
    const errors = validatePassword(password);
    if (errors.length === 0) return { strength: 'Strong', color: 'text-green-600' };
    if (errors.length <= 2) return { strength: 'Medium', color: 'text-yellow-600' };
    return { strength: 'Weak', color: 'text-red-600' };
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
                  Reset Password
                </h2>
                <p className="mb-5 text-base text-white/80">
                  {step === 'email' && 'Enter your email to reset your password'}
                  {step === 'verify' && 'Check your email for the verification code'}
                  {step === 'newPassword' && 'Create a new password'}
                  {step === 'success' && 'Password reset successful!'}
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
                      Reset Password
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

                {errors.length > 0 && (
                  <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <ul className="text-red-700 text-sm text-left">
                      {errors.map((error, index) => (
                        <li key={index} className="mb-1">{error}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Step 1: Email */}
                {step === 'email' && (
                  <form onSubmit={handleEmailSubmit}>
                    <div className="mb-[22px]">
                      <input
                        type="email"
                        name="email"
                        placeholder="Enter your email address"
                        value={formData.email}
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
                        Send Reset Code
                      </button>
                    </div>
                  </form>
                )}

                {/* Step 2: Verification */}
                {step === 'verify' && (
                  <form onSubmit={handleVerifySubmit}>
                    <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-blue-800 text-sm mb-2">Demo Mode: Your verification code is:</p>
                      <p className="text-blue-900 font-bold text-lg">{generatedCode}</p>
                      <p className="text-blue-600 text-xs mt-2">In a real app, this would be sent to your email</p>
                    </div>

                    <div className="mb-[22px]">
                      <input
                        type="text"
                        name="verificationCode"
                        placeholder="Enter verification code"
                        value={formData.verificationCode}
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
                        Verify Code
                      </button>
                    </div>
                  </form>
                )}

                {/* Step 3: New Password */}
                {step === 'newPassword' && (
                  <form onSubmit={handlePasswordSubmit}>
                    <div className="mb-[22px]">
                      <input
                        type="password"
                        name="newPassword"
                        placeholder="New Password"
                        value={formData.newPassword}
                        onChange={handleChange}
                        required
                        className="w-full px-5 py-3 text-base transition bg-transparent border rounded-md outline-none border-stroke dark:border-dark-3 text-body-color dark:text-dark-6 placeholder:text-dark-6 focus:border-primary dark:focus:border-primary focus-visible:shadow-none"
                      />
                      {formData.newPassword && (
                        <div className="mt-2 text-left">
                          <span className={`text-sm ${getPasswordStrength(formData.newPassword).color}`}>
                            Password strength: {getPasswordStrength(formData.newPassword).strength}
                          </span>
                        </div>
                      )}
                    </div>
                    
                    <div className="mb-[22px]">
                      <input
                        type="password"
                        name="confirmPassword"
                        placeholder="Confirm New Password"
                        value={formData.confirmPassword}
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
                        Reset Password
                      </button>
                    </div>
                  </form>
                )}

                {/* Step 4: Success */}
                {step === 'success' && (
                  <div>
                    <div className="mb-6 text-green-600 text-6xl">✓</div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-4">Password Reset Successful!</h3>
                    <p className="text-gray-600 mb-6">Your password has been updated successfully.</p>
                    <button
                      onClick={() => navigate('/login')}
                      className="w-full px-5 py-3 text-base text-white transition duration-300 ease-in-out border rounded-md cursor-pointer border-primary bg-primary hover:bg-primary/90"
                    >
                      Sign In
                    </button>
                  </div>
                )}

                <div className="mt-6">
                  <Link
                    to="/login"
                    className="text-primary hover:underline"
                  >
                    Back to Sign In
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default ResetPassword;