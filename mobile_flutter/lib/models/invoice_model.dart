class LineItemModel {
  final int? id;
  final String description;
  final double? quantity;
  final double? unitPrice;
  final double? amount;

  LineItemModel({
    this.id,
    required this.description,
    this.quantity,
    this.unitPrice,
    this.amount,
  });

  factory LineItemModel.fromJson(Map<String, dynamic> json) {
    return LineItemModel(
      id: json['id'],
      description: json['description'] ?? '',
      quantity: (json['quantity'] as num?)?.toDouble(),
      unitPrice: (json['unit_price'] as num?)?.toDouble(),
      amount: (json['amount'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'description': description,
      'quantity': quantity,
      'unit_price': unitPrice,
      'amount': amount,
    };
  }
}

class InvoiceListItemModel {
  final int id;
  final String? invoiceNumber;
  final String? vendorName;
  final String? invoiceDate;
  final String? dueDate;
  final double? totalAmount;
  final String currency;
  final double? convertedAmount;
  final String? convertedCurrency;
  final String status;
  final bool isDuplicate;
  final int? duplicateOfId;
  final String? duplicateReason;
  final String createdAt;

  InvoiceListItemModel({
    required this.id,
    this.invoiceNumber,
    this.vendorName,
    this.invoiceDate,
    this.dueDate,
    this.totalAmount,
    required this.currency,
    this.convertedAmount,
    this.convertedCurrency,
    required this.status,
    required this.isDuplicate,
    this.duplicateOfId,
    this.duplicateReason,
    required this.createdAt,
  });

  factory InvoiceListItemModel.fromJson(Map<String, dynamic> json) {
    return InvoiceListItemModel(
      id: json['id'] as int,
      invoiceNumber: json['invoice_number'],
      vendorName: json['vendor_name'],
      invoiceDate: json['invoice_date'],
      dueDate: json['due_date'],
      totalAmount: (json['total_amount'] as num?)?.toDouble(),
      currency: json['currency'] ?? 'USD',
      convertedAmount: (json['converted_amount'] as num?)?.toDouble(),
      convertedCurrency: json['converted_currency'] ?? 'INR',
      status: json['status'] ?? 'processed',
      isDuplicate: json['is_duplicate'] ?? false,
      duplicateOfId: json['duplicate_of_id'],
      duplicateReason: json['duplicate_reason'],
      createdAt: json['created_at'] ?? '',
    );
  }
}

class InvoiceDetailModel extends InvoiceListItemModel {
  final String? customerName;
  final double? subtotal;
  final double? taxAmount;
  final String? paymentStatus;
  final String? sourceFilePath;
  final String fileHash;
  final Map<String, dynamic> confidenceScores;
  final List<String> extractionNotes;
  final List<LineItemModel> lineItems;

  InvoiceDetailModel({
    required super.id,
    super.invoiceNumber,
    super.vendorName,
    super.invoiceDate,
    super.dueDate,
    super.totalAmount,
    required super.currency,
    super.convertedAmount,
    super.convertedCurrency,
    required super.status,
    required super.isDuplicate,
    super.duplicateOfId,
    super.duplicateReason,
    required super.createdAt,
    this.customerName,
    this.subtotal,
    this.taxAmount,
    this.paymentStatus,
    this.sourceFilePath,
    required this.fileHash,
    required this.confidenceScores,
    required this.extractionNotes,
    required this.lineItems,
  });

  factory InvoiceDetailModel.fromJson(Map<String, dynamic> json) {
    final rawItems = json['line_items'] as List<dynamic>? ?? [];
    final items = rawItems
        .map((item) => LineItemModel.fromJson(item as Map<String, dynamic>))
        .toList();

    final notes = (json['extraction_notes'] as List<dynamic>? ?? [])
        .map((e) => e.toString())
        .toList();

    return InvoiceDetailModel(
      id: json['id'] as int,
      invoiceNumber: json['invoice_number'],
      vendorName: json['vendor_name'],
      invoiceDate: json['invoice_date'],
      dueDate: json['due_date'],
      totalAmount: (json['total_amount'] as num?)?.toDouble(),
      currency: json['currency'] ?? 'USD',
      convertedAmount: (json['converted_amount'] as num?)?.toDouble(),
      convertedCurrency: json['converted_currency'] ?? 'INR',
      status: json['status'] ?? 'processed',
      isDuplicate: json['is_duplicate'] ?? false,
      duplicateOfId: json['duplicate_of_id'],
      duplicateReason: json['duplicate_reason'],
      createdAt: json['created_at'] ?? '',
      customerName: json['customer_name'],
      subtotal: (json['subtotal'] as num?)?.toDouble(),
      taxAmount: (json['tax_amount'] as num?)?.toDouble(),
      paymentStatus: json['payment_status'],
      sourceFilePath: json['source_file_path'],
      fileHash: json['file_hash'] ?? '',
      confidenceScores: json['confidence_scores'] as Map<String, dynamic>? ?? {},
      extractionNotes: notes,
      lineItems: items,
    );
  }
}

