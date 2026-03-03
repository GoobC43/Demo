import React from 'react';
import { AlertCircle, ArrowRight, Clock, MapPin, Activity } from 'lucide-react';
import { Disruption } from '../../types';
import { formatDate } from '../../utils/formatters';
import { Link } from 'react-router-dom';

interface ActiveDisruptionsProps {
    disruptions: Disruption[];
}

const severityLabel = (score: number) => {
    if (score >= 0.8) return { text: 'Critical', color: '#991b1b', bg: 'rgba(153,27,27,0.08)' };
    if (score >= 0.7) return { text: 'High', color: '#b45309', bg: 'rgba(196,162,78,0.1)' };
    return { text: 'Moderate', color: '#92400e', bg: 'rgba(146,64,14,0.08)' };
};

const typeLabel = (type: string) => type.replace(/_/g, ' ');

export const ActiveDisruptions: React.FC<ActiveDisruptionsProps> = ({ disruptions }) => {
    if (!disruptions || disruptions.length === 0) {
        return (
            <div className="py-16 text-center">
                <p className="text-4xl font-extralight tracking-tight mb-3" style={{ color: '#15803d' }}>All Clear</p>
                <p className="text-sm" style={{ color: '#8a8a96' }}>Your supply chain is operating normally.</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {disruptions.map((disruption, index) => {
                const severity = severityLabel(disruption.severity_score);
                return (
                    <div
                        key={disruption.id}
                        className="relative transition-all duration-200"
                        style={{
                            borderTop: index === 0 ? '2px solid #c4a24e' : '1px solid rgba(26,26,46,0.08)',
                            paddingTop: index === 0 ? '0' : '24px',
                        }}
                    >
                        {/* Alert header */}
                        <div className="flex items-center justify-between py-4 mb-4" style={{ borderBottom: '1px solid rgba(26,26,46,0.06)' }}>
                            <div className="flex items-center gap-3">
                                <AlertCircle className="h-4 w-4" style={{ color: severity.color }} />
                                <span className="text-sm font-medium capitalize" style={{ color: '#1a1a2e' }}>
                                    {typeLabel(disruption.disruption_type)}
                                </span>
                                <span
                                    className="text-[10px] tracking-widest uppercase font-medium px-2.5 py-0.5 rounded-full"
                                    style={{ background: severity.bg, color: severity.color }}
                                >
                                    {severity.text}
                                </span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Activity className="h-3 w-3" style={{ color: '#c4a24e' }} />
                                <span className="text-[10px] tracking-widest uppercase font-medium" style={{ color: '#b45309' }}>
                                    Action Required
                                </span>
                            </div>
                        </div>

                        {/* Details grid */}
                        <div className="grid grid-cols-2 lg:grid-cols-5 gap-8 mb-6">
                            <div>
                                <div className="flex items-center gap-1.5 text-xs mb-2" style={{ color: '#8a8a96' }}>
                                    <MapPin className="h-3.5 w-3.5" />
                                    <span className="tracking-widest uppercase">Location</span>
                                </div>
                                <div className="text-base font-medium" style={{ color: '#1a1a2e' }}>
                                    Port {disruption.port_id.split('-')[0]}
                                </div>
                            </div>
                            <div>
                                <div className="flex items-center gap-1.5 text-xs mb-2" style={{ color: '#8a8a96' }}>
                                    <AlertCircle className="h-3.5 w-3.5" />
                                    <span className="tracking-widest uppercase">Type</span>
                                </div>
                                <div className="text-base font-medium capitalize" style={{ color: '#1a1a2e' }}>
                                    {typeLabel(disruption.disruption_type)}
                                </div>
                            </div>
                            <div>
                                <div className="flex items-center gap-1.5 text-xs mb-2" style={{ color: '#8a8a96' }}>
                                    <Clock className="h-3.5 w-3.5" />
                                    <span className="tracking-widest uppercase">Delay</span>
                                </div>
                                <div className="text-base font-medium" style={{ color: '#1a1a2e' }}>
                                    {disruption.expected_delay_days} Days
                                </div>
                            </div>
                            <div>
                                <div className="text-xs tracking-widest uppercase mb-2" style={{ color: '#8a8a96' }}>Confidence</div>
                                <div className="text-base font-medium" style={{ color: '#1a1a2e' }}>
                                    {(disruption.confidence_score * 100).toFixed(0)}%
                                </div>
                            </div>
                            <div>
                                <div className="text-xs tracking-widest uppercase mb-2" style={{ color: '#8a8a96' }}>Detected</div>
                                <div className="text-base font-medium" style={{ color: '#1a1a2e' }}>
                                    {formatDate(disruption.detected_at)}
                                </div>
                            </div>
                        </div>

                        {/* CTA */}
                        <div className="flex justify-end pt-4" style={{ borderTop: '1px solid rgba(26,26,46,0.04)' }}>
                            <Link
                                to={`/app/disruption/${disruption.id}`}
                                className="group inline-flex items-center px-5 py-2.5 text-sm font-medium rounded-full transition-all duration-300 hover:scale-105"
                                style={{ background: '#1a1a2e', color: '#f8f7f4' }}
                            >
                                Analyze & Mitigate
                                <ArrowRight className="h-4 w-4 ml-2 transition-transform group-hover:translate-x-1" />
                            </Link>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};
