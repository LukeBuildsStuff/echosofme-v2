/**
 * Dynamic API URL configuration utility
 * Automatically detects the correct Eleanor API URL based on the current hostname
 */

export const getEleanorApiUrl = (): string => {
  // Use relative path - Vite proxy will handle routing to Eleanor API
  const apiUrl = '/api';
  console.log('🔧 Using proxied API URL:', apiUrl);
  return apiUrl;
};

/**
 * Get the current access method for debugging
 */
export const getAccessInfo = () => {
  return {
    hostname: window.location.hostname,
    href: window.location.href,
    apiUrl: getEleanorApiUrl(),
    isLocal: ['localhost', '127.0.0.1'].includes(window.location.hostname),
    isPrivateIP: /^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)/.test(window.location.hostname)
  };
};