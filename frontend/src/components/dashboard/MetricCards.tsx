import React from 'react';
import { AlertTriangle, TrendingDown, Package, Ship, Settings } from 'lucide-react';
import { DashboardSummary } from '../../types';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

interface MetricCardsProps {
    data: DashboardSummary;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ data }) => {
    const { company, active_disruption, total_revenue_at_risk, key_metrics } = data;

    const metrics = [
        {
            label: 'Revenue at Risk',
            value: active_disruption ? formatCurrency(total_revenue_at_risk) : '$0',
            status: active_disruption ? 'Critical Action Required' : 'Operations Normal',
            statusColor: active_disruption ? '#b45309' : '#15803d',
            accent: active_disruption ? '#c4a24e' : '#15803d',
        },
        {
            label: 'Affected SKUs',
            value: key_metrics.affected_skus,
            status: 'High-priority items delayed',
            accent: '#c4a24e',
        },
        {
            label: 'Impacted Shipments',
            value: key_metrics.affected_shipments,
            status: 'In-transit containers',
            accent: '#c4a24e',
        },
        {
            label: 'SLA Target',
            value: formatPercentage(company.sla_target_percent),
            status: `Penalty Weight: ${formatPercentage(company.sla_weight)}`,
            accent: '#8a8a96',
        },
    ];

    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-px" style={{ background: 'rgba(26,26,46,0.06)', borderRadius: '12px', overflow: 'hidden' }}>
            {metrics.map((m, i) => (
                <div key={i} className="p-6" style={{ background: '#f8f7f4' }}>
                    <p className="text-xs tracking-widest uppercase mb-3" style={{ color: '#8a8a96' }}>{m.label}</p>
                    <p className="text-3xl font-extralight tracking-tight mb-4" style={{ color: '#1a1a2e' }}>{m.value}</p>
                    <p className="text-xs" style={{ color: m.statusColor || '#8a8a96' }}>
                        {active_disruption && i === 0 && <AlertTriangle className="h-3 w-3 inline mr-1" />}
                        {m.status}
                    </p>
                </div>
            ))}
        </div>
    );
};
