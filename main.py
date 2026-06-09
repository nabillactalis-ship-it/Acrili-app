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

# Firebase Config (Placeholders)
# Replace these with your actual Firebase project credentials
firebase_config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_AUTH_DOMAIN",
    "databaseURL": "YOUR_DATABASE_URL", # Must be https://project-id.firebaseio.com
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_STORAGE_BUCKET",
    "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
    "appId": "YOUR_APP_ID"
}

# Initialize Firebase Realtime Database
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
        # إزالة رموز التحكم Bidi التي قد تسبب مربعات في Kivy
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

# متغيرات عامة
current_user = None
cart = []

class LoadingView(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.6, 0.25)
        self.auto_dismiss = False
        self.background_color = (0, 0, 0, 0.8)
        self.add_widget(Label(text=ar("جاري التحميل... (Loading)"), font_name='Cairo', font_size=20))

KV = f'''
ScreenManager:
    LoginScreen:
    RegisterScreen:
    HomeScreen:
    ProductsScreen:
    AddProductScreen:
    CartScreen:
    OrdersScreen:
    ProfileScreen:

<SpinnerOption@Button>:
    font_name: 'Cairo'

<CustomButton@Button>:
    bg_color: (0.1, 0.6, 0.9, 1)
    font_name: 'Cairo'
    font_size: 18
    size_hint_y: None
    height: dp(50)
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
            halign: 'center'

        CustomLabel:
            text: "{ar('سجل دخولك للمتابعة')}"
            font_size: 16
            color: 0.6,0.6,0.6,1
            size_hint_y: None
            height: 30
            halign: 'center'

        TextInput:
            id: email
            hint_text: "{ar('البريد الإلكتروني')}"
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            font_size: 18
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
            font_size: 18
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
            text: "{ar('ليس لديك حساب؟ سجل الآن')}"
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
            size_hint_y: None
            height: 50

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
            hint_text: "{ar('رقم الهاتف')}"
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
            text: "{ar('إنشاء الحساب')}"
            bg_color: (0.1, 0.6, 0.9, 1)
            on_release: root.register()

        CustomButton:
            text: "{ar('رجوع لتسجيل الدخول')}"
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
                    text: "{ar('الملف الشخصي')}"
                    bg_color: (0.8, 0.5, 0.1, 1)
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
                text: "{ar('تسجيل الخروج')}"
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

            CustomButton:
                text: "{ar('تحديث')}"
                size_hint_x: 0.2
                bg_color: (0.1, 0.5, 0.1, 1)
                on_release: root.load_products()

        ScrollView:
            id: scroll
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
        spacing: 10
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.18, 1
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: 60
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
                text: "{ar('إضافة منتج جديد')}"
                font_size: 20
                bold: True

        TextInput:
            id: name
            hint_text: "{ar('اسم المنتج')}"
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            multiline: False
            size_hint_y: None
            height: dp(50)
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15

        TextInput:
            id: price
            hint_text: "{ar('السعر بالدينار')}"
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            input_type: 'number'
            multiline: False
            size_hint_y: None
            height: dp(50)
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15

        TextInput:
            id: quantity
            hint_text: "{ar('الكمية (Quantity)')}"
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            input_filter: 'int'
            multiline: False
            size_hint_y: None
            height: dp(60)
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15

        TextInput:
            id: desc
            hint_text: "{ar('وصف المنتج')}"
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            size_hint_y: None
            height: dp(80)
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15

        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: 10
            CustomButton:
                text: "{ar('حفظ المنتج')}"
                bg_color: (0.1, 0.6, 0.9, 1)
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
                text: "{ar('سلة المشتريات')}"
                font_size: 20
                bold: True

        ScrollView:
            id: scroll
            GridLayout:
                id: cart_grid
                cols: 1
                spacing: 10
                padding: 15
                size_hint_y: None
                height: self.minimum_height

        BoxLayout:
            size_hint_y: None
            height: 80
            padding: 15
            spacing: 10

            CustomLabel:
                id: total
                text: "{ar('الإجمالي: 0 دج')}"
                font_size: 18
                bold: True

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
                text: "{ar('طلباتي')}"
                font_size: 20
                bold: True

        ScrollView:
            id: scroll
            GridLayout:
                id: orders_grid
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
                text: "{ar('الملف الشخصي')}"
                font_size: 24
                bold: True

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 20

                CustomLabel:
                    id: user_name
                    text: ""
                    font_size: 22
                    size_hint_y: None
                    height: 50
                    halign: 'right'

                CustomLabel:
                    id: user_email
                    text: ""
                    font_size: 18
                    color: 0.7,0.7,0.7,1
                    size_hint_y: None
                    height: 40
                    halign: 'right'

                CustomLabel:
                    id: user_type
                    text: ""
                    font_size: 18
                    size_hint_y: None
                    height: 40
                    halign: 'right'

                CustomLabel:
                    id: user_phone
                    text: ""
                    font_size: 18
                    size_hint_y: None
                    height: 40
                    halign: 'right'

                CustomLabel:
                    id: user_balance
                    text: ""
                    font_size: 18
                    color: 0.2, 0.8, 0.2, 1
                    size_hint_y: None
                    height: 40
                    halign: 'right'
'''

