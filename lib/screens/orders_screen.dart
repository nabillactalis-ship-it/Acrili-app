import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/auth_provider.dart';
import '../services/order_service.dart';

class OrdersScreen extends StatefulWidget {
  const OrdersScreen({super.key});

  @override
  State<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends State<OrdersScreen> {
  final OrderService _orderService = OrderService();

  Future<void> _launchMaps(String urlString) async {
    if (urlString.isEmpty) return;
    final Uri url = Uri.parse(urlString);
    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تعذر فتح رابط الخريطة')),
        );
      }
    }
  }

  String _getTranslatedStatus(String status) {
    switch (status) {
      case OrderStatus.newOrder:
        return 'طلب جديد (جديد)';
      case OrderStatus.preparingPriced:
        return 'تم التسعير والتحضير';
      case OrderStatus.accepted:
        return 'مقبول من الزبون';
      case OrderStatus.assigned:
        return 'معين للموزع';
      case OrderStatus.delivered:
        return 'تم التوصيل';
      default:
        return status;
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case OrderStatus.newOrder:
        return Colors.orangeAccent;
      case OrderStatus.preparingPriced:
        return Colors.blueAccent;
      case OrderStatus.accepted:
        return Colors.purpleAccent;
      case OrderStatus.assigned:
        return const Color(0xFFD4AF37);
      case OrderStatus.delivered:
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = Provider.of<AuthProvider>(context).currentUser;

    if (user == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('طلباتي')),
        body: const Center(child: Text('يرجى تسجيل الدخول لمشاهدة الطلبات')),
      );
    }

    Stream<QuerySnapshot> stream;
    if (user.role == 'supplier' || user.role == 'admin') {
      stream = _orderService.streamSupplierOrders();
    } else if (user.role == 'driver') {
      stream = _orderService.streamDriverOrders(user.uid);
    } else {
      stream = _orderService.streamCustomerOrders(user.uid);
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('إدارة الطلبات'),
      ),
      body: StreamBuilder<QuerySnapshot>(
        stream: stream,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)));
          }

          if (snapshot.hasError) {
            return Center(child: Text('خطأ: ${snapshot.error}'));
          }

          final docs = snapshot.data?.docs ?? [];

          if (docs.isEmpty) {
            return const Center(
              child: Text(
                'لا توجد طلبات',
                style: TextStyle(fontSize: 18, color: Colors.grey),
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16.0),
            itemCount: docs.length,
            itemBuilder: (context, index) {
              final doc = docs[index];
              final data = doc.data() as Map<String, dynamic>;
              final orderId = doc.id;
              final status = data['status'] ?? OrderStatus.newOrder;
              final totalPrice = (data['totalPrice'] ?? 0).toDouble();
              final items = (data['items'] as List<dynamic>?) ?? [];
              final locationUrl = data['deliveryLocationUrl'] as String?;
              final customerName = data['customerName'] ?? 'زبون';

              return Card(
                margin: const EdgeInsets.only(bottom: 16.0),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'طلب #${orderId.substring(0, orderId.length > 6 ? 6 : orderId.length)}',
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: _getStatusColor(status).withOpacity(0.2),
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: _getStatusColor(status)),
                            ),
                            child: Text(
                              _getTranslatedStatus(status),
                              style: TextStyle(
                                color: _getStatusColor(status),
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'الزبون: $customerName',
                        style: const TextStyle(color: Color(0xFFA0A0A0)),
                      ),
                      Text(
                        'عدد المواد: ${items.length} | الإجمالي: $totalPrice دج',
                        style: const TextStyle(color: Color(0xFFA0A0A0)),
                      ),
                      if (locationUrl != null && locationUrl.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        ElevatedButton.icon(
                          onPressed: () => _launchMaps(locationUrl),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF252538),
                            foregroundColor: const Color(0xFFD4AF37),
                          ),
                          icon: const Icon(Icons.map, size: 18),
                          label: const Text('فتح موقع الطلب (Google Maps)'),
                        ),
                      ],
                      const SizedBox(height: 12),
                      _buildActionButtons(context, orderId, status, user.role, user.uid, user.name),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }

  Widget _buildActionButtons(
    BuildContext context,
    String orderId,
    String status,
    String role,
    String userId,
    String userName,
  ) {
    if ((role == 'supplier' || role == 'admin') && status == OrderStatus.newOrder) {
      return ElevatedButton(
        onPressed: () => _showPriceDialog(orderId),
        child: const Text('تحضير وتسعير الطلب'),
      );
    }

    if (role == 'customer' && status == OrderStatus.preparingPriced) {
      return ElevatedButton(
        onPressed: () async {
          await _orderService.customerAccept(orderId);
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('تم قبول السعر والطلب')),
            );
          }
        },
        style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFFF9F43)),
        child: const Text('تأكيد وقبول السعر'),
      );
    }

    if ((role == 'driver' || role == 'admin') && status == OrderStatus.accepted) {
      return ElevatedButton(
        onPressed: () async {
          await _orderService.driverAssign(orderId, userId, userName);
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('تم استلام وتعيين الطلب للعميل')),
            );
          }
        },
        child: const Text('استلام وتعيين الطلب للتوصيل'),
      );
    }

    if ((role == 'driver' || role == 'admin') && status == OrderStatus.assigned) {
      return ElevatedButton(
        onPressed: () async {
          await _orderService.markDelivered(orderId);
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('تم تأكيد توصيل الطلب بنجاح')),
            );
          }
        },
        style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
        child: const Text('تأكيد التوصيل (تم التسليم)'),
      );
    }

    return const SizedBox.shrink();
  }

  void _showPriceDialog(String orderId) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF2A2A3D),
        title: const Text('تسعير وتحضير الطلب', style: TextStyle(color: Colors.white)),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            hintText: 'أدخل السعر النهائي بالدينار',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('إلغاء', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () async {
              final price = double.tryParse(controller.text.trim());
              if (price != null) {
                await _orderService.supplierPrepareAndPrice(orderId, price);
                if (mounted) Navigator.pop(ctx);
              }
            },
            child: const Text('حفظ والتحديث'),
          ),
        ],
      ),
    );
  }
}
