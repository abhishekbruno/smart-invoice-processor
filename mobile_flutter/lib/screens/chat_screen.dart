import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/chat_provider.dart';
import '../models/chat_model.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  final List<String> _suggestions = [
    'What did we spend in total?',
    'What did we spend on AWS?',
    'Compare AWS and Google Cloud',
    'Which vendor charged the highest?',
  ];

  @override
  void dispose() {
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _sendMessage([String? textToSend]) {
    final text = textToSend ?? _inputController.text;
    if (text.trim().isEmpty) return;

    _inputController.clear();
    ref.read(chatMessagesProvider.notifier).sendMessage(text);
    _scrollToBottom();
  }

  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(chatMessagesProvider);
    final notifier = ref.read(chatMessagesProvider.notifier);

    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        title: const Text('Ask AI Workspace'),
        backgroundColor: const Color(0xFF020203),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, size: 18, color: Color(0xFFB7B7B9)),
            tooltip: 'Clear Conversation',
            onPressed: () => notifier.clearChat(),
          ),
        ],
      ),
      body: Column(
        children: [
          // Prompt suggestions
          Container(
            height: 44,
            color: const Color(0xFF020203),
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
              itemCount: _suggestions.length,
              itemBuilder: (context, index) {
                final s = _suggestions[index];
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: ActionChip(
                    label: Text(s, style: const TextStyle(fontSize: 10)),
                    backgroundColor: const Color(0xFF08070B),
                    labelStyle: const TextStyle(color: Color(0xFFB7B7B9)),
                    side: const BorderSide(color: Color(0xFF1A1625)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    padding: const EdgeInsets.symmetric(horizontal: 6),
                    visualDensity: VisualDensity.compact,
                    onPressed: () => _sendMessage(s),
                  ),
                );
              },
            ),
          ),

          // Messages list
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(14),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final msg = messages[index];
                return _buildMessageBubble(msg);
              },
            ),
          ),

          // Input field
          Container(
            padding: const EdgeInsets.fromLTRB(14, 8, 14, 14),
            color: const Color(0xFF020203),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _inputController,
                    style: const TextStyle(fontSize: 13, color: Color(0xFFF1F1F1)),
                    decoration: InputDecoration(
                      hintText: 'Ask a question about your invoices...',
                      hintStyle: const TextStyle(color: Color(0xFF72707D), fontSize: 12),
                      fillColor: const Color(0xFF08070B),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: const BorderSide(color: Color(0xFF1A1625)),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: const BorderSide(color: Color(0xFF1A1625)),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: const BorderSide(color: Color(0xFF8879A7), width: 1.2),
                      ),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  icon: const Icon(Icons.arrow_upward, size: 18),
                  style: IconButton.styleFrom(
                    backgroundColor: const Color(0xFF4B37B2),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  onPressed: () => _sendMessage(),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessageModel msg) {
    if (msg.isUser) {
      return Align(
        alignment: Alignment.centerRight,
        child: Container(
          margin: const EdgeInsets.only(bottom: 12, left: 48),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: const Color(0xFF4B37B2),
            borderRadius: BorderRadius.circular(16).copyWith(bottomRight: const Radius.circular(2)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x334B37B2),
                blurRadius: 12,
              ),
            ],
          ),
          child: Text(
            msg.text,
            style: const TextStyle(color: Colors.white, fontSize: 13),
          ),
        ),
      );
    }

    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 14, right: 36),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF08070B),
          borderRadius: BorderRadius.circular(16).copyWith(bottomLeft: const Radius.circular(2)),
          border: Border.all(color: const Color(0xFF1A1625), width: 1.0),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (msg.queryType != null) ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: const Color(0xFF4B37B2).withOpacity(0.2),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: const Color(0xFF8879A7).withOpacity(0.3)),
                    ),
                    child: Text(
                      msg.queryType!,
                      style: const TextStyle(color: Color(0xFFBAA7D1), fontSize: 9, fontWeight: FontWeight.bold),
                    ),
                  ),
                  InkWell(
                    onTap: () {
                      Clipboard.setData(ClipboardData(text: msg.text));
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Copied'), duration: Duration(seconds: 1)),
                      );
                    },
                    child: const Icon(Icons.copy, size: 12, color: Color(0xFF72707D)),
                  ),
                ],
              ),
              const SizedBox(height: 8),
            ],
            Text(
              msg.text,
              style: const TextStyle(color: Color(0xFFF1F1F1), fontSize: 13, height: 1.45),
            ),
            if (msg.citations.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                '${msg.citations.length} Grounded Source Citations',
                style: const TextStyle(color: Color(0xFFBAA7D1), fontSize: 10, fontWeight: FontWeight.bold),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
