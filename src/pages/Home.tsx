import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout/Layout';

const Home: React.FC = () => {
  return (
    <Layout>
      {/* Hero Section */}
      <div
        id="home"
        className="relative overflow-hidden bg-primary pt-[120px] md:pt-[130px] lg:pt-[160px] pb-[120px] md:pb-[130px] lg:pb-[160px]"
      >
        <div className="container px-4 mx-auto">
          <div className="flex flex-wrap items-center -mx-4">
            <div className="w-full px-4">
              <div className="hero-content mx-auto max-w-[780px] text-center">
                <h1 className="mb-6 text-3xl font-bold leading-snug text-white sm:text-4xl sm:leading-snug lg:text-5xl lg:leading-[1.2]">
                  Create Your Digital Echo
                </h1>
                <p className="mx-auto mb-9 max-w-[600px] text-base font-medium text-white sm:text-lg sm:leading-[1.44]">
                  An Echo is your personalized AI companion trained on your memories, reflections, and experiences. 
                  Build a lasting digital legacy that captures your essence and wisdom for future generations.
                </p>
                <ul className="flex flex-wrap items-center justify-center gap-5 mb-10">
                  <li>
                    <Link
                      to="/login"
                      className="inline-flex items-center justify-center rounded-md bg-white px-7 py-[14px] text-center text-base font-medium text-dark shadow-1 transition duration-300 ease-in-out hover:bg-gray-2 hover:text-body-color"
                    >
                      Start Your Journey
                    </Link>
                  </li>
                  <li>
                    <a
                      href="#features"
                      className="flex items-center gap-4 rounded-md bg-white/[0.12] px-6 py-[14px] text-base font-medium text-white transition duration-300 ease-in-out hover:bg-white hover:text-dark"
                    >
                      <svg
                        className="fill-current"
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path d="M12 2L2 7V17C2 17.55 2.45 18 3 18H21C21.55 18 22 17.55 22 17V7L12 2ZM12 4.84L19 8.16V16H5V8.16L12 4.84Z"/>
                        <path d="M12 9C10.9 9 10 9.9 10 11S10.9 13 12 13 14 12.1 14 11 13.1 9 12 9Z"/>
                      </svg>
                      Learn More
                    </a>
                  </li>
                </ul>
                <div>
                  <p className="mb-4 text-base font-medium text-center text-white">
                    Built with cutting-edge AI technology
                  </p>
                  <div className="flex items-center justify-center gap-4 text-center">
                    <div className="flex items-center gap-2 text-white/60">
                      <svg width="24" height="24" viewBox="0 0 24 24" className="fill-current">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                        <path d="M12 6.5c-3.03 0-5.5 2.47-5.5 5.5s2.47 5.5 5.5 5.5 5.5-2.47 5.5-5.5-2.47-5.5-5.5-5.5zm0 9c-1.93 0-3.5-1.57-3.5-3.5s1.57-3.5 3.5-3.5 3.5 1.57 3.5 3.5-1.57 3.5-3.5 3.5z"/>
                      </svg>
                      <span>AI Powered</span>
                    </div>
                    <div className="flex items-center gap-2 text-white/60">
                      <svg width="24" height="24" viewBox="0 0 24 24" className="fill-current">
                        <path d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 1Z"/>
                      </svg>
                      <span>Secure</span>
                    </div>
                    <div className="flex items-center gap-2 text-white/60">
                      <svg width="24" height="24" viewBox="0 0 24 24" className="fill-current">
                        <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1L13.5 2.5L16.17 5.17L13 8.34L15.66 11L18.83 7.83L21.5 10.5L23 9Z"/>
                      </svg>
                      <span>Personal</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Background decorations */}
        <div className="absolute left-0 top-0 z-[-1] opacity-30 lg:opacity-100">
          <svg
            width="364"
            height="201"
            viewBox="0 0 364 201"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M5.88928 72.3303C33.6599 66.4798 101.397 64.9086 150.178 105.427C211.155 156.076 229.59 162.093 264.333 166.607C299.076 171.12 337.718 183.657 362.889 201.414"
              stroke="url(#paint0_linear_25:218)"
            />
            <path
              d="M-22.1107 72.3303C5.65989 66.4798 73.3965 64.9086 122.178 105.427C183.155 156.076 201.59 162.093 236.333 166.607C271.076 171.12 309.718 183.657 334.889 201.414"
              stroke="url(#paint1_linear_25:218)"
            />
            <path
              d="M-53.1107 72.3303C-25.3401 66.4798 42.3965 64.9086 91.1783 105.427C152.155 156.076 170.59 162.093 205.333 166.607C240.076 171.12 278.718 183.657 303.889 201.414"
              stroke="url(#paint2_linear_25:218)"
            />
            <defs>
              <linearGradient
                id="paint0_linear_25:218"
                x1="184.389"
                y1="69.2405"
                x2="184.389"
                y2="212.24"
                gradientUnits="userSpaceOnUse"
              >
                <stop stopColor="#4A6CF7" stopOpacity="0" />
                <stop offset="1" stopColor="#4A6CF7" />
              </linearGradient>
              <linearGradient
                id="paint1_linear_25:218"
                x1="153.389"
                y1="69.2405"
                x2="153.389"
                y2="212.24"
                gradientUnits="userSpaceOnUse"
              >
                <stop stopColor="#4A6CF7" stopOpacity="0" />
                <stop offset="1" stopColor="#4A6CF7" />
              </linearGradient>
              <linearGradient
                id="paint2_linear_25:218"
                x1="122.389"
                y1="69.2405"
                x2="122.389"
                y2="212.24"
                gradientUnits="userSpaceOnUse"
              >
                <stop stopColor="#4A6CF7" stopOpacity="0" />
                <stop offset="1" stopColor="#4A6CF7" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div className="absolute right-0 top-0 z-[-1] opacity-30 lg:opacity-100">
          <svg
            width="364"
            height="201"
            viewBox="0 0 364 201"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M364 72.3303C336.23 66.4798 268.493 64.9086 219.712 105.427C158.734 156.076 140.3 162.093 105.557 166.607C70.8135 171.12 32.1716 183.657 7.00006 201.414"
              stroke="url(#paint0_linear_25:218)"
            />
          </svg>
        </div>
      </div>

      {/* Features Section */}
      <section id="features" className="py-16 md:py-20 lg:py-28">
        <div className="container px-4 mx-auto">
          <div className="-mx-4 flex flex-wrap">
            <div className="w-full px-4">
              <div className="mx-auto mb-12 max-w-[510px] text-center lg:mb-20">
                <span className="mb-4 block text-lg font-semibold text-primary">
                  Features
                </span>
                <h2 className="mb-4 text-3xl font-bold text-black dark:text-white sm:text-4xl md:text-[40px]">
                  Build Your Digital Echo
                </h2>
                <p className="text-base text-body-color dark:text-dark-6">
                  Create an AI that knows you deeply through conversations, reflections, and memories. Your Echo learns your voice, values, and wisdom to preserve them forever.
                </p>
              </div>
            </div>
          </div>
          
          <div className="-mx-4 flex flex-wrap">
            <div className="w-full px-4 md:w-1/2 lg:w-1/3">
              <div className="group mb-12">
                <div className="relative z-10 mb-8 flex h-[70px] w-[70px] items-center justify-center rounded-2xl bg-primary">
                  <span className="absolute left-0 top-0 z-[-1] mb-8 flex h-[70px] w-[70px] rotate-[25deg] items-center justify-center rounded-2xl bg-primary bg-opacity-20 duration-300 group-hover:rotate-45"></span>
                  <svg
                    width="32"
                    height="32"
                    viewBox="0 0 32 32"
                    className="fill-white"
                  >
                    <path d="M16 4c6.6 0 12 5.4 12 12s-5.4 12-12 12S4 22.6 4 16 9.4 4 16 4m0-2C8.3 2 2 8.3 2 16s6.3 14 14 14 14-6.3 14-14S23.7 2 16 2z"/>
                    <path d="M16 8c-4.4 0-8 3.6-8 8h2c0-3.3 2.7-6 6-6s6 2.7 6 6-2.7 6-6 6v2c4.4 0 8-3.6 8-8s-3.6-8-8-8z"/>
                    <circle cx="16" cy="16" r="2"/>
                  </svg>
                </div>
                <h4 className="mb-3 text-xl font-bold text-black dark:text-white">
                  Converse with Your Echo
                </h4>
                <p className="mb-8 text-body-color dark:text-dark-6 lg:mb-11">
                  Have deep conversations with your personal AI that understands your unique perspective and helps you explore your thoughts and experiences.
                </p>
                <span className="text-base font-medium text-gray-400 dark:text-dark-6">
                  Coming Soon
                </span>
              </div>
            </div>
            
            <div className="w-full px-4 md:w-1/2 lg:w-1/3">
              <div className="group mb-12">
                <div className="relative z-10 mb-8 flex h-[70px] w-[70px] items-center justify-center rounded-2xl bg-primary">
                  <span className="absolute left-0 top-0 z-[-1] mb-8 flex h-[70px] w-[70px] rotate-[25deg] items-center justify-center rounded-2xl bg-primary bg-opacity-20 duration-300 group-hover:rotate-45"></span>
                  <svg
                    width="32"
                    height="32"
                    viewBox="0 0 32 32"
                    className="fill-white"
                  >
                    <path d="M28 4H4c-2.2 0-4 1.8-4 4v16c0 2.2 1.8 4 4 4h24c2.2 0 4-1.8 4-4V8c0-2.2-1.8-4-4-4zM4 6h24c1.1 0 2 .9 2 2v2H2V8c0-1.1.9-2 2-2zm24 20H4c-1.1 0-2-.9-2-2V12h28v12c0 1.1-.9 2-2 2z"/>
                    <path d="M6 16h4v2H6zm6 0h4v2h-4zm6 0h4v2h-4z"/>
                  </svg>
                </div>
                <h4 className="mb-3 text-xl font-bold text-black dark:text-white">
                  Memory Training
                </h4>
                <p className="mb-8 text-body-color dark:text-dark-6 lg:mb-11">
                  Feed your Echo through daily reflections, experiences, and memories. Each entry makes your digital self more authentic and complete.
                </p>
                <Link
                  to="/reflections"
                  className="text-base font-medium text-body-color hover:text-primary dark:text-dark-6"
                >
                  Train Your Echo
                </Link>
              </div>
            </div>
            
            <div className="w-full px-4 md:w-1/2 lg:w-1/3">
              <div className="group mb-12">
                <div className="relative z-10 mb-8 flex h-[70px] w-[70px] items-center justify-center rounded-2xl bg-primary">
                  <span className="absolute left-0 top-0 z-[-1] mb-8 flex h-[70px] w-[70px] rotate-[25deg] items-center justify-center rounded-2xl bg-primary bg-opacity-20 duration-300 group-hover:rotate-45"></span>
                  <svg
                    width="32"
                    height="32"
                    viewBox="0 0 32 32"
                    className="fill-white"
                  >
                    <path d="M16 2C8.3 2 2 8.3 2 16s6.3 14 14 14 14-6.3 14-14S23.7 2 16 2zm0 26C9.4 28 4 22.6 4 16S9.4 4 16 4s12 5.4 12 12-5.4 12-12 12z"/>
                    <path d="M21.7 10.3L16 16l-5.7-5.7-1.4 1.4L16 18.8l7.1-7.1z"/>
                    <path d="M8 14h2v8H8zm4-4h2v12h-2zm4-2h2v14h-2zm4 6h2v8h-2z"/>
                  </svg>
                </div>
                <h4 className="mb-3 text-xl font-bold text-black dark:text-white">
                  Echo History
                </h4>
                <p className="mb-8 text-body-color dark:text-dark-6 lg:mb-11">
                  Watch your Echo evolve over time through a beautiful timeline of conversations, memories, and growth milestones.
                </p>
                <Link
                  to="/legacy"
                  className="text-base font-medium text-body-color hover:text-primary dark:text-dark-6"
                >
                  Explore Echo
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="pt-16 md:pt-20 lg:pt-28 pb-16 md:pb-20 lg:pb-28 bg-slate-50 dark:bg-dark-2">
        <div className="container px-4 mx-auto">
          <div className="-mx-4 flex flex-wrap items-center">
            <div className="w-full px-4 lg:w-1/2">
              <div className="relative mx-auto mb-12 max-w-[500px] text-center lg:m-0">
                <div className="mx-auto mb-8 max-w-[350px]">
                  <div className="h-[250px] bg-gradient-to-r from-primary/20 to-secondary/20 rounded-2xl flex items-center justify-center">
                    <svg
                      width="120"
                      height="120"
                      viewBox="0 0 120 120"
                      className="text-primary"
                      fill="currentColor"
                    >
                      <path d="M60 10C32.4 10 10 32.4 10 60s22.4 50 50 50 50-22.4 50-50S87.6 10 60 10zm0 90c-22.1 0-40-17.9-40-40s17.9-40 40-40 40 17.9 40 40-17.9 40-40 40z"/>
                      <path d="M60 30c-16.5 0-30 13.5-30 30h8c0-12.1 9.9-22 22-22s22 9.9 22 22-9.9 22-22 22v8c16.5 0 30-13.5 30-30s-13.5-30-30-30z"/>
                      <circle cx="60" cy="60" r="6"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
            <div className="w-full px-4 lg:w-1/2">
              <div className="max-w-[470px]">
                <div className="mb-9">
                  <h3 className="mb-4 text-xl font-bold text-black dark:text-white sm:text-2xl lg:text-xl xl:text-2xl">
                    Your AI Clone for Life
                  </h3>
                  <p className="text-base font-medium leading-relaxed text-body-color dark:text-dark-6">
                    Your Echo learns from your conversations, reflections, and experiences to become a personalized AI companion that understands your unique perspective on life.
                  </p>
                </div>
                <div className="mb-9">
                  <h3 className="mb-4 text-xl font-bold text-black dark:text-white sm:text-2xl lg:text-xl xl:text-2xl">
                    Preserve Your Wisdom
                  </h3>
                  <p className="text-base font-medium leading-relaxed text-body-color dark:text-dark-6">
                    Create a lasting legacy by capturing your thoughts, experiences, and insights that can be shared with future generations or used for personal growth.
                  </p>
                </div>
                <div className="mb-1">
                  <h3 className="mb-4 text-xl font-bold text-black dark:text-white sm:text-2xl lg:text-xl xl:text-2xl">
                    Grow Through Reflection
                  </h3>
                  <p className="text-base font-medium leading-relaxed text-body-color dark:text-dark-6">
                    Regular reflection helps you understand patterns, celebrate progress, and make more intentional decisions about your life's direction.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Home;