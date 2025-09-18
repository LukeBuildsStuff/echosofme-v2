import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/SupabaseAuthContext';

interface NavbarProps {
  isAuthenticated?: boolean;
}

const Navbar: React.FC<NavbarProps> = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const isHome = location.pathname === '/';
  const profileRef = useRef<HTMLDivElement>(null);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const handleSignOut = () => {
    logout();
    navigate('/');
    setIsProfileOpen(false);
  };

  const handleSettingsClick = () => {
    navigate('/settings');
    setIsProfileOpen(false);
  };

  const toggleProfileDropdown = () => {
    setIsProfileOpen(!isProfileOpen);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setIsProfileOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className={`absolute top-0 left-0 z-40 flex items-center w-full ${isHome ? 'bg-transparent' : 'bg-white dark:bg-dark-2 shadow-lg'} ud-header`}>
      <div className="container px-4 mx-auto">
        <div className="relative flex items-center justify-between -mx-4">
          <div className="max-w-full px-4 w-60">
            <Link to="/" className="block w-full py-5 navbar-logo">
              <span className="text-2xl font-bold text-primary whitespace-nowrap">
                Echos of Me
              </span>
            </Link>
          </div>
          
          <div className="flex items-center justify-between w-full px-4">
            <div>
              <button
                onClick={toggleMenu}
                className={`absolute right-4 top-1/2 block -translate-y-1/2 rounded-lg p-3 ring-primary focus:ring-2 lg:hidden min-h-[44px] min-w-[44px] ${isOpen ? 'navbarTogglerActive' : ''}`}
              >
                <span className={`relative my-[6px] block h-[2px] w-[30px] ${isHome ? 'bg-white' : 'bg-dark'}`}></span>
                <span className={`relative my-[6px] block h-[2px] w-[30px] ${isHome ? 'bg-white' : 'bg-dark'}`}></span>
                <span className={`relative my-[6px] block h-[2px] w-[30px] ${isHome ? 'bg-white' : 'bg-dark'}`}></span>
              </button>
              
              <nav className={`${isOpen ? 'block' : 'hidden'} lg:block lg:static lg:w-full lg:max-w-full lg:bg-transparent lg:px-4 lg:py-0 lg:shadow-none xl:px-6 absolute top-full left-0 w-full bg-white lg:bg-transparent shadow-lg lg:shadow-none`}>
                {/* Mobile User Info - Only show when menu is open and user is authenticated */}
                {isOpen && isAuthenticated && (
                  <div className="block lg:hidden px-8 py-4 border-b border-gray-200">
                    <div className="text-lg font-semibold text-dark">{user?.displayName || 'User'}</div>
                    <div className="text-sm text-gray-600">{user?.email}</div>
                  </div>
                )}
                
                <ul className="block lg:flex 2xl:ml-20">
                  {/* Show marketing navigation only when NOT authenticated */}
                  {!isAuthenticated && (
                    <>
                      <li className="relative group">
                        <a
                          href="#features"
                          className="flex py-2 mx-8 text-base font-medium ud-menu-scroll lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 text-dark hover:text-primary"
                        >
                          Features
                        </a>
                      </li>
                      <li className="relative group">
                        <a
                          href="#about"
                          className="flex py-2 mx-8 text-base font-medium ud-menu-scroll lg:ml-7 lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 xl:ml-10 text-dark hover:text-primary transition-all duration-300 touch-target hover:scale-105"
                        >
                          Company
                        </a>
                      </li>
                      <li className="relative group">
                        <a
                          href="javascript:void(0)"
                          className="flex py-2 mx-8 text-base font-medium lg:ml-7 lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 xl:ml-10 text-dark hover:text-primary"
                        >
                          Blog
                        </a>
                      </li>
                      <li className="relative group">
                        <a
                          href="javascript:void(0)"
                          className="flex py-2 mx-8 text-base font-medium lg:ml-7 lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 xl:ml-10 text-dark hover:text-primary"
                        >
                          Pricing
                        </a>
                      </li>
                    </>
                  )}

                  {/* Show app navigation only when authenticated */}
                  {isAuthenticated && (
                    <>
                      <li className="relative group">
                        <Link
                          to="/dashboard"
                          className={`flex py-2 mx-8 text-base font-medium text-dark group-hover:text-primary dark:text-white lg:ml-7 lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 lg:group-hover:text-primary xl:ml-10`}
                        >
                          Dashboard
                        </Link>
                      </li>
                      <li className="relative group">
                        <Link
                          to="/chat"
                          className={`flex py-2 mx-8 text-base font-medium text-dark group-hover:text-primary dark:text-white lg:ml-7 lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 lg:group-hover:text-primary xl:ml-10`}
                        >
                          Echo Chat
                        </Link>
                      </li>
                      <li className="relative group">
                        <Link
                          to="/reflections"
                          className={`flex py-2 mx-8 text-base font-medium text-dark group-hover:text-primary dark:text-white lg:ml-7 lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 lg:group-hover:text-primary xl:ml-10`}
                        >
                          Reflections
                        </Link>
                      </li>
                      <li className="relative group">
                        <Link
                          to="/legacy"
                          className={`flex py-2 mx-8 text-base font-medium text-dark group-hover:text-primary dark:text-white lg:ml-7 lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 lg:group-hover:text-primary xl:ml-10`}
                        >
                          Legacy
                        </Link>
                      </li>
                      <li className="relative group">
                        <Link
                          to="/insights"
                          className={`flex py-2 mx-8 text-base font-medium text-dark group-hover:text-primary dark:text-white lg:ml-7 lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 lg:group-hover:text-primary xl:ml-10`}
                        >
                          Insights
                        </Link>
                      </li>
                    </>
                  )}
                  
                  {/* Mobile Settings and Sign Out - Only show in mobile menu */}
                  {isOpen && isAuthenticated && (
                    <>
                      <li className="block lg:hidden border-t border-gray-200">
                        <button 
                          onClick={handleSettingsClick}
                          className="flex py-3 mx-8 text-base font-medium text-dark hover:text-primary w-full text-left"
                        >
                          Settings
                        </button>
                      </li>
                      <li className="block lg:hidden">
                        <button 
                          onClick={handleSignOut}
                          className="flex py-3 mx-8 text-base font-medium text-dark hover:text-primary w-full text-left"
                        >
                          Sign Out
                        </button>
                      </li>
                    </>
                  )}
                </ul>
              </nav>
            </div>
            
            <div className="flex items-center justify-end pr-16 lg:pr-0">
              {!isAuthenticated ? (
                <>
                  <Link
                    to="/login"
                    className={`px-7 py-3 text-base font-medium ${isHome ? 'text-white hover:opacity-70' : 'text-dark hover:text-primary'} dark:text-white md:block`}
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/login"
                    className="rounded-lg bg-primary px-7 py-3 text-base font-medium text-white transition hover:bg-primary/90 min-h-[44px] flex items-center"
                  >
                    Get Started
                  </Link>
                </>
              ) : (
                <div ref={profileRef} className="hidden lg:block relative group">
                  {/* Desktop Profile Icon */}
                  <button
                    onClick={toggleProfileDropdown}
                    className="flex items-center px-4 py-2 text-base font-medium text-dark hover:text-primary dark:text-white min-h-[44px]"
                    aria-expanded={isProfileOpen}
                    aria-haspopup="true"
                  >
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                    </svg>
                    <svg
                      className="ml-2 fill-current"
                      width="16"
                      height="20"
                      viewBox="0 0 16 20"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="M7.99999 14.9C7.84999 14.9 7.72499 14.85 7.59999 14.75L1.84999 9.10005C1.62499 8.87505 1.62499 8.52505 1.84999 8.30005C2.07499 8.07505 2.42499 8.07505 2.64999 8.30005L7.99999 13.525L13.35 8.25005C13.575 8.02505 13.925 8.02505 14.15 8.25005C14.375 8.47505 14.375 8.82505 14.15 9.05005L8.39999 14.7C8.27499 14.825 8.14999 14.9 7.99999 14.9Z" />
                    </svg>
                  </button>
                  <div className={`submenu absolute right-0 top-[110%] w-[200px] rounded-lg bg-white p-4 shadow-lg transition-all duration-300 dark:bg-dark-2 ${
                    isProfileOpen
                      ? 'visible opacity-100 top-full'
                      : 'invisible opacity-0 group-hover:visible group-hover:top-full group-hover:opacity-100'
                  }`}>
                    <div className="px-4 py-2 text-sm text-gray-900 border-b border-gray-200">
                      <div className="font-medium">{user?.displayName || 'User'}</div>
                      <div className="text-gray-500">{user?.email}</div>
                    </div>
                    {user?.email === 'lukemoeller@yahoo.com' && (
                      <button
                        onClick={() => {
                          navigate('/admin/database');
                          setIsProfileOpen(false);
                        }}
                        className="block w-full rounded-sm px-4 py-2 text-left text-sm text-body-color hover:text-primary dark:text-dark-6 dark:hover:text-primary min-h-[44px]"
                      >
                        <div className="flex items-center">
                          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                          </svg>
                          Admin Panel
                        </div>
                      </button>
                    )}
                    <button
                      onClick={handleSettingsClick}
                      className="block w-full rounded-sm px-4 py-2 text-left text-sm text-body-color hover:text-primary dark:text-dark-6 dark:hover:text-primary min-h-[44px]"
                    >
                      Settings
                    </button>
                    <button 
                      onClick={handleSignOut}
                      className="block w-full rounded-sm px-4 py-2 text-left text-sm text-body-color hover:text-primary dark:text-dark-6 dark:hover:text-primary min-h-[44px]"
                    >
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Navbar;