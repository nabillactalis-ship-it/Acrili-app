import 'package:cloud_firestore/cloud_firestore.dart';

class OrderService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  /// الاستماع التلقائي للطلب لحظة بلحظة
  Stream<DocumentSnapshot<Map<String, dynamic>>> streamOrder(String orderId) {
    return _firestore.collection('orders').doc(orderId).snapshots();
  }

  /// 1. التاجر: تحديد السعر
  Future<void> merchantSetPrice(String orderId, double price) async {
    await _firestore.collection('orders').doc(orderId).update({
      'pricing': {
        'itemsPrice': price,
        'totalPrice': price,
      },
      'status': 'PREPARING_PRICED',
      'timestamps.pricedAt': FieldValue.serverTimestamp(),
    });
  }

  /// 2. الزبون: قبول السعر
  Future<void> customerAcceptPrice(String orderId) async {
    await _firestore.collection('orders').doc(orderId).update({
      'status': 'ACCEPTED',
      'timestamps.acceptedAt': FieldValue.serverTimestamp(),
    });
  }

  /// 3. الموزع: قبول استلام الطلبية
  Future<void> driverAcceptOrder(String orderId, String driverId) async {
    await _firestore.collection('orders').doc(orderId).update({
      'driverId': driverId,
      'status': 'ASSIGNED',
      'timestamps.assignedAt': FieldValue.serverTimestamp(),
    });
  }

  /// 4. الموزع: إنهاء التوصيل
  Future<void> driverCompleteOrder(String orderId) async {
    await _firestore.collection('orders').doc(orderId).update({
      'status': 'DELIVERED',
      'timestamps.deliveredAt': FieldValue.serverTimestamp(),
    });
  }
}
