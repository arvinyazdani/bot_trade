"""
ماژول Timing
-------------
مدیریت زمان‌بندی دقیق برای اجرای تریدها با دقت میلی‌ثانیه‌ای.
"""

import time

def wait_until(deadline_epoch):
    """
    توقف تا رسیدن به زمان مشخص (بر اساس epoch seconds)
    استفاده از busy-wait برای دقت میلی‌ثانیه‌ای (بدون sleep(0.01))
    """

    now = time.time()
    delay = deadline_epoch - now
    if delay <= 0:
        return

    # استفاده از time.perf_counter برای دقت بالا
    target = time.perf_counter() + delay

    # در چند میلی‌ثانیه پایانی busy-wait می‌کنیم
    while time.perf_counter() < target - 0.002:
        pass
    while time.perf_counter() < target:
        pass


def has_elapsed(start_time, seconds):
    """
    بررسی اینکه از زمان شروع، چند ثانیه گذشته یا نه.
    """
    return (time.time() - start_time) >= seconds


def precise_now():
    """
    بازگرداندن زمان دقیق با دقت بالا (برای لاگ‌ها و تحلیل تاخیر)
    """
    return time.perf_counter()