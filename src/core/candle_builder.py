# وظایف:
# ۱. دریافت تیک‌های قیمتی از websocket
# ۲. ساخت کندل‌های ۵ ثانیه‌ای (OHLC)
# ۳. تشخیص بسته شدن کندل دوم
# ۴. بازگرداندن اطلاعات برای strategy_five_sec.py
# ۵. ذخیره‌ی چند کندل آخر در حافظه برای تحلیل الگو

"""
ماژول CandleBuilder
--------------------
هدف: ساخت کندل‌های ۵ ثانیه‌ای از داده‌های تیک قیمت (tick data)
"""

import time
from collections import deque

class Candle:
    """
    کلاس Candle نمایانگر یک کندل واحد (OHLC) است.
    """
    def __init__(self, start_ts, end_ts):
        self.start_ts = start_ts   # زمان شروع کندل (epoch seconds)
        self.end_ts = end_ts       # زمان پایان کندل
        self.open = None           # قیمت باز شدن
        self.close = None          # قیمت بسته شدن
        self.high = float('-inf')  # بالاترین قیمت
        self.low = float('inf')    # پایین‌ترین قیمت

    def add_tick(self, price):
        """
        افزودن یک تیک قیمت به کندل جاری
        """
        if self.open is None:
            self.open = price
        self.close = price
        if price > self.high:
            self.high = price
        if price < self.low:
            self.low = price

    # چند ویژگی مفید برای تحلیل:
    @property
    def is_bullish(self):
        """آیا کندل صعودی است؟"""
        return self.close > self.open

    @property
    def is_bearish(self):
        """آیا کندل نزولی است؟"""
        return self.close < self.open

    @property
    def body(self):
        """طول بدنه کندل"""
        return abs(self.close - self.open)

    @property
    def range(self):
        """بازه‌ی کامل کندل"""
        return self.high - self.low

    def upper_wick(self):
        """طول شدوی بالایی"""
        return self.high - max(self.close, self.open)

    def lower_wick(self):
        """طول شدوی پایینی"""
        return min(self.close, self.open) - self.low


class CandleBuilder:
    """
    مدیریت ساخت و نگهداری کندل‌های ۵ ثانیه‌ای
    """

    def __init__(self, period_sec=5, max_keep=20):
        self.period = period_sec
        self.max_keep = max_keep
        self.candles = deque(maxlen=max_keep)
        self.current_candle = None

    def _align_to_period(self, ts):
        """
        تراز کردن زمان روی مضرب‌های ۵ ثانیه
        (مثلاً 12:00:00 → 12:00:05 → 12:00:10 ...)
        """
        start = ts - (ts % self.period)
        end = start + self.period
        return start, end

    def add_price(self, price, ts=None):
        """
        افزودن یک قیمت جدید و بررسی بستن کندل
        """
        now = ts or time.time()

        # اگر کندل فعلی وجود ندارد، ایجادش کن
        if self.current_candle is None:
            start, end = self._align_to_period(now)
            self.current_candle = Candle(start, end)

        # اگر زمان از پایان کندل فعلی گذشته، کندل را ببند و جدید بساز
        if now >= self.current_candle.end_ts:
            self.candles.append(self.current_candle)
            start, end = self._align_to_period(now)
            self.current_candle = Candle(start, end)

        # افزودن تیک به کندل فعلی
        self.current_candle.add_tick(price)

    def get_last_n(self, n):
        """
        برگرداندن آخرین n کندل بسته شده
        """
        return list(self.candles)[-n:]

    def get_current_open(self):
        """قیمت باز شدن کندل جاری"""
        return self.current_candle.open if self.current_candle else None

    def ready_for_strategy(self):
        """
        بررسی اینکه حداقل دو کندل بسته شده وجود دارد یا نه
        """
        return len(self.candles) >= 2