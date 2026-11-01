class CitationModel {
  final String? filename;
  final String? invoiceNumber;
  final String? vendor;
  final int? pageNumber;
  final String? snippet;

  CitationModel({
    this.filename,
    this.invoiceNumber,
    this.vendor,
    this.pageNumber,
    this.snippet,
  });

  factory CitationModel.fromJson(Map<String, dynamic> json) {
    return CitationModel(
      filename: json['filename'],
      invoiceNumber: json['invoice_number'],
      vendor: json['vendor'],
      pageNumber: json['page_number'],
      snippet: json['snippet'],
    );
  }
}

class ChatMessageModel {
  final String id;
  final bool isUser;
  final String text;
  final String? queryType;
  final List<CitationModel> citations;
  final Map<String, dynamic>? verifiedTotals;
  final bool isFallback;
  final String timestamp;

  ChatMessageModel({
    required this.id,
    required this.isUser,
    required this.text,
    this.queryType,
    this.citations = const [],
    this.verifiedTotals,
    this.isFallback = false,
    required this.timestamp,
  });
}

