[app]
title = Ashrili
package.name = ashrili
package.domain = org.ashrili
source.dir =.
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 0.1
requirements = python3,kivy,arabic-reshaper,python-bidi,pyrebase4,openssl,requests
orientation = portrait
fullscreen = 0
android.arch = arm64-v8a
android.api = 31
android.minapi = 21
android.sdk_path =.buildozer/android/platform/android-sdk
android.ndk_path =.buildozer/android/platform/android-ndk-r25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
