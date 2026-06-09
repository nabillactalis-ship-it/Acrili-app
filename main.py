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

# Firebase Config (Placeholders)
firebase_config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_AUTH_DOMAIN",
    "databaseURL": "YOUR_DATABASE_URL", # e.g., https://your-project.firebaseio.com
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_STORAGE_BUCKET",
    "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
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
current_user = {'name': 'مدير النظام', 'email': 'admin@nachrilak.com', 'type': 'admin', 'balance': 1000}
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
                    text: "{ar('طلباتي')}"
                    bg_color: (0.2, 0.7, 0.5, 1)
                    height: 120
                    on_release: root.manager.current = 'orders'

                CustomButton:
                    text: "{ar('إضافة منتج')}"
                    bg_color: (0.8, 0.5, 0.1, 1)
                    height: 120
                    id: add_btn
                    on_release: root.manager.current = 'add_product'

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

            CustomButton:
                text: "{ar('تحديث')}"
                size_hint_x: 0.2
                bg_color: (0.1, 0.5, 0.1, 1)
                on_release: root.load_products()

        ScrollView:
            id: scroll
            on_scroll_y: root.on_scroll(self, self.scroll_y)
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
            id: stock
            hint_text: "Quantity"
            font_name: 'Cairo'
            hint_text_font_name: 'Cairo'
            input_filter: 'int'
            multiline: False
            size_hint_y: None
            height: dp(48)
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
                    id: user_type
                    text: ""
                    font_size: 18
                    size_hint_y: None
                    height: 40
                    halign: 'right'

                Widget:
                    size_hint_y: None
                    height: dp(100)

<CartScreen>:
    name: 'cart'
    BoxLayout:
        orientation: 'vertical'
        CustomLabel:
            text: "{ar('سلة المشتريات (قريباً)')}"
        CustomButton:
            text: "{ar('رجوع')}"
            on_release: root.manager.current = 'home'

<OrdersScreen>:
    name: 'orders'
    BoxLayout:
        orientation: 'vertical'
        CustomLabel:
            text: "{ar('طلباتي (قريباً)')}"
        CustomButton:
            text: "{ar('رجوع')}"
            on_release: root.manager.current = 'home'
'''

class BaseScreen(Screen):
    def show_popup(self, title, msg):
        popup = Popup(
            title=ar(title),
            content=Label(text=ar(msg), font_name='Cairo'),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class HomeScreen(BaseScreen):
    def on_enter(self):
        if 'welcome' in self.ids:
            self.ids.welcome.text = ar(f'مرحبا {current_user["name"]}')

        try:
            profile = self.manager.get_screen('profile')
            profile.ids.user_name.text = ar(f"الاسم: {current_user['name']}")
            types_map = {'customer': 'زبون', 'supplier': 'تاجر', 'driver': 'سائق', 'admin': 'مدير'}
            display_type = types_map.get(current_user['type'], current_user['type'])
            profile.ids.user_type.text = ar(f"نوع الحساب: {display_type}")
        except:
            pass

    def logout(self):
        self.show_popup("تنبيه", "تم تعطيل تسجيل الخروج مؤقتاً")

class ProductsScreen(BaseScreen):
    is_loading = False

    def on_pre_enter(self):
        self.load_products()

    def on_scroll(self, scrollview, scroll_y):
        if scroll_y > 1.05 and not self.is_loading: # Pull to refresh detection
            self.load_products()

    def load_products(self):
        if self.is_loading:
            return
        self.is_loading = True

        grid = self.ids.products_grid
        grid.clear_widgets()

        if not db:
            grid.add_widget(Label(text=ar('لا يوجد اتصال بقاعدة البيانات'), font_name='Cairo'))
            self.is_loading = False
            return

        loading = LoadingView()
        loading.open()

        def fetch_data(dt):
            try:
                products_data = db.child("products").get().val()
                loading.dismiss()
                self.is_loading = False

                if not products_data:
                    grid.add_widget(Label(text=ar('No products yet, add your first product'), font_name='Cairo', size_hint_y=None, height=dp(100)))
                    return

                products_list = products_data.values() if isinstance(products_data, dict) else products_data

                for p in products_list:
                    if not p: continue
                    box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), padding=10)
                    with box.canvas.before:
                        Color(rgba=COLORS['card'])
                        rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[15])
                    box.bind(pos=lambda inst, pos, r=rect: setattr(r, 'pos', pos))
                    box.bind(size=lambda inst, size, r=rect: setattr(r, 'size', size))

                    box.add_widget(Label(text=ar(p['name']), font_name='Cairo', font_size=18, bold=True, size_hint_y=0.4))
                    box.add_widget(Label(text=ar(f"السعر: {p['price']} دج | الكمية: {p.get('stock', 0)}"), font_name='Cairo', font_size=14, size_hint_y=0.3))
                    grid.add_widget(box)
            except Exception as e:
                if loading: loading.dismiss()
                self.is_loading = False
                grid.add_widget(Label(text=ar(f'خطأ في التحميل: {str(e)}'), font_name='Cairo'))

        Clock.schedule_once(fetch_data, 0.1)

class AddProductScreen(BaseScreen):
    def clear_fields(self):
        self.ids.name.text = ''
        self.ids.price.text = ''
        self.ids.stock.text = ''
        self.ids.desc.text = ''

    def add_product(self):
        if not db:
            self.show_popup('خطأ', 'لا يوجد اتصال بالإنترنت')
            return

        name = self.ids.name.text.strip()
        price_str = self.ids.price.text.strip()
        stock_str = self.ids.stock.text.strip()
        desc = self.ids.desc.text.strip()

        if not name or not price_str or not stock_str:
            self.show_popup('خطأ', 'املأ جميع الحقول المطلوبة')
            return

        try:
            price = int(price_str)
            stock = int(stock_str)
        except ValueError:
            self.show_popup('خطأ', 'Enter valid number')
            return

        if stock <= 0:
            self.show_popup('خطأ', 'الكمية يجب أن تكون أكبر من 0')
            return

        loading = LoadingView()
        loading.open()

        def save_data(dt):
            try:
                db.child("products").push({
                    'name': name,
                    'price': price,
                    'stock': stock,
                    'desc': desc,
                    'supplier': current_user['email'],
                    'created_at': {".sv": "timestamp"}
                })
                loading.dismiss()
                self.show_popup('نجاح', 'تم إضافة المنتج بنجاح')
                self.clear_fields()
            except Exception as e:
                if loading: loading.dismiss()
                self.show_popup('خطأ', f'فشل الإضافة: {str(e)}')

        Clock.schedule_once(save_data, 0.1)

class CartScreen(BaseScreen): pass
class OrdersScreen(BaseScreen): pass
class ProfileScreen(BaseScreen): pass

class NeshrblekApp(App):
    def build(self):
        self.title = ar('نشربلك')
        return Builder.load_string(KV)

if __name__ == '__main__':
    NeshrblekApp().run()
