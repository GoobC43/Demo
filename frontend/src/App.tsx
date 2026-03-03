import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { api } from './api/endpoints';
import { DashboardSummary } from './types';
import { AppLayout } from './components/layout/AppLayout';

import Dashboard from './pages/Dashboard';
import DisruptionDetail from './pages/DisruptionDetail';
import Login from './pages/Login';
import LandingPage from './pages/LandingPage';
import { AuthProvider, useAuth } from './context/AuthContext';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) return null;

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }
    return <>{children}</>;
}

function MainApp() {
    const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const initializeApp = async () => {
            try {
                setIsLoading(true);
                // Attempt to load dashboard data. If missing, seed it.
                try {
                    const data = await api.getDashboard();
                    setDashboardData(data);
                } catch (e: any) {
                    if (e.response && e.response.status === 404) {
                        console.log("No data found, seeding demo data...");
                        await api.seedData();
                        const data = await api.getDashboard();
                        setDashboardData(data);
                    } else {
                        throw e;
                    }
                }
            } catch (err: any) {
                setError(err.message || 'Failed to initialize app');
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };

        initializeApp();
    }, []);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
                <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full border border-red-100">
                    <h2 className="text-xl font-bold text-red-600 mb-4">Initialization Error</h2>
                    <p className="text-slate-600 mb-6">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/app" element={
                <ProtectedRoute>
                    <AppLayout company={dashboardData?.company}>
                        <Dashboard />
                    </AppLayout>
                </ProtectedRoute>
            } />
            <Route path="/app/disruption/:id" element={
                <ProtectedRoute>
                    <AppLayout company={dashboardData?.company}>
                        <DisruptionDetail />
                    </AppLayout>
                </ProtectedRoute>
            } />
            <Route path="/login" element={<Login />} />
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}

export default function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <MainApp />
            </AuthProvider>
        </BrowserRouter>
    );
}
