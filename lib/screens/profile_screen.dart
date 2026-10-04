import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  String _getRoleName(String role) {
    switch (role) {
      case 'supplier':
        return 'تاجر';
      case 'driver':
        return 'سائق';
      case 'admin':
        return 'مدير النظام';
      case 'customer':
      default:
        return 'زبون';
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final user = authProvider.currentUser;

    return Scaffold(
      appBar: AppBar(
        title: const Text('الملف الشخصي'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            children: [
              const CircleAvatar(
                radius: 45,
                backgroundColor: Color(0xFF2A2A3D),
                child: Icon(Icons.person, size: 50, color: Color(0xFFD4AF37)),
              ),
              const SizedBox(height: 16),
              Text(
                user?.name ?? 'المستخدم',
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                _getRoleName(user?.role ?? ''),
                style: const TextStyle(
                  fontSize: 16,
                  color: Color(0xFFD4AF37),
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 24),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      _buildProfileItem(
                        icon: Icons.email,
                        label: 'البريد الإلكتروني',
                        value: user?.email ?? 'غير محدد',
                      ),
                      const Divider(color: Color(0xFF3F3F5A)),
                      _buildProfileItem(
                        icon: Icons.phone,
                        label: 'رقم الهاتف',
                        value: user?.phone.isNotEmpty == true ? user!.phone : 'غير محدد',
                      ),
                      const Divider(color: Color(0xFF3F3F5A)),
                      _buildProfileItem(
                        icon: Icons.account_balance_wallet,
                        label: 'الرصيد الحالي',
                        value: '${user?.balance ?? 0} دج',
                        valueColor: Colors.green,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton.icon(
                  onPressed: () {
                    authProvider.logout();
                    Navigator.pushReplacementNamed(context, '/login');
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.redAccent.withOpacity(0.8),
                    foregroundColor: Colors.white,
                  ),
                  icon: const Icon(Icons.logout),
                  label: const Text('تسجيل الخروج'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProfileItem({
    required IconData icon,
    required String label,
    required String value,
    Color? valueColor,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFFD4AF37), size: 22),
          const SizedBox(width: 12),
          Text(
            label,
            style: const TextStyle(fontSize: 15, color: Color(0xFFA0A0A0)),
          ),
          const Spacer(),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: valueColor ?? Colors.white,
            ),
          ),
        ],
      ),
    );
  }
}