class BaseScreen(Screen):
    def show_popup(self, title, msg):
        popup = Popup(
            title=ar(title),
            content=Label(text=ar(msg), font_name='Cairo'),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class LoginScreen(BaseScreen):
    def login(self):
        global current_user
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()

        if not db:
            self.show_popup('خطأ', 'لا يوجد اتصال بالإنترنت')
            return

        loading = LoadingView()
        loading.open()
        try:
            user_key = email.replace('.', ',')
            user_data = db.child("users").child(user_key).get().val()

            if user_data and user_data['password'] == password:
                current_user = user_data
                current_user['email'] = email
                self.manager.get_screen('home').ids.welcome.text = ar(f'مرحبا {user_data["name"]}')

                # Update profile info
                profile = self.manager.get_screen('profile')
                profile.ids.user_name.text = ar(f"الاسم: {user_data['name']}")
                profile.ids.user_email.text = f"البريد: {email}"

                types_map = {'customer': 'زبون', 'supplier': 'تاجر', 'driver': 'سائق'}
                display_type = types_map.get(user_data['type'], user_data['type'])
                profile.ids.user_type.text = ar(f"نوع الحساب: {display_type}")
                profile.ids.user_phone.text = ar(f"رقم الهاتف: {user_data['phone']}")
                profile.ids.user_balance.text = ar(f"الرصيد: {user_data['balance']} دج")

                # Update add button visibility
                add_btn = self.manager.get_screen('home').ids.add_btn
                if user_data['type'] in ['supplier', 'admin']:
                    add_btn.opacity = 1
                    add_btn.disabled = False
                else:
                    add_btn.opacity = 0
                    add_btn.disabled = True

                self.manager.current = 'home'
                self.ids.email.text = ''
                self.ids.password.text = ''
            else:
                self.show_popup('خطأ', 'البريد أو كلمة السر غير صحيحة')
        except Exception as e:
            self.show_popup('خطأ', f'فشل الاتصال: {str(e)}')
        finally:
            loading.dismiss()

class RegisterScreen(BaseScreen):
    def register(self):
        name = self.ids.name.text.strip()
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()
        phone = self.ids.phone.text.strip()
        user_type_display = self.ids.user_type.text

        if not db:
            self.show_popup('خطأ', 'لا يوجد اتصال بالإنترنت')
            return

        if not all([name, email, password, phone]) or user_type_display == ar('اختر نوع الحساب'):
            self.show_popup('خطأ', 'املأ جميع الحقول')
            return

        types_map = {'زبون': 'customer', 'تاجر': 'supplier', 'سائق': 'driver'}
        logical_type = 'customer'
        for k, v in types_map.items():
            if ar(k) == user_type_display:
                logical_type = v
                break

        loading = LoadingView()
        loading.open()
        try:
            user_key = email.replace('.', ',')
            if db.child("users").child(user_key).get().val():
                self.show_popup('خطأ', 'البريد موجود مسبقا')
                return

            db.child("users").child(user_key).set({
                'name': name,
                'password': password,
                'phone': phone,
                'type': logical_type,
                'balance': 0,
                'created_at': {".sv": "timestamp"}
            })
            self.show_popup('نجاح', 'تم إنشاء الحساب بنجاح')
            self.manager.current = 'login'
        except Exception as e:
            self.show_popup('خطأ', f'فشل التسجيل: {str(e)}')
        finally:
            loading.dismiss()

class HomeScreen(BaseScreen):
    def logout(self):
        global current_user, cart
        current_user = None
        cart = []
        self.manager.current = 'login'

class ProductsScreen(BaseScreen):
    def on_pre_enter(self):
        self.load_products()

    def load_products(self):
        grid = self.ids.products_grid
        grid.clear_widgets()

        if not db:
            grid.add_widget(Label(text=ar('لا يوجد اتصال'), font_name='Cairo'))
            return

        loading = LoadingView()
        loading.open()
        try:
            products_data = db.child("products").get().val()
            if not products_data:
                grid.add_widget(Label(text=ar('لا توجد منتجات حتى الآن، أضف منتجك الأول'), font_name='Cairo', size_hint_y=None, height=50))
                return

            products_list = products_data.values() if isinstance(products_data, dict) else products_data

            for p in products_list:
                if not p: continue
                box = BoxLayout(orientation='vertical', size_hint_y=None, height=120, padding=10)
                with box.canvas.before:
                    Color(rgba=COLORS['card'])
                    rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[15])
                box.bind(pos=lambda inst, pos, r=rect: setattr(r, 'pos', pos))
                box.bind(size=lambda inst, size, r=rect: setattr(r, 'size', size))

                box.add_widget(Label(text=ar(p['name']), font_name='Cairo', font_size=18, bold=True, size_hint_y=0.4))
                box.add_widget(Label(text=ar(p.get('desc', '')), font_name='Cairo', font_size=14, color=(0.7,0.7,0.7,1), size_hint_y=0.3))

                btn_box = BoxLayout(size_hint_y=0.3, spacing=10)
                btn_box.add_widget(Label(text=ar(f"{p['price']} دج"), font_name='Cairo', bold=True))
                btn = Button(text=ar('إضافة للسلة'), font_name='Cairo', background_color=COLORS['accent'])
                btn.bind(on_release=lambda x, prod=p: self.add_to_cart(prod))
                btn_box.add_widget(btn)
                box.add_widget(btn_box)
                grid.add_widget(box)
        except Exception as e:
            grid.add_widget(Label(text=ar(f'خطأ في التحميل: {str(e)}'), font_name='Cairo'))
        finally:
            loading.dismiss()

    def add_to_cart(self, product):
        cart.append(product)
        self.show_popup('تم', f"تم إضافة {product['name']} للسلة")

