import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:smart_invoice_mobile/core/effects.dart';
import 'package:smart_invoice_mobile/core/theme.dart';
import 'package:smart_invoice_mobile/widgets/celestial_energy_widget.dart';

void main() {
  Widget core({required bool reduced}) => MaterialApp(
        theme: AppTheme.darkTheme,
        // Do not count MaterialApp's unrelated theme interpolation as a core ticker.
        themeAnimationDuration: Duration.zero,
        home: MediaQuery(
          data: MediaQueryData(disableAnimations: reduced),
          child: const Center(child: CelestialEnergyWidget(size: 200)),
        ),
      );

  testWidgets(
      'system reduced motion renders a still core with no scheduled ticker',
      (tester) async {
    await tester.pumpWidget(core(reduced: true));
    await tester.pump(const Duration(seconds: 1));
    expect(find.byType(CelestialEnergyWidget), findsOneWidget);
    expect(tester.binding.transientCallbackCount, 0);
    expect(tester.takeException(), isNull);
  });

  testWidgets('preference changes stop the active ticker and unmount cleans up',
      (tester) async {
    await tester.pumpWidget(core(reduced: false));
    await tester.pump(const Duration(milliseconds: 100));
    expect(tester.binding.transientCallbackCount, greaterThan(0));
    await tester.pumpWidget(core(reduced: true));
    await tester.pump();
    expect(tester.binding.transientCallbackCount, 0);
    await tester.pumpWidget(core(reduced: false));
    await tester.pump();
    expect(tester.binding.transientCallbackCount, greaterThan(0));
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
    expect(tester.binding.transientCallbackCount, 0);
    expect(tester.takeException(), isNull);
  });

  testWidgets('backgrounding suspends native decoration and resume restarts it',
      (tester) async {
    tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.resumed);
    await tester.pumpWidget(const MaterialApp(
        home: CosmicEnvironment(
      reducedEffects: false,
      child: Center(child: CelestialEnergyWidget(size: 200)),
    )));
    await tester.pump(const Duration(milliseconds: 50));
    expect(tester.binding.transientCallbackCount, greaterThan(0));
    tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.paused);
    await tester.pump();
    expect(tester.binding.transientCallbackCount, 0);
    tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.resumed);
    await tester.pump();
    expect(tester.binding.transientCallbackCount, greaterThan(0));
    await tester.pumpWidget(const SizedBox.shrink());
    expect(tester.takeException(), isNull);
  });
}
