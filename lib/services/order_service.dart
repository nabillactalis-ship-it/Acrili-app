import 'package:cloud_firestore/cloud_firestore.dart';

class OrderStatus {
  static const String newOrder = 'NEW';
  static const String preparingPriced = 'PREPARING_PRICED';
  static const String accepted = 'ACCEPTED';
  static const String assigned = 'ASSIGNED';
  static const String delivered = 'DELIVERED';
}

class OrderService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  CollectionReference get _ordersRef => _firestore.collection('orders');

  // Stream all orders
  Stream<QuerySnapshot> streamAllOrders() {
    return _ordersRef.orderBy('createdAt', descending: true).snapshots();
  }

  // Stream user orders by customerId
  Stream<QuerySnapshot> streamCustomerOrders(String customerId) {
    return _ordersRef
        .where('customerId', isEqualTo: customerId)
        .snapshots();
  }

  // Stream orders for suppliers
  Stream<QuerySnapshot> streamSupplierOrders() {
    return _ordersRef.snapshots();
  }

  // Stream orders available for drivers
  Stream<QuerySnapshot> streamDriverOrders(String driverId) {
    return _ordersRef.snapshots();
  }

  // Step 1: Create new order (NEW)
  Future<String> createOrder({
    required String customerId,
    required String customerEmail,
    required String customerName,
    required List<Map<String, dynamic>> items,
    required double totalPrice,
    String? deliveryLocationUrl,
  }) async {
    final docRef = await _ordersRef.add({
      'customerId': customerId,
      'customerEmail': customerEmail,
      'customerName': customerName,
      'items': items,
      'totalPrice': totalPrice,
      'status': OrderStatus.newOrder,
      'deliveryLocationUrl': deliveryLocationUrl ?? '',
      'createdAt': FieldValue.serverTimestamp(),
      'updatedAt': FieldValue.serverTimestamp(),
    });
    return docRef.id;
  }

  // Step 2: Supplier prepares and prices order (PREPARING_PRICED)
  Future<void> supplierPrepareAndPrice(String orderId, double price) async {
    await _ordersRef.doc(orderId).update({
      'status': OrderStatus.preparingPriced,
      'totalPrice': price,
      'updatedAt': FieldValue.serverTimestamp(),
    });
  }

  // Step 3: Customer accepts price/order (ACCEPTED)
  Future<void> customerAccept(String orderId) async {
    await _ordersRef.doc(orderId).update({
      'status': OrderStatus.accepted,
      'updatedAt': FieldValue.serverTimestamp(),
    });
  }

  // Step 4: Driver accepts assignment (ASSIGNED)
  Future<void> driverAssign(String orderId, String driverId, String driverName) async {
    await _ordersRef.doc(orderId).update({
      'status': OrderStatus.assigned,
      'driverId': driverId,
      'driverName': driverName,
      'updatedAt': FieldValue.serverTimestamp(),
    });
  }

  // Step 5: Update delivery in progress
  Future<void> startDelivery(String orderId) async {
    await _ordersRef.doc(orderId).update({
      'status': OrderStatus.assigned,
      'inTransit': true,
      'updatedAt': FieldValue.serverTimestamp(),
    });
  }

  // Step 6: Mark as delivered (DELIVERED)
  Future<void> markDelivered(String orderId) async {
    await _ordersRef.doc(orderId).update({
      'status': OrderStatus.delivered,
      'updatedAt': FieldValue.serverTimestamp(),
    });
  }

  // Generic status update
  Future<void> updateStatus(String orderId, String status) async {
    await _ordersRef.doc(orderId).update({
      'status': status,
      'updatedAt': FieldValue.serverTimestamp(),
    });
  }
}
