import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:go_router/go_router.dart';
import '../providers/api_provider.dart';
import '../providers/invoice_provider.dart';
import '../providers/analytics_provider.dart';

class InvoiceUploadScreen extends ConsumerStatefulWidget {
  const InvoiceUploadScreen({super.key});

  @override
  ConsumerState<InvoiceUploadScreen> createState() => _InvoiceUploadScreenState();
}

class _InvoiceUploadScreenState extends ConsumerState<InvoiceUploadScreen> {
  String? _selectedFilePath;
  String? _selectedFileName;
  int? _fileSize;
  bool _isUploading = false;
  Map<String, dynamic>? _uploadResult;
  String? _errorMessage;

  Future<void> _pickFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf'],
      );

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.first;
        if (file.path != null) {
          setState(() {
            _selectedFilePath = file.path;
            _selectedFileName = file.name;
            _fileSize = file.size;
            _uploadResult = null;
            _errorMessage = null;
          });
        }
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to select PDF: $e';
      });
    }
  }

  Future<void> _uploadAndProcess() async {
    if (_selectedFilePath == null) return;

    setState(() {
      _isUploading = true;
      _errorMessage = null;
      _uploadResult = null;
    });

    try {
      final api = ref.read(apiServiceProvider);
      final res = await api.uploadInvoice(_selectedFilePath!);
      setState(() {
        _uploadResult = res;
      });
      ref.invalidate(invoicesListProvider);
      ref.invalidate(fullAnalyticsProvider);
    } catch (e) {
      setState(() {
        _errorMessage = 'Extraction error: $e';
      });
    } finally {
      setState(() {
        _isUploading = false;
      });
    }
  }

  void _reset() {
    setState(() {
      _selectedFilePath = null;
      _selectedFileName = null;
      _fileSize = null;
      _uploadResult = null;
      _errorMessage = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        title: const Text('Upload Document', style: TextStyle(color: Color(0xFFF1F1F1), fontSize: 17, fontWeight: FontWeight.w600)),
        backgroundColor: const Color(0xFF020203),
        elevation: 0,
        centerTitle: false,
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        children: [
          const Text(
            'SELECT DOCUMENT',
            style: TextStyle(
              color: Color(0xFF72707D),
              fontSize: 10,
              fontWeight: FontWeight.w600,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),

          // Upload Dropzone Card
          InkWell(
            onTap: _isUploading ? null : _pickFile,
            borderRadius: BorderRadius.circular(16),
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 36, horizontal: 20),
              decoration: BoxDecoration(
                color: const Color(0xFF08070B),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: _selectedFilePath != null
                      ? const Color(0xFF8879A7)
                      : const Color(0xFF1A1625),
                  width: _selectedFilePath != null ? 1.5 : 1.0,
                ),
              ),
              child: Column(
                children: [
                  Container(
                    width: 52,
                    height: 52,
                    decoration: BoxDecoration(
                      color: _selectedFilePath != null
                          ? const Color(0xFF4B37B2).withOpacity(0.2)
                          : const Color(0xFF14121E),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Icon(
                      _selectedFilePath != null ? Icons.picture_as_pdf_outlined : Icons.upload_file_outlined,
                      color: _selectedFilePath != null ? const Color(0xFFBAA7D1) : const Color(0xFF72707D),
                      size: 26,
                    ),
                  ),
                  const SizedBox(height: 16),
                  if (_selectedFileName != null) ...[
                    Text(
                      _selectedFileName!,
                      style: const TextStyle(
                        color: Color(0xFFF1F1F1),
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${((_fileSize ?? 0) / 1024).toStringAsFixed(1)} KB • Ready for extraction',
                      style: const TextStyle(color: Color(0xFF10B981), fontSize: 12),
                    ),
                  ] else ...[
                    const Text(
                      'Tap to choose PDF from device',
                      style: TextStyle(
                        color: Color(0xFFF1F1F1),
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Supports standard digital PDF invoices',
                      style: TextStyle(color: Color(0xFF72707D), fontSize: 11),
                    ),
                  ],
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Action Buttons
          if (_selectedFilePath != null && _uploadResult == null) ...[
            Container(
              width: double.infinity,
              height: 44,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF4B37B2), Color(0xFF8879A7)],
                ),
                borderRadius: BorderRadius.circular(10),
              ),
              child: ElevatedButton(
                onPressed: _isUploading ? null : _uploadAndProcess,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.transparent,
                  shadowColor: Colors.transparent,
                  foregroundColor: Colors.white,
                  elevation: 0,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                child: _isUploading
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Text(
                        'Process & Extract Document',
                        style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                      ),
              ),
            ),
            const SizedBox(height: 8),
            SizedBox(
              width: double.infinity,
              height: 40,
              child: TextButton(
                onPressed: _isUploading ? null : _reset,
                child: const Text('Choose a different file', style: TextStyle(color: Color(0xFF72707D), fontSize: 12)),
              ),
            ),
          ],

          // Error Display
          if (_errorMessage != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF4B334D).withOpacity(0.5),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF923F53)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline, color: Color(0xFFFCA5A5), size: 18),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(color: Color(0xFFFCA5A5), fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ],

          // Success Result Card
          if (_uploadResult != null) ...[
            const SizedBox(height: 20),
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
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: const Color(0xFF10B981).withOpacity(0.15),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Icon(Icons.check, color: Color(0xFF34D399), size: 16),
                      ),
                      const SizedBox(width: 10),
                      const Text(
                        'Extracted Successfully',
                        style: TextStyle(
                          color: Color(0xFFF1F1F1),
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const Spacer(),
                      Text(
                        'ID #${_uploadResult!['invoice_id'] ?? ''}',
                        style: const TextStyle(color: Color(0xFF72707D), fontSize: 12),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Divider(color: Color(0xFF1A1625), height: 1),
                  const SizedBox(height: 12),
                  _buildResultRow('Vendor', _uploadResult!['vendor'] ?? 'N/A'),
                  _buildResultRow('Invoice Number', _uploadResult!['invoice_number'] ?? 'N/A'),
                  _buildResultRow(
                    'Total Amount',
                    '${_uploadResult!['currency'] ?? ''} ${_uploadResult!['total_amount'] ?? ''}',
                  ),
                  _buildResultRow(
                    'Status',
                    _uploadResult!['is_duplicate'] == true ? 'Suspected Duplicate' : 'Verified Unique',
                    isHighlight: _uploadResult!['is_duplicate'] == true,
                  ),
                  const SizedBox(height: 18),
                  Row(
                    children: [
                      Expanded(
                        child: SizedBox(
                          height: 40,
                          child: OutlinedButton(
                            onPressed: _reset,
                            style: OutlinedButton.styleFrom(
                              foregroundColor: const Color(0xFFF1F1F1),
                              backgroundColor: const Color(0xFF14121E),
                              side: const BorderSide(color: Color(0xFF1A1625)),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                            ),
                            child: const Text('Upload Another', style: TextStyle(fontSize: 12)),
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      if (_uploadResult!['invoice_id'] != null)
                        Expanded(
                          child: Container(
                            height: 40,
                            decoration: BoxDecoration(
                              gradient: const LinearGradient(
                                colors: [Color(0xFF4B37B2), Color(0xFF8879A7)],
                              ),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: ElevatedButton(
                              onPressed: () {
                                final id = _uploadResult!['invoice_id'];
                                context.push('/invoices/$id');
                              },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.transparent,
                                shadowColor: Colors.transparent,
                                foregroundColor: Colors.white,
                                elevation: 0,
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                              ),
                              child: const Text('Inspect Details', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildResultRow(String label, String value, {bool isHighlight = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Color(0xFF72707D), fontSize: 12)),
          Text(
            value,
            style: TextStyle(
              color: isHighlight ? const Color(0xFF923F53) : const Color(0xFFF1F1F1),
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
