from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ListProperty
import json
import os
import sys
from datetime import datetime

# إعداد تسجيل الأعطال في مكان قابل للكتابة
def get_log_path():
    try:
        from kivy.utils import platform
        if platform == 'android':
            from android.storage import app_storage_dir
            return os.path.join(app_storage_dir(), "crash_log.txt")
    except:
        pass
    return os.path.join(os.getcwd(), "crash_log.txt")

LOG_FILE = get_log_path()

def log_error(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

# استيراد Kivy بحذر
try:
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.textinput import TextInput
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.gridlayout import GridLayout
    from kivy.core.text import LabelBase
    from kivy.utils import get_color_from_hex
    from kivy.graphics import Color, RoundedRectangle
    from kivy.properties import ListProperty
except Exception as e:
    log_error(f"Kivy Import Error: {e}")
    raise

# دوال مساعدة للاستيراد المتأخر (Lazy Loading) مع التخزين المؤقت
_reshaper = None
_bidi = None

def get_ar_tools():
    global _reshaper, _bidi
    if _reshaper is None or _bidi is None:
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            _reshaper = arabic_reshaper
            _bidi = get_display
        except Exception as e:
            log_error(f"Arabic Tools Import Error: {e}")
    return _reshaper, _bidi

def ar(text):
    """دالة تعالج العربية باش تتلصق وتترتب من اليمين"""
    if not text:
        return ""
    reshaper, bidi = get_ar_tools()
    if not reshaper or not bidi:
        return str(text)
    try:
        reshaped = reshaper.reshape(str(text))
        return bidi(reshaped)
    except Exception:
        return str(text)

# تسجيل خط عربي
try:
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Cairo-Regular.ttf')
    if os.path.exists(font_path):
        LabelBase.register(name='Cairo', fn_regular=font_path)
    else:
        log_error("Font file Cairo-Regular.ttf not found")
except Exception as e:
    log_error(f"Font Registration Error: {e}")

# ألوان التطبيق
COLORS = {
    'bg': get_color_from_hex('#1a1a2e'),
    'card': get_color_from_hex('#16213e'),
    'primary': get_color_from_hex('#0f3460'),
    'accent': get_color_from_hex('#e94560'),
    'text': get_color_from_hex('#ffffff'),
    'text_dim': get_color_from_hex('#a0a0a0')
}

# ملفات التخزين
DATA_DIR = os.path.join(os.getcwd(), 'nachrilak_data')
os.makedirs(DATA_DIR, exist_ok=True)
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')

def load_json(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hash_password(password):
    """تشفير كلمة السر"""
    try:
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    except Exception as e:
        log_error(f"Hashing Error: {e}")
        return password

# تهيئة Firebase (تأجيلها لتفادي التعطل عند الانطلاق)
db = None

def get_db():
    global db
    if db is None:
        try:
            import pyrebase
            firebase_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'google-services.json')
            if not os.path.exists(firebase_config_file):
                log_error(f"Config file {firebase_config_file} not found")
                return None

            with open(firebase_config_file, 'r') as f:
                google_services = json.load(f)

            project_info = google_services['project_info']
            client_info = google_services['client'][0]
            api_key = client_info['api_key'][0]['current_key']

            firebase_config = {
                "apiKey": api_key,
                "authDomain": f"{project_info['project_id']}.firebaseapp.com",
                "databaseURL": f"https://{project_info['project_id']}-default-rtdb.firebaseio.com",
                "projectId": project_info['project_id'],
                "storageBucket": project_info['storage_bucket'],
                "messagingSenderId": project_info['project_number'],
                "appId": client_info.get('client_info', {}).get('mobilesdk_app_id', "")
            }

            firebase = pyrebase.initialize_app(firebase_config)
            db = firebase.database()
        except Exception as e:
            log_error(f"Firebase Init Error: {e}")
            return None
    return db

# متغيرات عامة
current_user = None
cart = []

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
            text: "{ar('مرحبا بك في نشريلك')}"
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
            height: 50
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
            height: 50
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15

        TextInput:
            id: desc
            hint_text: "{ar('وصف المنتج')}"
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            size_hint_y: None
            height: 100
            background_color: 0.15,0.15,0.25,1
            foreground_color: 1,1,1,1
            padding: 15

        CustomButton:
            text: "{ar('حفظ المنتج')}"
            bg_color: (0.1, 0.6, 0.9, 1)
            on_release: root.add_product()

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
        from kivy.uix.popup import Popup
        popup = Popup(title=ar(title), content=Label(text=ar(msg), font_name='Cairo'),
                     size_hint=(0.8, 0.4))
        popup.open()

class LoginScreen(BaseScreen):
    def login(self):
        global current_user
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()

        if not email or not password:
            self.show_popup('خطأ', 'الرجاء إدخال البريد وكلمة السر')
            return

        # Fetch user from Firebase
        database = get_db()
        if not database:
            self.show_popup('خطأ', 'لا يمكن الاتصال بقاعدة البيانات')
            return

        safe_email = email.replace('.', ',')
        try:
            user_data = database.child("users").child(safe_email).get()
            user = user_data.val()
        except Exception as e:
            self.show_popup('خطأ', f'فشل الاتصال: {e}')
            return

        if user and user['password'] == hash_password(password):
            current_user = user
            self.manager.get_screen('home').ids.welcome.text = ar(f'مرحبا {user["name"]}')

            # Update profile info
            profile = self.manager.get_screen('profile')
            profile.ids.user_name.text = ar(f"الاسم: {user['name']}")
            profile.ids.user_email.text = f"البريد: {user['email']}"

            types_map = {'customer': 'زبون', 'supplier': 'تاجر', 'driver': 'سائق'}
            display_type = types_map.get(user['type'], user['type'])
            profile.ids.user_type.text = ar(f"نوع الحساب: {display_type}")
            profile.ids.user_phone.text = ar(f"رقم الهاتف: {user['phone']}")
            profile.ids.user_balance.text = ar(f"الرصيد: {user['balance']} دج")

            # Update add button visibility
            add_btn = self.manager.get_screen('home').ids.add_btn
            if user['type'] in ['supplier', 'admin']:
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

class RegisterScreen(BaseScreen):
    def register(self):
        name = self.ids.name.text.strip()
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()
        phone = self.ids.phone.text.strip()
        user_type_display = self.ids.user_type.text

        if not all([name, email, password, phone]) or user_type_display == ar('اختر نوع الحساب'):
            self.show_popup('خطأ', 'املأ جميع الحقول')
            return

        # Correctly map display types to logical types
        types_map = {'زبون': 'customer', 'تاجر': 'supplier', 'سائق': 'driver'}
        logical_type = 'customer'
        for k, v in types_map.items():
            if ar(k) == user_type_display:
                logical_type = v
                break

        # Check if user exists in Firebase
        database = get_db()
        if not database:
            self.show_popup('خطأ', 'لا يمكن الاتصال بقاعدة البيانات')
            return

        safe_email = email.replace('.', ',')
        try:
            # Optimized existence check by only getting the password field
            if database.child("users").child(safe_email).child("password").get().val():
                self.show_popup('خطأ', 'البريد موجود مسبقا')
                return

            user_obj = {
                'name': name,
                'email': email,
                'password': hash_password(password),
                'phone': phone,
                'type': logical_type,
                'balance': 0,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
            }

            database.child("users").child(safe_email).set(user_obj)
        except Exception as e:
            self.show_popup('خطأ', f'فشل العملية: {e}')
            return
        self.show_popup('نجاح', 'تم إنشاء الحساب بنجاح')
        self.manager.current = 'login'

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

        database = get_db()
        if not database:
            grid.add_widget(Label(text=ar('خطأ في قاعدة البيانات'), font_name='Cairo', size_hint_y=None, height=50))
            return

        # Fetch products from Firebase
        try:
            products_data = database.child("products").get()
            products = []
            if products_data.val():
                if isinstance(products_data.val(), list):
                    products = [p for p in products_data.val() if p is not None]
                else:
                    products = list(products_data.val().values())
        except Exception as e:
            grid.add_widget(Label(text=ar(f'فشل التحميل: {e}'), font_name='Cairo', size_hint_y=None, height=50))
            return

        if not products:
            grid.add_widget(Label(text=ar('لا توجد منتجات'), font_name='Cairo', size_hint_y=None, height=50))
            return

        for p in products:
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=120, padding=10)

            # Closure fix for dynamic background
            with box.canvas.before:
                Color(rgba=COLORS['card'])
                rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[15])

            box.bind(pos=lambda inst, pos, r=rect: setattr(r, 'pos', pos),
                     size=lambda inst, size, r=rect: setattr(r, 'size', size))

            box.add_widget(Label(text=ar(p['name']), font_name='Cairo', font_size=18, bold=True, size_hint_y=0.4))
            box.add_widget(Label(text=ar(p.get('desc', '')), font_name='Cairo', font_size=14, color=(0.7,0.7,0.7,1), size_hint_y=0.3))

            btn_box = BoxLayout(size_hint_y=0.3, spacing=10)
            btn_box.add_widget(Label(text=ar(f"{p['price']} دج"), font_name='Cairo', bold=True))
            btn = Button(text=ar('إضافة للسلة'), font_name='Cairo', background_color=COLORS['accent'])
            btn.bind(on_release=lambda x, prod=p: self.add_to_cart(prod))
            btn_box.add_widget(btn)
            box.add_widget(btn_box)
            grid.add_widget(box)

    def add_to_cart(self, product):
        cart.append(product)
        self.show_popup('تم', f"تم إضافة {product['name']} للسلة")

