import json
import os
import re
from datetime import datetime

import arabic_reshaper
from bidi.algorithm import get_display
import pyrebase

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.modalview import ModalView
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

# Firebase Configuration (Replace with your actual config)
firebase_config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_PROJECT.firebaseapp.com",
    "databaseURL": "https://YOUR_PROJECT.firebaseio.com",
    "projectId": "YOUR_PROJECT",
    "storageBucket": "YOUR_PROJECT.appspot.com",
    "messagingSenderId": "YOUR_SENDER_ID",
    "appId": "YOUR_APP_ID"
}

# Initialize Firebase
try:
    firebase = pyrebase.initialize_app(firebase_config)
    db = firebase.database()
except Exception as e:
    print(f"Firebase initialization failed: {e}")
    db = None

# تسجيل خط عربي
font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Cairo-Regular.ttf')
LabelBase.register(name='Cairo', fn_regular=font_path)

def ar(text):
    """دالة تعالج العربية باش تتلصق وتترتب من اليمين"""
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped)
        # Remove common control characters that might mess up rendering in some Kivy versions
        bidi_text = re.sub(r'[\u200e\u200f\u202a-\u202e]', '', bidi_text)
        return bidi_text
    except Exception:
        return str(text)

# ألوان التطبيق
COLORS = {
    'bg': get_color_from_hex('#1a1a2e'),
    'card': get_color_from_hex('#16213e'),
    'primary': get_color_from_hex('#0f3460'),
    'accent': get_color_from_hex('#e94560'),
    'text': get_color_from_hex('#ffffff'),
    'text_dim': get_color_from_hex('#a0a0a0')
}

# Loading Spinner
class LoadingView(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.4, 0.2)
        self.auto_dismiss = False
        self.background_color = (0, 0, 0, 0.8)
        layout = BoxLayout(orientation='vertical', padding=10)
        layout.add_widget(Label(text=ar("جاري التحميل..."), font_name='Cairo'))
        self.add_widget(layout)

# متغيرات عامة
current_user = None
cart = []

