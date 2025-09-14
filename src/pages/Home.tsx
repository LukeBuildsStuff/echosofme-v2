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
                  Your thoughts and memories, preserved for eternity. Create a digital reflection of yourself through daily reflections that becomes a lasting gift for loved ones when you're gone.
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
                    Powered by AI • Privacy First • Your Legacy
                  </p>
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
                  Create a digital representation of yourself using conversations, reflections and memories. Over time, your Echo will learn your "voice", values and wisdom to preserve forever.
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
                    <path d="M16 6c-2.8 0-5 2.2-5 5v6c0 2.8 2.2 5 5 5s5-2.2 5-5v-6c0-2.8-2.2-5-5-5zm0 2c1.7 0 3 1.3 3 3v6c0 1.7-1.3 3-3 3s-3-1.3-3-3v-6c0-1.7 1.3-3 3-3z"/>
                    <path d="M8 16c0 4.4 3.6 8 8 8s8-3.6 8-8h2c0 5.3-4.1 9.7-9.3 10v2h3v2h-8v-2h3v-2C9.1 25.7 5 21.3 5 16h3z"/>
                    <circle cx="4" cy="12" r="1" opacity="0.6"/>
                    <circle cx="6" cy="8" r="1" opacity="0.4"/>
                    <circle cx="26" cy="8" r="1" opacity="0.4"/>
                    <circle cx="28" cy="12" r="1" opacity="0.6"/>
                  </svg>
                </div>
                <h4 className="mb-3 text-xl font-bold text-black dark:text-white">
                  Your Voice Lives On
                </h4>
                <p className="mb-8 text-body-color dark:text-dark-6 lg:mb-11">
                  Once trained, your Echo becomes a bridge between generations—allowing loved ones to seek your guidance, hear your stories, and feel your presence through meaningful conversations.
                </p>
                <Link
                  to="/chat"
                  className="text-base font-medium text-body-color hover:text-primary dark:text-dark-6"
                >
                  Connect Across Time
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
                    <path d="M26 4H6c-1.1 0-2 .9-2 2v20c0 1.1.9 2 2 2h20c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zM6 6h20v20H6V6z"/>
                    <path d="M8 8v16l2-2 2 2 2-2 2 2 2-2 2 2 2-2 2 2V8H8zm2 2h12v2H10v-2zm0 4h12v2H10v-2zm0 4h8v2h-8v-2z"/>
                    <path d="M24 16c.6 0 1-.4 1-1s-.4-1-1-1-1 .4-1 1 .4 1 1 1z" opacity="0.7"/>
                    <path d="M26 18c.6 0 1-.4 1-1s-.4-1-1-1-1 .4-1 1 .4 1 1 1z" opacity="0.5"/>
                  </svg>
                </div>
                <h4 className="mb-3 text-xl font-bold text-black dark:text-white">
                  Build Your Story
                </h4>
                <p className="mb-8 text-body-color dark:text-dark-6 lg:mb-11">
                  Through daily reflections, you're not just journaling—you're carefully crafting the memories, lessons, and experiences that will define your digital legacy.
                </p>
                <Link
                  to="/reflections"
                  className="text-base font-medium text-body-color hover:text-primary dark:text-dark-6"
                >
                  Start Your Story
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
                    <path d="M16 26l-6.4-6.4C7.6 17.6 6 15.4 6 12.8c0-2.6 2-4.8 4.6-4.8 1.4 0 2.8.6 3.8 1.6L16 11l1.6-1.4c1-1 2.4-1.6 3.8-1.6 2.6 0 4.6 2.2 4.6 4.8 0 2.6-1.6 4.8-3.6 6.8L16 26z"/>
                  </svg>
                </div>
                <h4 className="mb-3 text-xl font-bold text-black dark:text-white">
                  Moments That Matter
                </h4>
                <p className="mb-8 text-body-color dark:text-dark-6 lg:mb-11">
                  Watch your digital legacy take shape through a beautiful timeline of reflections, insights, and memories—a gift that grows more precious with time.
                </p>
                <Link
                  to="/legacy"
                  className="text-base font-medium text-body-color hover:text-primary dark:text-dark-6"
                >
                  See Your Journey
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
                      <rect x="57" y="50" width="6" height="35" fill="currentColor" opacity="0.8"/>
                      <path d="M60 105C50 105 40 100 30 95C25 93 25 87 30 87C40 87 50 90 60 90C70 90 80 87 90 87C95 87 95 93 90 95C80 100 70 105 60 105Z" opacity="0.4"/>
                      <path d="M60 50C50 35 35 25 25 20C20 18 22 12 27 14C37 19 52 29 60 44C68 29 83 19 93 14C98 12 100 18 95 20C85 25 70 35 60 50Z"/>
                      <circle cx="25" cy="20" r="8" opacity="0.7"/>
                      <circle cx="40" cy="30" r="6" opacity="0.6"/>
                      <circle cx="60" cy="25" r="7" opacity="0.8"/>
                      <circle cx="80" cy="30" r="6" opacity="0.6"/>
                      <circle cx="95" cy="20" r="8" opacity="0.7"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
            <div className="w-full px-4 lg:w-1/2">
              <div className="max-w-[470px]">
                <div className="mb-9">
                  <h3 className="mb-4 text-xl font-bold text-black dark:text-white sm:text-2xl lg:text-xl xl:text-2xl">
                    Create Your Digital Legacy
                  </h3>
                  <p className="text-base font-medium leading-relaxed text-body-color dark:text-dark-6">
                    Transform your daily reflections into a meaningful digital legacy. Your Echo becomes a gift for loved ones—a way to share your wisdom, memories, and perspective long after you're gone.
                  </p>
                </div>
                <div className="mb-1">
                  <h3 className="mb-4 text-xl font-bold text-black dark:text-white sm:text-2xl lg:text-xl xl:text-2xl">
                    Grow Through Daily Reflection
                  </h3>
                  <p className="text-base font-medium leading-relaxed text-body-color dark:text-dark-6">
                    Daily reflection helps you understand patterns, celebrate progress, and make more intentional decisions. While building your legacy, you also gain insights that enrich your present life.
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