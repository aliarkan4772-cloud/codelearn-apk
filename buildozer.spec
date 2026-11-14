[app]
title = CodeLearn
package.name = codelearn
package.domain = org.codelearn
source.dir = .
source.include_exts = py,db,xml
version = 6.0
requirements = python3,sqlite3
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 34
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.bootstrap = webview
p4a.port = 8085
android.extra_manifest_application_arguments = extra_app_args.xml

[buildozer]
log_level = 2
warn_on_root = 0
