import pychrome
import time
import requests  # در بالای فایل اضافه شد
from pychrome.tab import Tab

class ChromeConnector:
    """
    مدیریت ارتباط با Chrome از طریق DevTools Protocol
    """

    def __init__(self, port=9222):
        # پورت پیش‌فرض برای ارتباط با مرورگر
        self.port = port
        self.browser = pychrome.Browser(url=f"http://127.0.0.1:{self.port}")
        self.tab = None

    def connect(self):
        """
        یافتن تب Pocket Option و فعال‌سازی پروتکل‌ها (DOM/Network)
        با تلاش خودکار برای اتصال تا ۵ بار.
        """
        if self.tab:
            print("ℹ️ تب Chrome از قبل متصل است، نیازی به اتصال مجدد نیست.")
            return

        for attempt in range(5):
            print(f"🕓 تلاش برای اتصال ({attempt + 1}/5) ...")

            try:
                # ۱️⃣ گرفتن لیست تب‌ها به‌صورت امن از طریق درخواست مستقیم به Chrome DevTools
                try:
                    response = requests.get(f"http://127.0.0.1:{self.port}/json")
                    raw_tabs = response.json()
                    tabs = []
                    for tab_data in raw_tabs:
                        # فقط تب‌هایی از نوع page را اضافه کن
                        if tab_data.get("type") == "page":
                            tabs.append(tab_data)
                except Exception as e:
                    print("⚠️ خطا در دریافت تب‌ها از DevTools:", e)
                    tabs = []

                if not tabs:
                    print("⚠️ هیچ تبی در مرورگر پیدا نشد.")
                    time.sleep(1)
                    continue

                # ۲️⃣ بررسی هر تب با اطلاعات اولیه (بدون start)
                for t in tabs:
                    type_ = t.get("type", "")
                    title = str(t.get("title") or "").lower()
                    url = str(t.get("url") or "").lower()
                    favicon = str(t.get("faviconUrl") or "").lower()

                    print("🔍 بررسی تب:", title, "|", url)

                    # فقط تب‌های نوع page بررسی شوند
                    if type_ != "page":
                        continue

                    # بررسی شرایط شناسایی تب Pocket Option
                    if (
                        "pocketoption.com" in url
                        or "pocketoption.com" in favicon
                        or "trading platform" in title
                    ):
                        print("✅ تب Pocket Option شناسایی شد، در حال شروع ارتباط ...")
                        ws_url = t.get("webSocketDebuggerUrl")
                        if ws_url:
                            try:
                                self.tab = Tab(ws_url=ws_url)
                                self.tab.start()
                                break
                            except Exception as e:
                                if "Already has another client" in str(e):
                                    print("⚠️ این تب قبلاً به یک client دیگر متصل است، تلاش برای تب دیگر...")
                                    print("🆕 باز کردن تب جدید Pocket Option ...")
                                    try:
                                        new_tab = self.browser.new_tab("https://pocketoption.com/en/cabinet")
                                        new_tab.start()
                                        print("🚀 تب جدید Pocket Option فعال شد و Session pychrome آغاز شد.")

                                        # انتظار برای بارگذاری کامل صفحه تا ۹۰ ثانیه (۳۰ تلاش × ۳ ثانیه)
                                        for i in range(30):
                                            try:
                                                info = requests.get(f"http://127.0.0.1:{self.port}/json").json()
                                                for tab_info in info:
                                                    url = tab_info.get("url", "")
                                                    if "pocketoption.com/en/cabinet" in url and "blank" not in url.lower():
                                                        print(f"✅ صفحه Pocket Option با موفقیت بارگذاری شد: {url}")
                                                        self.tab = new_tab
                                                        time.sleep(3)
                                                        break
                                                else:
                                                    print(f"⏳ در انتظار بارگذاری کامل صفحه... ({i+1}/30)")
                                                    time.sleep(3)
                                                    continue
                                                break
                                            except Exception as e:
                                                print(f"⚠️ خطا در بررسی لود صفحه: {e}")
                                                time.sleep(3)
                                        else:
                                            print("⚠️ صفحه هنوز بارگذاری نشده، لطفاً بررسی دستی کنید.")

                                        # فعال‌سازی پروتکل‌ها
                                        try:
                                            time.sleep(3)
                                            self.tab.call_method("Page.enable")
                                            self.tab.call_method("DOM.enable")
                                            self.tab.call_method("Runtime.enable")
                                            self.tab.call_method("Network.enable")
                                            print("🌐 پروتکل‌های Chrome فعال شدند و تب آماده دریافت فرمان است.")
                                        except Exception as e:
                                            print("⚠️ خطا در فعال‌سازی پروتکل‌ها:", e)

                                        break
                                    except Exception as e2:
                                        print("⚠️ خطا در باز کردن تب جدید:", e2)
                                        continue
                                else:
                                    print("⚠️ خطای غیرمنتظره هنگام اتصال به تب:", e)
                                    continue

                # اگر تب پیدا شد، از حلقه بیرون برو
                if self.tab:
                    break

            except Exception as e:
                print("⚠️ خطا در تلاش اتصال:", e)

            # تغییر: افزایش مکث بین تلاش‌های اصلی اتصال از ۱ ثانیه به ۳ ثانیه
            # این مکث به منظور جلوگیری از تلاش‌های سریع و پشت سر هم است
            time.sleep(3)

        # ۴️⃣ اگر بعد از ۵ تلاش هنوز تب پیدا نشد
        if not self.tab:
            raise RuntimeError("❌ تب Pocket Option پیدا نشد. لطفاً سایت را در همان مرورگر باز نگه دارید.")

        # ۵️⃣ فعال‌سازی پروتکل‌های لازم برای کنترل DOM و Network
        try:
            self.tab.call_method("Page.enable")
            self.tab.call_method("DOM.enable")
            self.tab.call_method("Runtime.enable")
            self.tab.call_method("Network.enable")
            print("🌐 پروتکل‌های Chrome فعال شدند و تب آماده دریافت فرمان است.")
        except Exception as e:
            print("⚠️ خطا در فعال‌سازی پروتکل‌ها:", e)

    def evaluate_js(self, script):
        """
        اجرای دستور جاوااسکریپت در تب فعال و بازگرداندن نتیجه.
        """
        if not self.tab:
            raise RuntimeError("❌ هنوز تب فعال متصل نشده است.")
        try:
            result = self.tab.call_method("Runtime.evaluate", expression=script)
            value = result.get("result", {}).get("value")
            return value
        except Exception as e:
            print(f"⚠️ خطا در اجرای JavaScript: {e}")
            return None

    def _find_price_in_iframes(self):
        """
        تلاش برای یافتن قیمت داخل iframeها (مثلاً فریم چارت یا tradingview).
        از DevTools /json لیست targetها گرفته می‌شود و روی هر iframe تلاش می‌کنیم.
        به محض یافتن مقدار معتبر، همان برگردانده می‌شود.
        """
        try:
            info = requests.get(f"http://127.0.0.1:{self.port}/json").json()
            for t in info:
                t_type = t.get("type", "")
                t_url = (t.get("url") or "").lower()
                # فقط iframeها یا targetهایی که احتمالاً حاوی چارت هستند بررسی شوند
                if t_type not in ("iframe",):
                    continue
                if not ("pocketoption" in t_url or "tradingview" in t_url or "chart" in t_url):
                    continue

                ws = t.get("webSocketDebuggerUrl")
                if not ws:
                    continue
                try:
                    temp_tab = Tab(ws_url=ws)
                    temp_tab.start()
                    # چند سلکتور رایج برای قیمت در چارت؛ در صورت نیاز بعداً دقیق‌تر می‌کنیم
                    js_code = """
                    (function(){
                        try {
                            const sels = ['.price', '.price-value', '.chart__price', '.trade-price', '.current-price', '[data-name="price"]'];
                            for (let s of sels) {
                                const el = document.querySelector(s);
                                if (el && (el.innerText || el.textContent)) {
                                    return (el.innerText || el.textContent).trim();
                                }
                            }
                            return null;
                        } catch(e){
                            return null;
                        }
                    })();
                    """
                    res = temp_tab.call_method("Runtime.evaluate", expression=js_code)
                    val = (res or {}).get("result", {}).get("value")
                    try:
                        temp_tab.stop()
                    except Exception:
                        pass
                    if val:
                        return val
                except Exception as e:
                    # اگر اتصال به آن iframe ممکن نبود، صرفاً ادامه می‌دهیم
                    print(f"⚠️ خطا در بررسی iframe: {e}")
                    continue
            return None
        except Exception as e:
            print(f"⚠️ خطا در پیمایش targetهای iframe: {e}")
            return None

    def get_dom_price(self):
        """
        دریافت قیمت فعلی از صفحه Pocket Option.
        (در این نسخه از سلکتور فرضی استفاده می‌شود و باید با سلکتور واقعی جایگزین شود)
        """
        js_code = """
        (function() {
            try {
                let el = document.querySelector('.price-value, .current-price, [data-name="price"]');
                if (el && el.innerText) {
                    return el.innerText.trim();
                }
                return null;
            } catch (e) {
                return null;
            }
        })();
        """
        price = self.evaluate_js(js_code)
        if price:
            print(f"💰 قیمت فعلی (DOM اصلی): {price}")
            return price
        else:
            print("⚠️ قیمت در DOM اصلی پیدا نشد؛ تلاش برای یافتن در iframe ...")
            iframe_price = self._find_price_in_iframes()
            if iframe_price:
                print(f"💰 قیمت فعلی (داخل iframe): {iframe_price}")
                return iframe_price
            print("⚠️ قیمت فعلی پیدا نشد.")
            return None

    def close(self):
        """
        بستن ایمن اتصال WebSocket به تب و مرورگر.
        این متد در زمان خروج (Ctrl + C) فراخوانی می‌شود.
        """
        try:
            if self.tab:
                print("🔌 در حال بستن ارتباط با تب Chrome ...")
                try:
                    self.tab.stop()
                except Exception:
                    pass
                self.tab = None
            if self.browser:
                print("🧹 در حال آزادسازی ارتباط مرورگر ...")
                try:
                    self.browser = None
                except Exception:
                    pass
            print("✅ ارتباط با Chrome به‌صورت ایمن بسته شد.")
        except Exception as e:
            print(f"⚠️ خطا در بستن اتصال Chrome: {e}")