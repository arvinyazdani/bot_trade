# وظیفه:
# ۱. اتصال به websocket داخلی Pocket Option (با pychrome)
# ۲. دریافت و decode پیام‌ها (Base64 → JSON)
# ۳. استخراج symbol, period, price
# ۴. ارسال قیمت‌ها به CandleBuilder برای ساخت کندل‌ها
# ۵. مدیریت خطا و reconnect خودکار

"""
ماژول WebSocketHandler
-----------------------
شنود فریم‌های وب‌سوکت از طریق پروتکل DevTools و استخراج قیمت برای CandleBuilder.
"""

import json
import base64
import time

class WebSocketHandler:
    """
    این کلاس WebSocketFrameReceived های تب را گوش می‌دهد و قیمت‌ها را از پیام‌ها استخراج می‌کند.
    """

    def __init__(self, tab, on_tick, symbol_filter=None):
        # tab: همان self.tab از ChromeConnector
        # on_tick(price, ts): کال‌بک برای ارسال قیمت و زمان
        self.tab = tab
        self.on_tick = on_tick
        self.symbol_filter = symbol_filter  # اگر بخواهیم فقط یک نماد را پردازش کنیم
        self._enabled = False
        self._ws_urls = set()  # لیست ws ها برای فیلتر کردن

    def start(self):
        """
        فعال‌سازی شنود رویدادهای وب‌سوکت.
        """
        if self._enabled:
            return
        self._enabled = True

        # رویداد دریافت فریم وب‌سوکت
        self.tab.set_listener("Network.webSocketCreated", self._on_ws_created)
        self.tab.set_listener("Network.webSocketFrameReceived", self._on_ws_frame_received)

    def stop(self):
        """
        غیرفعال‌سازی شنود.
        """
        if not self._enabled:
            return
        self._enabled = False

        # پاک کردن لیسنرها
        self.tab.set_listener("Network.webSocketCreated", None)
        self.tab.set_listener("Network.webSocketFrameReceived", None)

    # ----------------- لیسنرها ----------------- #

    def _on_ws_created(self, **kwargs):
        """
        وقتی یک اتصال وب‌سوکت ایجاد می‌شود، URL آن را ذخیره می‌کنیم.
        """
        try:
            url = kwargs.get("url") or ""
            if "wss://" in url:
                self._ws_urls.add(url)
        except Exception:
            pass

    def _on_ws_frame_received(self, **kwargs):
        """
        وقتی فریم وب‌سوکت دریافت می‌شود، دیتای آن را می‌خوانیم.
        """
        if not self._enabled:
            return
        try:
            payload_data = kwargs.get("response", {}).get("payloadData", "")
            if not payload_data:
                return

            # برخی WS ها باینری Base64 هستند؛ اگر JSON متنی بود، همان را Parse می‌کنیم.
            data = self._decode_payload(payload_data)
            if not data:
                return

            # تلاش برای استخراج قیمت (این بخش بسته به فرمت واقعی پیام‌ها باید تنظیم شود)
            price = self._extract_price(data)
            if price is None:
                return

            # فیلتر نماد (اختیاری)
            sym = self._extract_symbol(data)
            if self.symbol_filter and sym and sym != self.symbol_filter:
                return

            ts = time.time()
            self.on_tick(price, ts)

        except Exception as e:
            # برای جلوگیری از قطع جریان، فقط گزارش کن
            print("⚠️ خطا در پردازش فریم WS:", e)

    # ----------------- ابزارهای استخراج ----------------- #

    def _decode_payload(self, payload):
        """
        تلاش برای Decode پیام:
        1) JSON ساده
        2) Base64 → متن → JSON
        3) Base64 → باینری خاص (غیرقابل استفاده در این سطح) → رد
        """
        # 1) اگر مستقیم JSON بود
        try:
            if payload and payload[0] in ("{", "["):
                return json.loads(payload)
        except Exception:
            pass

        # 2) Base64 → Try JSON
        try:
            raw = base64.b64decode(payload)
            txt = raw.decode("utf-8", errors="ignore").strip()
            if txt and txt[0] in ("{", "["):
                return json.loads(txt)
        except Exception:
            pass

        return None

    def _extract_price(self, data):
        """
        استخراج قیمت از ساختارهای رایج پیام‌ها.
        این تابع باید با ساختار واقعی Pocket Option تطبیق داده شود.
        چند الگوی رایج بررسی می‌شود.
        """
        try:
            # مثال‌های احتمالی (با توجه به پلتفرم):
            # 1) {"price": 1.23456}
            if isinstance(data, dict) and "price" in data:
                return float(data["price"])

            # 2) {"data": {"price": ...}}
            if isinstance(data, dict) and "data" in data and "price" in data["data"]:
                return float(data["data"]["price"])

            # 3) آرایه‌ای از تیک‌ها
            if isinstance(data, list) and data and isinstance(data[0], dict):
                cand = data[0]
                if "price" in cand:
                    return float(cand["price"])
        except Exception:
            return None
        return None

    def _extract_symbol(self, data):
        """
        تلاش برای استخراج نماد از پیام (اختیاری).
        """
        try:
            if isinstance(data, dict):
                if "symbol" in data:
                    return str(data["symbol"])
                if "data" in data and "symbol" in data["data"]:
                    return str(data["data"]["symbol"])
        except Exception:
            pass
        return None