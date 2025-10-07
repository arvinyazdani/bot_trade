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
ماژول ui.components
-------------------
شامل ویجت‌های آماده و سبک برای استفاده در رابط کاربری ربات.
"""

import customtkinter as ctk


def create_labeled_entry(master, label_text, default_value="", width=120):
    """
    ساخت ورودی همراه با برچسب
    -------------------------
    ورودی‌های عددی (مثلاً تعداد معاملات، مارتینگل، مکث)
    """
    frame = ctk.CTkFrame(master)
    label = ctk.CTkLabel(frame, text=label_text, anchor="w")
    entry = ctk.CTkEntry(frame, width=width)
    entry.insert(0, str(default_value))
    label.pack(side="left", padx=5)
    entry.pack(side="right", padx=5)
    return frame, entry


def create_checkbox(master, label_text, variable):
    """
    ساخت چک‌باکس عمومی
    -------------------
    """
    checkbox = ctk.CTkCheckBox(master, text=label_text, variable=variable)
    return checkbox


def create_button(master, text, command, color="green"):
    """
    ساخت دکمه با رنگ دلخواه
    -----------------------
    """
    button = ctk.CTkButton(master, text=text, command=command, fg_color=color)
    return button