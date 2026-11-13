import threading, os, traceback
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def _srv():
    try:
        import run
        from http.server import HTTPServer
        HTTPServer(("127.0.0.1", 8085), run.H).serve_forever()
    except Exception as e:
        print("SERVER ERROR:", e); traceback.print_exc()

threading.Thread(target=_srv, daemon=True).start()

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock

class MainApp(App):
    def build(self):
        Clock.schedule_once(self._wv, 3.0)
        return Widget()
    def _wv(self, dt):
        try:
            from android import mActivity
            from jnius import autoclass
            WebView = autoclass('android.webkit.WebView')
            WebViewClient = autoclass('android.webkit.WebViewClient')
            wv = WebView(mActivity)
            s = wv.getSettings()
            s.setJavaScriptEnabled(True)
            s.setDomStorageEnabled(True)
            wv.setWebViewClient(WebViewClient())
            wv.loadUrl("http://127.0.0.1:8085")
            mActivity.setContentView(wv)
        except Exception as e:
            print("WEBVIEW ERROR:", e); traceback.print_exc()

MainApp().run()
