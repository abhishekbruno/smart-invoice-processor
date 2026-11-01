import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Session-local preference. System accessibility always takes precedence.
final reducedEffectsProvider = StateProvider<bool>((ref) => false);

class CosmicEnvironment extends StatefulWidget {
  final Widget child;
  final bool reducedEffects;
  const CosmicEnvironment({
    super.key,
    required this.child,
    required this.reducedEffects,
  });
  @override
  State<CosmicEnvironment> createState() => _CosmicEnvironmentState();
}

class _CosmicEnvironmentState extends State<CosmicEnvironment>
    with WidgetsBindingObserver {
  bool _active =
      WidgetsBinding.instance.lifecycleState == null ||
      WidgetsBinding.instance.lifecycleState == AppLifecycleState.resumed;
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    setState(() => _active = state == AppLifecycleState.resumed);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final media = MediaQuery.of(context);
    return MediaQuery(
      data: media.copyWith(
        disableAnimations: media.disableAnimations || widget.reducedEffects,
      ),
      child: TickerMode(
        enabled: _active,
        child: Stack(
          fit: StackFit.expand,
          children: [
            const Positioned.fill(
              child: IgnorePointer(
                child: RepaintBoundary(
                  child: CustomPaint(painter: _SpacePainter()),
                ),
              ),
            ),
            widget.child,
          ],
        ),
      ),
    );
  }
}

class _SpacePainter extends CustomPainter {
  const _SpacePainter();
  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(
      Offset.zero & size,
      Paint()..color = const Color(0xFF05040B),
    );
    final glow = Paint()
      ..shader =
          const RadialGradient(
            colors: [Color(0x334F2B86), Color(0x10263865), Colors.transparent],
            stops: [0, 0.5, 1],
          ).createShader(
            Rect.fromCircle(
              center: Offset(size.width * .7, size.height * .25),
              radius: size.height * .65,
            ),
          );
    canvas.drawRect(Offset.zero & size, glow);
    final star = Paint()..color = const Color(0x668F81AD);
    for (var i = 0; i < 42; i++) {
      canvas.drawCircle(
        Offset(
          ((i * .618034) % 1) * size.width,
          ((i * .37213 + .07) % 1) * size.height,
        ),
        i % 7 == 0 ? 1 : .55,
        star,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _SpacePainter oldDelegate) => false;
}
