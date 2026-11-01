import 'package:flutter/material.dart';

class AppTheme {
  // Deep Cosmic Violet Glass Palette
  static const Color background = Color(0xFF020203);
  static const Color surface = Color(0xFF0C091C);
  static const Color surfaceLight = Color(0xFF140F2E);
  static const Color border = Color(0xFF1A1625);
  static const Color borderSubtle = Color(0xFF13101B);

  // Coordinated Typography Palette
  static const Color textPrimaryHeading = Color(0xFFF1EDF8);
  static const Color textMetallicHighlight = Color(0xFFE5DDFC);
  static const Color textSecondaryHeading = Color(0xFFD5CDE5);
  static const Color textBody = Color(0xFFB8B2C8);
  static const Color textMuted = Color(0xFF9892AB);
  static const Color textAccent = Color(0xFFBBA8F1);

  // Violet Glass Tokens
  static const Color glassBorder = Color(0x2EB8A0F8); // rgba(184, 160, 248, 0.18)
  static const Color glassHighlight = Color(0x1AD8C9FF); // rgba(216, 201, 255, 0.10)
  static const Color glassGlow = Color(0x126B42CD);

  static const Color accentLilac = Color(0xFF8879A7);
  static const Color accentViolet = Color(0xFF4B37B2);
  static const Color accentLavender = Color(0xFFBAA7D1);
  static const Color accentPlum = Color(0xFF4B334D);
  static const Color accentBerry = Color(0xFF923F53);

  static const Color primary = Color(0xFFBBA8F1);
  static const Color primarySubtle = Color(0x334B37B2);
  static const Color accent = Color(0xFF8879A7);

  static const Color success = Color(0xFF10B981);
  static const Color warning = Color(0xFFF59E0B);
  static const Color danger = Color(0xFFF43F5E);

  static const Color textPrimary = Color(0xFFF1EDF8);
  static const Color textSecondary = Color(0xFFB8B2C8);

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: Colors.transparent,
      primaryColor: accentViolet,
      colorScheme: const ColorScheme.dark(
        primary: textAccent,
        secondary: accentLilac,
        surface: surface,
        error: danger,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: textPrimaryHeading,
      ),
      fontFamily: 'Manrope',
      appBarTheme: const AppBarTheme(
        backgroundColor: background,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: textPrimaryHeading,
          fontFamily: 'Sora',
          fontSize: 18,
          fontWeight: FontWeight.w600,
          letterSpacing: -0.3,
        ),
        iconTheme: IconThemeData(color: textPrimaryHeading, size: 20),
      ),
      cardTheme: CardThemeData(
        color: surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: glassBorder, width: 1.0),
        ),
        margin: EdgeInsets.zero,
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: background,
        elevation: 0,
        indicatorColor: primarySubtle,
        labelTextStyle: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) {
            return const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: textAccent,
              fontFamily: 'Manrope',
            );
          }
          return const TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.normal,
            color: textMuted,
            fontFamily: 'Manrope',
          );
        }),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceLight,
        hintStyle: const TextStyle(color: textMuted, fontSize: 13, fontFamily: 'Manrope'),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: glassBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: glassBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: textAccent, width: 1.2),
        ),
      ),
    );
  }
}
