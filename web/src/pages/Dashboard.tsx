import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  ArrowUpRight,
  ArrowRight,
  Receipt,
  ScanLine,
  ShieldAlert,
  Wallet,
  Sparkles,
  FilePlus2,
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { fetchFullAnalytics, fetchInvoices } from '../services/api';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';
import { CosmicGlassPanel } from '../components/CosmicGlassPanel';
import { DashboardHero } from '../components/DashboardHero';
import { ScrollReveal } from '../components/ScrollReveal';
import { useEffects } from '../components/EffectsProvider';

export function Dashboard() {
  const { reduced } = useEffects();
  const analytics = useQuery({
    queryKey: ['analytics-full'],
    queryFn: () => fetchFullAnalytics(),
    staleTime: 30000,
  });
  const invoices = useQuery({
    queryKey: ['invoices', 'recent'],
    queryFn: () => fetchInvoices({ page: 1, limit: 5 }),
    staleTime: 30000,
  });

  const summary = analytics.data?.summary;
  const monthly = analytics.data?.monthly_spending ?? [];
  const vendors = (analytics.data?.vendor_spending ?? []).slice(0, 5);
  const currency = summary?.display_currency;

  const money = (value: number, unit = currency) =>
    unit
      ? new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency: unit,
          maximumFractionDigits: 2,
        }).format(value)
      : '—';

  const shortMoney = (value: number) =>
    currency
      ? new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency,
          notation: 'compact',
          maximumFractionDigits: 1,
        }).format(value)
      : '—';

  const loadingValue = analytics.isLoading ? '…' : '—';
  const vendorMax = Math.max(1, ...vendors.map((v) => v.converted_spent));

  return (
    <div className="dashboard space-y-12 pb-12">
      {/* 1. Hero Section with Centered Celestial Sphere, Background Watermark, and Floating Glass Panels */}
      <DashboardHero />

      {/* 2. Measurable Impact Section (AOVIX Reference Image 1) */}
      <ScrollReveal>
        <section aria-labelledby="impact-title" className="space-y-6 pt-2">
          <div className="flex flex-col items-center text-center max-w-2xl mx-auto space-y-2.5">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full cosmic-glass-pill">
              <span className="w-1.5 h-1.5 rounded-full bg-[#cab0ff] shadow-[0_0_8px_#ae78fd]" />
              <span className="font-mono text-[9px] uppercase tracking-[0.16em] text-[#d6c3fc]">
                Our impact
              </span>
            </div>
            <h2
              id="impact-title"
              className="text-2xl sm:text-3xl font-display font-medium text-[#F1EDF8] tracking-tight"
            >
              Measurable impact
            </h2>
            <p className="text-xs sm:text-sm text-[#9f94b8] max-w-lg leading-relaxed">
              Real results from intelligent automation. Every workflow optimized, every hour put to better use.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <CosmicGlassPanel className="p-6 text-left flex flex-col justify-between min-h-[175px]">
              <div className="text-4xl sm:text-5xl font-display font-semibold text-[#F1EDF8] tracking-tight mb-4">
                98%
              </div>
              <div>
                <h3 className="text-sm font-sans font-medium text-[#E5DDFC] mb-1">
                  Task automation rate
                </h3>
                <p className="text-xs text-[#988cae] leading-snug">
                  Automating repetitive tasks across workflows.
                </p>
              </div>
            </CosmicGlassPanel>

            <CosmicGlassPanel className="p-6 text-left flex flex-col justify-between min-h-[175px]">
              <div className="text-4xl sm:text-5xl font-display font-semibold text-[#F1EDF8] tracking-tight mb-4">
                40 hrs
              </div>
              <div>
                <h3 className="text-sm font-sans font-medium text-[#E5DDFC] mb-1">
                  Saved per week
                </h3>
                <p className="text-xs text-[#988cae] leading-snug">
                  Reducing manual work every week.
                </p>
              </div>
            </CosmicGlassPanel>

            <CosmicGlassPanel className="p-6 text-left flex flex-col justify-between min-h-[175px]">
              <div className="text-4xl sm:text-5xl font-display font-semibold text-[#F1EDF8] tracking-tight mb-4">
                3.2x
              </div>
              <div>
                <h3 className="text-sm font-sans font-medium text-[#E5DDFC] mb-1">
                  Productivity increase
                </h3>
                <p className="text-xs text-[#988cae] leading-snug">
                  Improving efficiency through automation.
                </p>
              </div>
            </CosmicGlassPanel>

            <CosmicGlassPanel className="p-6 text-left flex flex-col justify-between min-h-[175px]">
              <div className="text-4xl sm:text-5xl font-display font-semibold text-[#F1EDF8] tracking-tight mb-4">
                {summary ? `${summary.total_invoices}+` : '150+'}
              </div>
              <div>
                <h3 className="text-sm font-sans font-medium text-[#E5DDFC] mb-1">
                  Automated workflows
                </h3>
                <p className="text-xs text-[#988cae] leading-snug">
                  Building smarter business operations.
                </p>
              </div>
            </CosmicGlassPanel>
          </div>
        </section>
      </ScrollReveal>

      {/* 3. Core Capabilities Section (AOVIX Reference Image 2) */}
      <ScrollReveal>
        <section aria-labelledby="systems-title" className="space-y-6 pt-4">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-3 border-b border-white/[0.06]">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full cosmic-glass-pill mb-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#cab0ff] shadow-[0_0_8px_#ae78fd]" />
                <span className="font-mono text-[9px] uppercase tracking-[0.16em] text-[#d6c3fc]">
                  Our Service
                </span>
              </div>
              <h2
                id="systems-title"
                className="text-2xl sm:text-3xl font-display font-medium text-[#F1EDF8] tracking-tight"
              >
                Intelligent Systems We Build
              </h2>
            </div>
            <p className="text-xs text-[#9f94b8] max-w-md text-left md:text-right leading-relaxed">
              Four core service solutions designed to streamline operations, automate workflows, and accelerate business growth.
            </p>
          </div>

          <div className="space-y-3.5">
            {/* //01 AI Workflow Automation */}
            <CosmicGlassPanel className="p-5 sm:p-6 transition-all duration-200 hover:border-[#BBA8F1]/30">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                  <span className="font-mono text-xs text-[#8f82a5] shrink-0 mt-0.5">//01</span>
                  <div className="space-y-1.5">
                    <h3 className="text-base font-display font-medium text-[#F1EDF8]">
                      AI Workflow & Document Automation
                    </h3>
                    <p className="text-xs text-[#9f94b8] max-w-xl leading-relaxed">
                      Connect your documents, automate repetitive line-item extraction, and build seamless parsing workflows that keep finance running around the clock.
                    </p>
                    <div className="flex flex-wrap gap-2 pt-2">
                      {['PyMuPDF', 'Schema Validation', 'Multi-Currency', 'Line Items'].map((tag) => (
                        <span
                          key={tag}
                          className="text-[10px] font-mono px-2.5 py-0.5 rounded-md bg-white/[0.04] text-[#cfc2e6] border border-white/5"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="self-end md:self-center shrink-0">
                  <Link to="/upload" className="icon-link" aria-label="Open invoice upload">
                    <ArrowUpRight size={16} />
                  </Link>
                </div>
              </div>
            </CosmicGlassPanel>

            {/* //02 Conversational RAG */}
            <CosmicGlassPanel className="p-5 sm:p-6 transition-all duration-200 hover:border-[#BBA8F1]/30">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                  <span className="font-mono text-xs text-[#8f82a5] shrink-0 mt-0.5">//02</span>
                  <div className="space-y-1.5">
                    <h3 className="text-base font-display font-medium text-[#F1EDF8]">
                      Conversational RAG Intelligence
                    </h3>
                    <p className="text-xs text-[#9f94b8] max-w-xl leading-relaxed">
                      Custom semantic search, vector knowledge bases, and conversational AI systems powered by Google Gemini and ChromaDB to query any invoice instantly.
                    </p>
                    <div className="flex flex-wrap gap-2 pt-2">
                      {['ChromaDB', 'Gemini Pro', 'Vector Search', 'Source Citations'].map((tag) => (
                        <span
                          key={tag}
                          className="text-[10px] font-mono px-2.5 py-0.5 rounded-md bg-white/[0.04] text-[#cfc2e6] border border-white/5"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="self-end md:self-center shrink-0">
                  <Link to="/chat" className="icon-link" aria-label="Open Ask AI">
                    <ArrowUpRight size={16} />
                  </Link>
                </div>
              </div>
            </CosmicGlassPanel>

            {/* //03 Deterministic Duplicate Shield */}
            <CosmicGlassPanel className="p-5 sm:p-6 transition-all duration-200 hover:border-[#BBA8F1]/30">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                  <span className="font-mono text-xs text-[#8f82a5] shrink-0 mt-0.5">//03</span>
                  <div className="space-y-1.5">
                    <h3 className="text-base font-display font-medium text-[#F1EDF8]">
                      Deterministic Duplicate Shield
                    </h3>
                    <p className="text-xs text-[#9f94b8] max-w-xl leading-relaxed">
                      Multi-signal integrity scoring, routing, and checksum verification that ensures duplicate submissions are intercepted before reaching the ledger.
                    </p>
                    <div className="flex flex-wrap gap-2 pt-2">
                      {['Hash Matching', 'Fuzzy Vendor Check', 'Audit Trail', 'Risk Scoring'].map((tag) => (
                        <span
                          key={tag}
                          className="text-[10px] font-mono px-2.5 py-0.5 rounded-md bg-white/[0.04] text-[#cfc2e6] border border-white/5"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="self-end md:self-center shrink-0">
                  <Link
                    to="/invoices?status=suspected_duplicate"
                    className="icon-link"
                    aria-label="View suspected duplicates"
                  >
                    <ArrowUpRight size={16} />
                  </Link>
                </div>
              </div>
            </CosmicGlassPanel>

            {/* //04 Financial Telemetry & Reporting */}
            <CosmicGlassPanel className="p-5 sm:p-6 transition-all duration-200 hover:border-[#BBA8F1]/30">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                  <span className="font-mono text-xs text-[#8f82a5] shrink-0 mt-0.5">//04</span>
                  <div className="space-y-1.5">
                    <h3 className="text-base font-display font-medium text-[#F1EDF8]">
                      Financial Telemetry & Reporting
                    </h3>
                    <p className="text-xs text-[#9f94b8] max-w-xl leading-relaxed">
                      Automated spend trajectories, vendor concentration metrics, and export-ready compliance summaries for audit readiness.
                    </p>
                    <div className="flex flex-wrap gap-2 pt-2">
                      {['Spend Trends', 'Vendor Ratios', 'Ledger Export', 'Tax Aggregates'].map((tag) => (
                        <span
                          key={tag}
                          className="text-[10px] font-mono px-2.5 py-0.5 rounded-md bg-white/[0.04] text-[#cfc2e6] border border-white/5"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="self-end md:self-center shrink-0">
                  <Link to="/reports" className="icon-link" aria-label="Open Reports">
                    <ArrowUpRight size={16} />
                  </Link>
                </div>
              </div>
            </CosmicGlassPanel>
          </div>
        </section>
      </ScrollReveal>

      {/* 4. Financial Overview KPIs */}
      <ScrollReveal>
        <section id="financial-overview" aria-labelledby="overview-title" className="space-y-5 scroll-mt-24">
          <div className="section-heading">
            <div>
              <span className="section-kicker">THE BIG PICTURE</span>
              <h2 id="overview-title">Your financial overview</h2>
            </div>
            <span className="text-xs text-[#b4a8ce]">
              {currency ? currency + ' · Eligible spending' : 'Awaiting financial data'}
            </span>
          </div>

          {analytics.isError && (
            <div role="status" className="data-notice">
              Financial data is unavailable.{' '}
              {summary && 'Showing the last available values. '}
              <button onClick={() => analytics.refetch()}>
                Try again <ArrowRight size={13} />
              </button>
            </div>
          )}

          <div className="grid grid-cols-1 min-[420px]:grid-cols-2 xl:grid-cols-4 gap-4">
            <ScrollReveal delay={0}>
              <MetricCard
                title="Eligible spending"
                value={summary?.total_spending ?? loadingValue}
                format={money}
                subtitle={
                  summary
                    ? summary.eligible_invoices + ' invoices included'
                    : 'From your invoice ledger'
                }
                icon={Wallet}
              />
            </ScrollReveal>
            <ScrollReveal delay={45}>
              <MetricCard
                title="Total invoices"
                value={summary?.total_invoices ?? loadingValue}
                subtitle="All invoices in your workspace"
                icon={Receipt}
              />
            </ScrollReveal>
            <ScrollReveal delay={90}>
              <MetricCard
                title="Needs attention"
                value={summary?.needs_review ?? loadingValue}
                subtitle="Ready for your review"
                icon={ScanLine}
              />
            </ScrollReveal>
            <ScrollReveal delay={135}>
              <MetricCard
                title="Suspected duplicates"
                value={summary?.suspected_duplicates ?? loadingValue}
                subtitle="Check before including in spend"
                icon={ShieldAlert}
              />
            </ScrollReveal>
          </div>
        </section>
      </ScrollReveal>

      {/* 5. Spending Pulse Chart & Top Vendors */}
      <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.65fr)_minmax(0,1fr)] gap-5">
        <ScrollReveal>
          <CosmicGlassPanel className="p-5 sm:p-7 h-full">
            <div className="section-heading mb-6">
              <div>
                <span className="section-kicker">SPENDING PULSE</span>
                <h2>Clarity over time</h2>
                <p className="text-xs text-[#a99ebc] mt-2">
                  Eligible spending by invoice month{currency ? ' · ' + currency : ''}
                </p>
              </div>
              <Link to="/analytics" className="icon-link" aria-label="Explore spending analytics">
                <ArrowUpRight size={18} />
              </Link>
            </div>
            <div
              className="h-64 sm:h-72 min-w-0"
              role={monthly.length ? 'figure' : undefined}
              aria-label={
                monthly.length
                  ? 'Monthly eligible spending trend; exact values follow in the data table'
                  : undefined
              }
            >
              {monthly.length ? (
                <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                  <AreaChart data={monthly} margin={{ top: 12, right: 12, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="spending-lavender" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#a28ae8" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#a28ae8" stopOpacity={0.01} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid
                      vertical={false}
                      stroke="#bca5f5"
                      strokeOpacity={0.07}
                      strokeDasharray="3 6"
                    />
                    <XAxis
                      dataKey="month"
                      stroke="#a99ebc"
                      fontSize={10}
                      tickLine={false}
                      axisLine={false}
                      minTickGap={32}
                      dy={8}
                    />
                    <YAxis
                      stroke="#a99ebc"
                      fontSize={10}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={shortMoney}
                      width={65}
                    />
                    <Tooltip
                      contentStyle={{
                        background: '#151022',
                        border: '1px solid #54416e',
                        borderRadius: 12,
                        color: '#f1edf8',
                        fontSize: 12,
                      }}
                      formatter={(value) => [money(Number(value)), 'Eligible spending']}
                    />
                    <Area
                      type="monotone"
                      dataKey="converted_spent"
                      stroke="#bdabf6"
                      strokeWidth={2}
                      fill="url(#spending-lavender)"
                      dot={{ r: 2, fill: '#d7cafa', strokeWidth: 0 }}
                      activeDot={{ r: 5, stroke: '#211831', strokeWidth: 3 }}
                      isAnimationActive={!reduced}
                      animationDuration={550}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState
                  title={
                    analytics.isLoading
                      ? 'Gathering your spending…'
                      : analytics.isError
                      ? 'Spending data unavailable'
                      : 'Your spending story starts here'
                  }
                  text={
                    analytics.isError
                      ? 'Retry the financial overview to reconnect.'
                      : 'Upload an invoice to see your monthly spending.'
                  }
                  loading={analytics.isLoading || analytics.isError}
                />
              )}
            </div>
            {monthly.length > 0 && (
              <details className="chart-data">
                <summary>View monthly figures</summary>
                <table>
                  <thead>
                    <tr>
                      <th scope="col">Month</th>
                      <th scope="col">Spending</th>
                      <th scope="col">Invoices</th>
                    </tr>
                  </thead>
                  <tbody>
                    {monthly.map((row) => (
                      <tr key={row.month}>
                        <th scope="row">{row.month}</th>
                        <td>{money(row.converted_spent, row.display_currency)}</td>
                        <td>{row.invoice_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </details>
            )}
          </CosmicGlassPanel>
        </ScrollReveal>

        <ScrollReveal delay={80}>
          <CosmicGlassPanel className="p-5 sm:p-7 h-full">
            <div className="section-heading mb-7">
              <div>
                <span className="section-kicker">WHERE IT GOES</span>
                <h2>Top vendors</h2>
              </div>
              <span className="text-xs text-[#a99ebc]">By spending</span>
            </div>
            {vendors.length ? (
              <div className="space-y-6">
                {vendors.map((vendor, i) => (
                  <div key={vendor.vendor}>
                    <div className="flex items-center justify-between gap-3 text-xs mb-2.5">
                      <span className="flex items-center gap-2 min-w-0">
                        <span className="text-[#9183ad] font-mono text-[10px]">0{i + 1}</span>
                        <span className="truncate text-[#dfd6ed]">
                          {vendor.vendor || 'Unknown vendor'}
                        </span>
                      </span>
                      <span className="tabular-nums shrink-0 text-[#cfc0ec]">
                        {money(vendor.converted_spent, vendor.display_currency)}
                      </span>
                    </div>
                    <div className="vendor-track">
                      <div
                        style={{
                          width: Math.max(0, (vendor.converted_spent / vendorMax) * 100) + '%',
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                title={
                  analytics.isLoading
                    ? 'Loading vendors…'
                    : analytics.isError
                    ? 'Vendor data unavailable'
                    : 'A clearer view of every vendor'
                }
                text="Your eligible invoices will appear here, grouped by vendor."
                loading={analytics.isLoading || analytics.isError}
              />
            )}
            <Link to="/analytics" className="text-link mt-7">
              Explore all analytics <ArrowRight size={14} />
            </Link>
          </CosmicGlassPanel>
        </ScrollReveal>
      </div>

      {/* 6. Recent Invoices Activity Table */}
      <ScrollReveal>
        <CosmicGlassPanel className="activity-panel">
          <div className="section-heading p-5 sm:p-7">
            <div>
              <span className="section-kicker">YOUR WORKSPACE, IN MOTION</span>
              <h2>Recent invoices</h2>
            </div>
            <Link to="/invoices" className="text-link">
              View all <ArrowUpRight size={15} />
            </Link>
          </div>
          {invoices.isError && (
            <div role="status" className="data-notice mx-5 mb-4">
              Recent invoices could not be refreshed.
              <button onClick={() => invoices.refetch()}>Try again</button>
            </div>
          )}
          {invoices.data?.items.length ? (
            <div className="overflow-x-auto">
              <table className="activity-table">
                <thead>
                  <tr>
                    <th scope="col">Invoice / vendor</th>
                    <th scope="col">Received</th>
                    <th scope="col">Amount</th>
                    <th scope="col">Status</th>
                    <th scope="col">
                      <span className="sr-only">Open</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {invoices.data.items.map((invoice) => (
                    <tr key={invoice.id}>
                      <td>
                        <Link
                          to={'/invoices?invoice=' + invoice.id}
                          className="invoice-name"
                        >
                          <span className="invoice-icon">
                            <Receipt size={17} />
                          </span>
                          <span>
                            <strong>{invoice.vendor_name || 'Unknown vendor'}</strong>
                            <small>{invoice.invoice_number || 'Invoice #' + invoice.id}</small>
                          </span>
                        </Link>
                      </td>
                      <td className="whitespace-nowrap">
                        {new Date(invoice.created_at).toLocaleDateString('en-IN', {
                          day: 'numeric',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </td>
                      <td className="tabular-nums whitespace-nowrap">
                        {invoice.converted_amount != null && invoice.converted_currency
                          ? money(invoice.converted_amount, invoice.converted_currency)
                          : invoice.total_amount != null
                          ? money(invoice.total_amount, invoice.currency)
                          : '—'}
                      </td>
                      <td>
                        <StatusBadge
                          status={invoice.is_duplicate ? 'suspected_duplicate' : invoice.status}
                        />
                      </td>
                      <td>
                        <Link
                          className="icon-link"
                          to={'/invoices?invoice=' + invoice.id}
                          aria-label={'Open invoice ' + (invoice.invoice_number || invoice.id)}
                        >
                          <ArrowUpRight size={15} />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="pb-7">
              <EmptyState
                title={
                  invoices.isLoading
                    ? 'Loading recent invoices…'
                    : invoices.isError
                    ? 'Activity is unavailable'
                    : 'Make room for your first invoice'
                }
                text="Upload a PDF and keep its processing status in view."
                loading={invoices.isLoading || invoices.isError}
              />
            </div>
          )}
          {!!summary?.suspected_duplicates && (
            <Link
              to="/invoices?status=suspected_duplicate"
              className="duplicate-notice"
            >
              <ShieldAlert size={16} />
              <span>
                {summary.suspected_duplicates} suspected duplicate
                {summary.suspected_duplicates === 1 ? '' : 's'} awaiting review
              </span>
              <ArrowRight size={14} />
            </Link>
          )}
        </CosmicGlassPanel>
      </ScrollReveal>

      {/* 7. Bottom Callout Banner */}
      <ScrollReveal>
        <div className="workspace-next">
          <div className="flex items-center gap-4">
            <span className="next-spark">
              <Sparkles size={21} />
            </span>
            <div>
              <h2>A little curiosity. A lot of clarity.</h2>
              <p>Ask a question about your invoices and explore the details behind your spending.</p>
            </div>
          </div>
          <Link to="/chat" className="hero-secondary shrink-0">
            Ask AI <ArrowUpRight size={16} />
          </Link>
        </div>
      </ScrollReveal>
    </div>
  );
}

function EmptyState({
  title,
  text,
  loading = false,
}: {
  title: string;
  text: string;
  loading?: boolean;
}) {
  return (
    <div className="dashboard-empty">
      <FilePlus2 size={25} strokeWidth={1} />
      <h3>{title}</h3>
      <p>{text}</p>
      {!loading && (
        <Link className="text-link" to="/upload">
          Upload an invoice <ArrowRight size={14} />
        </Link>
      )}
    </div>
  );
}
