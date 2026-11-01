import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/api_provider.dart';
import '../core/api_client.dart';
import '../widgets/celestial_energy_widget.dart';

class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen> {
  bool _isChecking = true;
  bool _isConnected = false;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    _checkBackendConnection();
  }

  Future<void> _checkBackendConnection() async {
    setState(() {
      _isChecking = true;
      _errorMessage = '';
    });

    try {
      final api = ref.read(apiServiceProvider);
      final isHealthy = await api.checkHealth();
      if (!mounted) return;
      if (isHealthy) {
        setState(() {
          _isConnected = true;
          _isChecking = false;
        });
        await Future.delayed(const Duration(milliseconds: 500));
        if (mounted) context.go('/');
      } else {
        setState(() {
          _isConnected = false;
          _isChecking = false;
          _errorMessage = 'Backend reported non-healthy status.';
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isConnected = false;
        _isChecking = false;
        _errorMessage =
            'Unable to reach backend at ${ApiClient().currentBaseUrl}';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 36),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 90,
                height: 90,
                decoration: BoxDecoration(
                  color: const Color(0xFF08070B),
                  borderRadius: BorderRadius.circular(26),
                  border: Border.all(color: const Color(0xFF1A1625)),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x334B37B2),
                      blurRadius: 35,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: const Center(child: CelestialEnergyWidget(size: 82)),
              ),
              const SizedBox(height: 24),
              const Text(
                'Smart Invoice',
                style: TextStyle(
                  color: Color(0xFFF1F1F1),
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'AUTONOMOUS SYSTEMS',
                style: TextStyle(
                  color: Color(0xFF72707D),
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 1.5,
                ),
              ),
              const SizedBox(height: 48),
              if (_isChecking) ...[
                const SizedBox(
                  width: 22,
                  height: 22,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Color(0xFFBAA7D1),
                  ),
                ),
                const SizedBox(height: 14),
                const Text(
                  'Connecting to engine...',
                  style: TextStyle(color: Color(0xFF72707D), fontSize: 12),
                ),
              ] else if (!_isConnected) ...[
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0E0C16),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: const Color(0xFF1A1625)),
                  ),
                  child: Text(
                    _errorMessage,
                    textAlign: TextAlign.center,
                    style:
                        const TextStyle(color: Color(0xFFFCA5A5), fontSize: 11),
                  ),
                ),
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    ElevatedButton(
                      onPressed: _checkBackendConnection,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF4B37B2),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                      child: const Text('Retry'),
                    ),
                    const SizedBox(width: 10),
                    OutlinedButton(
                      onPressed: () => context.go('/settings'),
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Color(0xFF1A1625)),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                      child: const Text('Configure URL'),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextButton(
                  onPressed: () => context.go('/'),
                  child: const Text(
                    'Preview Workspace',
                    style: TextStyle(color: Color(0xFF72707D), fontSize: 12),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
