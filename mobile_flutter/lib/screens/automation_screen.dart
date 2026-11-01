import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/api_provider.dart';
import '../models/automation_model.dart';
import '../providers/invoice_provider.dart';
import '../providers/analytics_provider.dart';

final automationStatusProvider = FutureProvider.autoDispose<AutomationStatusModel>((ref) async {
  final api = ref.watch(apiServiceProvider);
  return api.getAutomationStatus();
});

final syncHistoryProvider = FutureProvider.autoDispose<List<SyncHistoryModel>>((ref) async {
  final api = ref.watch(apiServiceProvider);
  return api.getSyncHistory(limit: 10);
});

class AutomationScreen extends ConsumerStatefulWidget {
  const AutomationScreen({super.key});

  @override
  ConsumerState<AutomationScreen> createState() => _AutomationScreenState();
}

class _AutomationScreenState extends ConsumerState<AutomationScreen> {
  bool _isFolderScanning = false;
  bool _isGmailSyncing = false;

  Future<void> _scanFolder() async {
    setState(() => _isFolderScanning = true);
    try {
      final api = ref.read(apiServiceProvider);
      final res = await api.triggerFolderScan();
      ref.invalidate(automationStatusProvider);
      ref.invalidate(invoicesListProvider);
      ref.invalidate(fullAnalyticsProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: const Color(0xFF08070B),
            content: Text(
              'Folder scan finished: ${res['new_imported']} new imported, ${res['duplicates_skipped']} skipped',
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
            content: Text('Scan error: $e', style: const TextStyle(color: Color(0xFFFCA5A5))),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isFolderScanning = false);
    }
  }

  Future<void> _syncGmail() async {
    setState(() => _isGmailSyncing = true);
    try {
      final api = ref.read(apiServiceProvider);
      final res = await api.triggerGmailSync();
      ref.invalidate(syncHistoryProvider);
      ref.invalidate(automationStatusProvider);
      ref.invalidate(invoicesListProvider);
      ref.invalidate(fullAnalyticsProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: const Color(0xFF08070B),
            content: Text(
              'Gmail sync: ${res['invoices_imported']} imported, ${res['attachments_found']} found',
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
            content: Text('Sync error: $e', style: const TextStyle(color: Color(0xFFFCA5A5))),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isGmailSyncing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final statusAsync = ref.watch(automationStatusProvider);
    final historyAsync = ref.watch(syncHistoryProvider);

    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        title: const Text('Automation Pipelines', style: TextStyle(color: Color(0xFFF1F1F1), fontSize: 17, fontWeight: FontWeight.w600)),
        backgroundColor: const Color(0xFF020203),
        elevation: 0,
        centerTitle: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, size: 20, color: Color(0xFFB7B7B9)),
            onPressed: () {
              ref.invalidate(automationStatusProvider);
              ref.invalidate(syncHistoryProvider);
            },
            tooltip: 'Refresh pipelines',
          ),
        ],
      ),
      body: RefreshIndicator(
        color: const Color(0xFFBAA7D1),
        backgroundColor: const Color(0xFF08070B),
        onRefresh: () async {
          ref.invalidate(automationStatusProvider);
          ref.invalidate(syncHistoryProvider);
        },
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          children: [
            statusAsync.when(
              data: (status) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Section header
                    const Text(
                      'ACTIVE INTEGRATIONS',
                      style: TextStyle(
                        color: Color(0xFF72707D),
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Folder Monitor Card
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
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(9),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF4B37B2).withOpacity(0.15),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: const Icon(Icons.folder_outlined, color: Color(0xFFBAA7D1), size: 18),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text(
                                      'Watch Directory',
                                      style: TextStyle(
                                        color: Color(0xFFF1F1F1),
                                        fontSize: 15,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      status.watchDirectory,
                                      style: const TextStyle(color: Color(0xFF72707D), fontSize: 11),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ],
                                ),
                              ),
                              _buildStatusBadge(status.folderMonitorActive),
                            ],
                          ),
                          const SizedBox(height: 16),
                          SizedBox(
                            width: double.infinity,
                            height: 40,
                            child: ElevatedButton(
                              onPressed: _isFolderScanning ? null : _scanFolder,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF14121E),
                                foregroundColor: const Color(0xFFF1F1F1),
                                elevation: 0,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(10),
                                  side: const BorderSide(color: Color(0xFF1A1625)),
                                ),
                              ),
                              child: _isFolderScanning
                                  ? const SizedBox(
                                      width: 14,
                                      height: 14,
                                      child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFBAA7D1)),
                                    )
                                  : const Text(
                                      'Scan Watch Folder Now',
                                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                                    ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 12),

                    // Gmail RPA Card
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
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(9),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF4B37B2).withOpacity(0.15),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: const Icon(Icons.mail_outline, color: Color(0xFFBAA7D1), size: 18),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text(
                                      'Gmail Attachment Bot',
                                      style: TextStyle(
                                        color: Color(0xFFF1F1F1),
                                        fontSize: 15,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      status.gmailAuthenticated
                                          ? (status.gmailEmail ?? 'Connected')
                                          : 'OAuth credentials standby',
                                      style: const TextStyle(color: Color(0xFF72707D), fontSize: 11),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ],
                                ),
                              ),
                              _buildStatusBadge(status.gmailAuthenticated),
                            ],
                          ),
                          const SizedBox(height: 16),
                          Container(
                            width: double.infinity,
                            height: 40,
                            decoration: BoxDecoration(
                              gradient: const LinearGradient(
                                colors: [Color(0xFF4B37B2), Color(0xFF8879A7)],
                              ),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: ElevatedButton(
                              onPressed: _isGmailSyncing ? null : _syncGmail,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.transparent,
                                shadowColor: Colors.transparent,
                                foregroundColor: Colors.white,
                                elevation: 0,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(10),
                                ),
                              ),
                              child: _isGmailSyncing
                                  ? const SizedBox(
                                      width: 14,
                                      height: 14,
                                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                    )
                                  : const Text(
                                      'Trigger Gmail Sync',
                                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                                    ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                );
              },
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFBAA7D1)),
                ),
              ),
              error: (err, _) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Text('Error: $err', style: const TextStyle(color: Color(0xFF923F53))),
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Sync History Section
            const Text(
              'RECENT SYNC AUDIT LOG',
              style: TextStyle(
                color: Color(0xFF72707D),
                fontSize: 10,
                fontWeight: FontWeight.w600,
                letterSpacing: 1.2,
              ),
            ),
            const SizedBox(height: 12),

            historyAsync.when(
              data: (history) {
                if (history.isEmpty) {
                  return Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: const Color(0xFF08070B),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFF1A1625)),
                    ),
                    child: const Center(
                      child: Text(
                        'No Gmail sync records yet.',
                        style: TextStyle(color: Color(0xFF72707D), fontSize: 13),
                      ),
                    ),
                  );
                }

                return Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFF08070B),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFF1A1625)),
                  ),
                  child: ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: history.length,
                    separatorBuilder: (_, __) => const Divider(color: Color(0xFF1A1625), height: 1),
                    itemBuilder: (context, index) {
                      final item = history[index];
                      return Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  item.startedAt,
                                  style: const TextStyle(
                                    color: Color(0xFFF1F1F1),
                                    fontSize: 13,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                const SizedBox(height: 3),
                                Text(
                                  '${item.messagesScanned} scanned • ${item.attachmentsFound} found',
                                  style: const TextStyle(color: Color(0xFF72707D), fontSize: 11),
                                ),
                              ],
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFF10B981).withOpacity(0.12),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                '+${item.invoicesImported} imported',
                                style: const TextStyle(
                                  color: Color(0xFF34D399),
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                );
              },
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFBAA7D1)),
                ),
              ),
              error: (err, _) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text('Error loading history: $err', style: const TextStyle(color: Color(0xFF923F53))),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(bool isActive) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: (isActive ? const Color(0xFF10B981) : const Color(0xFF72707D)).withOpacity(0.12),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 5,
            height: 5,
            decoration: BoxDecoration(
              color: isActive ? const Color(0xFF10B981) : const Color(0xFF72707D),
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 5),
          Text(
            isActive ? 'ACTIVE' : 'STANDBY',
            style: TextStyle(
              color: isActive ? const Color(0xFF34D399) : const Color(0xFFB7B7B9),
              fontSize: 10,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
}
