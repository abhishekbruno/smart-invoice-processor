import 'dart:math' as math;

import 'package:flutter/material.dart';

class CelestialEnergyWidget extends StatefulWidget {
  final double size;
  const CelestialEnergyWidget({super.key, this.size = 64});

  @override
  State<CelestialEnergyWidget> createState() => _CelestialEnergyWidgetState();
}

class _CelestialEnergyWidgetState extends State<CelestialEnergyWidget>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 12),
    );
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.of(context).disableAnimations || !TickerMode.of(context)) {
      _controller.stop();
    } else if (!_controller.isAnimating) {
      _controller.repeat();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return CustomPaint(
            size: Size(widget.size, widget.size),
            painter: _CelestialPainter(
              progress: _controller.value,
              reduced: MediaQuery.of(context).disableAnimations,
            ),
          );
        },
      ),
    );
  }
}

class _CelestialPainter extends CustomPainter {
  final double progress;
  final bool reduced;
  _CelestialPainter({required this.progress, required this.reduced});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;

    // 1. Central Ambient Glow
    final glowPaint = Paint()
      ..shader = RadialGradient(
        colors: [
          const Color(0xFF4B37B2).withOpacity(0.45),
          const Color(0xFF8879A7).withOpacity(0.20),
          Colors.transparent,
        ],
        stops: const [0.0, 0.55, 1.0],
      ).createShader(Rect.fromCircle(center: center, radius: radius));
    canvas.drawCircle(center, radius, glowPaint);

    // 2. Orbital Filaments
    final time = progress * 2 * math.pi;
    final filamentColors = [
      const Color(0xFFBAA7D1),
      const Color(0xFF4B37B2),
      const Color(0xFF8879A7),
      const Color(0xFF6FADFF),
    ];

    for (int i = 0; i < 4; i++) {
      final angleOffset = (i * math.pi / 2) + time * (i % 2 == 0 ? 1.0 : -0.7);
      final tilt = (i * 0.45) - 0.3;

      final path = Path();
      const points = 36;
      final rx = radius * 0.78;
      final ry = radius * (0.35 + (i * 0.12));

      for (int step = 0; step <= points; step++) {
        final t = (step / points) * 2 * math.pi;
        final ripple = 1 + math.sin(t * 4 + time + i) * .045;
        final x = rx * math.cos(t) * ripple;
        final y = ry * math.sin(t) * ripple;

        // Rotate by tilt & angle
        final rotX = x * math.cos(angleOffset) - y * math.sin(angleOffset);
        final rotY =
            (x * math.sin(angleOffset) + y * math.cos(angleOffset)) *
            math.cos(tilt);

        final pt = Offset(center.dx + rotX, center.dy + rotY);
        if (step == 0) {
          path.moveTo(pt.dx, pt.dy);
        } else {
          path.lineTo(pt.dx, pt.dy);
        }
      }

      final strokePaint = Paint()
        ..color = filamentColors[i].withOpacity(0.55)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.2;
      canvas.drawPath(path, strokePaint);
    }

    // 3. Central Bioluminescent Core
    final corePaint = Paint()
      ..shader = RadialGradient(
        colors: [
          const Color(0xFFF1F1F1).withOpacity(0.9),
          const Color(0xFFBAA7D1).withOpacity(0.5),
          Colors.transparent,
        ],
        stops: const [0.0, 0.4, 1.0],
      ).createShader(Rect.fromCircle(center: center, radius: radius * 0.35));
    canvas.drawCircle(center, radius * 0.35, corePaint);

    // Sparse surface motes and a soft outward wave; no extra animation controller.
    final particlePaint = Paint()..color = const Color(0x99C7B1F2);
    for (var i = 0; i < 18; i++) {
      final angle = i * 2.39996 + time * .25;
      final r = radius * (.62 + .14 * math.sin(i * 1.7));
      canvas.drawCircle(
        center + Offset(math.cos(angle) * r, math.sin(angle) * r),
        .65,
        particlePaint,
      );
    }
    if (!reduced && progress < .3) {
      final age = progress / .3;
      final wave = Paint()
        ..color = const Color(0xFFBCA0EE)
            .withOpacity(math.sin(age * math.pi) * .2)
        ..style = PaintingStyle.stroke
        ..strokeWidth = .7;
      canvas.drawCircle(center, radius * (.72 + age * .25), wave);
    }
  }

  @override
  bool shouldRepaint(covariant _CelestialPainter oldDelegate) {
    return oldDelegate.progress != progress || oldDelegate.reduced != reduced;
  }
}
