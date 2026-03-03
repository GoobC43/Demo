import React, { Component, ErrorInfo, ReactNode } from 'react';
import { ShieldAlert, RefreshCw } from 'lucide-react';

interface Props {
    children?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class GlobalErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null
    };

    public static getDerivedStateFromError(error: Error): State {
        // Update state so the next render will show the fallback UI.
        return { hasError: true, error, errorInfo: null };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
        this.setState({ errorInfo });
        // In production, we'd send to Sentry/Datadog here.
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 font-sans">
                    <div className="bg-slate-800 border border-slate-700/50 rounded-2xl p-8 max-w-lg w-full shadow-2xl">
                        <div className="w-16 h-16 bg-red-500/10 rounded-xl flex items-center justify-center mb-6 mx-auto border border-red-500/20">
                            <ShieldAlert className="w-8 h-8 text-red-500" />
                        </div>
                        <h1 className="text-2xl font-bold text-white text-center mb-2">Service Interruption</h1>
                        <p className="text-slate-400 text-center text-sm mb-6 leading-relaxed">
                            HarborGuard AI encountered an unexpected client-side error. Our engineering team has been notified.
                            Please reload your dashboard or contact VP Technical Support.
                        </p>

                        <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50 font-mono text-xs text-slate-300 overflow-x-auto mb-8 max-h-[200px] overflow-y-auto">
                            <span className="text-red-400 font-bold block mb-2">{this.state.error?.toString()}</span>
                            {this.state.errorInfo?.componentStack}
                        </div>

                        <button
                            onClick={() => window.location.href = '/'}
                            className="w-full flex justify-center items-center py-3 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition-colors shadow-sm"
                        >
                            <RefreshCw className="w-5 h-5 mr-2" />
                            Reload Application
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
