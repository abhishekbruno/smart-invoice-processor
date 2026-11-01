import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/invoice_model.dart';
import 'api_provider.dart';

final invoiceFilterProvider = StateProvider<Map<String, dynamic>>((ref) {
  return {
    'vendor': '',
    'status': '',
    'currency': '',
    'include_duplicates': true,
  };
});

final invoicesListProvider = FutureProvider.autoDispose<List<InvoiceListItemModel>>((ref) async {
  final api = ref.watch(apiServiceProvider);
  final filters = ref.watch(invoiceFilterProvider);

  return api.getInvoices(
    vendor: filters['vendor'],
    status: filters['status'],
    currency: filters['currency'],
    includeDuplicates: filters['include_duplicates'] ?? true,
  );
});

final invoiceDetailProvider = FutureProvider.autoDispose.family<InvoiceDetailModel, int>((ref, id) async {
  final api = ref.watch(apiServiceProvider);
  return api.getInvoiceDetail(id);
});

