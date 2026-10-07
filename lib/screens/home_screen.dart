import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final user = authProvider.currentUser;

    final isSupplierOrAdmin = user != null &&
        (user.role == 'supplier' || user.role == 'admin');

    return Scaffold(
      appBar: AppBar(
        title: Text('مرحبا ${user?.name ?? ""}'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Color(0xFFD4AF37)),
            onPressed: () {
              authProvider.logout();
              Navigator.pushReplacementNamed(context, '/login');
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Expanded(
                child: GridView.count(
                  crossAxisCount: 2,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  children: [
                    _buildNavCard(
                      context,
                      title: 'المنتجات',
                      icon: Icons.storefront,
                      color: const Color(0xFF0F3460),
                      route: '/products',
                    ),
                    _buildNavCard(
                      context,
                      title: 'سلة المشتريات',
                      icon: Icons.shopping_cart,
                      color: const Color(0xFFE94560),
                      route: '/cart',
                    ),
                    _buildNavCard(
                      context,
                      title: 'طلباتي',
                      icon: Icons.assignment,
                      color: const Color(0xFF16C79A),
                      route: '/orders',
                    ),
                    _buildNavCard(
                      context,
                      title: 'الملف الشخصي',
                      icon: Icons.person,
                      color: const Color(0xFFFF9F43),
                      route: '/profile',
                    ),
                  ],
                ),
              ),
              if (isSupplierOrAdmin)
                Padding(
                  padding: const EdgeInsets.only(top: 16.0),
                  child: SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFD4AF37),
                        foregroundColor: Colors.black,
                      ),
                      onPressed: () {
                        Navigator.pushNamed(context, '/add_product');
                      },
                      icon: const Icon(Icons.add_box),
                      label: const Text(
                        'إضافة منتج جديد',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavCard(
    BuildContext context, {
    required String title,
    required IconData icon,
    required Color color,
    required String route,
  }) {
    return Card(
      child: InkWell(
        onTap: () => Navigator.pushNamed(context, route),
        borderRadius: BorderRadius.circular(15),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircleAvatar(
              radius: 30,
              backgroundColor: color.withOpacity(0.2),
              child: Icon(icon, size: 32, color: color),
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
