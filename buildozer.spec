[app]
title = Asteroids Game
package.name = asteroids
package.domain = com.yourdomain.asteroids

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,mp3

version = 1.0
requirements = python3,kivy,kivymd

[buildozer]
log_level = 2
warn_on_root = 1

[android]
# Android specific configurations
api = 33
minapi = 21
sdk = 31
ndk = 23b
gradle_dependencies = 

# Permisos
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE

# Orientación
orientation = portrait

# Icono de la app
icon.filename = icon.png

# Splash screen
presplash.filename = presplash.png

[ios]
# iOS specific configurations
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.7.0