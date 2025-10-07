# وظایف این بخش:
# ۱. ساخت پنجره‌ی اصلی ربات (CustomTkinter)
# ۲. ساخت چک‌باکس‌ها و ورودی‌ها (تعداد معاملات، مارتینگل، مکث، ... )
# ۳. افزودن چک‌باکس مخصوص روش "۵ ثانیه‌ای"
# ۴. تعریف توابع واکنشی هنگام تغییر مقادیر (مثل validate_input)
# ۵. فراخوانی توابع start / stop ربات از main.py

# ⚠️ نکته:
# منطق تصمیم‌گیری (ترید، تحلیل کندل و ...) نباید در UI باشد.
# UI فقط تنظیمات را از کاربر می‌گیرد و به main اطلاع می‌دهد.


"""
ماژول ui.app
-------------
رابط گرافیکی اصلی ربات (CustomTkinter)
"""

import customtkinter as ctk
from tkinter import StringVar, IntVar, BooleanVar
from ui.components import create_labeled_entry, create_checkbox, create_button

class BotApp(ctk.CTk):
    """
    پنجره‌ی اصلی ربات
    ------------------
    کنترل تنظیمات، دکمه‌های شروع/توقف و نمایش وضعیت کلی
    """

    def __init__(self, cfg, on_start=None, on_stop=None):
        super().__init__()
        self.title("Bot Trade Project ⚙️")
        self.geometry("420x480")
        self.resizable(False, False)

        self.cfg = cfg
        self.on_start = on_start
        self.on_stop = on_stop

        # متغیرهای UI برای تنظیمات
        self.var_martingale = IntVar(value=cfg.get("martingale_step", 2))
        self.var_max_trades = IntVar(value=cfg.get("max_trades", 20))
        self.var_pause = IntVar(value=cfg.get("pause_between_trades", 1))
        self.var_continue_loss = BooleanVar(value=cfg.get("continue_after_loss", True))
        self.var_five_sec = BooleanVar(value=cfg.get("five_second_mode", True))

        # ساخت بخش‌های رابط
        self._build_ui()

    # ---------------- بخش ساخت رابط ---------------- #

    def _build_ui(self):
        """
        طراحی کامل پنجره
        """

        # عنوان
        title_label = ctk.CTkLabel(self, text="🤖  ربات معاملاتی ۵ ثانیه‌ای", font=("IRANSans", 18, "bold"))
        title_label.pack(pady=15)

        # ورودی‌های عددی
        frame1, entry_trades = create_labeled_entry(self, "تعداد معاملات:", self.var_max_trades.get())
        frame2, entry_marti = create_labeled_entry(self, "ضریب مارتینگل:", self.var_martingale.get())
        frame3, entry_pause = create_labeled_entry(self, "مکث بین معاملات:", self.var_pause.get())

        frame1.pack(pady=5)
        frame2.pack(pady=5)
        frame3.pack(pady=5)

        # چک‌باکس‌ها
        chk_continue = create_checkbox(self, "ادامه مارتینگل بعد از ضرر", self.var_continue_loss)
        chk_continue.pack(pady=5)

        chk_five_sec = create_checkbox(self, "روش ۵ ثانیه‌ای", self.var_five_sec)
        chk_five_sec.pack(pady=5)

        # دکمه‌های کنترل
        btn_start = create_button(self, "▶ شروع ربات", self._on_start, color="#22bb33")
        btn_stop  = create_button(self, "⏹ توقف ربات", self._on_stop, color="#cc0000")

        btn_start.pack(pady=10)
        btn_stop.pack(pady=5)

        # وضعیت (Label)
        self.status_label = ctk.CTkLabel(self, text="وضعیت: غیرفعال ❌", text_color="gray")
        self.status_label.pack(pady=20)

        # فوتر
        footer = ctk.CTkLabel(self, text="Bot Trade Project © 2025 - Ahanino Labs", font=("IRANSans", 10))
        footer.pack(side="bottom", pady=10)

    # ---------------- متدهای کنترلی ---------------- #

    def _on_start(self):
        """
        کلیک روی دکمه شروع ربات
        """
        self.status_label.configure(text="وضعیت: فعال ✅", text_color="#22bb33")

        # مقدار متغیرها را در cfg به‌روزرسانی می‌کنیم
        self.cfg["martingale_step"] = self.var_martingale.get()
        self.cfg["max_trades"] = self.var_max_trades.get()
        self.cfg["pause_between_trades"] = self.var_pause.get()
        self.cfg["continue_after_loss"] = self.var_continue_loss.get()
        self.cfg["five_second_mode"] = self.var_five_sec.get()

        # اجرای کال‌بک
        if self.on_start:
            self.on_start()

    def _on_stop(self):
        """
        کلیک روی دکمه توقف ربات
        """
        self.status_label.configure(text="وضعیت: غیرفعال ❌", text_color="gray")
        if self.on_stop:
            self.on_stop()