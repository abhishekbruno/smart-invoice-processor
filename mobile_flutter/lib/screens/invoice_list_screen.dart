import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../providers/invoice_provider.dart';
import '../models/invoice_model.dart';

class InvoiceListScreen extends ConsumerStatefulWidget {
  const InvoiceListScreen({super.key});

  @override
  ConsumerState<InvoiceListScreen> createState() => _InvoiceListScreenState();
}

class _InvoiceListScreenState extends ConsumerState<InvoiceListScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _selectedStatus = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _applyFilter() {
    ref.read(invoiceFilterProvider.notifier).update((state) => {
          ...state,
          'vendor': _searchController.text.trim(),
          'status': _selectedStatus,
        });
  }

  @override
  Widget build(BuildContext context) {
    final invoicesAsync = ref.watch(invoicesListProvider);

    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        title: const Text('Invoice Repository'),
        backgroundColor: const Color(0xFF020203),
        elevation: 0,
      ),
      body: Column(
        children: [
          // Minimal Search & Filter row
          Container(
            padding: const EdgeInsets.fromLTRB(16, 4, 16, 12),
            color: const Color(0xFF020203),
            child: Column(
              children: [
                TextField(
                  controller: _searchController,
                  style: const TextStyle(fontSize: 13, color: Color(0xFFF1F1F1)),
                  decoration: InputDecoration(
                    hintText: 'Search supplier or vendor...',
                    prefixIcon: const Icon(Icons.search, size: 18, color: Color(0xFF72707D)),
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear, size: 16, color: Color(0xFF72707D)),
                            onPressed: () {
                              _searchController.clear();
                              _applyFilter();
                            },
                          )
                        : null,
                    fillColor: const Color(0xFF08070B),
                  ),
                  onSubmitted: (_) => _applyFilter(),
                ),
                const SizedBox(height: 10),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      _buildPill('All', ''),
                      _buildPill('Verified', 'verified'),
                      _buildPill('Processed', 'processed'),
                      _buildPill('Needs Review', 'needs_review'),
                      _buildPill('Duplicates', 'suspected_duplicate'),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Invoices List
          Expanded(
            child: RefreshIndicator(
              color: const Color(0xFFBAA7D1),
              backgroundColor: const Color(0xFF08070B),
              onRefresh: () async {
                ref.invalidate(invoicesListProvider);
              },
              child: invoicesAsync.when(
                data: (invoices) {
                  if (invoices.isEmpty) {
                    return ListView(
                      children: const [
                        Padding(
                          padding: EdgeInsets.symmetric(vertical: 60),
                          child: Center(
                            child: Text(
                              'No invoices found.',
                              style: TextStyle(color: Color(0xFF72707D), fontSize: 12),
                            ),
                          ),
                        ),
                      ],
                    );
                  }

                  return ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                    itemCount: invoices.length,
                    itemBuilder: (context, index) {
                      final inv = invoices[index];
                      return _buildInvoiceCard(context, inv);
                    },
                  );
                },
                loading: () => const Center(
                  child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFBAA7D1)),
                ),
                error: (err, _) => Center(
                  child: Text('Error: $err', style: const TextStyle(color: Color(0xFFEF4444), fontSize: 12)),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPill(String label, String value) {
    final isSelected = _selectedStatus == value;
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: GestureDetector(
        onTap: () {
          setState(() {
            _selectedStatus = isSelected ? '' : value;
          });
          _applyFilter();
        },
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF4B37B2).withOpacity(0.2) : const Color(0xFF08070B),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: isSelected ? const Color(0xFF8879A7).withOpacity(0.5) : const Color(0xFF1A1625),
            ),
          ),
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

  Widget _buildInvoiceCard(BuildContext context, InvoiceListItemModel inv) {
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
        color: const Color(0xFF08070B),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF1A1625), width: 1.0),
      ),
      child: InkWell(
        onTap: () => context.push('/invoices/${inv.id}'),
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              Container(
                width: 7,
                height: 7,
                decoration: BoxDecoration(
                  color: statusDotColor,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(color: statusDotColor.withOpacity(0.5), blurRadius: 4),
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
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    inrString,
                    style: const TextStyle(
                      color: Color(0xFFBAA7D1),
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      fontFeatures: [FontFeature.tabularFigures()],
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${inv.currency} ${inv.totalAmount?.toStringAsFixed(2) ?? '0.00'}',
                    style: const TextStyle(color: Color(0xFF72707D), fontSize: 10),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
