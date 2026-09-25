import 'package:flutter/material.dart';

class AppTheme {
  static const Color darkBackground = Color(0xFF1E1E2E);
  static const Color cardColor = Color(0xFF2A2A3D);
  static const Color goldAccent = Color(0xFFD4AF37);
  static const Color orangeButton = Color(0xFFFF9F43);
  static const Color textLight = Color(0xFFFFFFFF);
  static const Color textDim = Color(0xFFA0A0A0);

  static ThemeData get themeData {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: darkBackground,
      primaryColor: goldAccent,
      fontFamily: 'Cairo',
      colorScheme: const ColorScheme.dark(
        primary: goldAccent,
        secondary: orangeButton,
        surface: cardColor,
        background: darkBackground,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: cardColor,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          fontFamily: 'Cairo',
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: textLight,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: orangeButton,
          foregroundColor: Colors.white,
          textStyle: const TextStyle(
            fontFamily: 'Cairo',
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
        ),
      ),
      cardTheme: CardTheme(
        color: cardColor,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(15),
          side: const BorderSide(color: goldAccent, width: 0.5),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFF252538),
        hintStyle: const TextStyle(color: textDim, fontFamily: 'Cairo'),
        labelStyle: const TextStyle(color: goldAccent, fontFamily: 'Cairo'),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF3F3F5A)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: goldAccent, width: 1.5),
        ),
      ),
    );
  }
}
