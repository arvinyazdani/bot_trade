from core.chrome_connector import ChromeConnector
import time

# ---------------------------------------------------------
# 📡 LiveDataReader - ماژول دریافت داده زنده از Pocket Option
# ---------------------------------------------------------
class LiveDataReader:
    """
    این کلاس داده‌های زنده (real-time) بازار را از تب فعال Chrome می‌خواند.
    برای شروع، فقط قیمت فعلی را از DOM سایت Pocket Option استخراج می‌کند.
    """

    def __init__(self, tab=None):
        """
        مقداردهی ChromeConnector و فعال‌سازی تب.
        اگر تب از بیرون پاس داده شود، از همان استفاده می‌شود؛
        در غیر این صورت، اتصال جدید برقرار و تب جدید گرفته می‌شود.
        """
        self.chrome = ChromeConnector()
        # اگر تب موجود پاس داده شده باشد، از آن استفاده می‌کنیم؛
        # در غیر این صورت، اتصال جدید برقرار می‌شود و تب جدید گرفته می‌شود.
        if tab:
            self.tab = tab
        else:
            self.chrome.connect()
            self.tab = self.chrome.tab
        self.last_price = None

    def get_current_price(self):
        """
        اجرای اسکریپت جاوااسکریپت در صفحه‌ی Pocket Option برای خواندن قیمت فعلی.
        اگر کاربر در صفحه‌ی اصلی باشد (نه صفحه‌ی ترید)، هشدار داده می‌شود.
        """
        attempts = 0
        while attempts < 3:
            if not getattr(self.tab, "started", False):
                try:
                    self.tab.start()
                    print("🟢 تب Chrome فعال شد و آماده اجرای دستورات است.")
                except Exception as e:
                    msg = str(e)
                    if 'Already has another client connect to this tab' in msg:
                        print("⚠️ تب قبلاً توسط کلاینت دیگری متصل شده است، گرفتن تب جدید از ChromeConnector ...")
                        try:
                            self.chrome.connect()
                            self.tab = self.chrome.tab
                            self.tab.start()
                            print("🟢 تب جدید با موفقیت فعال شد.")
                        except Exception as ex:
                            print(f"❌ خطا در گرفتن تب جدید: {ex}")
                            return self.last_price
                    elif 'Cannot call method before it is started' in msg:
                        print("⏳ تب هنوز آماده نیست، ۲ ثانیه صبر می‌کنیم و دوباره تلاش می‌کنیم ...")
                        time.sleep(2)
                        attempts += 1
                        continue
                    else:
                        print(f"⚠️ خطا در فعال‌سازی تب: {e}")
                        return self.last_price

            try:
                # ابتدا URL فعلی صفحه را بررسی می‌کنیم
                js_url = "window.location.href"
                url_result = self.tab.Runtime.evaluate(expression=js_url, returnByValue=True)
                current_url = url_result.get("result", {}).get("value", "")
                if not current_url or ("/cabinet" not in current_url and "/trade" not in current_url):
                    print(f"⚠️ کاربر در صفحه‌ی ترید نیست ({current_url})، قیمت خوانده نمی‌شود.")
                    return self.last_price

                # حالا خواندن قیمت از DOM
                js_code = """
                (function() {
                    const selectors = ['.price', '.price-value', '.chart__price', '.trade-price', '.current-price'];
                    for (let s of selectors) {
                        let el = document.querySelector(s);
                        if (el && el.innerText) {
                            return el.innerText;
                        }
                    }
                    return null;
                })();
                """
                result = self.tab.Runtime.evaluate(expression=js_code, returnByValue=True)
                price_str = result.get("result", {}).get("value")

                if price_str:
                    try:
                        # حذف کاما و تبدیل به عدد اعشاری
                        clean_str = price_str.replace(',', '').strip()
                        self.last_price = float(clean_str)
                        print(f"📊 قیمت فعلی از DOM: {self.last_price}")
                        return self.last_price
                    except Exception as conv_err:
                        print(f"⚠️ خطا در تبدیل مقدار '{price_str}' به عدد: {conv_err}")
                        return self.last_price
                else:
                    print("⚠️ هیچ المنت قیمتی در DOM پیدا نشد (ممکن است در صفحه‌ی اشتباه باشید).")
                    attempts += 1
                    time.sleep(1)

            except Exception as e:
                msg = str(e)
                if 'Cannot call method before it is started' in msg:
                    print("⚠️ تب هنوز آماده نیست، کمی صبر می‌کنیم...")
                    time.sleep(2)
                else:
                    print(f"⚠️ خطا در دریافت قیمت فعلی: {e}")
                attempts += 1
                time.sleep(1)

        print(f"⚠️ بعد از {attempts} تلاش، قیمت جدید دریافت نشد. بازگرداندن آخرین قیمت معتبر: {self.last_price}")
        return self.last_price

    def collect_candle_loop(self, duration=30):
        """
        اجرای حلقه‌ی دریافت داده زنده به مدت مشخص (پیش‌فرض: ۳۰ ثانیه)
        هر ۵ ثانیه قیمت فعلی خوانده می‌شود.
        """
        print("🔹 شروع دریافت داده زنده از Pocket Option ...")
        start_time = time.time()

        while time.time() - start_time < duration:
            price = self.get_current_price()
            if price:
                print(f"📡 قیمت فعلی: {price}")
            else:
                print("⚠️ قیمت یافت نشد (ممکن است Selector اشتباه باشد).")

            time.sleep(5)

        print("✅ پایان دریافت داده زنده.")

    def get_live_price(self):
        """
        دریافت قیمت زنده برای سازگاری با CandleEngine
        """
        try:
            return self.get_current_price()
        except Exception as e:
            print(f"⚠️ خطا در get_live_price: {e}")
            return None

if __name__ == "__main__":
    reader = LiveDataReader()
    reader.collect_candle_loop(duration=30)
