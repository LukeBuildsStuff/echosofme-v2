import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <footer className="relative z-10 bg-white dark:bg-dark pt-20 pb-10 lg:pt-[120px] lg:pb-20">
      <div className="container mx-auto">
        <div className="-mx-4 flex flex-wrap">
          <div className="w-full px-4 md:w-1/2 lg:w-4/12 xl:w-5/12">
            <div className="mb-12 max-w-[360px] lg:mb-16">
              <Link to="/" className="mb-8 inline-block">
                <span className="text-2xl font-bold text-primary">
                  Echos of Me
                </span>
              </Link>
              <p className="text-base leading-relaxed text-body-color dark:text-dark-6 mb-9">
                Your personal AI memory companion that helps you preserve, reflect on, and learn from your life's most meaningful moments.
              </p>
              <div className="flex items-center -mx-3">
                <a
                  href="javascript:void(0)"
                  className="px-3 text-body-color hover:text-primary dark:text-dark-6 dark:hover:text-primary"
                >
                  <svg
                    width="22"
                    height="16"
                    viewBox="0 0 22 16"
                    className="fill-current"
                  >
                    <path d="M7.33341 15.4998H1.46675V5.83317H7.33341V15.4998ZM4.40008 3.2665C2.68341 3.2665 1.29175 1.87484 1.29175 0.158171C1.29175 -1.55849 2.68341 -2.95016 4.40008 -2.95016C6.11675 -2.95016 7.50841 -1.55849 7.50841 0.158171C7.50841 1.87484 6.11675 3.2665 4.40008 3.2665ZM20.3334 15.4998H14.4667V10.8332C14.4667 9.29984 14.4334 7.2915 12.2667 7.2915C10.0667 7.2915 9.73341 8.9665 9.73341 10.7248V15.4998H3.86675V5.83317H9.50008V7.6915H9.58341C10.4001 6.14984 12.4334 4.5165 15.4334 4.5165C21.3834 4.5165 22.0001 8.72484 22.0001 14.0915V15.4998H20.3334Z" />
                  </svg>
                </a>
                <a
                  href="javascript:void(0)"
                  className="px-3 text-body-color hover:text-primary dark:text-dark-6 dark:hover:text-primary"
                >
                  <svg
                    width="19"
                    height="14"
                    viewBox="0 0 19 14"
                    className="fill-current"
                  >
                    <path d="M16.3956 2.69C16.4081 2.8825 16.4081 3.075 16.4081 3.2675C16.4081 8.8375 12.3831 14 5.85062 14C3.68812 14 1.68062 13.3562 0 12.2125C0.32625 12.25 0.63875 12.2625 0.9775 12.2625C2.78375 12.2625 4.43312 11.6438 5.74812 10.6C4.08187 10.5625 2.67687 9.4875 2.20687 7.975C2.45187 8.0125 2.69687 8.0375 2.95562 8.0375C3.31312 8.0375 3.67062 7.9875 4.00312 7.9C2.27187 7.55 0.96375 6.0125 0.96375 4.175V4.125C1.46 4.4 2.025 4.575 2.62812 4.6C1.53562 3.9125 0.85 2.7 0.85 1.3375C0.85 0.6125 1.04875 -0.0375 1.39875 -0.6125C3.26375 1.7125 6.10812 3.1875 9.29687 3.375C9.23312 3.1 9.19437 2.8125 9.19437 2.525C9.19437 0.475 10.8606 -1.1625 12.9081 -1.1625C13.9706 -1.1625 14.9331 -0.725 15.6206 -0.0125C16.4694 -0.175 17.2806 -0.4875 18.0144 -0.925C17.7394 0.0125 17.1331 0.6125 16.3581 1C17.1081 0.9125 17.8331 0.7 18.5069 0.4C18.0169 1.0125 17.4106 1.5375 16.7231 1.925C16.4594 1.975 16.4206 2.825 16.3956 2.69Z" />
                  </svg>
                </a>
                <a
                  href="javascript:void(0)"
                  className="px-3 text-body-color hover:text-primary dark:text-dark-6 dark:hover:text-primary"
                >
                  <svg
                    width="18"
                    height="14"
                    viewBox="0 0 18 14"
                    className="fill-current"
                  >
                    <path d="M17.5058 2.07119C17.3068 1.2995 16.7068 0.70185 15.9358 0.503852C14.5611 0.140518 8.99911 0.140518 8.99911 0.140518C8.99911 0.140518 3.43711 0.140518 2.06244 0.503852C1.29144 0.70185 0.691439 1.2995 0.492439 2.07119C0.130106 3.44652 0.130106 6.31319 0.130106 6.31319C0.130106 6.31319 0.130106 9.17985 0.492439 10.5552C0.691439 11.3268 1.29144 11.9245 2.06244 12.1225C3.43711 12.4858 8.99911 12.4858 8.99911 12.4858C8.99911 12.4858 14.5611 12.4858 15.9358 12.1225C16.7068 11.9245 17.3068 11.3268 17.5058 10.5552C17.8681 9.17985 17.8681 6.31319 17.8681 6.31319C17.8681 6.31319 17.8681 3.44652 17.5058 2.07119ZM7.20244 9.00185V3.62452L11.7024 6.31319L7.20244 9.00185Z" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
          
          <div className="w-full px-4 sm:w-1/2 md:w-1/2 lg:w-2/12 xl:w-2/12">
            <div className="mb-12 lg:mb-16">
              <h2 className="mb-10 text-xl font-bold text-black dark:text-white">
                Features
              </h2>
              <ul>
                <li>
                  <Link
                    to="/chat"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    Echo Chat
                  </Link>
                </li>
                <li>
                  <Link
                    to="/reflections"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    Daily Reflections
                  </Link>
                </li>
                <li>
                  <Link
                    to="/legacy"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    Legacy Timeline
                  </Link>
                </li>
                <li>
                  <Link
                    to="/dashboard"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    Dashboard
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="w-full px-4 sm:w-1/2 md:w-1/2 lg:w-3/12 xl:w-2/12">
            <div className="mb-12 lg:mb-16">
              <h2 className="mb-10 text-xl font-bold text-black dark:text-white">
                About
              </h2>
              <ul>
                <li>
                  <a
                    href="javascript:void(0)"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    How it Works
                  </a>
                </li>
                <li>
                  <a
                    href="javascript:void(0)"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    Privacy & Security
                  </a>
                </li>
                <li>
                  <a
                    href="javascript:void(0)"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    Support
                  </a>
                </li>
                <li>
                  <a
                    href="javascript:void(0)"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    Contact Us
                  </a>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="w-full px-4 md:w-1/2 lg:w-4/12 xl:w-3/12">
            <div className="mb-12 lg:mb-16">
              <h2 className="mb-10 text-xl font-bold text-black dark:text-white">
                Partners
              </h2>
              <ul>
                <li>
                  <a
                    href="javascript:void(0)"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    TailGrids
                  </a>
                </li>
                <li>
                  <a
                    href="javascript:void(0)"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    Ayro UI
                  </a>
                </li>
                <li>
                  <a
                    href="javascript:void(0)"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    PlainAdmin
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="h-px w-full bg-gradient-to-r from-transparent via-[#D2D8E183] to-transparent dark:via-[#959CB183]"></div>
        <div className="py-8">
          <p className="text-center text-base text-body-color dark:text-white">
            Template by{' '}
            <a
              href="https://tailgrids.com"
              rel="nofollow noopener"
              target="_blank"
              className="hover:text-primary"
            >
              TailGrids
            </a>{' '}
            and{' '}
            <a
              href="https://uideck.com"
              rel="nofollow noopener"
              target="_blank"
              className="hover:text-primary"
            >
              UIdeck
            </a>
          </p>
        </div>
      </div>
      
      <div className="absolute right-0 top-14 z-[-1]">
        <svg
          width="55"
          height="99"
          viewBox="0 0 55 99"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle opacity="0.8" cx="49.5" cy="49.5" r="49.5" fill="#959CB1" />
          <mask
            id="mask0_94:899"
            style={{ maskType: 'alpha' }}
            maskUnits="userSpaceOnUse"
            x="0"
            y="0"
            width="99"
            height="99"
          >
            <circle opacity="0.8" cx="49.5" cy="49.5" r="49.5" fill="#4A6CF7" />
          </mask>
          <g mask="url(#mask0_94:899)">
            <circle opacity="0.8" cx="49.5" cy="49.5" r="49.5" fill="url(#paint0_radial_94:899)" />
          </g>
          <defs>
            <radialGradient
              id="paint0_radial_94:899"
              cx="0"
              cy="0"
              r="1"
              gradientUnits="userSpaceOnUse"
              gradientTransform="translate(49.5 49.5) rotate(90) scale(49.5)"
            >
              <stop stopColor="#4A6CF7" />
              <stop offset="1" stopColor="#4A6CF7" stopOpacity="0" />
            </radialGradient>
          </defs>
        </svg>
      </div>
      <div className="absolute bottom-24 left-0 z-[-1]">
        <svg
          width="79"
          height="94"
          viewBox="0 0 79 94"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <rect
            opacity="0.3"
            x="-41"
            y="26.9426"
            width="66.6667"
            height="66.6667"
            transform="rotate(-22.9007 -41 26.9426)"
            fill="url(#paint0_linear_94:889)"
          />
          <defs>
            <linearGradient
              id="paint0_linear_94:889"
              x1="-41"
              y1="26.9426"
              x2="-41"
              y2="93.6093"
              gradientUnits="userSpaceOnUse"
            >
              <stop stopColor="#4A6CF7" />
              <stop offset="1" stopColor="#4A6CF7" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>
      </div>
    </footer>
  );
};

export default Footer;