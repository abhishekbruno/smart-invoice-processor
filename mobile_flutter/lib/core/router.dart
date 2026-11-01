import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../screens/splash_screen.dart';
import '../screens/dashboard_screen.dart';
import '../screens/invoice_list_screen.dart';
import '../screens/invoice_detail_screen.dart';
import '../screens/invoice_upload_screen.dart';
import '../screens/chat_screen.dart';
import '../screens/analytics_screen.dart';
import '../screens/automation_screen.dart';
import '../screens/settings_screen.dart';

final GlobalKey<NavigatorState> _rootNavigatorKey = GlobalKey<NavigatorState>();
final GlobalKey<NavigatorState> _shellNavigatorKey =
    GlobalKey<NavigatorState>();

CustomTransitionPage<void> _cosmicPage(
  BuildContext context,
  GoRouterState state,
  Widget child,
) {
  final reduced = MediaQuery.of(context).disableAnimations;
  return CustomTransitionPage<void>(
    key: state.pageKey,
    child: child,
    transitionDuration:
        reduced ? Duration.zero : const Duration(milliseconds: 220),
    reverseTransitionDuration:
        reduced ? Duration.zero : const Duration(milliseconds: 180),
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      if (MediaQuery.of(context).disableAnimations) return child;
      final curve = animation.drive(CurveTween(curve: Curves.easeOut));
      return FadeTransition(
        opacity: curve,
        child: SlideTransition(
          position: Tween<Offset>(
            begin: const Offset(0, .025),
            end: Offset.zero,
          ).animate(curve),
          child: child,
        ),
      );
    },
  );
}

final router = GoRouter(
  navigatorKey: _rootNavigatorKey,
  initialLocation: '/splash',
  routes: [
    GoRoute(path: '/splash', builder: (context, state) => const SplashScreen()),
    ShellRoute(
      navigatorKey: _shellNavigatorKey,
      builder: (context, state, child) {
        return ScaffoldWithNav(child: child);
      },
      routes: [
        GoRoute(
          path: '/',
          pageBuilder: (context, state) =>
              _cosmicPage(context, state, const DashboardScreen()),
        ),
        GoRoute(
          path: '/invoices',
          pageBuilder: (context, state) =>
              _cosmicPage(context, state, const InvoiceListScreen()),
          routes: [
            GoRoute(
              path: ':id',
              pageBuilder: (context, state) {
                final id = int.parse(state.pathParameters['id']!);
                return _cosmicPage(
                  context,
                  state,
                  InvoiceDetailScreen(invoiceId: id),
                );
              },
            ),
          ],
        ),
        GoRoute(
          path: '/upload',
          pageBuilder: (context, state) =>
              _cosmicPage(context, state, const InvoiceUploadScreen()),
        ),
        GoRoute(
          path: '/chat',
          pageBuilder: (context, state) =>
              _cosmicPage(context, state, const ChatScreen()),
        ),
        GoRoute(
          path: '/analytics',
          pageBuilder: (context, state) =>
              _cosmicPage(context, state, const AnalyticsScreen()),
        ),
        GoRoute(
          path: '/automation',
          pageBuilder: (context, state) =>
              _cosmicPage(context, state, const AutomationScreen()),
        ),
        GoRoute(
          path: '/settings',
          pageBuilder: (context, state) =>
              _cosmicPage(context, state, const SettingsScreen()),
        ),
      ],
    ),
  ],
);

class ScaffoldWithNav extends StatelessWidget {
  final Widget child;
  const ScaffoldWithNav({super.key, required this.child});

  int _calculateSelectedIndex(BuildContext context) {
    final String location = GoRouterState.of(context).uri.path;
    if (location.startsWith('/invoices')) return 1;
    if (location.startsWith('/chat')) return 2;
    if (location.startsWith('/analytics')) return 3;
    if (location.startsWith('/settings')) return 4;
    return 0;
  }

  void _onItemTapped(int index, BuildContext context) {
    switch (index) {
      case 0:
        context.go('/');
        break;
      case 1:
        context.go('/invoices');
        break;
      case 2:
        context.go('/chat');
        break;
      case 3:
        context.go('/analytics');
        break;
      case 4:
        context.go('/settings');
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentIndex = _calculateSelectedIndex(context);

    return Scaffold(
      body: child,
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: Color(0xFF020203),
          border: Border(top: BorderSide(color: Color(0xFF1A1625), width: 1.0)),
        ),
        child: NavigationBar(
          selectedIndex: currentIndex,
          onDestinationSelected: (idx) => _onItemTapped(idx, context),
          backgroundColor: Colors.transparent,
          indicatorColor: const Color(0xFF4B37B2).withOpacity(0.25),
          height: 62,
          destinations: const [
            NavigationDestination(
              icon: Icon(Icons.dashboard_outlined, size: 20),
              selectedIcon: Icon(
                Icons.dashboard,
                size: 20,
                color: Color(0xFFBAA7D1),
              ),
              label: 'Overview',
            ),
            NavigationDestination(
              icon: Icon(Icons.receipt_outlined, size: 20),
              selectedIcon: Icon(
                Icons.receipt,
                size: 20,
                color: Color(0xFFBAA7D1),
              ),
              label: 'Invoices',
            ),
            NavigationDestination(
              icon: Icon(Icons.auto_awesome_outlined, size: 20),
              selectedIcon: Icon(
                Icons.auto_awesome,
                size: 20,
                color: Color(0xFFBAA7D1),
              ),
              label: 'Ask AI',
            ),
            NavigationDestination(
              icon: Icon(Icons.bar_chart_outlined, size: 20),
              selectedIcon: Icon(
                Icons.bar_chart,
                size: 20,
                color: Color(0xFFBAA7D1),
              ),
              label: 'Insights',
            ),
            NavigationDestination(
              icon: Icon(Icons.tune_outlined, size: 20),
              selectedIcon: Icon(
                Icons.tune,
                size: 20,
                color: Color(0xFFBAA7D1),
              ),
              label: 'Settings',
            ),
          ],
        ),
      ),
    );
  }
}
