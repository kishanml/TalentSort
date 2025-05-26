import React from 'react';
import { motion } from 'framer-motion';

const Hero = () => {
    const fadeInLeft = {
        hidden: { x: '-50%', opacity: 0 },
        show: {
            x: 0,
            opacity: 1,
            transition: { duration: 0.8, ease: 'easeOut' },
        },
    };

    const fadeInRight = {
        hidden: { x: '50%', opacity: 0 },
        show: {
            x: 0,
            opacity: 1,
            transition: { duration: 0.8, ease: 'easeOut' },
        },
    };

    return (
        <section
            className="relative z-10 overflow-hidden py-20 md:pt-40 md:pb-28"
            id="main-banner"
            style={{
                background: 'linear-gradient(135deg, #e0f2fe, #dbeafe, #bae6fd)',
            }}
        >
            <div className="container mx-auto px-4 lg:max-w-7xl">
                <div className="grid grid-cols-12 items-center gap-10">
                    {/* Left Content */}
                    <motion.div
                        className="col-span-12 md:col-span-6"
                        initial="hidden"
                        animate="show"
                        variants={fadeInLeft}
                    >

                        <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-blue-900 md:text-6xl leading-tight">
                            Find Your A-Players <br className="hidden md:block" />
                            Instantly.
                        </h1>

                        <p className="mt-6 text-lg text-gray-700 max-w-xl leading-relaxed">
                            Cutting through the noise to find you the perfect candidates—faster, smarter, and more effortlessly.
                        </p>

                        {/* Motion-enhanced CTA */}
                        <motion.div
                            whileHover={{
                                scale: 1.05,
                                boxShadow: '0px 0px 20px rgba(59, 130, 246, 0.5)',
                            }}
                            whileTap={{ scale: 0.97 }}
                            className="inline-block mt-8 rounded-full bg-blue-700 px-10 py-4 text-lg font-semibold text-white transition-all duration-300 cursor-pointer"
                        >
                            Get Started
                        </motion.div>
                    </motion.div>

                    {/* Right Image */}
                    <motion.div
                        className="col-span-12 md:col-span-6"
                        initial="hidden"
                        animate="show"
                        variants={fadeInRight}
                    >
                        <img
                            src="/assets/banner-image.png"
                            alt="AI-powered talent search illustration"
                            className="w-full drop-shadow-xl"
                        />
                    </motion.div>
                </div>
            </div>
        </section>
    );
};

export default Hero;
