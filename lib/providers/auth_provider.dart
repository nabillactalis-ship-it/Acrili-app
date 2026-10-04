import 'package:flutter/material.dart';

class UserData {
  final String uid;
  final String name;
  final String email;
  final String phone;
  final String role; // 'customer', 'supplier', 'driver'
  final double balance;

  UserData({
    required this.uid,
    required this.name,
    required this.email,
    required this.phone,
    required this.role,
    this.balance = 0.0,
  });

  factory UserData.fromMap(String uid, Map<String, dynamic> map) {
    return UserData(
      uid: uid,
      name: map['name'] ?? '',
      email: map['email'] ?? '',
      phone: map['phone'] ?? '',
      role: map['role'] ?? map['type'] ?? 'customer',
      balance: (map['balance'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'email': email,
      'phone': phone,
      'role': role,
      'type': role,
      'balance': balance,
    };
  }
}

class AuthProvider with ChangeNotifier {
  UserData? _currentUser;
  bool _isLoading = false;

  UserData? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  bool get isLoggedIn => _currentUser != null;

  void setUser(UserData? user) {
    _currentUser = user;
    notifyListeners();
  }

  void setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void logout() {
    _currentUser = null;
    notifyListeners();
  }
}
