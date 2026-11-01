import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/analytics_model.dart';
import 'api_provider.dart';

final analyticsModeProvider = StateProvider<String>((ref) => 'historical');

final fullAnalyticsProvider = FutureProvider.autoDispose<ExpenseAnalyticsModel>((ref) async {
  final api = ref.watch(apiServiceProvider);
  final mode = ref.watch(analyticsModeProvider);
  return api.getFullAnalytics(mode: mode);
});

