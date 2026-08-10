[app]
title = SatTracker Pro
package.name = sattrackerpro
package.domain = org.sattracker
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

# Dipendenze essenziali pulite
requirements = python3,kivy==2.3.0,kivymd,pillow,plyer,requests

android.permissions = ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, INTERNET

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
# Compiliamo SOLO per dispositivi 64-bit moderni per evitare timeout
archs = arm64-v8a
api = 33
minapi = 24
ndk = 25b
accept_sdk_licenses = True
