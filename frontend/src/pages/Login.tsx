import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Mail, Lock, Fingerprint, Loader2, QrCode, Smartphone } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { api } from '../api/endpoints';

export default function Login() {
    const { loginStep1, loginStep2, requiresMfa, isLoading, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    React.useEffect(() => {
        if (isAuthenticated) {
            navigate('/app');
        }
    }, [isAuthenticated, navigate]);

    // Step 1 State
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    // Step 2 State
    const [totpCode, setTotpCode] = useState('');

    // MFA Setup State (QR code)
    const [mfaSetupUri, setMfaSetupUri] = useState<string | null>(null);
    const [mfaSecret, setMfaSecret] = useState<string | null>(null);
    const [showSetup, setShowSetup] = useState(false);
    const [isSettingUp, setIsSettingUp] = useState(false);

    // UI State
    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleStep1Submit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsSubmitting(true);
        try {
            await loginStep1(password, email);
        } catch (err: any) {
            setError(err.message || 'Login failed');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleStep2Submit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsSubmitting(true);
        try {
            await loginStep2(totpCode);
            navigate('/app');
        } catch (err: any) {
            setError(err.message || 'Invalid Authenticator Code');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleSetupMfa = async () => {
        setIsSettingUp(true);
        setError(null);
        try {
            const res = await api.auth.setupMfa(email);
            setMfaSetupUri(res.qr_code_uri);
            setMfaSecret(res.secret);
            setShowSetup(true);
        } catch (err: any) {
            setError(err.message || 'Failed to generate MFA setup');
        } finally {
            setIsSettingUp(false);
        }
    };

    if (isLoading) return null;

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-900 font-sans p-4">

            {/* Background Corporate abstract shapes */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-1/2 -left-1/4 w-[1000px] h-[1000px] bg-indigo-900/20 rounded-full blur-[120px]"></div>
                <div className="absolute top-[20%] right-[-10%] w-[600px] h-[600px] bg-blue-900/20 rounded-full blur-[100px]"></div>
            </div>

            <div className="relative z-10 w-full max-w-md bg-slate-800/80 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl overflow-hidden">

                {/* Header Section */}
                <div className="px-8 pt-10 pb-8 text-center border-b border-slate-700/50">
                    <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-xl mx-auto flex items-center justify-center shadow-lg shadow-indigo-500/30 mb-6">
                        <ShieldCheck className="w-8 h-8 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-2">HarborGuard AI</h2>
                    <p className="text-slate-400 text-sm">Enterprise Decision-Support Platform</p>
                </div>

                {/* Body Section */}
                <div className="p-8">
                    {error && (
                        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm text-center">
                            {error}
                        </div>
                    )}

                    {!requiresMfa ? (
                        // STEP 1: CREDENTIALS
                        <form onSubmit={handleStep1Submit} className="space-y-5">
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Corporate Email</label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Mail className="h-5 w-5 text-slate-500" />
                                    </div>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full pl-10 pr-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                                        placeholder="vp@harborguard.ai"
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Lock className="h-5 w-5 text-slate-500" />
                                    </div>
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="w-full pl-10 pr-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                                        placeholder="••••••••"
                                        required
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 focus:ring-offset-slate-900 transition-colors mt-8 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : "Authenticate"}
                            </button>
                        </form>
                    ) : showSetup && mfaSetupUri ? (
                        // MFA SETUP: QR Code Enrollment
                        <div className="space-y-6">
                            <div className="text-center mb-4">
                                <div className="inline-flex items-center justify-center w-12 h-12 bg-indigo-500/10 rounded-full mb-4">
                                    <QrCode className="w-6 h-6 text-indigo-400" />
                                </div>
                                <h3 className="text-lg font-medium text-white mb-2">Setup Authenticator App</h3>
                                <p className="text-sm text-slate-400">
                                    Scan this QR code with <span className="text-slate-200 font-medium">Google Authenticator</span> or <span className="text-slate-200 font-medium">Microsoft Authenticator</span> to link your account.
                                </p>
                            </div>

                            {/* QR Code */}
                            <div className="flex justify-center">
                                <div className="bg-white p-4 rounded-xl shadow-lg">
                                    <QRCodeSVG
                                        value={mfaSetupUri}
                                        size={200}
                                        bgColor="#ffffff"
                                        fgColor="#1e293b"
                                        level="M"
                                    />
                                </div>
                            </div>

                            {/* Manual key fallback */}
                            {mfaSecret && (
                                <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                                    <p className="text-xs text-slate-500 mb-2">Can't scan? Enter this key manually:</p>
                                    <p className="text-sm font-mono text-indigo-300 tracking-wider break-all select-all">{mfaSecret}</p>
                                </div>
                            )}

                            <div className="flex items-start space-x-3 p-3 bg-indigo-500/5 border border-indigo-500/10 rounded-lg">
                                <Smartphone className="w-5 h-5 text-indigo-400 flex-shrink-0 mt-0.5" />
                                <p className="text-xs text-slate-400 leading-relaxed">
                                    After scanning, your authenticator app will show a 6-digit code that refreshes every 30 seconds. Enter it below to verify your setup.
                                </p>
                            </div>

                            {/* TOTP code entry after scanning */}
                            <form onSubmit={handleStep2Submit} className="space-y-4">
                                <input
                                    type="text"
                                    value={totpCode}
                                    onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').substring(0, 6))}
                                    className="w-full px-4 py-4 text-center tracking-[0.5em] text-2xl font-mono bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all placeholder-slate-600"
                                    placeholder="000000"
                                    required
                                    autoFocus
                                />

                                <button
                                    type="submit"
                                    disabled={isSubmitting || totpCode.length !== 6}
                                    className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 focus:ring-offset-slate-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : "Verify & Complete Setup"}
                                </button>
                            </form>

                            <div className="text-center">
                                <button type="button" onClick={() => window.location.reload()} className="text-xs text-slate-500 hover:text-slate-300 transition-colors">
                                    Cancel & Return to Login
                                </button>
                            </div>
                        </div>
                    ) : (
                        // STEP 2: MFA TOTP (for already-enrolled users, or first-time with setup option)
                        <div className="space-y-6">
                            <div className="text-center mb-6">
                                <div className="inline-flex items-center justify-center w-12 h-12 bg-indigo-500/10 rounded-full mb-4">
                                    <Fingerprint className="w-6 h-6 text-indigo-400" />
                                </div>
                                <h3 className="text-lg font-medium text-white mb-2">Multi-Factor Authentication</h3>
                                <p className="text-sm text-slate-400">
                                    Enter the 6-digit code from your authenticator app for <span className="text-slate-200 font-medium">{email}</span>.
                                </p>
                            </div>

                            <form onSubmit={handleStep2Submit} className="space-y-4">
                                <div>
                                    <input
                                        type="text"
                                        value={totpCode}
                                        onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').substring(0, 6))}
                                        className="w-full px-4 py-4 text-center tracking-[0.5em] text-2xl font-mono bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all placeholder-slate-600"
                                        placeholder="000000"
                                        required
                                        autoFocus
                                    />
                                </div>

                                <button
                                    type="submit"
                                    disabled={isSubmitting || totpCode.length !== 6}
                                    className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 focus:ring-offset-slate-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : "Verify & Login"}
                                </button>
                            </form>

                            {/* Setup MFA link for first-time users */}
                            <div className="text-center border-t border-slate-700/50 pt-5 space-y-3">
                                <button
                                    type="button"
                                    onClick={handleSetupMfa}
                                    disabled={isSettingUp}
                                    className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors flex items-center justify-center mx-auto font-medium"
                                >
                                    {isSettingUp ? (
                                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                                    ) : (
                                        <QrCode className="w-4 h-4 mr-2" />
                                    )}
                                    Setup Authenticator App (QR Code)
                                </button>
                                <button type="button" onClick={() => window.location.reload()} className="text-xs text-slate-500 hover:text-slate-300 transition-colors block mx-auto">
                                    Cancel & Return to Login
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-8 py-4 bg-slate-900/50 border-t border-slate-700/50 text-center">
                    <p className="text-xs text-slate-500">
                        Protected by HarborGuard AI Enterprise Security.
                    </p>
                </div>
            </div>
        </div>
    );
}
