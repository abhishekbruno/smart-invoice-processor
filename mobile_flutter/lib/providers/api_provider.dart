import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/api_client.dart';
import '../models/invoice_model.dart';
import '../models/analytics_model.dart';
import '../models/automation_model.dart';

final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService(ApiClient());
});

class ApiService {
  final ApiClient _client;
  ApiService(this._client);

  Dio get _dio => _client.dio;

  // Invoices
  Future<List<InvoiceListItemModel>> getInvoices({
    int page = 1,
    int limit = 20,
    String? vendor,
    String? status,
    String? currency,
    bool includeDuplicates = true,
  }) async {
    final res = await _dio.get('/invoices', queryParameters: {
      'page': page,
      'limit': limit,
      if (vendor != null && vendor.isNotEmpty) 'vendor': vendor,
      if (status != null && status.isNotEmpty) 'status': status,
      if (currency != null && currency.isNotEmpty) 'currency': currency,
      'include_duplicates': includeDuplicates,
    });
    final items = res.data['items'] as List<dynamic>? ?? [];
    return items.map((e) => InvoiceListItemModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<InvoiceDetailModel> getInvoiceDetail(int id) async {
    final res = await _dio.get('/invoices/$id');
    return InvoiceDetailModel.fromJson(res.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> uploadInvoice(String filePath) async {
    final fileName = filePath.split('/').last.split('\\').last;
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath, filename: fileName),
    });
    final res = await _dio.post('/invoices/upload', data: formData);
    return res.data as Map<String, dynamic>;
  }

  Future<bool> verifyInvoice(int id) async {
    final res = await _dio.post('/invoices/$id/verify');
    return res.data['success'] == true;
  }

  Future<bool> markInvoiceGenuine(int id) async {
    final res = await _dio.post('/invoices/$id/mark-genuine');
    return res.data['success'] == true;
  }

  Future<bool> confirmInvoiceDuplicate(int id) async {
    final res = await _dio.post('/invoices/$id/confirm-duplicate');
    return res.data['success'] == true;
  }

  Future<bool> deleteInvoice(int id) async {
    final res = await _dio.delete('/invoices/$id');
    return res.data['success'] == true;
  }

  // Analytics
  Future<AnalyticsSummaryModel> getAnalyticsSummary({String? currency, String mode = 'historical'}) async {
    final res = await _dio.get('/analytics/summary', queryParameters: {
      if (currency != null) 'currency': currency,
      'mode': mode,
    });
    return AnalyticsSummaryModel.fromJson(res.data as Map<String, dynamic>);
  }

  Future<ExpenseAnalyticsModel> getFullAnalytics({String? currency, String mode = 'historical'}) async {
    final res = await _dio.get('/analytics/expenses', queryParameters: {
      if (currency != null) 'currency': currency,
      'mode': mode,
    });
    return ExpenseAnalyticsModel.fromJson(res.data as Map<String, dynamic>);
  }

  // Chat
  Future<Map<String, dynamic>> queryChat(String query) async {
    final res = await _dio.post('/chat/query', data: {'query': query});
    return res.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getChatStatus() async {
    final res = await _dio.get('/chat/status');
    return res.data as Map<String, dynamic>;
  }

  // Automation
  Future<AutomationStatusModel> getAutomationStatus() async {
    final res = await _dio.get('/automation/status');
    return AutomationStatusModel.fromJson(res.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> triggerFolderScan() async {
    final res = await _dio.post('/automation/scan');
    return res.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> triggerGmailSync({String? query}) async {
    final res = await _dio.post('/automation/gmail/sync', queryParameters: {
      if (query != null && query.isNotEmpty) 'query': query,
    });
    return res.data as Map<String, dynamic>;
  }

  Future<List<SyncHistoryModel>> getSyncHistory({int limit = 15}) async {
    final res = await _dio.get('/automation/history', queryParameters: {'limit': limit});
    final items = res.data as List<dynamic>? ?? [];
    return items.map((e) => SyncHistoryModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  // Settings
  Future<Map<String, dynamic>> getSettings() async {
    final res = await _dio.get('/settings');
    return res.data as Map<String, dynamic>;
  }

  Future<bool> setPreferredCurrency(String currency) async {
    final res = await _dio.post('/settings/currency', data: {'currency': currency});
    return res.data['success'] == true;
  }

  Future<bool> reindexVectorStore() async {
    final res = await _dio.post('/settings/reindex');
    return res.data['success'] == true;
  }

  Future<bool> checkHealth() async {
    try {
      final res = await _dio.get('/health');
      return res.data['status'] == 'healthy';
    } catch (_) {
      return false;
    }
  }
}

