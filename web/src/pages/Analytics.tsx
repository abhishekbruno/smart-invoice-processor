import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart as RechartsPie,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { RefreshCw } from 'lucide-react';
import { fetchFullAnalytics } from '../services/api';
import { MetricCard } from '../components/MetricCard';
import { CosmicGlassPanel } from '../components/CosmicGlassPanel';
import { useEffects } from '../components/EffectsProvider';
import { ScrollReveal } from '../components/ScrollReveal';

const AOVIX_COLORS = ['#4B37B2', '#8879A7', '#BAA7D1', '#923F53', '#4B334D', '#72707D'];

export const Analytics: React.FC = () => {
  const { reduced } = useEffects();
  const [valuationMode, setValuationMode] = useState<'historical' | 'latest'>('historical');
  const [selectedCurrency, setSelectedCurrency] = useState('INR');
  const [activeTab, setActiveTab] = useState<'monthly' | 'vendors' | 'currencies'>('monthly');

  const { data: analytics, isLoading, refetch } = useQuery({
    queryKey: ['analytics-page', selectedCurrency, valuationMode],
    queryFn: () => fetchFullAnalytics(selectedCurrency, valuationMode),
    staleTime: 20000,
  });

  const summary = analytics?.summary;
  const monthlyData = analytics?.monthly_spending || [];
  const vendorData = analytics?.vendor_spending || [];
  const currencyData = analytics?.currency_distribution || [];
  const money = (value: number) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: summary?.display_currency || selectedCurrency, maximumFractionDigits: 2 }).format(value);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full cosmic-glass-pill mb-2">
            <span>Treasury Telemetry</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-semibold tracking-tight text-[#F1EDF8]">
            Financial Insights
          </h1>
          <p className="text-xs sm:text-sm text-[#B8B2C8] mt-1 font-sans font-light">
            Historical run-rate analytics, supplier expenditure ranks, and multi-currency distributions.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          {/* Target Currency Selector */}
          <select
            value={selectedCurrency}
            onChange={(e) => setSelectedCurrency(e.target.value)}
            className="px-3.5 py-2 cosmic-glass-control rounded-xl text-xs text-[#F1EDF8] focus:outline-none focus:border-[#BBA8F1]/60 cursor-pointer font-sans"
          >
            <option value="INR" className="bg-[#0B081E]">INR (₹)</option>
            <option value="USD" className="bg-[#0B081E]">USD ($)</option>
            <option value="EUR" className="bg-[#0B081E]">EUR (€)</option>
            <option value="GBP" className="bg-[#0B081E]">GBP (£)</option>
          </select>

          {/* Valuation Mode Segmented Pill */}
          <div className="cosmic-glass-control rounded-full p-1 flex items-center text-xs">
            <button
              onClick={() => setValuationMode('historical')}
              className={`px-3.5 py-1 rounded-full text-[11px] font-sans font-medium transition cursor-pointer ${
                valuationMode === 'historical'
                  ? 'aovix-gradient-btn shadow-sm'
                  : 'text-[#B8B2C8] hover:text-[#F1EDF8]'
              }`}
            >
              Historical
            </button>
            <button
              onClick={() => setValuationMode('latest')}
              className={`px-3.5 py-1 rounded-full text-[11px] font-sans font-medium transition cursor-pointer ${
                valuationMode === 'latest'
                  ? 'aovix-gradient-btn shadow-sm'
                  : 'text-[#B8B2C8] hover:text-[#F1EDF8]'
              }`}
            >
              Latest
            </button>
          </div>

          <button
            onClick={() => refetch()}
            className="p-2 rounded-xl cosmic-glass-control text-[#9892AB] hover:text-[#F1EDF8] transition cursor-pointer"
            title="Refresh analytics"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 3 Balanced Summary Cards */}
      <ScrollReveal className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title="Converted Total"
          value={summary?.formatted_total ?? '—'}
          subtitle={`Mode: ${valuationMode.toUpperCase()} | ${summary?.effective_rate_source || 'ECB'}`}
        />
        <MetricCard
          title="Active Suppliers"
          value={summary?.vendor_count ?? '—'}
          subtitle="Unique vendors across invoices"
        />
        <MetricCard
          title="Eligible Non-Duplicates"
          value={summary?.eligible_invoices ?? '—'}
          subtitle={`Out of ${summary?.total_invoices ?? 0} registered`}
        />
      </ScrollReveal>

      {/* Segmented View Switcher */}
      <div className="flex items-center gap-2 border-b border-white/6 pb-3 text-xs">
        <button
          onClick={() => setActiveTab('monthly')}
          className={`px-4 py-1.5 rounded-full font-sans font-medium transition cursor-pointer ${
            activeTab === 'monthly'
              ? 'bg-[#4B37B2]/30 text-[#BBA8F1] border border-[#BBA8F1]/40 shadow-[0_0_12px_rgba(75,55,178,0.25)]'
              : 'text-[#B8B2C8] hover:text-[#F1EDF8]'
          }`}
        >
          Monthly Run-Rate
        </button>
        <button
          onClick={() => setActiveTab('vendors')}
          className={`px-4 py-1.5 rounded-full font-sans font-medium transition cursor-pointer ${
            activeTab === 'vendors'
              ? 'bg-[#4B37B2]/30 text-[#BBA8F1] border border-[#BBA8F1]/40 shadow-[0_0_12px_rgba(75,55,178,0.25)]'
              : 'text-[#B8B2C8] hover:text-[#F1EDF8]'
          }`}
        >
          Supplier Rankings
        </button>
        <button
          onClick={() => setActiveTab('currencies')}
          className={`px-4 py-1.5 rounded-full font-sans font-medium transition cursor-pointer ${
            activeTab === 'currencies'
              ? 'bg-[#4B37B2]/30 text-[#BBA8F1] border border-[#BBA8F1]/40 shadow-[0_0_12px_rgba(75,55,178,0.25)]'
              : 'text-[#B8B2C8] hover:text-[#F1EDF8]'
          }`}
        >
          Currency Breakdown
        </button>
      </div>

      {/* Primary Focused Visualizer Area in Cosmic Violet Glass */}
      {activeTab === 'monthly' && (
        <CosmicGlassPanel className="p-6 sm:p-7">
          <div className="mb-4">
            <h2 className="text-sm font-display font-semibold text-[#F1EDF8] tracking-tight">Monthly Expenditure Run-Rate</h2>
            <p className="text-xs text-[#9892AB] font-sans">Normalized in {selectedCurrency} based on invoice issue dates</p>
          </div>
          <div className="h-72">
            {monthlyData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="month" stroke="#9892AB" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="#9892AB" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: selectedCurrency, notation: 'compact' }).format(v)} />
                  <Tooltip
                    cursor={{ fill: 'rgba(103, 70, 186, 0.12)' }}
                    contentStyle={{ backgroundColor: '#0B081E', borderColor: 'rgba(184, 160, 248, 0.25)', borderRadius: '14px', fontSize: '11px', color: '#F1EDF8' }}
                    formatter={(val: any) => [money(Number(val)), 'Converted Spend']}
                  />
                  <Bar isAnimationActive={!reduced} animationDuration={500} dataKey="converted_spent" fill="#8879A7" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-[#9892AB]">
                {isLoading ? 'Loading metrics...' : 'No data available'}
              </div>
            )}
          </div>
        </CosmicGlassPanel>
      )}

      {activeTab === 'vendors' && (
        <CosmicGlassPanel className="overflow-hidden p-0">
          <div className="px-6 py-4.5 border-b border-white/6">
            <h2 className="text-sm font-display font-semibold text-[#F1EDF8] tracking-tight">Supplier Expenditure Distribution</h2>
            <p className="text-xs text-[#9892AB] font-sans">Ranked by total converted expenditure in {selectedCurrency}</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-white/[0.015] text-[#9892AB] uppercase font-mono text-[10px] border-b border-white/6">
                <tr>
                  <th className="px-6 py-3.5 font-semibold">Supplier</th>
                  <th className="px-6 py-3.5 font-semibold text-right">Invoices</th>
                  <th className="px-6 py-3.5 font-semibold text-right">Converted Spend ({selectedCurrency})</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/4 text-[#B8B2C8]">
                {vendorData.map((v, idx) => (
                  <tr key={idx} className="hover:bg-white/[0.02] transition">
                    <td className="px-6 py-4 font-sans font-medium text-[#F1EDF8]">{v.vendor}</td>
                    <td className="px-6 py-4 text-right text-[#9892AB] font-mono">{v.invoice_count}</td>
                    <td className="px-6 py-4 text-right font-semibold text-[#BBA8F1] tabular-nums font-mono">
                      {money(v.converted_spent)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CosmicGlassPanel>
      )}

      {activeTab === 'currencies' && (
        <CosmicGlassPanel className="p-6 sm:p-7">
          <div className="mb-4">
            <h2 className="text-sm font-display font-semibold text-[#F1EDF8] tracking-tight">Original Currency Distribution</h2>
            <p className="text-xs text-[#9892AB] font-sans">Proportion of original invoice billing currencies</p>
          </div>
          <div className="h-72">
            {currencyData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPie>
                  <Pie isAnimationActive={!reduced} animationDuration={500}
                    data={currencyData}
                    dataKey="converted_total"
                    nameKey="currency"
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={4}
                  >
                    {currencyData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={AOVIX_COLORS[index % AOVIX_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0B081E', borderColor: 'rgba(184, 160, 248, 0.25)', borderRadius: '14px', fontSize: '11px', color: '#F1EDF8' }}
                    formatter={(val: any, name: any) => [
                      money(Number(val)),
                      `Currency: ${name}`,
                    ]}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', color: '#B8B2C8' }} />
                </RechartsPie>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-[#9892AB]">
                {isLoading ? 'Loading...' : 'No currency data'}
              </div>
            )}
          </div>
        </CosmicGlassPanel>
      )}
    </div>
  );
};
