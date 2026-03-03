import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ChevronDown } from 'lucide-react';
import { SupplyChainGlobe } from '../components/SupplyChainGlobe';
import { useScrollReveal, useParallax } from '../hooks/useScrollAnimations';

/* ——————————————————————————————————————————————
   DESIGN PHILOSOPHY
   ——————————————————————————————————————————————
   Anti-patterns avoided:
   - No card grids with identical rounded boxes
   - No gradient backgrounds on containers
   - No fake compliance badges (SOC2/ISO/AES)
   - No generic indigo/slate Tailwind palette
   - No hard section borders

   Instead:
   - Typography as the primary visual device
   - Asymmetric layouts with intentional whitespace
   - Warm charcoal base (#0c0c12) + cream text + amber accent
   - Scroll-triggered reveals and animated counters
   - Flowing page with no visible section breaks
   - Oversized numbers, editorial-style typesetting
   ——————————————————————————————————————————————*/

function RevealBlock({ children, className = '', delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
    const { ref, isVisible } = useScrollReveal(0.12);
    return (
        <div
            ref={ref}
            className={className}
            style={{
                opacity: isVisible ? 1 : 0,
                transform: isVisible ? 'translateY(0px)' : 'translateY(40px)',
                transition: `opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1) ${delay}s, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1) ${delay}s`,
            }}
        >
            {children}
        </div>
    );
}



export default function LandingPage() {
    const { ref: parallaxRef, offset } = useParallax(0.4);
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

    // Subtle mouse-follow effect for hero
    useEffect(() => {
        const handler = (e: MouseEvent) => {
            setMousePos({
                x: (e.clientX / window.innerWidth - 0.5) * 20,
                y: (e.clientY / window.innerHeight - 0.5) * 20,
            });
        };
        window.addEventListener('mousemove', handler);
        return () => window.removeEventListener('mousemove', handler);
    }, []);

    return (
        <div className="font-sans" style={{ background: '#0c0c12', color: '#e4e0d8' }}>

            {/* ———— NAVIGATION ———— */}
            <nav className="fixed top-0 w-full z-50" style={{ background: 'rgba(12, 12, 18, 0.85)', backdropFilter: 'blur(20px)' }}>
                <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
                    <div className="flex justify-between items-center h-16">
                        <Link to="/" className="text-lg font-semibold tracking-tight" style={{ color: '#e4e0d8' }}>
                            HarborGuard<span style={{ color: '#e8c872' }}>.</span>
                        </Link>
                        <div className="hidden md:flex items-center space-x-10">
                            <a href="#process" className="text-xs tracking-widest uppercase hover:opacity-100 transition-opacity" style={{ color: '#6b6b78' }}>Process</a>
                            <a href="#impact" className="text-xs tracking-widest uppercase hover:opacity-100 transition-opacity" style={{ color: '#6b6b78' }}>Impact</a>
                            <a href="#intelligence" className="text-xs tracking-widest uppercase hover:opacity-100 transition-opacity" style={{ color: '#6b6b78' }}>Intelligence</a>
                        </div>
                        <div className="flex items-center space-x-6">
                            <Link to="/login" className="text-xs tracking-widest uppercase" style={{ color: '#6b6b78' }}>Login</Link>
                            <Link
                                to="/login"
                                className="px-5 py-2 text-xs tracking-widest uppercase font-medium rounded-full transition-all duration-300 hover:scale-105"
                                style={{ background: '#e8c872', color: '#0c0c12' }}
                            >
                                Get Access
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* ———— HERO ———— */}
            <section className="relative min-h-screen flex items-center overflow-hidden">
                {/* Ambient light — single warm glow, NOT a gradient */}
                <div
                    className="absolute pointer-events-none"
                    style={{
                        width: '800px', height: '800px',
                        background: 'radial-gradient(circle, rgba(232, 200, 114, 0.04) 0%, transparent 70%)',
                        top: '10%', left: '50%', transform: `translate(-50%, 0) translate(${mousePos.x}px, ${mousePos.y}px)`,
                        transition: 'transform 0.3s ease-out',
                    }}
                />

                <div className="max-w-[1400px] mx-auto px-6 lg:px-12 w-full pt-24">
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
                        {/* Left side — Typography-driven */}
                        <div className="lg:col-span-6 xl:col-span-5">
                            <p className="text-xs tracking-[0.3em] uppercase mb-8" style={{ color: '#e8c872' }}>
                                Supply Chain Intelligence
                            </p>
                            <h1 className="text-[clamp(2.5rem,5vw,4.5rem)] font-extralight leading-[1.05] tracking-tight mb-8">
                                The company that reacts first
                                <span className="italic" style={{ color: '#e8c872' }}> wins.</span>
                            </h1>
                            <p className="text-lg leading-relaxed max-w-lg mb-12" style={{ color: '#8a8a96' }}>
                                HarborGuard gives mid-market electronics manufacturers autonomous risk detection, financial exposure mapping, and mathematically optimal mitigation strategies — before disruptions reach your P&L.
                            </p>
                            <div className="flex items-center space-x-6">
                                <Link
                                    to="/login"
                                    className="group inline-flex items-center px-8 py-4 text-sm font-medium rounded-full transition-all duration-300 hover:scale-105 hover:shadow-lg"
                                    style={{ background: '#e8c872', color: '#0c0c12' }}
                                >
                                    Enter Platform
                                    <ArrowRight className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" />
                                </Link>
                                <a href="#process" className="text-sm transition-colors" style={{ color: '#6b6b78' }}>
                                    Learn more ↓
                                </a>
                            </div>
                        </div>

                        {/* Right side — Globe */}
                        <div
                            className="lg:col-span-6 xl:col-span-7 hidden lg:flex justify-center items-center"
                            style={{ transform: `translate(${mousePos.x * 0.3}px, ${mousePos.y * 0.3}px)`, transition: 'transform 0.4s ease-out' }}
                        >
                            <SupplyChainGlobe
                                size={560}
                                dotColor="rgba(228, 224, 216, ALPHA)"
                                arcColor="rgba(232, 200, 114, 0.35)"
                                markerColor="rgba(232, 200, 114, 0.9)"
                            />
                        </div>
                    </div>
                </div>

                {/* Scroll indicator */}
                <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
                    <ChevronDown className="w-5 h-5" style={{ color: '#3a3a44' }} />
                </div>
            </section>


            {/* ———— THE PROBLEM — editorial asymmetric layout ———— */}
            <div ref={parallaxRef} className="max-w-[1400px] mx-auto px-6 lg:px-12 py-20">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
                    <RevealBlock className="lg:col-span-5">
                        <p className="text-xs tracking-[0.3em] uppercase mb-6" style={{ color: '#e8c872' }}>The Problem</p>
                        <h2 className="text-[clamp(2rem,4vw,3.5rem)] font-extralight leading-[1.1] tracking-tight">
                            Mid-market manufacturers lose <span style={{ color: '#e8c872' }}>$2.8M per incident</span> reacting to disruptions they should have predicted.
                        </h2>
                    </RevealBlock>

                    <div className="lg:col-span-6 lg:col-start-7 space-y-10" style={{ transform: `translateY(${offset}px)` }}>
                        <RevealBlock delay={0.1}>
                            <div className="flex items-start space-x-5">
                                <span className="text-3xl font-extralight flex-shrink-0" style={{ color: '#e8c872' }}>01</span>
                                <div>
                                    <h3 className="text-lg font-medium mb-2">72-hour blind spot</h3>
                                    <p style={{ color: '#6b6b78' }}>By the time your procurement team detects a port strike through manual monitoring, competitors have already secured alternate capacity.</p>
                                </div>
                            </div>
                        </RevealBlock>

                        <RevealBlock delay={0.2}>
                            <div className="flex items-start space-x-5">
                                <span className="text-3xl font-extralight flex-shrink-0" style={{ color: '#e8c872' }}>02</span>
                                <div>
                                    <h3 className="text-lg font-medium mb-2">Spreadsheet analysis paralysis</h3>
                                    <p style={{ color: '#6b6b78' }}>Your VP evaluates 4 strategies across 200 SKUs with no mathematical framework to optimize the tradeoff between expediting cost and SLA risk.</p>
                                </div>
                            </div>
                        </RevealBlock>

                        <RevealBlock delay={0.3}>
                            <div className="flex items-start space-x-5">
                                <span className="text-3xl font-extralight flex-shrink-0" style={{ color: '#e8c872' }}>03</span>
                                <div>
                                    <h3 className="text-lg font-medium mb-2">No enterprise tooling</h3>
                                    <p style={{ color: '#6b6b78' }}>Fortune 500 companies spend $2M+ on SAP IBP and Oracle SCM. You deserve the same algorithmic power without the enterprise price tag.</p>
                                </div>
                            </div>
                        </RevealBlock>
                    </div>
                </div>
            </div>


            {/* ———— PROCESS — large typographic step counter ———— */}
            <div id="process" className="py-32">
                <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
                    <RevealBlock className="mb-24">
                        <p className="text-xs tracking-[0.3em] uppercase mb-6" style={{ color: '#e8c872' }}>Process</p>
                        <h2 className="text-[clamp(2rem,4vw,3.5rem)] font-extralight leading-[1.1] tracking-tight max-w-3xl">
                            From disruption to resolution. Autonomously.
                        </h2>
                    </RevealBlock>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-20 gap-y-24">
                        {[
                            { step: 'Detect', desc: 'An NLP model identifies a labor strike at the Port of Los Angeles from breaking trade news. Your team is alerted within 90 seconds — 72 hours before manual processes would catch it.' },
                            { step: 'Quantify', desc: 'The Exposure Engine maps every affected SKU, shipment, and PO. Your dashboard shows $4.2M in margin at risk across 47 SKUs with per-item financial detail.' },
                            { step: 'Optimize', desc: 'MILP and TOPSIS rank 4 mitigation strategies. Monte Carlo simulates 500 scenarios. The optimal strategy costs $180K to protect $3.9M in margin — a 21x return.' },
                            { step: 'Execute', desc: 'Gemini drafts supplier communications and executive briefs. Your VP reviews, approves with MFA, and executes — all within the platform, fully audit-logged.' },
                        ].map((item, i) => (
                            <RevealBlock key={i} delay={0.1 * i}>
                                <div className="group">
                                    <span
                                        className="block text-[8rem] md:text-[10rem] font-extralight leading-none tracking-tighter transition-colors duration-500 group-hover:text-current"
                                        style={{ color: '#1a1a22' }}
                                    >
                                        {String(i + 1).padStart(2, '0')}
                                    </span>
                                    <div className="mt-[-2rem] relative z-10">
                                        <h3 className="text-2xl font-medium mb-4">{item.step}</h3>
                                        <p className="max-w-md leading-relaxed" style={{ color: '#6b6b78' }}>{item.desc}</p>
                                    </div>
                                </div>
                            </RevealBlock>
                        ))}
                    </div>
                </div>
            </div>

            {/* ———— IMPACT / ICP ———— */}
            <div id="impact" className="py-32 max-w-[1400px] mx-auto px-6 lg:px-12">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-start">
                    <RevealBlock className="lg:col-span-5">
                        <p className="text-xs tracking-[0.3em] uppercase mb-6" style={{ color: '#e8c872' }}>Built for You</p>
                        <h2 className="text-[clamp(2rem,4vw,3.5rem)] font-extralight leading-[1.1] tracking-tight mb-8">
                            Purpose-built for mid-market electronics manufacturing.
                        </h2>
                        <p className="text-lg leading-relaxed mb-10" style={{ color: '#6b6b78' }}>
                            HarborGuard is designed for manufacturers between $50M–$500M in revenue who source PCBs, semiconductors, passive components, and connectors from Asia-Pacific suppliers.
                        </p>
                        <Link
                            to="/login"
                            className="group inline-flex items-center px-8 py-4 text-sm font-medium rounded-full transition-all duration-300 hover:scale-105"
                            style={{ background: '#e8c872', color: '#0c0c12' }}
                        >
                            Request Access
                            <ArrowRight className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" />
                        </Link>
                    </RevealBlock>

                    <div className="lg:col-span-6 lg:col-start-7 space-y-6">
                        {[
                            'Contract Electronics Manufacturers (CEMs)',
                            'PCB Assembly & SMT Facilities',
                            'Semiconductor Component Distributors',
                            'Defense Electronics Subcontractors',
                            'Medical Device OEMs',
                            'Automotive Electronics Tier-2 Suppliers',
                        ].map((item, i) => (
                            <RevealBlock key={i} delay={0.05 * i}>
                                <div
                                    className="flex items-center justify-between py-5 group cursor-default"
                                    style={{ borderBottom: '1px solid rgba(232,200,114,0.08)' }}
                                >
                                    <span className="text-lg group-hover:translate-x-2 transition-transform duration-300">{item}</span>
                                    <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-40 transition-all duration-300" style={{ color: '#e8c872' }} />
                                </div>
                            </RevealBlock>
                        ))}
                    </div>
                </div>
            </div>

            {/* ———— INTELLIGENCE PLATFORM — flowing text, not cards ———— */}
            <div id="intelligence" className="py-32 max-w-[1400px] mx-auto px-6 lg:px-12">
                <RevealBlock className="max-w-3xl mb-24">
                    <p className="text-xs tracking-[0.3em] uppercase mb-6" style={{ color: '#e8c872' }}>Intelligence Platform</p>
                    <h2 className="text-[clamp(2rem,4vw,3.5rem)] font-extralight leading-[1.1] tracking-tight mb-8">
                        Six engines. One autonomous system.
                    </h2>
                    <p className="text-lg leading-relaxed" style={{ color: '#6b6b78' }}>
                        Every component of HarborGuard was purpose-built for electronics manufacturing supply chains — from semiconductor lead time modeling to APAC port congestion patterns.
                    </p>
                </RevealBlock>

                {/* Staggered feature reveals — NOT a grid of cards */}
                <div className="space-y-20">
                    {[
                        {
                            num: '01', name: 'Real-Time Risk Detection',
                            detail: 'NLP-powered monitoring of 10,000+ global trade signals. Classifies port strikes, weather events, semiconductor shortages, and geopolitical risks within 90 seconds of first report.',
                        },
                        {
                            num: '02', name: 'Financial Exposure Mapping',
                            detail: 'SKU-level revenue-at-risk using criticality-weighted Newsvendor models. Quantifies exactly which purchase orders are in danger and calculates your margin exposure down to the cent.',
                        },
                        {
                            num: '03', name: 'Monte Carlo Risk Engine',
                            detail: 'PERT-distributed Latin Hypercube Sampling across 500+ concurrent scenarios. VaR and CVaR tail-risk metrics give you confidence-interval backed worst-case exposure figures.',
                        },
                        {
                            num: '04', name: 'MILP Strategy Optimizer',
                            detail: 'Mixed-Integer Linear Programming calculates the budget-optimal mix of expedited shipping, dual-sourcing, and safety stock across every affected SKU simultaneously.',
                        },
                        {
                            num: '05', name: 'Adaptive GenAI Execution',
                            detail: 'Gemini Pro drafts targeted supplier communications and executive briefings calibrated to the selected strategy. Thompson Sampling ensures recommendations sharpen over time.',
                        },
                        {
                            num: '06', name: 'Autonomous Approval Workflow',
                            detail: 'Human-in-the-loop governance with Role-Based Access Control. Multi-Factor Authentication, immutable audit logging, and VP-level approval gates for every financial decision.',
                        },
                    ].map((feat, i) => (
                        <RevealBlock key={i} delay={0.05 * i}>
                            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-baseline group cursor-default">
                                <span className="lg:col-span-1 text-sm font-mono" style={{ color: '#3a3a44' }}>{feat.num}</span>
                                <h3 className="lg:col-span-4 text-2xl md:text-3xl font-extralight tracking-tight group-hover:opacity-100 transition-opacity" style={{ color: '#e8c872' }}>
                                    {feat.name}
                                </h3>
                                <p className="lg:col-span-7 text-base leading-relaxed" style={{ color: '#6b6b78' }}>
                                    {feat.detail}
                                </p>
                                {/* Subtle divider line */}
                                <div className="lg:col-span-12 mt-10 h-px" style={{ background: 'linear-gradient(to right, rgba(232,200,114,0.1), transparent)' }} />
                            </div>
                        </RevealBlock>
                    ))}
                </div>
            </div>

            {/* ———— SECURITY — honest, no fake badges ———— */}
            <div className="py-32 max-w-[1400px] mx-auto px-6 lg:px-12">
                <RevealBlock className="max-w-3xl">
                    <p className="text-xs tracking-[0.3em] uppercase mb-6" style={{ color: '#e8c872' }}>Security</p>
                    <h2 className="text-[clamp(2rem,4vw,3.5rem)] font-extralight leading-[1.1] tracking-tight mb-8">
                        Your BOM data is a trade secret. We treat it like one.
                    </h2>
                    <p className="text-lg leading-relaxed mb-12" style={{ color: '#6b6b78' }}>
                        HarborGuard enforces mandatory Multi-Factor Authentication via Google or Microsoft Authenticator, Role-Based Access Control so only VP-level users can approve financial workflows, and immutable audit logging for every action taken in the platform.
                    </p>
                    <div className="flex flex-wrap gap-4">
                        {['MFA Required', 'RBAC Enforced', 'Immutable Audit Logs', 'Rate-Limited APIs', 'Encrypted Storage'].map((tag, i) => (
                            <span
                                key={i}
                                className="px-4 py-2 text-xs tracking-widest uppercase rounded-full"
                                style={{ border: '1px solid rgba(232,200,114,0.15)', color: '#6b6b78' }}
                            >
                                {tag}
                            </span>
                        ))}
                    </div>
                </RevealBlock>
            </div>

            {/* ———— FINAL CTA ———— */}
            <div className="py-40 text-center max-w-[1400px] mx-auto px-6 lg:px-12">
                <RevealBlock>
                    <h2 className="text-[clamp(2.5rem,5vw,5rem)] font-extralight leading-[1.05] tracking-tight mb-10 max-w-4xl mx-auto">
                        Stop reacting. Start <span className="italic" style={{ color: '#e8c872' }}>predicting.</span>
                    </h2>
                    <Link
                        to="/login"
                        className="group inline-flex items-center px-10 py-5 text-base font-medium rounded-full transition-all duration-300 hover:scale-105 hover:shadow-xl"
                        style={{ background: '#e8c872', color: '#0c0c12' }}
                    >
                        Enter HarborGuard
                        <ArrowRight className="ml-3 w-5 h-5 transition-transform group-hover:translate-x-1" />
                    </Link>
                </RevealBlock>
            </div>

            {/* ———— FOOTER — minimal ———— */}
            <footer className="py-12 max-w-[1400px] mx-auto px-6 lg:px-12">
                <div className="h-px mb-12" style={{ background: 'rgba(232,200,114,0.06)' }} />
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center space-y-6 md:space-y-0">
                    <span className="text-sm font-medium">
                        HarborGuard<span style={{ color: '#e8c872' }}>.</span>
                    </span>
                    <div className="flex items-center space-x-8">
                        <a href="mailto:sales@harborguard.ai" className="text-xs tracking-widest uppercase transition-opacity hover:opacity-100" style={{ color: '#3a3a44' }}>Contact</a>
                        <span className="text-xs" style={{ color: '#3a3a44' }}>&copy; 2026</span>
                    </div>
                </div>
            </footer>
        </div>
    );
}
