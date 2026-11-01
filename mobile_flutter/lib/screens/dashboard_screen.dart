import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../providers/analytics_provider.dart';
import '../providers/invoice_provider.dart';
import '../models/invoice_model.dart';
import '../widgets/celestial_energy_widget.dart';
import '../widgets/cosmic_glass_card.dart';
import '../core/theme.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final analyticsAsync = ref.watch(fullAnalyticsProvider);
    final invoicesAsync = ref.watch(invoicesListProvider);

    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        title: const Text('Executive Overview'),
        backgroundColor: const Color(0xFF020203),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, size: 18, color: Color(0xFFB7B7B9)),
            onPressed: () {
              ref.invalidate(fullAnalyticsProvider);
              ref.invalidate(invoicesListProvider);
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        color: const Color(0xFFBAA7D1),
        backgroundColor: const Color(0xFF08070B),
        onRefresh: () async {
          ref.invalidate(fullAnalyticsProvider);
          ref.invalidate(invoicesListProvider);
        },
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          children: [
            // Abstract Celestial Hero Banner in Cosmic Violet Glass
            CosmicGlassCard(
              margin: const EdgeInsets.only(bottom: 16),
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    width: 58,
                    height: 58,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(14),
                      color: const Color(0xFF020203),
                    ),
                    child: const Center(
                      child: CelestialEnergyWidget(size: 54),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: const Color(0xFF140F2E),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(color: AppTheme.glassBorder),
                          ),
                          child: const Text(
                            'YOUR FINANCIAL WORKSPACE',
                            style: TextStyle(
                              color: AppTheme.textAccent,
                              fontSize: 9,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 0.8,
                            ),
                          ),
                        ),
                        const SizedBox(height: 6),
                        ShaderMask(
                          shaderCallback: (bounds) => const LinearGradient(
                            colors: [Color(0xFFFFFFFF), Color(0xFFE5DDFC), Color(0xFFBBA8F1)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ).createShader(bounds),
                          child: const Text(
                            'Every invoice. One workspace.',
                            style: TextStyle(
                              color: Colors.white,
                              fontFamily: 'Sora',
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              letterSpacing: -0.4,
                            ),
                          ),
                        ),
                        const SizedBox(height: 3),
                        const Text(
                          'Your invoices, brought into focus.',
                          style: TextStyle(
                            color: AppTheme.textMuted,
                            fontFamily: 'Manrope',
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Executive Spend Card in Cosmic Violet Glass
            analyticsAsync.when(
              data: (analytics) {
                final summary = analytics.summary;
                return CosmicGlassCard(
                  padding: const EdgeInsets.all(22),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'TOTAL PORTFOLIO SPENDING',
                            style: TextStyle(
                              color: AppTheme.textMuted,
                              fontFamily: 'Manrope',
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
                              border: Border.all(color: AppTheme.glassBorder),
                            ),
                            child: Text(
                              summary.displayCurrency,
                              style: const TextStyle(
                                color: AppTheme.textAccent,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(
                        summary.formattedTotal,
                        style: const TextStyle(
                          color: AppTheme.textPrimaryHeading,
                          fontFamily: 'Sora',
                          fontSize: 28,
                          fontWeight: FontWeight.w700,
                          letterSpacing: -0.5,
                          fontFeatures: [FontFeature.tabularFigures()],
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Across ${summary.eligibleInvoices} validated eligible invoices',
                        style: const TextStyle(color: AppTheme.textMuted, fontSize: 11, fontFamily: 'Manrope'),
                      ),
                      const SizedBox(height: 18),
                      const Divider(color: Color(0x1AFFFFFF), height: 1),
                      const SizedBox(height: 14),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildSubMetric('Verified', '${summary.verifiedInvoices}', const Color(0xFF10B981)),
                          _buildSubMetric('Needs Review', '${summary.needsReview}', const Color(0xFFF59E0B)),
                          _buildSubMetric('Duplicates', '${summary.suspectedDuplicates}', const Color(0xFFF43F5E)),
                        ],
                      ),
                    ],
                  ),
                );
              },
              loading: () => Container(
                height: 160,
                decoration: BoxDecoration(
                  color: const Color(0xFF08070B),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFF1A1625)),
                ),
                child: const Center(
                  child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFBAA7D1)),
                ),
              ),
              error: (err, _) => Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF08070B),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFF923F53)),
                ),
                child: Text('Unable to load totals: $err', style: const TextStyle(color: Color(0xFFFCA5A5), fontSize: 12)),
              ),
            ),

            const SizedBox(height: 18),

            // Quick Actions Bar
            Row(
              children: [
                Expanded(
                  child: _buildActionChip(
                    icon: Icons.north_east,
                    label: 'Upload',
                    onTap: () => context.push('/upload'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildActionChip(
                    icon: Icons.chat_bubble_outline,
                    label: 'Ask AI',
                    onTap: () => context.push('/chat'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildActionChip(
                    icon: Icons.sync_alt,
                    label: 'Pipelines',
                    onTap: () => context.push('/automation'),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 26),

            // Recent Invoices Section Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'RECENT INVOICES',
                  style: TextStyle(
                    color: Color(0xFF72707D),
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 1.1,
                  ),
                ),
                TextButton(
                  onPressed: () => context.go('/invoices'),
                  style: TextButton.styleFrom(
                    visualDensity: VisualDensity.compact,
                    padding: EdgeInsets.zero,
                  ),
                  child: const Text('View All', style: TextStyle(fontSize: 11, color: Color(0xFFBAA7D1))),
                ),
              ],
            ),
            const SizedBox(height: 8),

            invoicesAsync.when(
              data: (invoices) {
                if (invoices.isEmpty) {
                  return const Padding(
                    padding: EdgeInsets.symmetric(vertical: 24),
                    child: Center(
                      child: Text('No invoices recorded.', style: TextStyle(color: Color(0xFF72707D), fontSize: 12)),
                    ),
                  );
                }
                final displayList = invoices.take(5).toList();
                return Column(
                  children: displayList.map((inv) => _buildInvoiceItemCard(context, inv)).toList(),
                );
              },
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFBAA7D1)),
                ),
              ),
              error: (err, _) => Text('Error: $err', style: const TextStyle(color: Color(0xFFEF4444), fontSize: 12)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSubMetric(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            color: color,
            fontSize: 16,
            fontWeight: FontWeight.bold,
            fontFeatures: const [FontFeature.tabularFigures()],
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(color: Color(0xFF72707D), fontSize: 10),
        ),
      ],
    );
  }

  Widget _buildActionChip({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(14),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFF0E0C16),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFF1A1625), width: 1.0),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 16, color: const Color(0xFFBAA7D1)),
            const SizedBox(width: 6),
            Text(
              label,
              style: const TextStyle(
                color: Color(0xFFF1F1F1),
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInvoiceItemCard(BuildContext context, InvoiceListItemModel inv) {
    Color statusDotColor = const Color(0xFFBAA7D1);
    if (inv.status == 'verified') {
      statusDotColor = const Color(0xFF10B981);
    } else if (inv.status == 'needs_review') {
      statusDotColor = const Color(0xFFF59E0B);
    } else if (inv.isDuplicate || inv.status == 'suspected_duplicate') {
      statusDotColor = const Color(0xFFF43F5E);
    }

    final currencyFormatter = NumberFormat.currency(symbol: '₹', decimalDigits: 2);
    final inrString = inv.convertedAmount != null
        ? currencyFormatter.format(inv.convertedAmount)
        : '₹0.00';

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF0C091C),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.glassBorder, width: 1.0),
      ),
      child: InkWell(
        onTap: () => context.push('/invoices/${inv.id}'),
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 13),
          child: Row(
            children: [
              Container(
                width: 6,
                height: 6,
                decoration: BoxDecoration(
                  color: statusDotColor,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: statusDotColor.withOpacity(0.5),
                      blurRadius: 4,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      inv.vendorName ?? 'Unknown',
                      style: const TextStyle(
                        color: Color(0xFFF1F1F1),
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${inv.invoiceNumber ?? 'N/A'} • ${inv.invoiceDate ?? 'N/A'}',
                      style: const TextStyle(color: Color(0xFF72707D), fontSize: 10),
                    ),
                  ],
                ),
              ),
              Text(
                inrString,
                style: const TextStyle(
                  color: Color(0xFFBAA7D1),
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  fontFeatures: [FontFeature.tabularFigures()],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
