import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../models/chat_model.dart';
import 'api_provider.dart';

final chatMessagesProvider = StateNotifierProvider<ChatNotifier, List<ChatMessageModel>>((ref) {
  final api = ref.watch(apiServiceProvider);
  return ChatNotifier(api);
});

class ChatNotifier extends StateNotifier<List<ChatMessageModel>> {
  final ApiService _api;

  ChatNotifier(this._api)
      : super([
          ChatMessageModel(
            id: 'welcome',
            isUser: false,
            text:
                'Hello! I am your mobile Smart Invoice Assistant. Ask me questions about total spending, vendor comparisons, or specific invoice items.',
            timestamp: DateFormat('hh:mm a').format(DateTime.now()),
          ),
        ]);

  bool _isSending = false;
  bool get isSending => _isSending;

  Future<void> sendMessage(String text) async {
    final query = text.trim();
    if (query.isEmpty || _isSending) return;

    final userMsg = ChatMessageModel(
      id: 'user-${DateTime.now().millisecondsSinceEpoch}',
      isUser: true,
      text: query,
      timestamp: DateFormat('hh:mm a').format(DateTime.now()),
    );

    state = [...state, userMsg];
    _isSending = true;

    try {
      final res = await _api.queryChat(query);
      final rawCitations = res['citations'] as List<dynamic>? ?? [];
      final citations = rawCitations
          .map((c) => CitationModel.fromJson(c as Map<String, dynamic>))
          .toList();

      final assistantMsg = ChatMessageModel(
        id: 'assistant-${DateTime.now().millisecondsSinceEpoch}',
        isUser: false,
        text: res['answer'] ?? 'No response generated.',
        queryType: res['query_type'],
        citations: citations,
        verifiedTotals: res['verified_totals'] as Map<String, dynamic>?,
        isFallback: res['is_fallback'] == true,
        timestamp: DateFormat('hh:mm a').format(DateTime.now()),
      );

      state = [...state, assistantMsg];
    } catch (e) {
      final errorMsg = ChatMessageModel(
        id: 'error-${DateTime.now().millisecondsSinceEpoch}',
        isUser: false,
        text: 'Error processing query: $e',
        timestamp: DateFormat('hh:mm a').format(DateTime.now()),
      );
      state = [...state, errorMsg];
    } finally {
      _isSending = false;
    }
  }

  void clearChat() {
    state = [
      ChatMessageModel(
        id: 'welcome',
        isUser: false,
        text: 'Chat history cleared. How can I assist you with your invoices today?',
        timestamp: DateFormat('hh:mm a').format(DateTime.now()),
      ),
    ];
  }
}

