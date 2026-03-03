import React, { useState, useEffect } from 'react';
import { api } from '../api/endpoints';
import { DashboardSummary } from '../types';
import { MetricCards } from '../components/dashboard/MetricCards';
import { ActiveDisruptions } from '../components/dashboard/ActiveDisruptions';

export const Dashboard: React.FC = () => {
    const [data, setData] = useState<DashboardSummary | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                const res = await api.getDashboard();
                setData(res);
            } catch (err) {
                console.error("Failed to fetch dashboard", err);
            } finally {
                setLoading(false);
            }
        };
        fetchDashboard();
    }, []);

    if (loading) {
        return (
            <div className="py-20">
                <div className="space-y-8 animate-pulse">
                    <div className="h-3 w-64 rounded" style={{ background: 'rgba(26,26,46,0.05)' }}></div>
                    <div className="h-2 w-96 rounded" style={{ background: 'rgba(26,26,46,0.04)' }}></div>
                    <div className="grid grid-cols-4 gap-px rounded-xl overflow-hidden" style={{ background: 'rgba(26,26,46,0.06)' }}>
                        {[0, 1, 2, 3].map(i => <div key={i} className="h-28" style={{ background: '#f8f7f4' }}></div>)}
                    </div>
                </div>
            </div>
        );
    }

    if (!data) return (
        <div className="py-20 text-center">
            <p className="text-lg font-extralight" style={{ color: '#8a8a96' }}>Unable to load dashboard data.</p>
        </div>
    );

    return (
        <div className="space-y-12">
            <div>
                <h1 className="text-3xl font-extralight tracking-tight mb-2" style={{ color: '#1a1a2e' }}>
                    Supply Chain Control Tower
                </h1>
                <p className="text-sm" style={{ color: '#8a8a96' }}>
                    Current risk overview and active alerts.
                </p>
            </div>

            <MetricCards data={data} />

            <div className="space-y-4">
                <h2 className="text-xs tracking-widest uppercase font-medium" style={{ color: '#c4a24e' }}>Active Alerts</h2>
                <ActiveDisruptions disruptions={data.active_disruptions || (data.active_disruption ? [data.active_disruption] : [])} />
            </div>
        </div>
    );
};

export default Dashboard;
