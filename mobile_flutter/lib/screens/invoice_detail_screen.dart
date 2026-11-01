import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../providers/api_provider.dart';
import '../providers/invoice_provider.dart';
import '../providers/analytics_provider.dart';

class InvoiceDetailScreen extends ConsumerStatefulWidget {
  final int invoiceId;
  const InvoiceDetailScreen({super.key, required this.invoiceId});

  @override
  ConsumerState<InvoiceDetailScreen> createState() => _InvoiceDetailScreenState();
}

class _InvoiceDetailScreenState extends ConsumerState<InvoiceDetailScreen> {
  bool _isActionLoading = false;
  int _selectedTab = 0; // 0 = Overview, 1 = Line Items

  Future<void> _verifyInvoice() async {
    setState(() => _isActionLoading = true);
    try {
      final api = ref.read(apiServiceProvider);
      await api.verifyInvoice(widget.invoiceId);
      ref.invalidate(invoiceDetailProvider(widget.invoiceId));
      ref.invalidate(invoicesListProvider);
      ref.invalidate(fullAnalyticsProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Invoice verified')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isActionLoading = false);
    }
  }

  Future<void> _markGenuine() async {
    setState(() => _isActionLoading = true);
    try {
      final api = ref.read(apiServiceProvider);
      await api.markInvoiceGenuine(widget.invoiceId);
      ref.invalidate(invoiceDetailProvider(widget.invoiceId));
      ref.invalidate(invoicesListProvider);
      ref.invalidate(fullAnalyticsProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Marked as genuine')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isActionLoading = false);
    }
  }

  Future<void> _confirmDuplicate() async {
    setState(() => _isActionLoading = true);
    try {
      final api = ref.read(apiServiceProvider);
      await api.confirmInvoiceDuplicate(widget.invoiceId);
      ref.invalidate(invoiceDetailProvider(widget.invoiceId));
      ref.invalidate(invoicesListProvider);
      ref.invalidate(fullAnalyticsProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Duplicate confirmed')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isActionLoading = false);
    }
  }

  Future<void> _deleteInvoice() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF08070B),
        title: const Text('Delete Invoice?', style: TextStyle(fontSize: 16, color: Color(0xFFF1F1F1))),
        content: const Text(
          'This will permanently remove the invoice from the database and vector index.',
          style: TextStyle(fontSize: 12, color: Color(0xFFB7B7B9)),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF72707D))),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF923F53)),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    setState(() => _isActionLoading = true);
    try {
      final api = ref.read(apiServiceProvider);
      await api.deleteInvoice(widget.invoiceId);
      ref.invalidate(invoicesListProvider);
      ref.invalidate(fullAnalyticsProvider);
      if (mounted) {
        context.pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Invoice deleted')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isActionLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final detailAsync = ref.watch(invoiceDetailProvider(widget.invoiceId));

    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        title: Text('Invoice #${widget.invoiceId}'),
        backgroundColor: const Color(0xFF020203),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline, color: Color(0xFF923F53), size: 18),
            onPressed: _isActionLoading ? null : _deleteInvoice,
          ),
        ],
      ),
      body: detailAsync.when(
        data: (detail) {
          final currencyFormatter = NumberFormat.currency(symbol: '₹', decimalDigits: 2);
          final inrString = detail.convertedAmount != null
              ? currencyFormatter.format(detail.convertedAmount)
              : '₹0.00';

          return ListView(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            children: [
              // Suspected duplicate warning
              if (detail.isDuplicate)
                Container(
                  margin: const EdgeInsets.only(bottom: 14),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFF923F53).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: const Color(0xFF923F53).withOpacity(0.4)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.warning_amber_rounded, color: Color(0xFFF43F5E), size: 18),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          detail.duplicateReason ?? 'Duplicate flagged. Excluded from spending totals.',
                          style: const TextStyle(color: Color(0xFFFCA5A5), fontSize: 11),
                        ),
                      ),
                    ],
                  ),
                ),

              // Segmented Tab Switcher
              Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: const Color(0xFF08070B),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF1A1625)),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: _buildTabPill('Overview & Totals', _selectedTab == 0, () => setState(() => _selectedTab = 0)),
                    ),
                    Expanded(
                      child: _buildTabPill('Line Items (${detail.lineItems.length})', _selectedTab == 1, () => setState(() => _selectedTab = 1)),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              if (_selectedTab == 0) ...[
                // Overview Card
                Container(
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: const Color(0xFF08070B),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFF1A1625), width: 1.0),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        detail.vendorName ?? 'Unknown Vendor',
                        style: const TextStyle(color: Color(0xFFF1F1F1), fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 14),
                      _buildRow('Invoice Number', detail.invoiceNumber ?? 'N/A'),
                      _buildRow('Issue Date', detail.invoiceDate ?? 'N/A'),
                      _buildRow('Due Date', detail.dueDate ?? 'N/A'),
                      _buildRow('Status', detail.status.toUpperCase()),
                      const Divider(color: Color(0xFF13101B), height: 22),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Original Amount', style: TextStyle(color: Color(0xFF72707D), fontSize: 10)),
                              const SizedBox(height: 3),
                              Text(
                                '${detail.currency} ${detail.totalAmount?.toStringAsFixed(2) ?? '0.00'}',
                                style: const TextStyle(color: Color(0xFFF1F1F1), fontSize: 14, fontWeight: FontWeight.w600),
                              ),
                            ],
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              const Text('Converted (INR)', style: TextStyle(color: Color(0xFF72707D), fontSize: 10)),
                              const SizedBox(height: 3),
                              Text(
                                inrString,
                                style: const TextStyle(
                                  color: Color(0xFFBAA7D1),
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  fontFeatures: [FontFeature.tabularFigures()],
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ] else ...[
                // Line Items List
                if (detail.lineItems.isEmpty)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 30),
                    child: Center(
                      child: Text('No itemized lines detected.', style: TextStyle(color: Color(0xFF72707D), fontSize: 12)),
                    ),
                  )
                else
                  ...detail.lineItems.map(
                    (item) => Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: const Color(0xFF08070B),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: const Color(0xFF1A1625), width: 1.0),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  item.description,
                                  style: const TextStyle(color: Color(0xFFF1F1F1), fontSize: 12, fontWeight: FontWeight.w500),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  'Qty: ${item.quantity ?? 1} • Unit: ${detail.currency} ${item.unitPrice?.toStringAsFixed(2) ?? '0.00'}',
                                  style: const TextStyle(color: Color(0xFF72707D), fontSize: 10),
                                ),
                              ],
                            ),
                          ),
                          Text(
                            '${detail.currency} ${item.amount?.toStringAsFixed(2) ?? '0.00'}',
                            style: const TextStyle(color: Color(0xFFF1F1F1), fontSize: 12, fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],

              const SizedBox(height: 24),

              // Bottom Verification Action Buttons
              if (detail.isDuplicate) ...[
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton(
                        onPressed: _isActionLoading ? null : _markGenuine,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF10B981),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        child: const Text('Mark Genuine', style: TextStyle(fontSize: 12)),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: ElevatedButton(
                        onPressed: _isActionLoading ? null : _confirmDuplicate,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFF59E0B),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        child: const Text('Confirm Duplicate', style: TextStyle(fontSize: 12)),
                      ),
                    ),
                  ],
                ),
              ] else if (detail.status != 'verified') ...[
                ElevatedButton(
                  onPressed: _isActionLoading ? null : _verifyInvoice,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF4B37B2),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    minimumSize: const Size.fromHeight(44),
                  ),
                  child: const Text('Verify Invoice', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                ),
              ],
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFBAA7D1))),
        error: (err, _) => Center(child: Text('Error: $err', style: const TextStyle(color: Color(0xFFEF4444), fontSize: 12))),
      ),
    );
  }

  Widget _buildTabPill(String label, bool isSelected, VoidCallback onTap) {
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
              color: isSelected ? const Color(0xFFBAA7D1) : const Color(0xFFB7B7B9),
              fontSize: 11,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3.5),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Color(0xFF72707D), fontSize: 11)),
          Text(value, style: const TextStyle(color: Color(0xFFF1F1F1), fontSize: 11, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
