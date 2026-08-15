[app]
title = SkyTrackerPro
package.name = skytrackerpro
package.domain = org.skytracker
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

orientation = portrait
fullscreen = 0
requirements = python3,kivy,requests

android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

android.archs = arm64-v8a

android.minapi = 21
android.api = 33
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
