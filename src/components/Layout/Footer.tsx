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
                Create a digital reflection of yourself through daily reflections. Build a meaningful legacy that preserves your thoughts and memories for loved ones.
              </p>
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
                    to="/insights"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    Personal Insights
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
                    href="#features"
                    className="mb-4 inline-block text-base leading-loose text-body-color hover:text-primary dark:text-dark-6"
                  >
                    How it Works
                  </a>
                </li>
                <li>
                  <span className="mb-4 inline-block text-base leading-loose text-body-color/60 dark:text-dark-6/60">
                    Privacy & Security
                  </span>
                </li>
                <li>
                  <span className="mb-4 inline-block text-base leading-loose text-body-color/60 dark:text-dark-6/60">
                    Support
                  </span>
                </li>
                <li>
                  <span className="mb-4 inline-block text-base leading-loose text-body-color/60 dark:text-dark-6/60">
                    Contact Us
                  </span>
                </li>
              </ul>
            </div>
          </div>
          
        </div>
        
        <div className="h-px w-full bg-gradient-to-r from-transparent via-[#D2D8E183] to-transparent dark:via-[#959CB183]"></div>
        <div className="py-8">
          <p className="text-center text-base text-body-color dark:text-white">
            © 2024 Echos of Me. All rights reserved.
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