KV = f'''
<SpinnerOption@Button>:
    font_name: 'Cairo'

<CustomButton@Button>:
    bg_color: (0.1, 0.6, 0.9, 1)
    font_name: 'Cairo'
    font_size: 18
    size_hint_y: None
    height: 50
    background_color: 0,0,0,0
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15]

<CustomLabel@Label>:
    font_name: 'Cairo'
    color: 1,1,1,1

ScreenManager:
    LoginScreen:
    RegisterScreen:
    HomeScreen:
    ProductsScreen:
    AddProductScreen:
    CartScreen:
    OrdersScreen:
    DriverScreen:
    ProfileScreen:

<LoginScreen>:
    name: 'login'
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.18, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Widget:
            size_hint_y: 0.3

        CustomLabel:
            text: "{ar('مرحبا بك في نشربلك')}"
            font_size: 28
            bold: True
            size_hint_y: None
            height: 50

        TextInput:
            id: email
            hint_text: "{ar('البريد الإلكتروني')}"
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            multiline: False
            size_hint_y: None
            height: 50
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15

        TextInput:
            id: password
            hint_text: "{ar('كلمة السر')}"
            password: True
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            multiline: False
            size_hint_y: None
            height: 50
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15

        CustomButton:
            text: "{ar('تسجيل الدخول')}"
            bg_color: (0.1, 0.6, 0.9, 1)
            on_release: root.login()

        CustomButton:
            text: "{ar('إنشاء حساب جديد')}"
            bg_color: (0.2,0.2,0.3,1)
            on_release: root.manager.current = 'register'

        Widget:
            size_hint_y: 0.3

<RegisterScreen>:
    name: 'register'
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 15
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.18, 1
            Rectangle:
                pos: self.pos
                size: self.size

        CustomLabel:
            text: "{ar('إنشاء حساب جديد')}"
            font_size: 26
            bold: True

        TextInput:
            id: name
            hint_text: "{ar('الاسم الكامل')}"
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            multiline: False
            size_hint_y: None
            height: 50
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15
        TextInput:
            id: email
            hint_text: "{ar('البريد الإلكتروني')}"
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            multiline: False
            size_hint_y: None
            height: 50
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15
        TextInput:
            id: password
            hint_text: "{ar('كلمة السر')}"
            password: True
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            multiline: False
            size_hint_y: None
            height: 50
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15
        TextInput:
            id: phone
            hint_text: "{ar('رقم الهاتف (05/06/07)')}"
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            multiline: False
            input_type: 'number'
            size_hint_y: None
            height: 50
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15

        Spinner:
            id: user_type
            text: "{ar('اختر نوع الحساب')}"
            values: ["{ar('زبون')}", "{ar('تاجر')}", "{ar('سائق')}"]
            font_name: 'Cairo'
            option_cls: 'SpinnerOption'
            size_hint_y: None
            height: 50
            background_color: 0.15,0.15,0.25,1
            color: 1,1,1,1

        CustomButton:
            text: "{ar('تأكيد التسجيل')}"
            bg_color: (0.1, 0.6, 0.9, 1)
            on_release: root.register()

        CustomButton:
            text: "{ar('رجوع')}"
            bg_color: (0.2,0.2,0.3,1)
            on_release: root.manager.current = 'login'

<HomeScreen>:
    name: 'home'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.18, 1
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: 60
            padding: 10
            canvas.before:
                Color:
                    rgba: 0.15,0.15,0.25,1
                Rectangle:
                    pos: self.pos
                    size: self.size
            CustomLabel:
                id: welcome
                text: "{ar('مرحبا')}"
                font_size: 20
                bold: True

        ScrollView:
            GridLayout:
                cols: 2
                spacing: 15
                padding: 20
                size_hint_y: None
                height: self.minimum_height

                CustomButton:
                    text: "{ar('المنتجات')}"
                    bg_color: (0.1, 0.5, 0.8, 1)
                    height: 120
                    on_release: root.manager.current = 'products'

                CustomButton:
                    text: "{ar('سلة المشتريات')}"
                    bg_color: (0.9, 0.3, 0.4, 1)
                    height: 120
                    on_release: root.manager.current = 'cart'

                CustomButton:
                    text: "{ar('طلباتي')}"
                    bg_color: (0.2, 0.7, 0.5, 1)
                    height: 120
                    on_release: root.manager.current = 'orders'

                CustomButton:
                    text: "{ar('لوحة السائق')}"
                    id: driver_btn
                    bg_color: (0.5, 0.2, 0.8, 1)
                    height: 120
                    on_release: root.manager.current = 'driver'

                CustomButton:
                    text: "{ar('الملف الشخصي')}"
                    bg_color: (0.4, 0.4, 0.4, 1)
                    height: 120
                    on_release: root.manager.current = 'profile'

        BoxLayout:
            size_hint_y: None
            height: 80
            padding: 15
            spacing: 10
            CustomButton:
                text: "{ar('إضافة منتج')}"
                bg_color: (0.8, 0.5, 0.1, 1)
                id: add_btn
                on_release: root.manager.current = 'add_product'
            CustomButton:
                text: "{ar('خروج')}"
                bg_color: (0.5,0.2,0.2,1)
                on_release: root.logout()

<ProductsScreen>:
    name: 'products'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.18, 1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: 60
            padding: 10
            canvas.before:
                Color:
                    rgba: 0.15,0.15,0.25,1
                Rectangle:
                    pos: self.pos
                    size: self.size
            CustomButton:
                text: "{ar('رجوع')}"
                size_hint_x: 0.2
                bg_color: (0.3,0.3,0.4,1)
                on_release: root.manager.current = 'home'
            CustomLabel:
                text: "{ar('المنتجات المتاحة')}"
                font_size: 20
                bold: True
        ScrollView:
            GridLayout:
                id: products_grid
                cols: 1
                spacing: 10
                padding: 15
                size_hint_y: None
                height: self.minimum_height

<AddProductScreen>:
    name: 'add_product'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.18, 1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: 60
            CustomButton:
                text: "{ar('رجوع')}"
                size_hint_x: 0.2
                bg_color: (0.3,0.3,0.4,1)
                on_release: root.manager.current = 'home'
            CustomLabel:
                text: "{ar('إضافة منتج جديد')}"
                font_size: 20
                bold: True
        TextInput:
            id: name
            hint_text: "{ar('اسم المنتج')}"
            font_name: 'Cairo'
            multiline: False
            size_hint_y: None
            height: 50
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15
        TextInput:
            id: price
            hint_text: "{ar('السعر بالدينار')}"
            font_name: 'Cairo'
            input_type: 'number'
            multiline: False
            size_hint_y: None
            height: 50
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15
        TextInput:
            id: stock
            hint_text: "{ar('الكمية المتوفرة')}"
            font_name: 'Cairo'
            input_type: 'number'
            multiline: False
            size_hint_y: None
            height: 50
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15
        TextInput:
            id: desc
            hint_text: "{ar('وصف المنتج')}"
            font_name: 'Cairo'
            size_hint_y: None
            height: 100
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15
        BoxLayout:
            size_hint_y: None
            height: 60
            spacing: 10
            CustomButton:
                text: "{ar('حفظ المنتج')}"
                on_release: root.add_product()
            CustomButton:
                text: "{ar('مسح الحقول')}"
                bg_color: (0.4, 0.4, 0.4, 1)
                on_release: root.clear_fields()

<CartScreen>:
    name: 'cart'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.18, 1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: 60
            padding: 10
            CustomButton:
                text: "{ar('رجوع')}"
                size_hint_x: 0.2
                bg_color: (0.3,0.3,0.4,1)
                on_release: root.manager.current = 'home'
            CustomLabel:
                text: "{ar('سلة المشتريات')}"
                font_size: 20
                bold: True
        ScrollView:
            GridLayout:
                id: cart_grid
                cols: 1
                spacing: 10
                padding: 15
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: 160
            orientation: 'vertical'
            padding: 15
            spacing: 10
            CustomLabel:
                id: total
                text: "{ar('الإجمالي: 0 دج')}"
                font_size: 18
                bold: True
            Spinner:
                id: payment_method
                text: "{ar('اختر طريقة الدفع')}"
                values: ["{ar('دفع عند الاستلام')}", "{ar('بريدي موب / CCP')}"]
                font_name: 'Cairo'
                size_hint_y: None
                height: 50
                background_color: 0.15,0.15,0.25,1
            CustomButton:
                text: "{ar('تأكيد الطلب')}"
                bg_color: (0.1, 0.7, 0.4, 1)
                on_release: root.confirm_order()

<OrdersScreen>:
    name: 'orders'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.18, 1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: 60
            padding: 10
            CustomButton:
                text: "{ar('رجوع')}"
                size_hint_x: 0.2
                bg_color: (0.3,0.3,0.4,1)
                on_release: root.manager.current = 'home'
            CustomLabel:
                text: "{ar('طلباتي المشتراة')}"
                font_size: 20
                bold: True
        ScrollView:
            GridLayout:
                id: orders_grid
                cols: 1
                spacing: 10
                padding: 15
                size_hint_y: None
                height: self.minimum_height

<DriverScreen>:
    name: 'driver'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.18, 1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: 60
            padding: 10
            CustomButton:
                text: "{ar('رجوع')}"
                size_hint_x: 0.2
                bg_color: (0.3,0.3,0.4,1)
                on_release: root.manager.current = 'home'
            CustomLabel:
                text: "{ar('طلبات التوصيل المتاحة')}"
                font_size: 20
                bold: True
        ScrollView:
            GridLayout:
                id: driver_grid
                cols: 1
                spacing: 10
                padding: 15
                size_hint_y: None
                height: self.minimum_height

<ProfileScreen>:
    name: 'profile'
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.18, 1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: 60
            CustomButton:
                text: "{ar('رجوع')}"
                size_hint_x: 0.2
                bg_color: (0.3,0.3,0.4,1)
                on_release: root.manager.current = 'home'
            CustomLabel:
                text: "{ar('الملف الشخصي')}"
                font_size: 24
                bold: True
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 15
                CustomLabel:
                    id: user_name
                    text: ""
                    font_size: 20
                CustomLabel:
                    id: user_email
                    text: ""
                    color: 0.7,0.7,0.7,1
                CustomLabel:
                    id: user_type
                    text: ""
                CustomLabel:
                    id: user_phone
                    text: ""
'''

