from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.core.text import LabelBase
import json
import os
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

# إعدادات النافذة
Window.clearcolor = (0.12, 0.12, 0.12, 1)
Window.softinput_mode = 'resize'

# سجل الخط العربي - لازم ملف Cairo-Regular.ttf يكون حدا الكود
font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Cairo-Regular.ttf')
LabelBase.register(name='Cairo', fn_regular=font_path)

def ar(text):
    """دالة تعالج العربية باش تتلصق وتترتب من اليمين"""
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# مسار التخزين
app_dir = os.path.join(os.getcwd(), 'nachrilak_data')
os.makedirs(app_dir, exist_ok=True)

PRODUCTS_FILE = os.path.join(app_dir, 'products.json')
ORDERS_FILE = os.path.join(app_dir, 'orders.json')
USERS_FILE = os.path.join(app_dir, 'users.json')

def load_products():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return [{'name': 'بيتزا', 'price': 800, 'supplier': 'admin@nachrilak.com', 'payment_methods': ['points'], 'ccp_number': ''}]

def save_products(products_list):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(products_list, f, ensure_ascii=False, indent=2)

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_orders(orders_list):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders_list, f, ensure_ascii=False, indent=2)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users_dict):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_dict, f, ensure_ascii=False, indent=2)

users = load_users()
current_user = None
current_email = None
user_type = 'زبون'
products = load_products()
orders = load_orders()
selected_product = None

class BaseScreen(Screen):
    def add_back_button(self, target='home_screen'):
        back_btn = Button(
            text=ar('< رجوع'),
            font_name='Cairo',
            font_size=18,
            size_hint=(0.25, 0.09),
            pos_hint={'x': 0.02, 'top': 0.98},
            background_normal='',
            background_color=(0.2, 0.2, 0.2, 1)
        )
        back_btn.bind(on_press=lambda x: self.go_back(target))
        self.add_widget(back_btn)

    def go_back(self, target):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = target

    def switch(self, screen):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = screen

class LoginScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        scroll = ScrollView(do_scroll_x=False)
        scroll_content = FloatLayout(size_hint_y=None, height=800)

        scroll_content.add_widget(Label(
            text=ar('نشريلك'),
            font_name='Cairo',
            font_size=40,
            bold=True,
            size_hint=(0.9, 0.12),
            pos_hint={'center_x': 0.5, 'top': 0.95}
        ))

        self.type_spinner = Spinner(
            text=ar('زبون'),
            values=[ar('زبون'), ar('تاجر'), ar('سائق')],
            font_name='Cairo',
            font_size=22,
            background_normal='',
            background_color=(0.15, 0.15, 0.15, 1),
            size_hint=(0.9, 0.13),
            pos_hint={'center_x': 0.5, 'top': 0.8}
        )
        scroll_content.add_widget(self.type_spinner)

        self.email_input = TextInput(
            hint_text=ar('البريد الإلكتروني'),
            font_name='Cairo',
            multiline=False,
            font_size=24,
            padding=[20, 25],
            background_color=(1, 1, 1, 1),
            size_hint=(0.9, 0.15),
            pos_hint={'center_x': 0.5, 'top': 0.63}
        )
        scroll_content.add_widget(self.email_input)

        self.password_input = TextInput(
            hint_text=ar('كلمة المرور'),
            font_name='Cairo',
            password=True,
            multiline=False,
            font_size=24,
            padding=[20, 25],
            background_color=(1, 1, 1, 1),
            size_hint=(0.9, 0.15),
            pos_hint={'center_x': 0.5, 'top': 0.44}
        )
        scroll_content.add_widget(self.password_input)

        def update_fields(instance, value):
            global user_type
            if value == ar('زبون'): user_type = 'زبون'
            elif value == ar('تاجر'): user_type = 'تاجر'
            elif value == ar('سائق'): user_type = 'سائق'
        self.type_spinner.bind(text=update_fields)

        login_btn = Button(
            text=ar('دخول'),
            font_name='Cairo',
            font_size=24,
            bold=True,
            size_hint=(0.9, 0.15),
            pos_hint={'center_x': 0.5, 'y': 0.08},
            background_normal='',
            background_color=(0.0, 0.4, 0.8, 1)
        )
        login_btn.bind(on_press=self.login)
        scroll_content.add_widget(login_btn)

        scroll.add_widget(scroll_content)
        self.layout.add_widget(scroll)
        self.add_widget(self.layout)

    def login(self, instance):
        global current_user, current_email
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        if not email or not password:
            self.email_input.hint_text = ar('املأ الكل')
            return
        if email not in users:
            balance = 100 if user_type == 'زبون' else 0
            users[email] = {'password': password, 'balance': balance, 'type': user_type}
            save_users(users)
        elif users[email]['password']!= password:
            self.password_input.text = ''
            self.password_input.hint_text = ar('خطأ')
            return
        current_user = users[email]
        current_email = email
        self.manager.current = 'home_screen'

