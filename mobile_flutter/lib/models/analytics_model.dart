class AnalyticsSummaryModel {
  final int totalInvoices;
  final int eligibleInvoices;
  final int processedCleanly;
  final int needsReview;
  final int verifiedInvoices;
  final int suspectedDuplicates;
  final double totalSpending;
  final String displayCurrency;
  final String formattedTotal;
  final int vendorCount;
  final String effectiveRateSource;

  AnalyticsSummaryModel({
    required this.totalInvoices,
    required this.eligibleInvoices,
    required this.processedCleanly,
    required this.needsReview,
    required this.verifiedInvoices,
    required this.suspectedDuplicates,
    required this.totalSpending,
    required this.displayCurrency,
    required this.formattedTotal,
    required this.vendorCount,
    required this.effectiveRateSource,
  });

  factory AnalyticsSummaryModel.fromJson(Map<String, dynamic> json) {
    return AnalyticsSummaryModel(
      totalInvoices: json['total_invoices'] ?? 0,
      eligibleInvoices: json['eligible_invoices'] ?? 0,
      processedCleanly: json['processed_cleanly'] ?? 0,
      needsReview: json['needs_review'] ?? 0,
      verifiedInvoices: json['verified_invoices'] ?? 0,
      suspectedDuplicates: json['suspected_duplicates'] ?? 0,
      totalSpending: (json['total_spending'] as num?)?.toDouble() ?? 0.0,
      displayCurrency: json['display_currency'] ?? 'INR',
      formattedTotal: json['formatted_total'] ?? '₹0.00',
      vendorCount: json['vendor_count'] ?? 0,
      effectiveRateSource: json['effective_rate_source'] ?? 'Frankfurter / ECB',
    );
  }
}

class MonthlySpendingModel {
  final String month;
  final double convertedSpent;
  final int invoiceCount;
  final String displayCurrency;

  MonthlySpendingModel({
    required this.month,
    required this.convertedSpent,
    required this.invoiceCount,
    required this.displayCurrency,
  });

  factory MonthlySpendingModel.fromJson(Map<String, dynamic> json) {
    return MonthlySpendingModel(
      month: json['month'] ?? '',
      convertedSpent: (json['converted_spent'] as num?)?.toDouble() ?? 0.0,
      invoiceCount: json['invoice_count'] ?? 0,
      displayCurrency: json['display_currency'] ?? 'INR',
    );
  }
}

class VendorSpendingModel {
  final String vendor;
  final double convertedSpent;
  final int invoiceCount;
  final String displayCurrency;

  VendorSpendingModel({
    required this.vendor,
    required this.convertedSpent,
    required this.invoiceCount,
    required this.displayCurrency,
  });

  factory VendorSpendingModel.fromJson(Map<String, dynamic> json) {
    return VendorSpendingModel(
      vendor: json['vendor'] ?? '',
      convertedSpent: (json['converted_spent'] as num?)?.toDouble() ?? 0.0,
      invoiceCount: json['invoice_count'] ?? 0,
      displayCurrency: json['display_currency'] ?? 'INR',
    );
  }
}

class CurrencyDistributionModel {
  final String currency;
  final int invoiceCount;
  final double originalTotal;
  final double convertedTotal;
  final String displayCurrency;

  CurrencyDistributionModel({
    required this.currency,
    required this.invoiceCount,
    required this.originalTotal,
    required this.convertedTotal,
    required this.displayCurrency,
  });

  factory CurrencyDistributionModel.fromJson(Map<String, dynamic> json) {
    return CurrencyDistributionModel(
      currency: json['currency'] ?? '',
      invoiceCount: json['invoice_count'] ?? 0,
      originalTotal: (json['original_total'] as num?)?.toDouble() ?? 0.0,
      convertedTotal: (json['converted_total'] as num?)?.toDouble() ?? 0.0,
      displayCurrency: json['display_currency'] ?? 'INR',
    );
  }
}

class ExpenseAnalyticsModel {
  final AnalyticsSummaryModel summary;
  final List<MonthlySpendingModel> monthlySpending;
  final List<VendorSpendingModel> vendorSpending;
  final List<CurrencyDistributionModel> currencyDistribution;

  ExpenseAnalyticsModel({
    required this.summary,
    required this.monthlySpending,
    required this.vendorSpending,
    required this.currencyDistribution,
  });

  factory ExpenseAnalyticsModel.fromJson(Map<String, dynamic> json) {
    final monthly = (json['monthly_spending'] as List<dynamic>? ?? [])
        .map((e) => MonthlySpendingModel.fromJson(e as Map<String, dynamic>))
        .toList();
    final vendors = (json['vendor_spending'] as List<dynamic>? ?? [])
        .map((e) => VendorSpendingModel.fromJson(e as Map<String, dynamic>))
        .toList();
    final currencies = (json['currency_distribution'] as List<dynamic>? ?? [])
        .map((e) => CurrencyDistributionModel.fromJson(e as Map<String, dynamic>))
        .toList();

    return ExpenseAnalyticsModel(
      summary: AnalyticsSummaryModel.fromJson(json['summary'] as Map<String, dynamic>),
      monthlySpending: monthly,
      vendorSpending: vendors,
      currencyDistribution: currencies,
    );
  }
}

