[app]
title = ControlAccesos
package.name = controlaccesos
package.domain = org.tecnm
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,qrcode,pillow,opencv-python-headless,pyzbar,smtplib,email,supabase
orientation = portrait
fullscreen = 1
android.permissions = INTERNET,CAMERA
android.minapi = 21
android.sdk = 30
android.ndk = 23b
android.arch = armeabi-v7a,arm64-v8a
android.logcat_filters = *:S python:D
android.enable_androidx = 1
android.use_android_support = 0
android.hardware.camera = True
android.hardware.camera.autofocus = True
presplash.filename = splash.png
icon.filename = icon.png

[buildozer]
log_level = 2
warn_on_root = 1

[python]
# No necesitas cambiar esto normalmente
# No necesitas site-packages externos si tus libs están en requirements