class AddProductScreen(BaseScreen):
    def clear_fields(self):
        self.ids.name.text = ''
        self.ids.price.text = ''
        self.ids.quantity.text = ''
        self.ids.desc.text = ''

    def add_product(self):
        if not db:
            self.show_popup('خطأ', 'لا يوجد اتصال بالإنترنت')
            return

        if not current_user or current_user['type'] not in ['supplier', 'admin']:
            self.show_popup('خطأ', 'ليس لديك صلاحية')
            return

        name = self.ids.name.text.strip()
        price_str = self.ids.price.text.strip()
        quantity_str = self.ids.quantity.text.strip()
        desc = self.ids.desc.text.strip()

        if not name or not price_str or not quantity_str:
            self.show_popup('خطأ', 'املأ جميع الحقول المطلوبة')
            return

        try:
            price = int(price_str)
            quantity = int(quantity_str)
        except ValueError:
            self.show_popup('خطأ', 'أدخل أرقاماً صالحة (Enter valid number)')
            return

        if quantity <= 0:
            self.show_popup('خطأ', 'الكمية يجب أن تكون أكبر من 0')
            return

        loading = LoadingView()
        loading.open()
        try:
            db.child("products").push({
                'name': name,
                'price': price,
                'quantity': quantity,
                'desc': desc,
                'supplier': current_user['email'],
                'created_at': {".sv": "timestamp"}
            })
            self.show_popup('نجاح', 'تم إضافة المنتج بنجاح')
            self.clear_fields()
        except Exception as e:
            self.show_popup('خطأ', f'فشل الإضافة: {str(e)}')
        finally:
            loading.dismiss()