class AddProductScreen(BaseScreen):
    def add_product(self):
        if not current_user or current_user['type'] not in ['supplier', 'admin']:
            self.show_popup('خطأ', 'ليس لديك صلاحية')
            return

        name = self.ids.name.text.strip()
        price = self.ids.price.text.strip()
        desc = self.ids.desc.text.strip()

        if not all([name, price]):
            self.show_popup('خطأ', 'املأ اسم وسعر المنتج')
            return

        product_obj = {
            'name': name,
            'price': int(price),
            'desc': desc,
            'supplier': current_user['email'],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        database = get_db()
        if not database:
            self.show_popup('خطأ', 'قاعدة البيانات غير متوفرة')
            return

        try:
            database.child("products").push(product_obj)
        except Exception as e:
            self.show_popup('خطأ', f'فشل الحفظ: {e}')
            return
        self.show_popup('نجاح', 'تم إضافة المنتج')
        self.ids.name.text = ''
        self.ids.price.text = ''
        self.ids.desc.text = ''

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
        if not cart:
            self.show_popup('خطأ', 'السلة فارغة')
            return

        database = get_db()
        if not database:
            self.show_popup('خطأ', 'لا يوجد اتصال')
            return

        order = {
            'customer': current_user['email'],
            'products': cart.copy(),
            'total': sum(p['price'] for p in cart),
            'status': 'قيد المعالجة',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        try:
            database.child("orders").push(order)
        except Exception as e:
            self.show_popup('خطأ', f'فشل الطلب: {e}')
            return
        cart.clear()
        self.show_popup('نجاح', 'تم تأكيد الطلب بنجاح')
        self.manager.current = 'home'

class OrdersScreen(BaseScreen):
    def on_pre_enter(self):
        self.load_orders()

    def load_orders(self):
        grid = self.ids.orders_grid
        grid.clear_widgets()

        database = get_db()
        if not database:
            grid.add_widget(Label(text=ar('خطأ في الاتصال'), font_name='Cairo', size_hint_y=None, height=50))
            return

        # Fetch orders from Firebase
        try:
            all_orders_data = database.child("orders").get()
            user_orders = []
            if all_orders_data.val():
                all_orders = []
                if isinstance(all_orders_data.val(), list):
                    all_orders = [o for o in all_orders_data.val() if o is not None]
                else:
                    # Use key as ID if it doesn't have one
                    for key, val in all_orders_data.val().items():
                        val['firebase_key'] = key
                        all_orders.append(val)

                user_orders = [o for o in all_orders if o.get('customer') == current_user['email']]
        except Exception as e:
            grid.add_widget(Label(text=ar(f'فشل التحميل: {e}'), font_name='Cairo', size_hint_y=None, height=50))
            return

        if not user_orders:
            grid.add_widget(Label(text=ar('لا توجد طلبات'), font_name='Cairo', size_hint_y=None, height=50))
            return

        for i, o in enumerate(user_orders):
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=100, padding=10)

            with box.canvas.before:
                Color(rgba=COLORS['card'])
                rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[15])

            box.bind(pos=lambda inst, pos, r=rect: setattr(r, 'pos', pos),
                     size=lambda inst, size, r=rect: setattr(r, 'size', size))

            order_id = o.get('id', i+1)
            box.add_widget(Label(text=ar(f"طلب رقم {order_id} - {o['date']}"), font_name='Cairo', bold=True, size_hint_y=0.3))
            box.add_widget(Label(text=ar(f"عدد المنتجات: {len(o['products'])}"), font_name='Cairo', size_hint_y=0.3))
            box.add_widget(Label(text=ar(f"الإجمالي: {o['total']} دج - الحالة: {o['status']}"), font_name='Cairo', color=(0.2,0.8,0.4,1), size_hint_y=0.4))
            grid.add_widget(box)

class ProfileScreen(BaseScreen):
    pass

class NacrilkApp(App):
    def build(self):
        self.title = ar('نشريلك')
        try:
            return Builder.load_string(KV)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            log_error(f"KV Loading Error: {error_details}")
            return Label(text=f"Error loading UI:\n{e}")

if __name__ == '__main__':
    try:
        NacrilkApp().run()
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        log_error(f"Top-level Crash: {error_details}")
        # Show error in console/logcat as well
        print(error_details)