class BaseScreen(Screen):
    def show_popup(self, title, msg):
        popup = Popup(title=ar(title), content=Label(text=ar(msg), font_name='Cairo'),
                     size_hint=(0.8, 0.4))
        popup.open()

class LoginScreen(BaseScreen):
    def login(self):
        global current_user
        email = self.ids.email.text.strip().lower()
        password = self.ids.password.text.strip()

        if not email or not password:
            self.show_popup('خطأ', 'أدخل البريد وكلمة السر')
            return

        loading = LoadingView()
        loading.open()

        def do_login(dt):
            try:
                users = db.child("users").get().val()
                loading.dismiss()
                user_found = None
                if users:
                    for uid, u in users.items():
                        if u.get('email') == email and u.get('password') == password:
                            u['id'] = uid
                            user_found = u
                            break

                if user_found:
                    current_user = user_found
                    self.update_ui()
                    self.manager.current = 'home'
                else:
                    self.show_popup('خطأ', 'البريد أو كلمة السر غير صحيحة')
            except Exception as e:
                loading.dismiss()
                self.show_popup('خطأ اتصال', f'فشل الاتصال: {str(e)}')

        Clock.schedule_once(do_login, 0.1)

    def update_ui(self):
        home = self.manager.get_screen('home')
        home.ids.welcome.text = ar(f'مرحبا {current_user["name"]}')

        # Role-based visibility
        home.ids.add_btn.opacity = 1 if current_user['type'] in ['supplier', 'admin'] else 0
        home.ids.add_btn.disabled = current_user['type'] not in ['supplier', 'admin']
        home.ids.driver_btn.opacity = 1 if current_user['type'] in ['driver', 'admin'] else 0
        home.ids.driver_btn.disabled = current_user['type'] not in ['driver', 'admin']

        profile = self.manager.get_screen('profile')
        profile.ids.user_name.text = ar(f"الاسم: {current_user['name']}")
        profile.ids.user_email.text = f"Email: {current_user['email']}"
        types_map = {'customer': 'زبون', 'supplier': 'تاجر', 'driver': 'سائق'}
        profile.ids.user_type.text = ar(f"النوع: {types_map.get(current_user['type'], current_user['type'])}")
        profile.ids.user_phone.text = ar(f"الهاتف: {current_user['phone']}")

