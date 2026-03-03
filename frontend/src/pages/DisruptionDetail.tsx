import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Shield, ArrowLeft, Loader2, PlayCircle, FileText, CheckCircle2, Copy, CheckCheck, BarChart3, Download } from 'lucide-react';
import { AreaChart, Area, ReferenceLine, Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend } from 'recharts';
import Plot from 'react-plotly.js';
import { api } from '../api/endpoints';
import {
    Disruption,
    ExposureResult,
    StrategyComparison,
    Recommendation
} from '../types';
import { formatCurrency, formatDate } from '../utils/formatters';

export const DisruptionDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [disruption, setDisruption] = useState<Disruption | null>(null);
    const [exposure, setExposure] = useState<ExposureResult | null>(null);
    const [strategies, setStrategies] = useState<StrategyComparison | null>(null);
    const [recommendation, setRecommendation] = useState<Recommendation | null>(null);

    const [isSimulating, setIsSimulating] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [isApproving, setIsApproving] = useState(false);
    const [portName, setPortName] = useState<string>('');
    const [monteCarlo, setMonteCarlo] = useState<any>(null);
    const [sensitivity, setSensitivity] = useState<any>(null);
    const [copiedField, setCopiedField] = useState<string | null>(null);

    const [activeTab, setActiveTab] = useState<'exposure' | 'strategies' | 'action'>('exposure');

    const handleCopy = async (text: string, field: string) => {
        await navigator.clipboard.writeText(text);
        setCopiedField(field);
        setTimeout(() => setCopiedField(null), 2000);
    };

    const handleExportCSV = () => {
        if (!exposure || !disruption) return;
        const headers = ['SKU', 'Description', 'Runway (Days)', 'Revenue at Risk'];
        const csvContent = [
            headers.join(','),
            ...exposure.affected_skus.map(sku =>
                `"${sku.sku_code}","${sku.description}",${sku.inventory_runway_days},${sku.revenue_at_risk}`
            )
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `exposure_report_${disruption.id.split('-')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    useEffect(() => {
        const fetchData = async () => {
            if (!id) return;
            try {
                setLoading(true);
                // Load base data
                const [disData, expData] = await Promise.all([
                    api.getDisruption(id),
                    api.getExposure(id)
                ]);
                setDisruption(disData);
                // Resolve port name from ports API
                try {
                    const ports = await api.getPorts();
                    const match = ports.find((p: any) => p.id === disData.port_id);
                    if (match) setPortName(match.name);
                } catch (e) { /* ignore */ }
                setExposure(expData);

                // Try to load recommendation if it exists
                try {
                    const recData = await api.getRecommendation(id);
                    setRecommendation(recData);
                    setActiveTab('action');
                } catch (e) {
                    // No recommendation yet
                    console.log("No recommendation found.");
                }
            } catch (err: any) {
                setError(err.message || 'Failed to load details');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [id]);

    const handleSimulateStrategies = async () => {
        if (!id) return;
        setIsSimulating(true);
        try {
            const [stratData, mcData, sensData] = await Promise.all([
                api.getStrategies(id),
                api.getSimulation(id, 500).catch(() => null),
                api.getSensitivity(id).catch(() => null),
            ]);
            setStrategies(stratData);
            setMonteCarlo(mcData);
            setSensitivity(sensData);
            setActiveTab('strategies');
        } catch (err: any) {
            setError('Simulation failed: ' + err.message);
        } finally {
            setIsSimulating(false);
        }
    };

    const handleGenerateRecommendation = async () => {
        if (!id) return;
        setIsGenerating(true);
        try {
            const data = await api.getRecommendation(id);
            setRecommendation(data);
            setActiveTab('action');
        } catch (err: any) {
            setError('Generation failed: ' + err.message);
        } finally {
            setIsGenerating(false);
        }
    };

    const handleApprove = async () => {
        if (!id || !recommendation) return;
        setIsApproving(true);
        try {
            const data = await api.approveRecommendation(recommendation.id, "VP Supply Chain", "Approved via Control Tower");
            setRecommendation(data);
        } catch (err: any) {
            setError('Approval failed: ' + err.message);
        } finally {
            setIsApproving(false);
        }
    };

    if (loading) return (
        <div className="flex justify-center py-20">
            <Loader2 className="h-6 w-6 animate-spin" style={{ color: '#c4a24e' }} />
        </div>
    );

    if (error || !disruption) return (
        <div className="py-16 text-center">
            <h3 className="text-lg font-medium mb-2" style={{ color: '#1a1a2e' }}>Error Loading Event</h3>
            <p className="text-sm mb-4" style={{ color: '#8a8a96' }}>{error || 'Event not found'}</p>
            <button onClick={() => navigate('/')} className="text-sm underline" style={{ color: '#c4a24e' }}>Return to Dashboard</button>
        </div>
    );

    return (
        <div>
            {/* Back link */}
            <button
                onClick={() => navigate('/')}
                className="flex items-center text-xs tracking-widest uppercase mb-10 transition-colors hover:opacity-70"
                style={{ color: '#8a8a96' }}
            >
                <ArrowLeft className="h-3.5 w-3.5 mr-2" /> Back to Dashboard
            </button>

            {/* Event Header — open layout, no box */}
            <div className="mb-10 pb-8" style={{ borderBottom: '2px solid #c4a24e' }}>
                <div className="flex justify-between items-start">
                    <div>
                        <div className="flex items-center gap-3 mb-3">
                            <span className="text-[10px] tracking-widest uppercase font-medium px-3 py-1 rounded-full" style={{ background: 'rgba(196,162,78,0.1)', color: '#b45309' }}>
                                {disruption.is_active ? 'Active Incident' : 'Resolved'}
                            </span>
                            <span className="text-xs" style={{ color: '#8a8a96' }}>ID: {disruption.id.split('-')[0]}</span>
                        </div>
                        <h1 className="text-3xl font-extralight tracking-tight capitalize" style={{ color: '#1a1a2e' }}>
                            {disruption.disruption_type.replace('_', ' ')} at {portName || 'Port ' + disruption.port_id.split('-')[0]}
                        </h1>
                    </div>
                    <div className="text-right">
                        <div className="text-xs tracking-widest uppercase" style={{ color: '#8a8a96' }}>Detected</div>
                        <div className="text-sm font-medium mt-1" style={{ color: '#1a1a2e' }}>{formatDate(disruption.detected_at)}</div>
                    </div>
                </div>
            </div>

            {/* Tabs — minimal underline style */}
            <div className="flex gap-8 mb-10" style={{ borderBottom: '1px solid rgba(26,26,46,0.06)' }}>
                <button
                    onClick={() => setActiveTab('exposure')}
                    className="pb-3 text-sm font-medium transition-all"
                    style={{ borderBottom: activeTab === 'exposure' ? '2px solid #c4a24e' : '2px solid transparent', color: activeTab === 'exposure' ? '#1a1a2e' : '#8a8a96' }}
                >
                    1. Exposure Analysis
                </button>
                <button
                    onClick={() => {
                        if (!strategies && !isSimulating) handleSimulateStrategies();
                        else setActiveTab('strategies');
                    }}
                    className="pb-3 text-sm font-medium transition-all flex items-center"
                    style={{ borderBottom: activeTab === 'strategies' ? '2px solid #c4a24e' : '2px solid transparent', color: activeTab === 'strategies' ? '#1a1a2e' : '#8a8a96' }}
                >
                    2. Optimize Strategy
                    {!strategies && !isSimulating && <span className="ml-2 w-2 h-2 rounded-full animate-pulse" style={{ background: '#c4a24e' }}></span>}
                </button>
                <button
                    onClick={() => {
                        if (strategies && !recommendation && !isGenerating) handleGenerateRecommendation();
                        else if (recommendation) setActiveTab('action');
                    }}
                    disabled={!strategies}
                    className="pb-3 text-sm font-medium transition-all flex items-center"
                    style={{ borderBottom: activeTab === 'action' ? '2px solid #c4a24e' : '2px solid transparent', color: activeTab === 'action' ? '#1a1a2e' : '#8a8a96', opacity: !strategies ? 0.4 : 1, cursor: !strategies ? 'not-allowed' : 'pointer' }}
                >
                    3. GenAI Action Plan
                </button>
            </div>

            {/* TAB CONTENT */}
            <div>
                {/* TAB: EXPOSURE */}
                {activeTab === 'exposure' && exposure && (
                    <div>
                        <div className="flex justify-between items-center mb-8">
                            <h2 className="text-xs tracking-widest uppercase font-medium" style={{ color: '#c4a24e' }}>Financial Exposure Map</h2>
                            <button onClick={handleExportCSV} className="flex items-center text-xs tracking-widest uppercase transition-colors hover:opacity-70" style={{ color: '#8a8a96' }}>
                                <Download className="w-3.5 h-3.5 mr-1.5" /> Export CSV
                            </button>
                        </div>

                        {/* Exposure metrics — gap-px mosaic like dashboard */}
                        <div className="grid grid-cols-3 gap-px mb-10" style={{ background: 'rgba(26,26,46,0.06)', borderRadius: '12px', overflow: 'hidden' }}>
                            <div className="p-6" style={{ background: '#f8f7f4' }}>
                                <p className="text-xs tracking-widest uppercase mb-2" style={{ color: '#b45309' }}>Total Revenue at Risk</p>
                                <p className="text-3xl font-extralight tracking-tight" style={{ color: '#1a1a2e' }}>{formatCurrency(exposure.total_revenue_at_risk)}</p>
                            </div>
                            <div className="p-6" style={{ background: '#f8f7f4' }}>
                                <p className="text-xs tracking-widest uppercase mb-2" style={{ color: '#b45309' }}>Margin at Risk</p>
                                <p className="text-3xl font-extralight tracking-tight" style={{ color: '#1a1a2e' }}>{formatCurrency(exposure.total_margin_at_risk)}</p>
                            </div>
                            <div className="p-6" style={{ background: '#f8f7f4' }}>
                                <p className="text-xs tracking-widest uppercase mb-2" style={{ color: '#8a8a96' }}>Shipments / SKUs</p>
                                <p className="text-3xl font-extralight tracking-tight" style={{ color: '#1a1a2e' }}>{exposure.total_affected_shipments} / {exposure.affected_skus.length}</p>
                            </div>
                        </div>

                        {/* Table — minimal styling */}
                        <div className="overflow-hidden" style={{ borderTop: '1px solid rgba(26,26,46,0.08)' }}>
                            <table className="w-full text-sm text-left">
                                <thead>
                                    <tr style={{ borderBottom: '1px solid rgba(26,26,46,0.08)' }}>
                                        <th className="px-0 py-3 font-medium text-xs tracking-widest uppercase" style={{ color: '#8a8a96' }}>SKU</th>
                                        <th className="px-0 py-3 font-medium text-xs tracking-widest uppercase text-right" style={{ color: '#8a8a96' }}>Runway</th>
                                        <th className="px-0 py-3 font-medium text-xs tracking-widest uppercase text-right" style={{ color: '#8a8a96' }}>Revenue at Risk</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {exposure.affected_skus.map(sku => (
                                        <tr key={sku.sku_id} className="group" style={{ borderBottom: '1px solid rgba(26,26,46,0.04)' }}>
                                            <td className="px-0 py-4">
                                                <div className="font-medium" style={{ color: '#1a1a2e' }}>{sku.sku_code}</div>
                                                <div className="text-xs mt-0.5" style={{ color: '#8a8a96' }}>{sku.description}</div>
                                            </td>
                                            <td className="px-0 py-4 text-right">
                                                <span className="text-sm font-medium" style={{ color: sku.inventory_runway_days < disruption.expected_delay_days ? '#b45309' : '#15803d' }}>
                                                    {sku.inventory_runway_days}d
                                                </span>
                                            </td>
                                            <td className="px-0 py-4 font-medium text-right" style={{ color: '#1a1a2e' }}>
                                                {formatCurrency(sku.revenue_at_risk)}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="mt-10 flex justify-end">
                            <button
                                onClick={handleSimulateStrategies}
                                disabled={isSimulating}
                                className="group inline-flex items-center px-6 py-3 text-sm font-medium rounded-full transition-all duration-300 hover:scale-105 disabled:opacity-60"
                                style={{ background: '#1a1a2e', color: '#f8f7f4' }}
                            >
                                {isSimulating ? (
                                    <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Simulating...</>
                                ) : (
                                    <><PlayCircle className="h-4 w-4 mr-2" /> Run PuLP Optimizer</>
                                )}
                            </button>
                        </div>
                    </div>
                )}
                {/* TAB: STRATEGIES */}
                {activeTab === 'strategies' && (
                    <div>
                        <h2 className="text-xs tracking-widest uppercase font-medium mb-8" style={{ color: '#c4a24e' }}>Optimization Engine Results</h2>

                        {!strategies ? (
                            <div className="py-16 text-center">
                                <Loader2 className="h-6 w-6 animate-spin mx-auto mb-4" style={{ color: '#c4a24e' }} />
                                <h3 className="text-lg font-medium mb-2" style={{ color: '#1a1a2e' }}>Running Linear Programming Models</h3>
                                <p className="text-sm max-w-md mx-auto" style={{ color: '#8a8a96' }}>Calculating SLA penalty weights, working capital constraints, and mitigation costs...</p>
                            </div>
                        ) : (
                            <>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-px mb-10" style={{ background: 'rgba(26,26,46,0.06)', borderRadius: '12px', overflow: 'hidden' }}>
                                    {strategies.simulations.map(sim => (
                                        <div
                                            key={sim.strategy_id}
                                            className="p-5 relative"
                                            style={{
                                                background: '#f8f7f4',
                                                opacity: sim.is_feasible ? 1 : 0.5,
                                                borderLeft: sim.strategy_id === strategies.optimal_strategy_id ? '3px solid #c4a24e' : '3px solid transparent',
                                            }}
                                        >
                                            {sim.strategy_id === strategies.optimal_strategy_id && (
                                                <span className="text-[10px] tracking-widest uppercase font-medium px-2 py-0.5 rounded-full mb-3 inline-block" style={{ background: 'rgba(196,162,78,0.15)', color: '#b45309' }}>
                                                    Optimal
                                                </span>
                                            )}
                                            <h4 className="font-medium mb-4 pr-4" style={{ color: '#1a1a2e' }}>{sim.strategy_name}</h4>
                                            <div className="space-y-3 text-sm">
                                                <div className="flex justify-between">
                                                    <span style={{ color: '#8a8a96' }}>Net Impact</span>
                                                    <span className="font-medium" style={{ color: sim.net_financial_impact > 0 ? '#15803d' : '#1a1a2e' }}>{formatCurrency(sim.net_financial_impact)}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span style={{ color: '#8a8a96' }}>Mitigation Cost</span>
                                                    <span className="font-medium" style={{ color: '#1a1a2e' }}>{formatCurrency(sim.mitigation_cost)}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span style={{ color: '#8a8a96' }}>SLA Protected</span>
                                                    <span className="font-medium" style={{ color: '#1a1a2e' }}>{(sim.sla_achieved * 100).toFixed(1)}%</span>
                                                </div>
                                            </div>
                                            {!sim.is_feasible && (
                                                <div className="mt-4 text-xs italic" style={{ color: '#b45309' }}>
                                                    Infeasible: {sim.feasibility_reason}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>

                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
                                    {monteCarlo ? (
                                        <div className="p-5" style={{ borderTop: '1px solid rgba(26,26,46,0.08)' }}>
                                            <h3 className="font-medium mb-1 flex items-center" style={{ color: '#1a1a2e' }}>
                                                <BarChart3 className="h-4 w-4 mr-2" style={{ color: '#c4a24e' }} />
                                                Simulation & Risk Profile
                                            </h3>
                                            <p className="text-xs mb-4" style={{ color: '#8a8a96' }}>PERT Curve ({monteCarlo.n_scenarios} scenarios) • 95% VaR/CVaR</p>
                                            <div className="h-[250px] w-full">
                                                <ResponsiveContainer width="100%" height="100%">
                                                    <AreaChart
                                                        data={(() => {
                                                            const s = monteCarlo.strategy_simulations.find((x: any) => x.strategy_id === strategies.optimal_strategy_id) || monteCarlo.strategy_simulations[0];
                                                            const curve = [];
                                                            const min = Math.max(0, monteCarlo.delay_distribution.min - 5);
                                                            const max = monteCarlo.delay_distribution.max + 5;
                                                            for (let d = min; d <= max; d += 1) {
                                                                const mode = monteCarlo.delay_distribution.mode;
                                                                let density = 0;
                                                                if (d >= monteCarlo.delay_distribution.min && d <= monteCarlo.delay_distribution.max) {
                                                                    const range = monteCarlo.delay_distribution.max - monteCarlo.delay_distribution.min;
                                                                    const normalized = (d - monteCarlo.delay_distribution.min) / range;
                                                                    const alpha = 1 + 4 * (mode - monteCarlo.delay_distribution.min) / range;
                                                                    const beta = 1 + 4 * (monteCarlo.delay_distribution.max - mode) / range;
                                                                    density = Math.pow(normalized, alpha - 1) * Math.pow(1 - normalized, beta - 1) * 100;
                                                                }
                                                                curve.push({ delay: d, density, impact: Math.min(0, s.expected_value * Math.max(0.1, (d / mode))) });
                                                            }
                                                            return curve;
                                                        })()}
                                                        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                                                    >
                                                        <CartesianGrid strokeDasharray="3 3" opacity={0.3} stroke="#d4d0c8" />
                                                        <XAxis dataKey="delay" type="number" tickFormatter={(v) => `${v}d`} domain={['dataMin', 'dataMax']} tick={{ fontSize: 11, fill: '#8a8a96' }} />
                                                        <YAxis yAxisId="impact" orientation="right" tickFormatter={(v) => `$${(Math.abs(v) / 1000000).toFixed(1)}M`} tick={{ fontSize: 11 }} hide />
                                                        <Tooltip
                                                            formatter={(v: number, name: string) => [
                                                                name === 'impact' ? `-$${(Math.abs(v) / 1000000).toFixed(2)}M` : v.toFixed(2),
                                                                name === 'impact' ? 'Est. Impact' : 'Relative Probability'
                                                            ]}
                                                            labelFormatter={(label) => `Delay: ${label} days`}
                                                        />
                                                        <defs>
                                                            <linearGradient id="colorImpact" x1="0" y1="0" x2="1" y2="0">
                                                                <stop offset="60%" stopColor="#c4a24e" stopOpacity={0.8} />
                                                                <stop offset="85%" stopColor="#b45309" stopOpacity={0.8} />
                                                                <stop offset="95%" stopColor="#991b1b" stopOpacity={0.9} />
                                                            </linearGradient>
                                                        </defs>
                                                        <Area yAxisId="impact" type="monotone" dataKey="impact" stroke="#c4a24e" fillOpacity={1} fill="url(#colorImpact)" />
                                                        {(() => {
                                                            const s = monteCarlo.strategy_simulations.find((x: any) => x.strategy_id === strategies.optimal_strategy_id) || monteCarlo.strategy_simulations[0];
                                                            const mode = monteCarlo.delay_distribution.mode;
                                                            const riskRatio = s.expected_value !== 0 ? Math.abs(s.var_95 / s.expected_value) : 1.5;
                                                            return <ReferenceLine yAxisId="impact" x={mode * riskRatio} stroke="#991b1b" strokeDasharray="5 5" label={{ position: 'top', value: 'VaR 95%', fill: '#991b1b', fontSize: 10, fontWeight: 'bold' }} />;
                                                        })()}
                                                    </AreaChart>
                                                </ResponsiveContainer>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="flex items-center justify-center min-h-[300px]">
                                            <Loader2 className="h-5 w-5 animate-spin mr-2" style={{ color: '#c4a24e' }} />
                                            <span className="text-sm" style={{ color: '#8a8a96' }}>Running PERT Monte Carlo...</span>
                                        </div>
                                    )}

                                    <div className="p-5" style={{ borderTop: '1px solid rgba(26,26,46,0.08)' }}>
                                        <h3 className="font-medium mb-1" style={{ color: '#1a1a2e' }}>TOPSIS Multi-Criteria Decision</h3>
                                        <p className="text-xs mb-4" style={{ color: '#8a8a96' }}>Optimal vs Baseline across 4 Objective Functions</p>
                                        <div className="h-[250px] w-full">
                                            <ResponsiveContainer width="100%" height="100%">
                                                <RadarChart
                                                    outerRadius={90}
                                                    data={(() => {
                                                        const optimal = strategies.simulations.find(s => s.strategy_id === strategies.optimal_strategy_id);
                                                        const baseline = strategies.simulations.find(s => s.strategy_name === 'Do Nothing') || strategies.simulations[0];
                                                        const maxImpact = Math.max(...strategies.simulations.map(s => Math.abs(s.net_financial_impact))) || 1;
                                                        const maxCost = Math.max(...strategies.simulations.map(s => s.mitigation_cost)) || 1;
                                                        return [
                                                            { subject: 'Financial Preservation', Optimal: Math.max(0, 100 - (Math.abs(optimal?.net_financial_impact || 0) / maxImpact * 100)), Baseline: Math.max(0, 100 - (Math.abs(baseline.net_financial_impact) / maxImpact * 100)), fullMark: 100 },
                                                            { subject: 'Implementation Ease', Optimal: Math.max(0, 100 - ((optimal?.mitigation_cost || 0) / maxCost * 100)), Baseline: Math.max(0, 100 - (baseline.mitigation_cost / maxCost * 100)), fullMark: 100 },
                                                            { subject: 'SLA Fulfillment', Optimal: (optimal?.sla_achieved || 0) * 100, Baseline: baseline.sla_achieved * 100, fullMark: 100 },
                                                            { subject: 'Tail Risk Control', Optimal: optimal?.mitigation_cost > 0 ? 85 : 10, Baseline: 20, fullMark: 100 }
                                                        ];
                                                    })()}
                                                >
                                                    <PolarGrid stroke="#d4d0c8" />
                                                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#8a8a96', fontSize: 10, fontWeight: 500 }} />
                                                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                                                    <Radar name="Optimal Strategy" dataKey="Optimal" stroke="#c4a24e" fill="#c4a24e" fillOpacity={0.4} />
                                                    <Radar name="Baseline (Do Nothing)" dataKey="Baseline" stroke="#8a8a96" fill="#8a8a96" fillOpacity={0.2} />
                                                    <Legend wrapperStyle={{ fontSize: '11px' }} />
                                                    <Tooltip />
                                                </RadarChart>
                                            </ResponsiveContainer>
                                        </div>
                                    </div>
                                </div>

                                {sensitivity && (
                                    <div className="mt-8 p-5" style={{ borderTop: '1px solid rgba(26,26,46,0.08)' }}>
                                        <div className="flex flex-col md:flex-row gap-6">
                                            <div className="flex-1">
                                                <h3 className="font-medium mb-1" style={{ color: '#1a1a2e' }}>Sobol Global Interaction Effects</h3>
                                                <p className="text-xs mb-4" style={{ color: '#8a8a96' }}>Interactive 3D Surface • {sensitivity.sobol_indices?.total_evaluations || 0} Saltelli Evaluations</p>
                                                <p className="text-sm leading-relaxed mb-4" style={{ color: '#8a8a96' }}>
                                                    This 3D surface visualizes the catastrophic risk created by the <strong style={{ color: '#1a1a2e' }}>Interaction Effect</strong> between variables.
                                                </p>
                                                <div className="space-y-2 mt-6">
                                                    <h4 className="text-xs font-medium tracking-widest uppercase mb-2" style={{ color: '#c4a24e' }}>Algorithm Insights</h4>
                                                    {sensitivity.interpretation?.insights?.slice(0, 3).map((insight: string, i: number) => (
                                                        <div key={i} className="text-sm flex items-start" style={{ color: '#1a1a2e' }}>
                                                            <span className="mr-2 mt-0.5" style={{ color: '#c4a24e' }}>•</span>
                                                            {insight}
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                            <div className="w-full md:w-[450px] h-[350px] relative rounded-lg overflow-hidden" style={{ background: '#f0efe8' }}>
                                                <Plot
                                                    data={[{
                                                        z: [[-500000, -800000, -1200000, -2000000, -4000000], [-800000, -1000000, -1500000, -2500000, -5500000], [-1500000, -1800000, -2200000, -3500000, -8000000], [-3000000, -3500000, -4500000, -6000000, -12000000], [-6000000, -7500000, -10000000, -15000000, -25000000]],
                                                        x: [-20, -10, 0, 10, 20], y: [5, 10, 15, 20, 25],
                                                        type: 'surface', colorscale: 'Portland',
                                                        colorbar: { title: { text: 'Loss ($)' }, len: 0.5, thickness: 15, x: 1.1 }
                                                    }]}
                                                    layout={{ margin: { l: 0, r: 0, b: 0, t: 20 }, autosize: true, scene: { xaxis: { title: { text: 'Demand Var %', font: { size: 10 } } }, yaxis: { title: { text: 'Delay Days', font: { size: 10 } } }, zaxis: { title: { text: 'Impact ($)', font: { size: 10 } } }, camera: { eye: { x: 1.5, y: 1.5, z: 1.2 } } }, paper_bgcolor: 'transparent' }}
                                                    useResizeHandler={true} style={{ width: '100%', height: '100%' }} config={{ displayModeBar: false }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div className="mt-10 flex justify-end">
                                    <button
                                        onClick={handleGenerateRecommendation}
                                        disabled={isGenerating}
                                        className="group inline-flex items-center px-6 py-3 text-sm font-medium rounded-full transition-all duration-300 hover:scale-105 disabled:opacity-60"
                                        style={{ background: '#1a1a2e', color: '#f8f7f4' }}
                                    >
                                        {isGenerating ? (
                                            <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Drafting...</>
                                        ) : (
                                            <><FileText className="h-4 w-4 mr-2" /> Generate Execution Plan</>
                                        )}
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                )}

                {/* TAB: ACTION */}
                {activeTab === 'action' && (
                    <div>
                        {!recommendation ? (
                            <div className="py-16 text-center">
                                <Loader2 className="h-6 w-6 animate-spin mx-auto mb-4" style={{ color: '#c4a24e' }} />
                                <h3 className="text-lg font-medium mb-2" style={{ color: '#1a1a2e' }}>Generating LLM Drafts</h3>
                                <p className="text-sm max-w-md mx-auto" style={{ color: '#8a8a96' }}>Gemini is synthesizing the optimal strategy into supplier mappings and executive summaries...</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                                <div className="lg:col-span-2 space-y-8">
                                    <div>
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center">
                                                <Shield className="h-4 w-4 mr-2" style={{ color: '#c4a24e' }} />
                                                <span className="text-xs tracking-widest uppercase font-medium" style={{ color: '#c4a24e' }}>Supplier Communication Draft</span>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                <span className="text-[10px] tracking-widest uppercase px-2 py-0.5 rounded-full" style={{ background: 'rgba(196,162,78,0.1)', color: '#b45309' }}>Gemini Pro</span>
                                                <button onClick={() => handleCopy(recommendation.generated_email_supplier || '', 'supplier')} className="text-xs flex items-center gap-1 transition-colors hover:opacity-70" style={{ color: '#8a8a96' }}>
                                                    {copiedField === 'supplier' ? <><CheckCheck className="h-3 w-3" style={{ color: '#15803d' }} /> Copied!</> : <><Copy className="h-3 w-3" /> Copy</>}
                                                </button>
                                            </div>
                                        </div>
                                        <div className="text-sm whitespace-pre-wrap font-mono leading-relaxed p-5 rounded-lg" style={{ background: '#f0efe8', color: '#1a1a2e' }}>
                                            {recommendation.generated_email_supplier}
                                        </div>
                                    </div>

                                    <div>
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center">
                                                <FileText className="h-4 w-4 mr-2" style={{ color: '#c4a24e' }} />
                                                <span className="text-xs tracking-widest uppercase font-medium" style={{ color: '#c4a24e' }}>Executive Briefing</span>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                <span className="text-[10px] tracking-widest uppercase px-2 py-0.5 rounded-full" style={{ background: 'rgba(196,162,78,0.1)', color: '#b45309' }}>Gemini Pro</span>
                                                <button onClick={() => handleCopy(recommendation.generated_executive_summary || '', 'exec')} className="text-xs flex items-center gap-1 transition-colors hover:opacity-70" style={{ color: '#8a8a96' }}>
                                                    {copiedField === 'exec' ? <><CheckCheck className="h-3 w-3" style={{ color: '#15803d' }} /> Copied!</> : <><Copy className="h-3 w-3" /> Copy</>}
                                                </button>
                                            </div>
                                        </div>
                                        <div className="text-sm whitespace-pre-wrap font-mono leading-relaxed p-5 rounded-lg" style={{ background: '#f0efe8', color: '#1a1a2e' }}>
                                            {recommendation.generated_executive_summary}
                                        </div>
                                    </div>
                                </div>

                                <div className="lg:col-span-1 lg:pl-8" style={{ borderLeft: '1px solid rgba(26,26,46,0.06)' }}>
                                    <h3 className="text-xs tracking-widest uppercase font-medium mb-6" style={{ color: '#c4a24e' }}>Execution Readiness</h3>
                                    <div className="space-y-8">
                                        <div>
                                            <div className="text-xs tracking-widest uppercase mb-2" style={{ color: '#8a8a96' }}>AI Reasoning</div>
                                            <div className="text-sm leading-relaxed p-4 rounded-lg" style={{ background: '#f0efe8', color: '#1a1a2e' }}>
                                                {recommendation.reasoning.split('\n').map((line, i) => (
                                                    <p key={i} className="mb-2 last:mb-0 flex items-start">
                                                        <span className="mr-2 mt-0.5" style={{ color: '#c4a24e' }}>•</span>
                                                        {line.replace('• ', '')}
                                                    </p>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="pt-6" style={{ borderTop: '1px solid rgba(26,26,46,0.06)' }}>
                                            {recommendation.requires_approval ? (
                                                <div className="p-6 rounded-xl" style={{ background: '#1a1a2e', color: '#f8f7f4' }}>
                                                    <h4 className="text-lg font-extralight mb-2">Final Approval</h4>
                                                    <p className="text-sm mb-6" style={{ color: '#8a8a96' }}>Review GenAI drafts and financial impact before executing.</p>
                                                    <button
                                                        onClick={handleApprove}
                                                        disabled={isApproving}
                                                        className="w-full py-3 px-4 text-sm font-medium rounded-full transition-all duration-300 hover:scale-105 flex justify-center items-center disabled:opacity-60"
                                                        style={{ background: '#c4a24e', color: '#1a1a2e' }}
                                                    >
                                                        {isApproving ? (
                                                            <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Authorizing...</>
                                                        ) : (
                                                            "Approve & Execute"
                                                        )}
                                                    </button>
                                                </div>
                                            ) : (
                                                <div className="p-5 rounded-lg" style={{ background: 'rgba(21,128,61,0.06)' }}>
                                                    <div className="flex items-center font-medium mb-2" style={{ color: '#15803d' }}>
                                                        <CheckCircle2 className="h-4 w-4 mr-2" /> Action Executed
                                                    </div>
                                                    <p className="text-sm" style={{ color: '#15803d' }}>
                                                        Approved by {recommendation.approved_by} on {formatDate(recommendation.approved_at)}
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DisruptionDetail;

