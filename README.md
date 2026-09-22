# Nacrilk App (تطبيق نكرليك)

تطبيق Nacrilk (Acrili / نكرليك) هو تطبيق تجارة إلكترونية مبني باستخدام Kivy و Python و Firebase.

## كيفية تحميل التطبيق (How to download the APK)

### Option 1: Downloading from GitHub Actions (طريقة التحميل من GitHub Actions)
1. اذهب إلى علامة التبويب **Actions** في مستودع GitHub الخاص بالمركاز.
2. اختر أحدث تشغيل لبرنامج البناء الناجح (**Build APK** workflow).
3. في أسفل الصفحة ضمن قسم **Artifacts** (الملحقات)، قم بتحميل ملف **package** (والذي يحتوي على ملف الـ APK).
4. فك الضغط عن الملف وقم بتثبيت ملف الـ `.apk` على هاتف أندرويد الخاص بك.

---

### Option 2: Building locally with Buildozer (طريقة بناء التطبيق محلياً)
إذا كنت تريد بناء ملف APK محلياً باستخدام Buildozer:

1. قم بتثبيت المتطلبات الأساسية على نظام لينكس (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install -y build-essential libffi-dev libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev expat liblzma-dev tk-dev openjdk-17-jdk-headless autoconf libtool pkg-config automake m4 gettext libltdl-dev
```

2. قم بتثبيت Buildozer و Cython:
```bash
pip install --user --upgrade buildozer cython
```

3. قم ببناء التطبيق:
```bash
buildozer -v android debug
```
سيتم إنشاء ملف الـ APK داخل مجلد `bin/`.