class RegisterScreen(BaseScreen):
    def register(self):
        name = self.ids.name.text.strip()
        email = self.ids.email.text.strip().lower()
        password = self.ids.password.text.strip()
        phone = self.ids.phone.text.strip()
        user_type_ar = self.ids.user_type.text

        # Validation
        if not all([name, email, password, phone]) or user_type_ar == ar('اختر نوع الحساب'):
            self.show_popup('خطأ', 'املأ جميع الحقول')
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.show_popup('خطأ', 'بريد إلكتروني غير صالح')
            return
        if not re.match(r"^(05|06|07)\d{8}$", phone):
            self.show_popup('خطأ', 'رقم هاتف جزائري غير صالح')
            return

        types_map = {ar('زبون'): 'customer', ar('تاجر'): 'supplier', ar('سائق'): 'driver'}
        user_type = types_map.get(user_type_ar, 'customer')

        loading = LoadingView()
        loading.open()

        def do_register(dt):
            try:
                # Check if email exists
                existing = db.child("users").order_by_child("email").equal_to(email).get().val()
                if existing:
                    loading.dismiss()
                    self.show_popup('خطأ', 'البريد موجود مسبقا')
                    return

                db.child("users").push({
                    'name': name, 'email': email, 'password': password,
                    'phone': phone, 'type': user_type, 'balance': 0
                })
                loading.dismiss()
                self.show_popup('نجاح', 'تم إنشاء الحساب')
                self.manager.current = 'login'
            except Exception as e:
                loading.dismiss()
                self.show_popup('خطأ', str(e))

        Clock.schedule_once(do_register, 0.1)

class HomeScreen(BaseScreen):
    def logout(self):
        global current_user, cart
        current_user = None
        cart = []
        self.manager.current = 'login'

class ProductsScreen(BaseScreen):
    def on_pre_enter(self): self.load_products()
    def load_products(self):
        grid = self.ids.products_grid
        grid.clear_widgets()
        loading = LoadingView(); loading.open()
        def fetch(dt):
            try:
                products = db.child("products").get().val()
                loading.dismiss()
                if not products:
                    grid.add_widget(Label(text=ar('لا توجد منتجات حاليا'), font_name='Cairo'))
                    return
                for pid, p in products.items():
                    box = BoxLayout(orientation='vertical', size_hint_y=None, height=130, padding=10)
                    with box.canvas.before:
                        Color(rgba=COLORS['card'])
                        rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[15])
                    box.bind(pos=lambda i,p,r=rect: setattr(r,'pos',p), size=lambda i,s,r=rect: setattr(r,'size',s))
                    box.add_widget(Label(text=ar(p['name']), bold=True, font_name='Cairo'))
                    box.add_widget(Label(text=ar(f"{p['price']} دج | {p.get('stock',0)} قطعة"), font_name='Cairo'))
                    btn = CustomButton(text=ar('أضف للسلة'), height=40, bg_color=COLORS['accent'])
                    btn.bind(on_release=lambda x, p=p, pid=pid: self.add_to_cart(p, pid))
                    box.add_widget(btn)
                    grid.add_widget(box)
            except Exception as e: loading.dismiss(); self.show_popup('خطأ', str(e))
        Clock.schedule_once(fetch, 0.1)

    def add_to_cart(self, p, pid):
        p['id'] = pid
        cart.append(p)
        self.show_popup('تم', f'أضفت {p["name"]} للسلة')

