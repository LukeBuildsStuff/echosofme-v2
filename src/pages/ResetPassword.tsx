import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout/Layout';
import { useAuth } from '../contexts/SupabaseAuthContext';
import { validatePassword, getPasswordStrengthColor } from '../utils/passwordValidator';
import { api } from '../lib/supabase';

const ResetPassword: React.FC = () => {
  const [step, setStep] = useState<'email' | 'newPassword' | 'success'>('email');
  const [formData, setFormData] = useState({
    email: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { resetPassword, updatePassword, verifyPasswordReset } = useAuth();

  // Check for password reset tokens or errors in URL on component mount
  useEffect(() => {
    // Check for errors in hash fragment first
    const hash = window.location.hash;
    if (hash.includes('error=')) {
      const urlParams = new URLSearchParams(hash.substring(1));
      const error = urlParams.get('error');
      const errorCode = urlParams.get('error_code');
      const errorDescription = urlParams.get('error_description');

      if (error === 'access_denied' && errorCode === 'otp_expired') {
        setErrors(['Your password reset link has expired. Please request a new one below.']);
      } else if (errorDescription) {
        setErrors([decodeURIComponent(errorDescription)]);
      } else {
        setErrors(['Password reset failed. Please try requesting a new reset link.']);
      }

      // Clear the hash to clean up the URL
      window.history.replaceState(null, '', window.location.pathname);
      return;
    }

    // Check for valid tokens
    const tokens = api.getPasswordResetTokensFromUrl();
    if (tokens) {
      // User clicked reset link from email
      handlePasswordResetFromEmail(tokens.accessToken, tokens.refreshToken);
    }
  }, []);

  const validateEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handlePasswordResetFromEmail = async (accessToken: string, refreshToken: string) => {
    try {
      setLoading(true);
      setErrors([]);

      // Verify the reset token and log the user in
      await verifyPasswordReset(accessToken, refreshToken);

      // Move to password update step
      setStep('newPassword');
    } catch (error: any) {
      console.error('Password reset verification failed:', error);
      setErrors(['Invalid or expired reset link. Please request a new password reset.']);
    } finally {
      setLoading(false);
    }
  };

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateEmail(formData.email)) {
      setErrors(['Please enter a valid email address']);
      return;
    }

    try {
      setLoading(true);
      setErrors([]);

      await resetPassword(formData.email);

      // Show success message
      setStep('success');
    } catch (error: any) {
      console.error('Password reset failed:', error);
      setErrors([error.message || 'Failed to send reset email. Please try again.']);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validation = validatePassword(formData.newPassword);

    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setErrors(['Passwords do not match']);
      return;
    }

    try {
      setLoading(true);
      setErrors([]);

      await updatePassword(formData.newPassword);

      // Password updated successfully
      setStep('success');
    } catch (error: any) {
      console.error('Password update failed:', error);
      setErrors([error.message || 'Failed to update password. Please try again.']);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const getPasswordStrength = (password: string) => {
    const validation = validatePassword(password);
    return {
      strength: validation.strength.charAt(0).toUpperCase() + validation.strength.slice(1),
      color: getPasswordStrengthColor(validation.strength)
    };
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
                  {step === 'email' && 'Enter your email to receive a password reset link'}
                  {step === 'newPassword' && 'Create a new secure password'}
                  {step === 'success' && 'Password reset completed successfully!'}
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
                        disabled={loading}
                        className="w-full px-5 py-3 text-base transition bg-transparent border rounded-md outline-none border-stroke dark:border-dark-3 text-body-color dark:text-dark-6 placeholder:text-dark-6 focus:border-primary dark:focus:border-primary focus-visible:shadow-none disabled:opacity-50"
                      />
                    </div>

                    <div className="mb-9">
                      <button
                        type="submit"
                        disabled={loading}
                        className="w-full px-5 py-3 text-base text-white transition duration-300 ease-in-out border rounded-md cursor-pointer border-primary bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading ? (
                          <div className="flex items-center justify-center">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Sending Reset Link...
                          </div>
                        ) : (
                          'Send Reset Link'
                        )}
                      </button>
                    </div>
                  </form>
                )}

                {/* Step 2: New Password */}
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
                        disabled={loading}
                        className="w-full px-5 py-3 text-base transition bg-transparent border rounded-md outline-none border-stroke dark:border-dark-3 text-body-color dark:text-dark-6 placeholder:text-dark-6 focus:border-primary dark:focus:border-primary focus-visible:shadow-none disabled:opacity-50"
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
                        disabled={loading}
                        className="w-full px-5 py-3 text-base transition bg-transparent border rounded-md outline-none border-stroke dark:border-dark-3 text-body-color dark:text-dark-6 placeholder:text-dark-6 focus:border-primary dark:focus:border-primary focus-visible:shadow-none disabled:opacity-50"
                      />
                    </div>

                    <div className="mb-9">
                      <button
                        type="submit"
                        disabled={loading}
                        className="w-full px-5 py-3 text-base text-white transition duration-300 ease-in-out border rounded-md cursor-pointer border-primary bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading ? (
                          <div className="flex items-center justify-center">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Updating Password...
                          </div>
                        ) : (
                          'Update Password'
                        )}
                      </button>
                    </div>
                  </form>
                )}

                {/* Step 3: Success */}
                {step === 'success' && (
                  <div>
                    <div className="mb-6 text-green-600 text-6xl">✓</div>
                    {formData.newPassword ? (
                      // Password was updated
                      <>
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Password Updated Successfully!</h3>
                        <p className="text-gray-600 dark:text-gray-300 mb-6">Your password has been updated successfully. You can now sign in with your new password.</p>
                        <button
                          onClick={() => navigate('/login')}
                          className="w-full px-5 py-3 text-base text-white transition duration-300 ease-in-out border rounded-md cursor-pointer border-primary bg-primary hover:bg-primary/90"
                        >
                          Sign In
                        </button>
                      </>
                    ) : (
                      // Reset email was sent
                      <>
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Reset Link Sent!</h3>
                        <p className="text-gray-600 dark:text-gray-300 mb-6">
                          We've sent a password reset link to <strong>{formData.email}</strong>.
                          Check your email and click the link to reset your password.
                        </p>
                        <div className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                          <p>Didn't receive the email? Check your spam folder or</p>
                          <button
                            onClick={() => setStep('email')}
                            className="text-primary hover:underline ml-1"
                          >
                            try again
                          </button>
                        </div>
                      </>
                    )}
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