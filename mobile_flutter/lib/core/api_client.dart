import 'package:dio/dio.dart';

class ApiClient {
  static const String defaultBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000/api',
  );

  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;

  late Dio dio;
  String _currentBaseUrl = defaultBaseUrl;

  ApiClient._internal() {
    _initDio(_currentBaseUrl);
  }

  void _initDio(String baseUrl) {
    dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          return handler.next(options);
        },
        onResponse: (response, handler) {
          return handler.next(response);
        },
        onError: (DioException e, handler) {
          return handler.next(e);
        },
      ),
    );
  }

  String get currentBaseUrl => _currentBaseUrl;

  void updateBaseUrl(String newUrl) {
    var formatted = newUrl.trim();
    if (!formatted.endsWith('/api')) {
      if (formatted.endsWith('/')) {
        formatted = '${formatted}api';
      } else {
        formatted = '$formatted/api';
      }
    }
    _currentBaseUrl = formatted;
    dio.options.baseUrl = formatted;
  }
}

