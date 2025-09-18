/**
 * Dynamic API URL configuration utility
 * Automatically detects the correct Eleanor API URL based on the current hostname
 */

/**
 * Check if Eleanor API is enabled for the current environment
 */
export const isEleanorEnabled = (): boolean => {
  // Check if we're in a browser environment
  if (typeof window === 'undefined') {
    return true; // SSR fallback - assume enabled for local dev
  }

  const hostname = window.location.hostname;
  const isLocal = ['localhost', '127.0.0.1'].includes(hostname);
  const isPrivateIP = /^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)/.test(hostname);

  // Local development - Eleanor is available
  if (isLocal || isPrivateIP) {
    return true;
  }

  // Production - check if explicitly disabled
  const prodApiUrl = import.meta.env.VITE_ELEANOR_API_URL;
  return prodApiUrl !== 'disabled';
};

export const getEleanorApiUrl = (): string => {
  // Check if Eleanor is enabled first
  if (!isEleanorEnabled()) {
    throw new Error('Eleanor API is disabled in production environment');
  }

  // Check if we're in a browser environment
  if (typeof window === 'undefined') {
    return 'http://localhost:8001'; // SSR fallback
  }

  const hostname = window.location.hostname;
  const isLocal = ['localhost', '127.0.0.1'].includes(hostname);
  const isPrivateIP = /^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)/.test(hostname);

  // Local development
  if (isLocal || isPrivateIP) {
    const apiUrl = 'http://localhost:8001';
    console.log('🔧 Using local Eleanor API:', apiUrl);
    return apiUrl;
  }

  // Production - use environment variable
  const prodApiUrl = import.meta.env.VITE_ELEANOR_API_URL;
  const finalApiUrl = prodApiUrl || 'https://your-api-domain.com';
  console.log('🚀 Using production Eleanor API:', finalApiUrl);
  return finalApiUrl;
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