import 'dart:ui';

import 'package:flutter/material.dart';

class CosmicGlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry margin;
  final double borderRadius;
  final bool enableBlur;
  final VoidCallback? onTap;

  const CosmicGlassCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(20),
    this.margin = EdgeInsets.zero,
    this.borderRadius = 22,
    this.enableBlur = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final cardContent = Container(
      padding: padding,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(borderRadius),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xDD261936), Color(0xEA100C1C), Color(0xDD20152E)],
          stops: [0.0, 0.55, 1.0],
        ),
        border: Border.all(
          color: const Color(0x2EB8A0F8), // rgba(184, 160, 248, 0.18)
          width: 1.0,
        ),
        boxShadow: const [
          BoxShadow(
            color: Color(0x3D000000),
            blurRadius: 30,
            offset: Offset(0, 10),
          ),
          BoxShadow(color: Color(0x126B42CD), blurRadius: 20),
        ],
      ),
      child: child,
    );

    Widget effectiveWidget;
    // On budget devices or when blur is active, wrap in lightweight BackdropFilter
    if (enableBlur && !MediaQuery.of(context).disableAnimations) {
      effectiveWidget = ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 6, sigmaY: 6),
          child: cardContent,
        ),
      );
    } else {
      effectiveWidget = cardContent;
    }

    if (onTap != null) {
      return Padding(
        padding: margin,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(borderRadius),
          child: effectiveWidget,
        ),
      );
    }

    return Padding(padding: margin, child: effectiveWidget);
  }
}
