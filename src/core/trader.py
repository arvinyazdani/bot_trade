# trader.py
# شامل توابع زیر است:
#   place_trade(command, reverse=False)
#       → فرمان خرید/فروش را به مرورگر می‌فرستد.
#   reverse_trade()
#       → در صورت ضرر، معامله‌ی معکوس را اجرا می‌کند.
#   build_open_order()
#       → ساخت و نگهداری وضعیت سفارش باز.
#   trade_counter و order_counter
#       → شمارنده‌ی معاملات انجام شده.
#   stop_loss و profit_stop
#       → کنترل ضرر و سود کل.

# martingale.py
# شامل منطق زیر است:
#   calculate_next_amount()
#       → مبلغ پله بعدی بر اساس ضریب منظم (۲، ۲.۵، ...)
#   reset_after_win()
#       → بازگشت به مبلغ اولیه پس از سود.
#   continue_after_loss()
#       → ادامه پله‌ها در صورت فعال بودن گزینه‌ی "ادامه بعد از حد ضرر".



"""
ماژول Trader
-------------
مدیریت انجام معاملات، شمارنده‌ها و کنترل وضعیت مارتینگل
"""

from core.martingale import MartingaleManager
from core.timing import wait_until
import time

class Trader:
    """
    کلاس Trader مسئول اجرای تریدها و مدیریت وضعیت کلی معاملات است.
    """

    def __init__(self, chrome_interface, config):
        # chrome_interface: آبجکت برای ارسال کلیک به مرورگر (pychrome)
        # config: تنظیمات عمومی از config.json
        self.chrome = chrome_interface
        self.config = config

        # شمارنده‌ها و وضعیت‌ها
        self.trade_counter = 0         # تعداد کل معاملات انجام شده
        self.current_amount = 1        # مبلغ فعلی معامله
        self.last_result = None        # نتیجه آخرین معامله (win/loss/None)
        self.is_open = False           # وضعیت معامله باز
        self.martingale = MartingaleManager(config)

    def place_trade(self, direction):
        """
        اجرای معامله جدید بر اساس جهت داده‌شده:
        direction = 0 → خرید (CALL)
        direction = 1 → فروش (PUT)
        """

        if self.trade_counter >= self.config["max_trades"]:
            print("⛔️ تعداد معاملات به حد نهایی رسید.")
            return

        # محاسبه مبلغ جدید (اگر معامله قبلی باخت)
        if self.last_result == "loss":
            self.current_amount = self.martingale.next_step(self.current_amount)
        else:
            self.current_amount = self.martingale.reset_amount()

        # ثبت زمان شروع معامله
        self.trade_counter += 1
        self.is_open = True
        start_time = time.strftime("%H:%M:%S")

        # اجرای معامله از طریق Chrome
        cmd = "CALL" if direction == 0 else "PUT"
        print(f"🚀 [{start_time}] معامله شماره {self.trade_counter}: {cmd} مبلغ {self.current_amount}")

        try:
            # ارسال کلیک به دکمه مناسب در مرورگر
            self.chrome.click_button(direction)
        except Exception as e:
            print(f"⚠️ خطا در ارسال معامله به مرورگر: {e}")

    def update_result(self, result):
        """
        بروزرسانی وضعیت آخرین معامله
        result = "win" یا "loss"
        """
        self.last_result = result
        self.is_open = False

        if result == "win":
            print("✅ معامله با سود بسته شد.")
            self.current_amount = self.martingale.reset_amount()
        elif result == "loss":
            print("❌ معامله با ضرر بسته شد. مارتینگل فعال می‌شود.")
        else:
            print("⚠️ وضعیت معامله نامشخص است.")