class AddProductScreen(BaseScreen):
    def clear_fields(self):
        for i in ['name', 'price', 'stock', 'desc']: self.ids[i].text = ''
    def add_product(self):
        name = self.ids.name.text.strip()
        price = self.ids.price.text.strip()
        stock = self.ids.stock.text.strip()
        if not all([name, price, stock]):
            self.show_popup('خطأ', 'املأ الحقول الأساسية'); return

        try:
            p_val = int(price)
            s_val = int(stock)
            if p_val <= 0 or s_val <= 0: raise ValueError
        except ValueError:
            self.show_popup('خطأ', 'السعر والكمية يجب أن يكونا أرقام موجبة'); return

        loading = LoadingView(); loading.open()
        def save(dt):
            try:
                db.child("products").push({
                    'name': name, 'price': int(price), 'stock': int(stock),
                    'desc': self.ids.desc.text, 'supplier': current_user['email']
                })
                loading.dismiss(); self.show_popup('نجاح', 'تمت إضافة المنتج'); self.clear_fields()
            except Exception as e: loading.dismiss(); self.show_popup('خطأ', str(e))
        Clock.schedule_once(save, 0.1)

class CartScreen(BaseScreen):
    def on_pre_enter(self): self.load_cart()
    def load_cart(self):
        grid = self.ids.cart_grid; grid.clear_widgets()
        total = sum(p['price'] for p in cart)
        self.ids.total.text = ar(f'الإجمالي: {total} دج')
        for i, p in enumerate(cart):
            row = BoxLayout(size_hint_y=None, height=50, spacing=10)
            row.add_widget(Label(text=ar(p['name']), font_name='Cairo'))
            row.add_widget(Label(text=f"{p['price']} DA"))
            btn = Button(text="X", size_hint_x=0.2, background_color=(1,0,0,1))
            btn.bind(on_release=lambda x, idx=i: self.remove(idx))
            row.add_widget(btn)
            grid.add_widget(row)

    def remove(self, idx): cart.pop(idx); self.load_cart()

    def confirm_order(self):
        pay = self.ids.payment_method.text
        if not cart or pay == ar('اختر طريقة الدفع'):
            self.show_popup('خطأ', 'السلة فارغة أو لم تختر الدفع'); return
        loading = LoadingView(); loading.open()
        def push_order(dt):
            try:
                db.child("orders").push({
                    'customer': current_user['email'], 'customer_name': current_user['name'],
                    'customer_phone': current_user['phone'], 'items': cart,
                    'total': sum(p['price'] for p in cart), 'payment': pay,
                    'status': 'pending', 'driver': None, 'date': str(datetime.now())
                })
                loading.dismiss(); cart.clear(); self.show_popup('نجاح', 'تم تأكيد الطلب'); self.manager.current = 'home'
            except Exception as e: loading.dismiss(); self.show_popup('خطأ', str(e))
        Clock.schedule_once(push_order, 0.1)