class CartScreen(BaseScreen):
    def on_pre_enter(self):
        self.load_cart()

    def load_cart(self):
        grid = self.ids.cart_grid
        grid.clear_widgets()
        total = sum(p['price'] for p in cart)
        self.ids.total.text = ar(f'الإجمالي: {total} دج')

        if not cart:
            grid.add_widget(Label(text=ar('السلة فارغة'), font_name='Cairo', size_hint_y=None, height=50))
            return

        for i, p in enumerate(cart):
            box = BoxLayout(size_hint_y=None, height=60, padding=10)
            box.add_widget(Label(text=ar(p['name']), font_name='Cairo'))
            box.add_widget(Label(text=ar(f"{p['price']} دج"), font_name='Cairo'))
            btn = Button(text=ar('حذف'), size_hint_x=0.2, background_color=(0.8,0.2,0.2,1))
            btn.bind(on_release=lambda x, idx=i: self.remove_item(idx))
            box.add_widget(btn)
            grid.add_widget(box)

    def remove_item(self, idx):
        cart.pop(idx)
        self.load_cart()

    def confirm_order(self):
        if not db:
            self.show_popup('خطأ', 'لا يوجد اتصال بالإنترنت')
            return

        if not cart:
            self.show_popup('خطأ', 'السلة فارغة')
            return

        loading = LoadingView()
        loading.open()
        try:
            db.child("orders").push({
                'customer': current_user['email'],
                'products': cart.copy(),
                'total': sum(p['price'] for p in cart),
                'status': 'قيد المعالجة',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'created_at': {".sv": "timestamp"}
            })
            cart.clear()
            self.show_popup('نجاح', 'تم تأكيد الطلب بنجاح')
            self.manager.current = 'home'
        except Exception as e:
            self.show_popup('خطأ', f'فشل تأكيد الطلب: {str(e)}')
        finally:
            loading.dismiss()

class OrdersScreen(BaseScreen):
    def on_pre_enter(self):
        self.load_orders()

    def load_orders(self):
        grid = self.ids.orders_grid
        grid.clear_widgets()

        if not db:
            grid.add_widget(Label(text=ar('لا يوجد اتصال'), font_name='Cairo'))
            return

        loading = LoadingView()
        loading.open()
        try:
            all_orders = db.child("orders").get().val()
            if not all_orders:
                grid.add_widget(Label(text=ar('لا توجد طلبات'), font_name='Cairo', size_hint_y=None, height=50))
                return

            orders_list = all_orders.values() if isinstance(all_orders, dict) else all_orders
            user_orders = [o for o in orders_list if o and o['customer'] == current_user['email']]

            if not user_orders:
                grid.add_widget(Label(text=ar('لا توجد طلبات'), font_name='Cairo', size_hint_y=None, height=50))
                return

            for idx, o in enumerate(user_orders):
                box = BoxLayout(orientation='vertical', size_hint_y=None, height=100, padding=10)
                with box.canvas.before:
                    Color(rgba=COLORS['card'])
                    rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[15])
                box.bind(pos=lambda inst, pos, r=rect: setattr(r, 'pos', pos))
                box.bind(size=lambda inst, size, r=rect: setattr(r, 'size', size))

                box.add_widget(Label(text=ar(f"طلب رقم {idx+1} - {o['date']}"), font_name='Cairo', bold=True, size_hint_y=0.3))
                box.add_widget(Label(text=ar(f"عدد المنتجات: {len(o['products'])}"), font_name='Cairo', size_hint_y=0.3))
                box.add_widget(Label(text=ar(f"الإجمالي: {o['total']} دج - الحالة: {o['status']}"), font_name='Cairo', color=(0.2,0.8,0.4,1), size_hint_y=0.4))
                grid.add_widget(box)
        except Exception as e:
            grid.add_widget(Label(text=ar(f'خطأ: {str(e)}'), font_name='Cairo'))
        finally:
            loading.dismiss()

class ProfileScreen(BaseScreen):
    pass

class NeshrblekApp(App):
    def build(self):
        self.title = ar('نشربلك')
        return Builder.load_string(KV)

if __name__ == '__main__':
    NeshrblekApp().run()