class HomeScreen(BaseScreen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = FloatLayout()
        self.add_back_button('login_screen')

        btn1 = Button(
            text=ar('المنتجات'),
            font_name='Cairo',
            font_size=24, bold=True,
            size_hint=(0.85, 0.15),
            pos_hint={'center_x': 0.5, 'top': 0.85},
            background_normal='', background_color=(0.25, 0.25, 0.25, 1)
        )
        btn1.bind(on_press=lambda x: self.switch('products_screen'))
        layout.add_widget(btn1)

        if current_user and current_user['type'] == 'تاجر':
            btn_orders = Button(
                text=ar('الطلبات'),
                font_name='Cairo',
                font_size=24, bold=True,
                size_hint=(0.85, 0.15),
                pos_hint={'center_x': 0.5, 'center_y': 0.65},
                background_normal='', background_color=(0.8, 0.4, 0.0, 1)
            )
            btn_orders.bind(on_press=lambda x: self.switch('supplier_orders_screen'))
            layout.add_widget(btn_orders)

            btn_add = Button(
                text=ar('أضف منتج'),
                font_name='Cairo',
                font_size=24, bold=True,
                size_hint=(0.85, 0.15),
                pos_hint={'center_x': 0.5, 'center_y': 0.45},
                background_normal='', background_color=(0.0, 0.6, 0.3, 1)
            )
            btn_add.bind(on_press=lambda x: self.switch('add_product_screen'))
            layout.add_widget(btn_add)
            settings_y = 0.25
        elif current_user and current_user['type'] == 'سائق':
            btn_orders = Button(
                text=ar('الطلبات'),
                font_name='Cairo',
                font_size=24, bold=True,
                size_hint=(0.85, 0.15),
                pos_hint={'center_x': 0.5, 'center_y': 0.65},
                background_normal='', background_color=(0.0, 0.5, 0.8, 1)
            )
            btn_orders.bind(on_press=lambda x: self.switch('driver_orders_screen'))
            layout.add_widget(btn_orders)
            settings_y = 0.45
        else:
            settings_y = 0.65

        btn2 = Button(
            text=ar('الإعدادات'),
            font_name='Cairo',
            font_size=24, bold=True,
            size_hint=(0.85, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': settings_y},
            background_normal='', background_color=(0.25, 0.25, 0.25, 1)
        )
        btn2.bind(on_press=lambda x: self.switch('settings_screen'))
        layout.add_widget(btn2)
        self.add_widget(layout)

class ProductsScreen(BaseScreen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = FloatLayout()
        self.add_back_button('home_screen')

        if current_user and current_user['type'] == 'زبون':
            add_order_btn = Button(
                text=ar('أضف طلب'),
                font_name='Cairo',
                font_size=22, bold=True,
                size_hint=(0.9, 0.1),
                pos_hint={'center_x': 0.5, 'top': 0.88},
                background_normal='', background_color=(0.8, 0.2, 0.2, 1)
            )
            add_order_btn.bind(on_press=lambda x: self.switch('search_product_screen'))
            layout.add_widget(add_order_btn)
            scroll_y = 0.4
        else:
            scroll_y = 0.5

        scroll = ScrollView(size_hint=(0.9, 0.65), pos_hint={'center_x': 0.5, 'center_y': scroll_y})
        grid = GridLayout(cols=1, size_hint_y=None, spacing=12, padding=20)
        grid.bind(minimum_height=grid.setter('height'))

        for p in products:
            grid.add_widget(Label(
                text=ar(f"{p['name']} - {p['price']} نقطة"),
                font_name='Cairo',
                font_size=22, size_hint_y=None, height=70
            ))
        scroll.add_widget(grid)
        layout.add_widget(scroll)
        self.add_widget(layout)

class AddProductScreen(BaseScreen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout_float = FloatLayout()
        self.add_back_button('home_screen')

        scroll = ScrollView(do_scroll_x=False, size_hint=(1, 0.85), pos_hint={'top': 0.85})
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        layout.add_widget(Label(text=ar('إضافة منتج'), font_name='Cairo', font_size=30, bold=True, size_hint_y=None, height=70))

        self.name_input = TextInput(hint_text=ar('اسم المنتج'), font_name='Cairo', font_size=22, padding=[20, 25], background_color=(1, 1, 1, 1), size_hint_y=None, height=85)
        layout.add_widget(self.name_input)

        self.price_input = TextInput(hint_text=ar('السعر بالنقاط'), font_name='Cairo', input_filter='int', font_size=22, padding=[20, 25], background_color=(1, 1, 1, 1), size_hint_y=None, height=85)
        layout.add_widget(self.price_input)

        layout.add_widget(Label(text=ar('طرق الدفع'), font_name='Cairo', font_size=22, bold=True, size_hint_y=None, height=50))
        self.pay_points = Button(text=ar('[ ] نقاط'), font_name='Cairo', font_size=20, size_hint_y=None, height=70, background_color=(0.3,0.3,0.3,1))
        self.pay_ccp = Button(text=ar('[ ] CCP'), font_name='Cairo', font_size=20, size_hint_y=None, height=70, background_color=(0.3,0.3,0.3,1))
        self.pay_cash = Button(text=ar('[ ] كاش'), font_name='Cairo', font_size=20, size_hint_y=None, height=70, background_color=(0.3,0.3,0.3,1))

        self.pay_points.bind(on_press=lambda x: self.toggle_btn(self.pay_points, 'نقاط'))
        self.pay_ccp.bind(on_press=lambda x: self.toggle_btn(self.pay_ccp, 'CCP'))
        self.pay_cash.bind(on_press=lambda x: self.toggle_btn(self.pay_cash, 'كاش'))

        layout.add_widget(self.pay_points)
        layout.add_widget(self.pay_ccp)
        layout.add_widget(self.pay_cash)

        self.ccp_input = TextInput(hint_text=ar('رقم CCP'), font_name='Cairo', font_size=22, padding=[20, 25], background_color=(1, 1, 1, 1), size_hint_y=None, height=85)
        layout.add_widget(self.ccp_input)

        add_btn = Button(text=ar('إضافة'), font_name='Cairo', font_size=24, bold=True, size_hint_y=None, height=85, background_normal='', background_color=(0.0, 0.6, 0.4, 1))
        add_btn.bind(on_press=self.add_product)
        layout.add_widget(add_btn)

        layout.add_widget(Label(size_hint_y=None, height=100))
        scroll.add_widget(layout)
        layout_float.add_widget(scroll)
        self.add_widget(layout_float)

    def toggle_btn(self, btn, label):
        if getattr(btn, 'active', False):
             btn.active = False
             btn.text = ar(f'[ ] {label}')
             btn.background_color = (0.3, 0.3, 0.3, 1)
        else:
             btn.active = True
             btn.text = ar(f'[x] {label}')
             btn.background_color = (0.0, 0.6, 0.4, 1)

    def add_product(self, x):
        name = self.name_input.text.strip()
        try:
            price = int(self.price_input.text)
            methods = []
            if getattr(self.pay_points, 'active', False): methods.append('points')
            if getattr(self.pay_ccp, 'active', False): methods.append('ccp')
            if getattr(self.pay_cash, 'active', False): methods.append('cash')

            if name and price > 0 and methods and current_email:
                products.append({
                    'name': name,
                    'price': price,
                    'supplier': current_email,
                    'payment_methods': methods,
                    'ccp_number': self.ccp_input.text.strip() if 'ccp' in methods else ''
                })
                save_products(products)
                self.switch('home_screen')
        except:
            self.price_input.hint_text = ar('خطأ')

class SearchProductScreen(BaseScreen):
    def on_pre_enter(self):
        self.clear_widgets()
        self.add_back_button('products_screen')

        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text=ar('اختر المنتج'), font_name='Cairo', font_size=28, bold=True, size_hint_y=None, height=60))

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=10)
        grid.bind(minimum_height=grid.setter('height'))

        for idx, p in enumerate(products):
            btn = Button(
                text=ar(f"{p['name']} - {p['price']} نقطة"),
                font_name='Cairo',
                font_size=20,
                size_hint_y=None,
                height=70,
                background_normal='',
                background_color=(0.3, 0.3, 0.3, 1)
            )
            btn.bind(on_press=lambda x, i=idx: self.select_product(i))
            grid.add_widget(btn)

        scroll.add_widget(grid)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def select_product(self, idx):
        global selected_product
        selected_product = products[idx]
        self.switch('confirm_order_screen')

class ConfirmOrderScreen(BaseScreen):
    def on_pre_enter(self):
        self.clear_widgets()
        self.add_back_button('search_product_screen')

        scroll = ScrollView(do_scroll_x=False)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        if selected_product:
            layout.add_widget(Label(text=ar(f"المنتج: {selected_product['name']}"), font_name='Cairo', font_size=26, bold=True, size_hint_y=None, height=60))
            layout.add_widget(Label(text=ar(f"السعر: {selected_product['price']} نقطة"), font_name='Cairo', font_size=24, size_hint_y=None, height=50))
            layout.add_widget(Label(text=ar(f"رصيدك: {current_user['balance']} نقطة"), font_name='Cairo', font_size=22, size_hint_y=None, height=50))

            layout.add_widget(Label(text=ar('طريقة الدفع'), font_name='Cairo', font_size=22, bold=True, size_hint_y=None, height=50))

            vals = []
            display_to_logical = {}
            for v in selected_product['payment_methods']:
                if v == 'points': d = ar('نقاط')
                elif v == 'ccp': d = 'CCP'
                elif v == 'cash': d = ar('كاش')
                else: d = v
                vals.append(d)
                display_to_logical[d] = v

            self.pay_choice = Spinner(
                text=vals[0] if vals else "",
                values=vals,
                font_name='Cairo',
                font_size=22,
                size_hint_y=None,
                height=80,
                background_color=(0.15, 0.15, 0.15, 1)
            )
            layout.add_widget(self.pay_choice)

            if 'ccp' in selected_product['payment_methods']:
                layout.add_widget(Label(text=ar(f"رقم CCP: {selected_product.get('ccp_number', 'لا يوجد')}"), font_name='Cairo', font_size=18, color=(1,0,0,1), size_hint_y=None, height=40))

            confirm_btn = Button(text=ar('تأكيد الطلب'), font_name='Cairo', font_size=24, bold=True, size_hint_y=None, height=80, background_color=(0.0, 0.6, 0.3, 1))

            def confirm_order(x):
                global orders
                order = {
                    'id': len(orders) + 1,
                    'customer': current_email,
                    'product': selected_product['name'],
                    'price': selected_product['price'],
                    'supplier': selected_product['supplier'],
                    'driver': None,
                    'payment_method': display_to_logical.get(self.pay_choice.text, self.pay_choice.text),
                    'status': 'قيد الانتظار',
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                orders.append(order)
                save_orders(orders)
                self.switch('home_screen')
            confirm_btn.bind(on_press=confirm_order)
            layout.add_widget(confirm_btn)

        layout.add_widget(Label(size_hint_y=None, height=100))
        scroll.add_widget(layout)
        self.add_widget(scroll)

class SupplierOrdersScreen(BaseScreen):
    def on_pre_enter(self):
        self.clear_widgets()
        self.add_back_button('home_screen')

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text=ar('الطلبات الواردة'), font_name='Cairo', font_size=28, bold=True, size_hint_y=None, height=60))

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=10)
        grid.bind(minimum_height=grid.setter('height'))

        my_orders = [o for o in orders if o['supplier'] == current_email and o['status'] == 'قيد الانتظار']
        if not my_orders:
            grid.add_widget(Label(text=ar('لا توجد طلبات'), font_name='Cairo', font_size=20))
        else:
            for o in my_orders:
                box = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=5)
                box.add_widget(Label(
                    text=ar(f"طلب رقم #{o['id']}\n{o['product']} - {o['price']} نقطة\nالزبون: {o['customer']}\nالدفع: {o['payment_method']}"),
                    font_name='Cairo',
                    font_size=18
                ))

                validate_btn = Button(
                    text=ar('تأكيد'),
                    font_name='Cairo',
                    size_hint_y=None,
                    height=50,
                    background_color=(0.0, 0.6, 0.3, 1)
                )
                validate_btn.bind(on_press=lambda x, order_id=o['id']: self.validate_order(order_id))
                box.add_widget(validate_btn)
                grid.add_widget(box)

        scroll.add_widget(grid)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def validate_order(self, order_id):
        global orders, users
        for o in orders:
            if o['id'] == order_id and o['status'] == 'قيد الانتظار':
                customer_email = o['customer']
                price = o['price']
                payment = o['payment_method']

                if payment == 'points':
                    if users[customer_email]['balance'] >= price:
                        users[customer_email]['balance'] -= price
                        users[current_email]['balance'] += price
                        o['status'] = 'جاهز للتوصيل'
                        save_users(users)
                        save_orders(orders)
                    else:
                        o['status'] = 'ملغي'
                        save_orders(orders)
                else:
                    o['status'] = 'جاهز للتوصيل'
                    save_orders(orders)
                break
        self.on_pre_enter()

