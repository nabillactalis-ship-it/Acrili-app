[app]
title = Neshrblek
package.name = neshrblek
package.domain = org.neshrblek
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 0.3.1
requirements = python3,kivy,arabic-reshaper,python-bidi,pyrebase4
orientation = portrait
fullscreen = 0
android.arch = arm64-v8a
android.api = 31
android.minapi = 21
android.sdk_path = .buildozer/android/platform/android-sdk
android.ndk_path = .buildozer/android/platform/android-ndk-r25b

[buildozer]
log_level = 2
warn_on_root = 1