class OrdersScreen(BaseScreen):
    def on_pre_enter(self): self.load_orders()
    def load_orders(self):
        grid = self.ids.orders_grid; grid.clear_widgets()
        loading = LoadingView(); loading.open()
        def fetch(dt):
            try:
                orders = db.child("orders").order_by_child("customer").equal_to(current_user['email']).get().val()
                loading.dismiss()
                if not orders:
                    grid.add_widget(Label(text=ar('ليس لديك طلبات سابقة'), font_name='Cairo'))
                    return
                # Sort by date
                sorted_orders = sorted(orders.items(), key=lambda x: x[1]['date'], reverse=True)
                status_map = {'pending': 'قيد الانتظار', 'accepted': 'تم القبول', 'delivering': 'في الطريق', 'completed': 'تم التوصيل'}
                for oid, o in sorted_orders:
                    height = 140 if o.get('driver') else 120
                    box = BoxLayout(orientation='vertical', size_hint_y=None, height=height, padding=10)
                    with box.canvas.before:
                        Color(rgba=COLORS['card']); r = RoundedRectangle(pos=box.pos, size=box.size, radius=[15])
                    box.bind(pos=lambda i,p,rect=r: setattr(rect,'pos',p), size=lambda i,s,rect=r: setattr(rect,'size',s))
                    box.add_widget(Label(text=ar(f"طلب رقم: {oid[-6:]}"), bold=True, font_name='Cairo'))
                    box.add_widget(Label(text=ar(f"الحالة: {status_map.get(o['status'], o['status'])}"), color=(1,1,0,1), font_name='Cairo'))
                    if o.get('driver'):
                        box.add_widget(Label(text=ar(f"السائق: {o['driver']}"), color=(0.6,0.8,1,1), font_name='Cairo', font_size=14))
                    box.add_widget(Label(text=ar(f"الإجمالي: {o['total']} دج"), font_name='Cairo'))
                    grid.add_widget(box)
            except Exception as e: loading.dismiss(); self.show_popup('خطأ', str(e))
        Clock.schedule_once(fetch, 0.1)

class DriverScreen(BaseScreen):
    def on_pre_enter(self): self.load_available_orders()
    def load_available_orders(self):
        grid = self.ids.driver_grid; grid.clear_widgets()
        loading = LoadingView(); loading.open()
        def fetch(dt):
            try:
                # Get all pending or orders assigned to me
                all_orders = db.child("orders").get().val()
                loading.dismiss()
                if not all_orders: return
                for oid, o in all_orders.items():
                    if o['status'] == 'pending' or (o['driver'] == current_user['email'] and o['status'] != 'completed'):
                        box = BoxLayout(orientation='vertical', size_hint_y=None, height=160, padding=10)
                        with box.canvas.before:
                            Color(rgba=COLORS['card']); r = RoundedRectangle(pos=box.pos, size=box.size, radius=[15])
                        box.bind(pos=lambda i,p,rect=r: setattr(rect,'pos',p), size=lambda i,s,rect=r: setattr(rect,'size',s))
                        box.add_widget(Label(text=ar(f"زبون: {o['customer_name']} | {o['total']} دج"), font_name='Cairo'))
                        box.add_widget(Label(text=ar(f"هاتف: {o['customer_phone']}"), font_name='Cairo'))

                        btn_box = BoxLayout(spacing=10)
                        if o['status'] == 'pending':
                            btn = CustomButton(text=ar('قبول الطلب'), bg_color=(0,0.6,0,1))
                            btn.bind(on_release=lambda x, i=oid: self.update_status(i, 'accepted'))
                            btn_box.add_widget(btn)
                        elif o['status'] == 'accepted':
                            btn = CustomButton(text=ar('بدء التوصيل'), bg_color=(1,0.5,0,1))
                            btn.bind(on_release=lambda x, i=oid: self.update_status(i, 'delivering'))
                            btn_box.add_widget(btn)
                        elif o['status'] == 'delivering':
                            btn = CustomButton(text=ar('تم التوصيل'), bg_color=(0,0.4,0.8,1))
                            btn.bind(on_release=lambda x, i=oid: self.update_status(i, 'completed'))
                            btn_box.add_widget(btn)

                        box.add_widget(btn_box)
                        grid.add_widget(box)
            except Exception as e: loading.dismiss(); self.show_popup('خطأ', str(e))
        Clock.schedule_once(fetch, 0.1)

    def update_status(self, oid, new_status):
        loading = LoadingView(); loading.open()
        def update(dt):
            try:
                db.child("orders").child(oid).update({'status': new_status, 'driver': current_user['email']})
                loading.dismiss(); self.load_available_orders()
            except Exception as e: loading.dismiss(); self.show_popup('خطأ', str(e))
        Clock.schedule_once(update, 0.1)

class ProfileScreen(BaseScreen): pass

class NeshrblekApp(App):
    def build(self):
        self.title = ar('نشربلك - النسخة الاحترافية')
        return Builder.load_string(KV)

if __name__ == '__main__':
    NeshrblekApp().run()
