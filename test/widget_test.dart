import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:neshrblek/theme/app_theme.dart';

void main() {
  test('App theme check', () {
    final theme = AppTheme.themeData;
    expect(theme.scaffoldBackgroundColor, equals(const Color(0xFF1E1E2E)));
    expect(theme.primaryColor, equals(const Color(0xFFD4AF37)));
  });
}
