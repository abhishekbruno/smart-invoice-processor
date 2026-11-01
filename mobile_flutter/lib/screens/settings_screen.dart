import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/api_client.dart';
import '../providers/api_provider.dart';
import '../providers/analytics_provider.dart';
import '../providers/invoice_provider.dart';
import '../core/effects.dart';

final settingsDataProvider = FutureProvider.autoDispose<Map<String, dynamic>>((
  ref,
) async {
  final api = ref.watch(apiServiceProvider);
  return api.getSettings();
});

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  late TextEditingController _urlController;
  bool _isReindexing = false;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(text: ApiClient().currentBaseUrl);
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  void _updateUrl() {
    final text = _urlController.text.trim();
    if (text.isEmpty) return;

    ApiClient().updateBaseUrl(text);
    ref.invalidate(settingsDataProvider);
    ref.invalidate(fullAnalyticsProvider);
    ref.invalidate(invoicesListProvider);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: const Color(0xFF08070B),
        content: Text(
          'API base URL updated to: ${ApiClient().currentBaseUrl}',
          style: const TextStyle(color: Color(0xFFF1F1F1)),
        ),
      ),
    );
  }

  Future<void> _updateCurrency(String code) async {
    try {
      final api = ref.read(apiServiceProvider);
      await api.setPreferredCurrency(code);
      ref.invalidate(settingsDataProvider);
      ref.invalidate(fullAnalyticsProvider);
      ref.invalidate(invoicesListProvider);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: const Color(0xFF08070B),
            content: Text(
              'Valuation currency updated to $code',
              style: const TextStyle(color: Color(0xFFF1F1F1)),
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: const Color(0xFF4B334D),
            content: Text(
              'Error: $e',
              style: const TextStyle(color: Color(0xFFFCA5A5)),
            ),
          ),
        );
      }
    }
  }

  Future<void> _reindexVectorStore() async {
    setState(() => _isReindexing = true);
    try {
      final api = ref.read(apiServiceProvider);
      await api.reindexVectorStore();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            backgroundColor: Color(0xFF08070B),
            content: Text(
              'ChromaDB re-indexing completed successfully',
              style: TextStyle(color: Color(0xFFF1F1F1)),
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: const Color(0xFF4B334D),
            content: Text(
              'Reindex error: $e',
              style: const TextStyle(color: Color(0xFFFCA5A5)),
            ),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isReindexing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final settingsAsync = ref.watch(settingsDataProvider);

    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        title: const Text(
          'System Preferences',
          style: TextStyle(
            color: Color(0xFFF1F1F1),
            fontSize: 17,
            fontWeight: FontWeight.w600,
          ),
        ),
        backgroundColor: const Color(0xFF020203),
        elevation: 0,
        centerTitle: false,
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        children: [
          SwitchListTile.adaptive(
            title: const Text('Reduced effects'),
            subtitle: const Text(
              'Still energy core and shorter transitions for this session. System reduced motion is always respected.',
            ),
            value: ref.watch(reducedEffectsProvider),
            onChanged: (value) =>
                ref.read(reducedEffectsProvider.notifier).state = value,
            activeColor: const Color(0xFFBBA8F1),
          ),
          const SizedBox(height: 20),
          // Section: Valuation Currency
          const Text(
            'VALUATION CURRENCY',
            style: TextStyle(
              color: Color(0xFF72707D),
              fontSize: 10,
              fontWeight: FontWeight.w600,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),

          settingsAsync.when(
            data: (rawSettings) {
              final data = rawSettings['data'] as Map<String, dynamic>? ?? {};
              final prefCurr = data['preferred_display_currency'] ?? 'INR';
              final rates =
                  data['latest_reference_rates_usd'] as Map<String, dynamic>? ??
                  {};

              return Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: const Color(0xFF08070B),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF1A1625)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        _buildCurrencyPill('INR', '₹', prefCurr == 'INR'),
                        const SizedBox(width: 8),
                        _buildCurrencyPill('USD', '\$', prefCurr == 'USD'),
                        const SizedBox(width: 8),
                        _buildCurrencyPill('EUR', '€', prefCurr == 'EUR'),
                        const SizedBox(width: 8),
                        _buildCurrencyPill('GBP', '£', prefCurr == 'GBP'),
                      ],
                    ),
                    const SizedBox(height: 16),
                    const Divider(color: Color(0xFF1A1625), height: 1),
                    const SizedBox(height: 12),
                    const Text(
                      'Frankfurter / ECB Daily Reference Rates',
                      style: TextStyle(
                        color: Color(0xFFBAA7D1),
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'USD 1.00 = INR ₹${rates['INR'] ?? '87.45'} • EUR €${rates['EUR'] ?? '0.965'} • GBP £${rates['GBP'] ?? '0.805'}',
                      style: const TextStyle(
                        color: Color(0xFF72707D),
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              );
            },
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Color(0xFFBAA7D1),
                ),
              ),
            ),
            error: (err, _) => Padding(
              padding: const EdgeInsets.all(12),
              child: Text(
                'Error: $err',
                style: const TextStyle(color: Color(0xFF923F53)),
              ),
            ),
          ),

          const SizedBox(height: 24),

          // Section: API Server
          const Text(
            'FASTAPI ENDPOINT',
            style: TextStyle(
              color: Color(0xFF72707D),
              fontSize: 10,
              fontWeight: FontWeight.w600,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),

          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: const Color(0xFF08070B),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF1A1625)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Backend Connection URI',
                  style: TextStyle(
                    color: Color(0xFFF1F1F1),
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Use 127.0.0.1:8000 for USB reverse adb, or LAN IP for WiFi debugging.',
                  style: TextStyle(color: Color(0xFF72707D), fontSize: 11),
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Expanded(
                      child: Container(
                        height: 40,
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0E0C16),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: const Color(0xFF1A1625)),
                        ),
                        child: TextField(
                          controller: _urlController,
                          style: const TextStyle(
                            color: Color(0xFFF1F1F1),
                            fontSize: 13,
                          ),
                          decoration: const InputDecoration(
                            isDense: true,
                            contentPadding: EdgeInsets.symmetric(vertical: 10),
                            border: InputBorder.none,
                            hintText: 'http://127.0.0.1:8000/api',
                            hintStyle: TextStyle(color: Color(0xFF72707D)),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      height: 40,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF4B37B2), Color(0xFF8879A7)],
                        ),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: ElevatedButton(
                        onPressed: _updateUrl,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          shadowColor: Colors.transparent,
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          minimumSize: const Size(0, 40),
                        ),
                        child: const Text(
                          'Save',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // Section: Maintenance
          const Text(
            'MAINTENANCE & VECTOR DATABASE',
            style: TextStyle(
              color: Color(0xFF72707D),
              fontSize: 10,
              fontWeight: FontWeight.w600,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),

          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: const Color(0xFF08070B),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF1A1625)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'ChromaDB Vector Store',
                  style: TextStyle(
                    color: Color(0xFFF1F1F1),
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Re-indexes all SQLite invoices and regenerates document embeddings.',
                  style: TextStyle(color: Color(0xFF72707D), fontSize: 11),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  height: 40,
                  child: OutlinedButton(
                    onPressed: _isReindexing ? null : _reindexVectorStore,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFFF1F1F1),
                      side: const BorderSide(color: Color(0xFF1A1625)),
                      backgroundColor: const Color(0xFF14121E),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                    child: _isReindexing
                        ? const SizedBox(
                            width: 14,
                            height: 14,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Color(0xFFBAA7D1),
                            ),
                          )
                        : const Text(
                            'Re-index ChromaDB Embeddings',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCurrencyPill(String code, String symbol, bool isSelected) {
    return Expanded(
      child: GestureDetector(
        onTap: () => _updateCurrency(code),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            color: isSelected
                ? const Color(0xFF4B37B2).withOpacity(0.18)
                : const Color(0xFF14121E),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: isSelected
                  ? const Color(0xFF8879A7)
                  : const Color(0xFF1A1625),
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                symbol,
                style: TextStyle(
                  color: isSelected
                      ? const Color(0xFFBAA7D1)
                      : const Color(0xFFF1F1F1),
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                code,
                style: TextStyle(
                  color: isSelected
                      ? const Color(0xFFBAA7D1)
                      : const Color(0xFF72707D),
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
