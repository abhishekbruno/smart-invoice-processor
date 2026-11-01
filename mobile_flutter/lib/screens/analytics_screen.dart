import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../providers/analytics_provider.dart';

class AnalyticsScreen extends ConsumerStatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  ConsumerState<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends ConsumerState<AnalyticsScreen> {
  int _selectedTabIndex = 0; // 0: Trend, 1: Suppliers, 2: Currencies

  @override
  Widget build(BuildContext context) {
    final analyticsAsync = ref.watch(fullAnalyticsProvider);
    final currentMode = ref.watch(analyticsModeProvider);

    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        title: const Text('Financial Analytics'),
        backgroundColor: const Color(0xFF020203),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, size: 20, color: Color(0xFFB7B7B9)),
            onPressed: () => ref.invalidate(fullAnalyticsProvider),
            tooltip: 'Refresh analytics',
          ),
        ],
      ),
      body: RefreshIndicator(
        color: const Color(0xFFBAA7D1),
        backgroundColor: const Color(0xFF08070B),
        onRefresh: () async => ref.invalidate(fullAnalyticsProvider),
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          children: [
            // Rate Mode Selector Capsule
            Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: const Color(0xFF08070B),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFF1A1625)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: _buildModeTab(
                      'Historical Rates',
                      currentMode == 'historical',
                      () => ref.read(analyticsModeProvider.notifier).state = 'historical',
                    ),
                  ),
                  Expanded(
                    child: _buildModeTab(
                      'Latest ECB Rates',
                      currentMode == 'latest',
                      () => ref.read(analyticsModeProvider.notifier).state = 'latest',
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            analyticsAsync.when(
              data: (data) {
                final summary = data.summary;
                final monthly = data.monthlySpending;
                final vendors = data.vendorSpending;
                final currencies = data.currencyDistribution;
                final currencySymbol = summary.displayCurrency == 'INR' ? '₹' : (summary.displayCurrency == 'EUR' ? '€' : (summary.displayCurrency == 'GBP' ? '£' : '\$'));
                final currencyFormatter = NumberFormat.currency(symbol: currencySymbol, decimalDigits: 0);

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Executive Valuation Header Card
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(22),
                      decoration: BoxDecoration(
                        color: const Color(0xFF08070B),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: const Color(0xFF1A1625)),
                        boxShadow: const [
                          BoxShadow(
                            color: Color(0x264B37B2),
                            blurRadius: 25,
                            spreadRadius: -5,
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'TOTAL VALUATION (${summary.displayCurrency})',
                                style: const TextStyle(
                                  color: Color(0xFF72707D),
                                  fontSize: 10,
                                  fontWeight: FontWeight.w600,
                                  letterSpacing: 1.1,
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF4B37B2).withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: const Color(0xFF8879A7).withOpacity(0.3)),
                                ),
                                child: Text(
                                  '${summary.eligibleInvoices} Eligible',
                                  style: const TextStyle(
                                    color: Color(0xFFBAA7D1),
                                    fontSize: 10,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          Text(
                            summary.formattedTotal,
                            style: const TextStyle(
                              color: Color(0xFFF1F1F1),
                              fontSize: 30,
                              fontWeight: FontWeight.w700,
                              fontFeatures: [FontFeature.tabularFigures()],
                            ),
                          ),
                          const SizedBox(height: 6),
                          Row(
                            children: [
                              const Icon(Icons.info_outline, size: 12, color: Color(0xFF72707D)),
                              const SizedBox(width: 5),
                              Expanded(
                                child: Text(
                                  'Converted via ${summary.effectiveRateSource}',
                                  style: const TextStyle(color: Color(0xFF72707D), fontSize: 11),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),

                    // Section Tab Switcher
                    Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: const Color(0xFF08070B),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF1A1625)),
                      ),
                      child: Row(
                        children: [
                          _buildSectionTab('Monthly Trend', 0),
                          _buildSectionTab('Top Vendors', 1),
                          _buildSectionTab('Currencies', 2),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),

                    // Tab 0: Monthly Trend Chart
                    if (_selectedTabIndex == 0) ...[
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: const Color(0xFF08070B),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: const Color(0xFF1A1625)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Monthly Run-Rate',
                              style: TextStyle(
                                color: Color(0xFFF1F1F1),
                                fontSize: 15,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Normalized to ${summary.displayCurrency} for period comparisons',
                              style: const TextStyle(color: Color(0xFF72707D), fontSize: 11),
                            ),
                            const SizedBox(height: 24),
                            SizedBox(
                              height: 190,
                              child: monthly.isEmpty
                                  ? const Center(
                                      child: Text(
                                        'No monthly data available',
                                        style: TextStyle(color: Color(0xFF72707D), fontSize: 13),
                                      ),
                                    )
                                  : BarChart(
                                      BarChartData(
                                        alignment: BarChartAlignment.spaceAround,
                                        maxY: (monthly
                                                    .map((e) => e.convertedSpent)
                                                    .reduce((a, b) => a > b ? a : b) *
                                                1.25),
                                        barTouchData: BarTouchData(
                                          touchTooltipData: BarTouchTooltipData(
                                            getTooltipItem: (group, groupIndex, rod, rodIndex) {
                                              return BarTooltipItem(
                                                '${monthly[groupIndex].month}\n$currencySymbol${rod.toY.toStringAsFixed(0)}',
                                                const TextStyle(color: Color(0xFFF1F1F1), fontSize: 11, fontWeight: FontWeight.w600),
                                              );
                                            },
                                          ),
                                        ),
                                        titlesData: FlTitlesData(
                                          show: true,
                                          bottomTitles: AxisTitles(
                                            sideTitles: SideTitles(
                                              showTitles: true,
                                              getTitlesWidget: (val, meta) {
                                                final idx = val.toInt();
                                                if (idx >= 0 && idx < monthly.length) {
                                                  final label = monthly[idx].month;
                                                  return Padding(
                                                    padding: const EdgeInsets.only(top: 8),
                                                    child: Text(
                                                      label.length > 5 ? label.substring(5) : label,
                                                      style: const TextStyle(
                                                        color: Color(0xFF72707D),
                                                        fontSize: 10,
                                                        fontWeight: FontWeight.w500,
                                                      ),
                                                    ),
                                                  );
                                                }
                                                return const SizedBox();
                                              },
                                            ),
                                          ),
                                          leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                        ),
                                        gridData: const FlGridData(show: false),
                                        borderData: FlBorderData(show: false),
                                        barGroups: monthly.asMap().entries.map((entry) {
                                          return BarChartGroupData(
                                            x: entry.key,
                                            barRods: [
                                              BarChartRodData(
                                                toY: entry.value.convertedSpent,
                                                color: const Color(0xFF8879A7),
                                                width: 14,
                                                borderRadius: const BorderRadius.vertical(top: Radius.circular(5)),
                                              ),
                                            ],
                                          );
                                        }).toList(),
                                      ),
                                    ),
                            ),
                          ],
                        ),
                      ),
                    ],

                    // Tab 1: Top Vendors List
                    if (_selectedTabIndex == 1) ...[
                      Container(
                        decoration: BoxDecoration(
                          color: const Color(0xFF08070B),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: const Color(0xFF1A1625)),
                        ),
                        child: ListView.separated(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          itemCount: vendors.length,
                          separatorBuilder: (_, __) => const Divider(color: Color(0xFF13101B), height: 1),
                          itemBuilder: (context, index) {
                            final v = vendors[index];
                            final maxSpend = vendors.isNotEmpty ? vendors.first.convertedSpent : 1.0;
                            final ratio = (v.convertedSpent / (maxSpend > 0 ? maxSpend : 1.0)).clamp(0.05, 1.0);

                            return Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Expanded(
                                        child: Text(
                                          v.vendor,
                                          style: const TextStyle(
                                            color: Color(0xFFF1F1F1),
                                            fontSize: 14,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                      ),
                                      Text(
                                        currencyFormatter.format(v.convertedSpent),
                                        style: const TextStyle(
                                          color: Color(0xFFBAA7D1),
                                          fontSize: 14,
                                          fontWeight: FontWeight.w700,
                                          fontFeatures: [FontFeature.tabularFigures()],
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 6),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        '${v.invoiceCount} ${v.invoiceCount == 1 ? 'invoice' : 'invoices'}',
                                        style: const TextStyle(color: Color(0xFF72707D), fontSize: 11),
                                      ),
                                      Text(
                                        '#${index + 1}',
                                        style: const TextStyle(color: Color(0xFF72707D), fontSize: 11, fontWeight: FontWeight.w600),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  ClipRRect(
                                    borderRadius: BorderRadius.circular(2),
                                    child: LinearProgressIndicator(
                                      value: ratio,
                                      minHeight: 3,
                                      backgroundColor: const Color(0xFF13101B),
                                      valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF8879A7)),
                                    ),
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
                      ),
                    ],

                    // Tab 2: Currencies
                    if (_selectedTabIndex == 2) ...[
                      Container(
                        decoration: BoxDecoration(
                          color: const Color(0xFF08070B),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: const Color(0xFF1A1625)),
                        ),
                        child: currencies.isEmpty
                            ? const Padding(
                                padding: EdgeInsets.all(24),
                                child: Center(
                                  child: Text('No currency data available', style: TextStyle(color: Color(0xFF72707D))),
                                ),
                              )
                            : ListView.separated(
                                shrinkWrap: true,
                                physics: const NeverScrollableScrollPhysics(),
                                itemCount: currencies.length,
                                separatorBuilder: (_, __) => const Divider(color: Color(0xFF13101B), height: 1),
                                itemBuilder: (context, index) {
                                  final c = currencies[index];
                                  return Padding(
                                    padding: const EdgeInsets.all(16),
                                    child: Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Row(
                                          children: [
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                              decoration: BoxDecoration(
                                                color: const Color(0xFF0E0C16),
                                                borderRadius: BorderRadius.circular(8),
                                                border: Border.all(color: const Color(0xFF1A1625)),
                                              ),
                                              child: Text(
                                                c.currency,
                                                style: const TextStyle(
                                                  color: Color(0xFFBAA7D1),
                                                  fontSize: 12,
                                                  fontWeight: FontWeight.bold,
                                                ),
                                              ),
                                            ),
                                            const SizedBox(width: 12),
                                            Column(
                                              crossAxisAlignment: CrossAxisAlignment.start,
                                              children: [
                                                Text(
                                                  '${c.invoiceCount} ${c.invoiceCount == 1 ? 'invoice' : 'invoices'}',
                                                  style: const TextStyle(color: Color(0xFFF1F1F1), fontSize: 13, fontWeight: FontWeight.w500),
                                                ),
                                                const SizedBox(height: 2),
                                                Text(
                                                  'Orig: ${c.currency} ${c.originalTotal.toStringAsFixed(2)}',
                                                  style: const TextStyle(color: Color(0xFF72707D), fontSize: 11),
                                                ),
                                              ],
                                            ),
                                          ],
                                        ),
                                        Column(
                                          crossAxisAlignment: CrossAxisAlignment.end,
                                          children: [
                                            Text(
                                              currencyFormatter.format(c.convertedTotal),
                                              style: const TextStyle(
                                                color: Color(0xFFBAA7D1),
                                                fontSize: 14,
                                                fontWeight: FontWeight.w700,
                                                fontFeatures: [FontFeature.tabularFigures()],
                                              ),
                                            ),
                                            const SizedBox(height: 2),
                                            Text(
                                              'in ${summary.displayCurrency}',
                                              style: const TextStyle(color: Color(0xFF72707D), fontSize: 10),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  );
                                },
                              ),
                      ),
                    ],
                  ],
                );
              },
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(40),
                  child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFBAA7D1)),
                ),
              ),
              error: (err, _) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Text('Error loading analytics: $err', style: const TextStyle(color: Color(0xFFEF4444))),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildModeTab(String label, bool isSelected, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF4B37B2).withOpacity(0.3) : Colors.transparent,
          borderRadius: BorderRadius.circular(10),
          border: isSelected ? Border.all(color: const Color(0xFF8879A7).withOpacity(0.4)) : null,
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              color: isSelected ? const Color(0xFFBAA7D1) : const Color(0xFF72707D),
              fontSize: 12,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTab(String title, int index) {
    final isSelected = _selectedTabIndex == index;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _selectedTabIndex = index),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF0E0C16) : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
            border: isSelected ? Border.all(color: const Color(0xFF1A1625)) : null,
          ),
          child: Center(
            child: Text(
              title,
              style: TextStyle(
                color: isSelected ? const Color(0xFFF1F1F1) : const Color(0xFF72707D),
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
