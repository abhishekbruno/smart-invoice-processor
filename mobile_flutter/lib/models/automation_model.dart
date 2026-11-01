class AutomationStatusModel {
  final bool folderMonitorActive;
  final String watchDirectory;
  final String processedDirectory;
  final bool gmailConfigured;
  final bool gmailAuthenticated;
  final String? gmailEmail;
  final String? gmailLastSyncedAt;
  final bool backgroundPollerRunning;
  final int pollerIntervalMinutes;

  AutomationStatusModel({
    required this.folderMonitorActive,
    required this.watchDirectory,
    required this.processedDirectory,
    required this.gmailConfigured,
    required this.gmailAuthenticated,
    this.gmailEmail,
    this.gmailLastSyncedAt,
    required this.backgroundPollerRunning,
    required this.pollerIntervalMinutes,
  });

  factory AutomationStatusModel.fromJson(Map<String, dynamic> json) {
    return AutomationStatusModel(
      folderMonitorActive: json['folder_monitor_active'] ?? false,
      watchDirectory: json['watch_directory'] ?? '',
      processedDirectory: json['processed_directory'] ?? '',
      gmailConfigured: json['gmail_configured'] ?? false,
      gmailAuthenticated: json['gmail_authenticated'] ?? false,
      gmailEmail: json['gmail_email'],
      gmailLastSyncedAt: json['gmail_last_synced_at'],
      backgroundPollerRunning: json['background_poller_running'] ?? false,
      pollerIntervalMinutes: json['poller_interval_minutes'] ?? 15,
    );
  }
}

class SyncHistoryModel {
  final int id;
  final String startedAt;
  final String? completedAt;
  final String status;
  final int messagesScanned;
  final int attachmentsFound;
  final int invoicesImported;
  final int duplicatesSkipped;
  final int failedCount;
  final String? errorDetails;

  SyncHistoryModel({
    required this.id,
    required this.startedAt,
    this.completedAt,
    required this.status,
    required this.messagesScanned,
    required this.attachmentsFound,
    required this.invoicesImported,
    required this.duplicatesSkipped,
    required this.failedCount,
    this.errorDetails,
  });

  factory SyncHistoryModel.fromJson(Map<String, dynamic> json) {
    return SyncHistoryModel(
      id: json['id'] as int,
      startedAt: json['started_at'] ?? '',
      completedAt: json['completed_at'],
      status: json['status'] ?? 'unknown',
      messagesScanned: json['messages_scanned'] ?? 0,
      attachmentsFound: json['attachments_found'] ?? 0,
      invoicesImported: json['invoices_imported'] ?? 0,
      duplicatesSkipped: json['duplicates_skipped'] ?? 0,
      failedCount: json['failed_count'] ?? 0,
      errorDetails: json['error_details'],
    );
  }
}

