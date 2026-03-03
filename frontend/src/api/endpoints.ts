import apiClient from './client';
import {
    DashboardSummary,
    Disruption,
    ExposureResult,
    StrategyComparison,
    Recommendation
} from '../types';

export const api = {
    // Auth
    auth: {
        login: async (credentials: URLSearchParams) => {
            const res: any = await apiClient.post('/auth/token', credentials, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            return res;
        },
        verifyMfa: async (email: string, totp_code: string) => {
            const res: any = await apiClient.post('/auth/mfa/verify', { email, totp_code });
            return res;
        },
        setupMfa: async (email: string) => {
            const res: any = await apiClient.post(`/auth/mfa/setup?email=${encodeURIComponent(email)}`);
            return res;
        }
    },

    seedData: () => apiClient.post('/seed-data'),

    getDashboard: (): Promise<DashboardSummary> => apiClient.get('/dashboard'),

    createDisruption: (data: any): Promise<Disruption> => apiClient.post('/disruptions', data),
    getDisruption: (id: string): Promise<Disruption> => apiClient.get(`/disruptions/${id}`),

    getPorts: (): Promise<any[]> => apiClient.get('/disruptions/ports'),

    getExposure: (id: string): Promise<ExposureResult> => apiClient.get(`/disruptions/${id}/exposure`),

    getStrategies: (id: string): Promise<StrategyComparison> => apiClient.get(`/disruptions/${id}/strategies`),

    getRecommendation: (id: string): Promise<Recommendation> => apiClient.get(`/disruptions/${id}/recommendation`),
    approveRecommendation: (recId: string, approver_name: string, notes?: string): Promise<Recommendation> =>
        apiClient.post(`/recommendations/${recId}/approve`, { approver_name, notes }),

    // Monte Carlo simulation
    getSimulation: (id: string, scenarios?: number): Promise<any> =>
        apiClient.get(`/disruptions/${id}/simulation${scenarios ? `?scenarios=${scenarios}` : ''}`),

    // Sensitivity (tornado) analysis
    getSensitivity: (id: string): Promise<any> =>
        apiClient.get(`/disruptions/${id}/sensitivity`),

    // Perception — detect disruption from news text
    detectFromNews: (headline: string, body?: string): Promise<any> =>
        apiClient.post('/disruptions/detect', { headline, body: body || '' }),

    // ML Feedback — record outcome
    recordOutcome: (recId: string, data: any): Promise<any> =>
        apiClient.post(`/outcomes/${recId}`, data),

    // ML Feedback — get history
    getOutcomeHistory: (limit?: number): Promise<any> =>
        apiClient.get(`/outcomes/history${limit ? `?limit=${limit}` : ''}`),

    // Strategy confidence
    getStrategyConfidence: (strategyId: string, disruptionType?: string): Promise<any> =>
        apiClient.get(`/strategies/${strategyId}/confidence${disruptionType ? `?disruption_type=${disruptionType}` : ''}`),
};