class DriverOrdersScreen(BaseScreen):
    def on_pre_enter(self):
        self.clear_widgets()
        self.add_back_button('home_screen')

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text=ar('الطلبات الجاهزة'), font_name='Cairo', font_size=28, bold=True, size_hint_y=None, height=60))

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        available = [o for o in orders if o['status'] == 'جاهز للتوصيل' and o['driver'] is None]
        if not available:
            grid.add_widget(Label(text=ar('لا توجد طلبات'), font_name='Cairo', font_size=20))
        else:
            for o in available:
                btn = Button(
                    text=ar(f"طلب #{o['id']}\n{o['product']} - {o['price']} نقطة\nالتاجر: {o['supplier']}"),
                    font_name='Cairo',
                    font_size=18,
                    size_hint_y=None,
                    height=90,
                    background_normal='',
                    background_color=(0.0, 0.5, 0.8, 1)
                )
                btn.bind(on_press=lambda x, order_id=o['id']: self.accept_order(order_id))
                grid.add_widget(btn)

        scroll.add_widget(grid)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def accept_order(self, order_id):
        for o in orders:
            if o['id'] == order_id:
                o['driver'] = current_email
                o['status'] = 'قيد التوصيل'
                save_orders(orders)
                break
        self.switch('home_screen')

class SettingsScreen(BaseScreen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = FloatLayout()
        self.add_back_button('home_screen')

        balance = current_user['balance'] if current_user else 0
        self.balance_label = Label(
            text=ar(f'الرصيد: {balance} نقطة'),
            font_name='Cairo',
            font_size=26, bold=True,
            size_hint=(0.85, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.7}
        )
        layout.add_widget(self.balance_label)

        if current_user and current_user['type'] == 'زبون':
            topup_btn = Button(
                text=ar('شحن الرصيد'),
                font_name='Cairo',
                font_size=24, bold=True,
                size_hint=(0.85, 0.15),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                background_normal='', background_color=(0.0, 0.6, 0.4, 1)
            )
            topup_btn.bind(on_press=lambda x: self.switch('topup_screen'))
            layout.add_widget(topup_btn)
            logout_y = 0.3
        else:
            logout_y = 0.5

        logout_btn = Button(
            text=ar('تسجيل الخروج'),
            font_name='Cairo',
            font_size=24, bold=True,
            size_hint=(0.85, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': logout_y},
            background_normal='', background_color=(0.8, 0.2, 0.2, 1)
        )
        def logout(x):
            global current_user, current_email
            current_user = None
            current_email = None
            self.switch('login_screen')
        logout_btn.bind(on_press=logout)
        layout.add_widget(logout_btn)
        self.add_widget(layout)

class TopUpScreen(BaseScreen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout_float = FloatLayout()
        self.add_back_button('settings_screen')
        scroll = ScrollView(do_scroll_x=False, size_hint=(1, 0.85), pos_hint={'top': 0.85})
        layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=35, spacing=25)
        layout.bind(minimum_height=layout.setter('height'))

        layout.add_widget(Label(text=ar('شحن الرصيد'), font_name='Cairo', size_hint_y=None, height=80, font_size=30, bold=True))
        layout.add_widget(Label(text=ar('CCP: 1234 5678 99 00'), font_name='Cairo', font_size=22, size_hint_y=None, height=60))
        layout.add_widget(Label(text=ar('1 نقطة = 10 دج'), font_name='Cairo', font_size=22, size_hint_y=None, height=60))

        self.amount = TextInput(
            hint_text=ar('المبلغ بالدينار'),
            font_name='Cairo',
            multiline=False, input_filter='int',
            font_size=24, padding=[20, 25],
            background_color=(1, 1, 1, 1),
            size_hint_y=None, height=100
        )
        layout.add_widget(self.amount)

        btn = Button(
            text=ar('طلب الشحن'),
            font_name='Cairo',
            font_size=24, bold=True,
            size_hint_y=None, height=90,
            background_normal='', background_color=(0.0, 0.6, 0.4, 1)
        )
        btn.bind(on_press=self.request_topup)
        layout.add_widget(btn)

        scroll.add_widget(layout)
        layout_float.add_widget(scroll)
        self.add_widget(layout_float)

    def request_topup(self, x):
        try:
            amount = int(self.amount.text)
            if current_user and amount >= 10:
                current_user['balance'] += amount // 10
                users[current_email] = current_user
                save_users(users)
                self.amount.text = ''
                self.switch('settings_screen')
        except:
            self.amount.hint_text = ar('قيمة خاطئة')

class MainApp(App):
    def build(self):
        self.title = ar('نشريلك')
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login_screen'))
        sm.add_widget(HomeScreen(name='home_screen'))
        sm.add_widget(ProductsScreen(name='products_screen'))
        sm.add_widget(AddProductScreen(name='add_product_screen'))
        sm.add_widget(SearchProductScreen(name='search_product_screen'))
        sm.add_widget(ConfirmOrderScreen(name='confirm_order_screen'))
        sm.add_widget(SupplierOrdersScreen(name='supplier_orders_screen'))
        sm.add_widget(DriverOrdersScreen(name='driver_orders_screen'))
        sm.add_widget(SettingsScreen(name='settings_screen'))
        sm.add_widget(TopUpScreen(name='topup_screen'))
        sm.current = 'login_screen'
        return sm

if __name__ == '__main__':
    MainApp().run()
