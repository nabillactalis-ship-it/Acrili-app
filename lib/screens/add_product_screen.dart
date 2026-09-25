import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class AddProductScreen extends StatefulWidget {
  const AddProductScreen({super.key});

  @override
  State<AddProductScreen> createState() => _AddProductScreenState();
}

class _AddProductScreenState extends State<AddProductScreen> {
  final _nameController = TextEditingController();
  final _priceController = TextEditingController();
  final _descController = TextEditingController();
  bool _isLoading = false;

  Future<void> _addProduct() async {
    final name = _nameController.text.trim();
    final priceStr = _priceController.text.trim();
    final desc = _descController.text.trim();

    if (name.isEmpty || priceStr.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('الرجاء إدخال اسم وسعر المنتج')),
      );
      return;
    }

    final price = double.tryParse(priceStr);
    if (price == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('الرجاء إدخال سعر صحيح')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final user = Provider.of<AuthProvider>(context, listen: false).currentUser;

      await FirebaseFirestore.instance.collection('products').add({
        'name': name,
        'price': price,
        'desc': desc,
        'supplierEmail': user?.email ?? '',
        'supplierId': user?.uid ?? '',
        'createdAt': FieldValue.serverTimestamp(),
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تم إضافة المنتج بنجاح')),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('فشل إضافة المنتج: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('إضافة منتج جديد'),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextField(
                  controller: _nameController,
                  textDirection: TextDirection.rtl,
                  decoration: const InputDecoration(
                    hintText: 'اسم المنتج',
                    prefixIcon: Icon(Icons.shopping_bag, color: Color(0xFFD4AF37)),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _priceController,
                  keyboardType: TextInputType.number,
                  textDirection: TextDirection.rtl,
                  decoration: const InputDecoration(
                    hintText: 'السعر بالدينار (دج)',
                    prefixIcon: Icon(Icons.attach_money, color: Color(0xFFD4AF37)),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _descController,
                  maxLines: 3,
                  textDirection: TextDirection.rtl,
                  decoration: const InputDecoration(
                    hintText: 'وصف المنتج',
                    prefixIcon: Icon(Icons.description, color: Color(0xFFD4AF37)),
                  ),
                ),
                const SizedBox(height: 28),
                SizedBox(
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _addProduct,
                    child: _isLoading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text('حفظ المنتج'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
