# شامل پیاده‌سازی شرط‌های زیر است:
#   الف) در محدوده‌های رنج یا کندل‌های موازی، ترید نکند.
#   پ) اگر ابتدای کندل سوم هم‌جهت با دو کندل قبلی بود، ترید کند.
#   ت) اگر کندل دوم دوجی بود، ترید نکند.
#   ث) اگر شدوی بالا روی کندل نزولی بود، ترید کند.
#   ج) اگر شدوی پایین روی کندل صعودی بود، ترید کند.
#   ح) اگر کندل دوم بدون شدو بود، مانعی برای ترید نیست.
#   خ) ترید حداکثر ۱۵ میلی‌ثانیه پس از بسته شدن کندل دوم انجام شود.

# خروجی نهایی این فایل:
#   decide_on_second_close(c1, c2, current_open, current_price)
#       → خروجی ۰ برای خرید (Buy)
#       → خروجی ۱ برای فروش (Sell)
#       → خروجی None برای عدم ترید


"""
ماژول StrategyFiveSec
----------------------
هدف: تصمیم‌گیری در مورد اجرای ترید بر اساس تحلیل دو کندل قبلی و کندل جاری.
شامل شرط‌های الف تا خ.
"""

# پارامترهای قابل تنظیم برای حساسیت کندل‌ها
DOJI_BODY_RATIO = 0.1       # نسبت بدنه به رنج برای تشخیص دوجی
PARALLEL_MAX_RANGE = 0.0005 # حداقل اختلاف برای موازی بودن کندل‌ها

class StrategyFiveSec:
    """
    این کلاس شامل منطق تصمیم‌گیری برای روش ۵ ثانیه‌ای است.
    """

    def __init__(self, config):
        self.config = config

    # --- توابع کمکی تشخیص الگوها --- #

    def is_doji(self, candle):
        """تشخیص کندل دوجی"""
        if candle.range == 0:
            return True
        return (candle.body / candle.range) <= DOJI_BODY_RATIO

    def is_parallel(self, c1, c2):
        """تشخیص دو کندل موازی (در رنج محدود)"""
        return (c1.range <= PARALLEL_MAX_RANGE) and (c2.range <= PARALLEL_MAX_RANGE)

    def decide_trade(self, c1, c2, current_open, current_price):
        """
        تصمیم نهایی برای اجرای ترید طبق شرط‌های الف تا خ.
        ورودی:
            c1: کندل اول
            c2: کندل دوم
            current_open: قیمت باز کندل سوم
            current_price: قیمت فعلی بازار
        خروجی:
            ۰ → خرید (CALL)
            ۱ → فروش (PUT)
            None → عدم ترید
        """

        # --- شرط ت) دوجی ---
        if self.is_doji(c2):
            # اگر کندل دوم دوجی بود، ترید نکن
            return None

        # --- شرط الف) موازی ---
        if self.is_parallel(c1, c2):
            return None

        # --- جهت کلی دو کندل ---
        both_bull = c1.is_bullish and c2.is_bullish
        both_bear = c1.is_bearish and c2.is_bearish

        # --- شرط پ) هم‌جهتی کندل سوم ---
        third_confirms = False
        if current_open is not None:
            if both_bull and current_price >= current_open:
                third_confirms = True
            if both_bear and current_price <= current_open:
                third_confirms = True

        # --- شرط ث) شدوی بالا روی کندل نزولی ---
        shadow_sell = c2.is_bearish and (c2.upper_wick() > 0)

        # --- شرط ج) شدوی پایین روی کندل صعودی ---
        shadow_buy = c2.is_bullish and (c2.lower_wick() > 0)

        # --- شرط ح) کندل دوم بدون سایه مانعی ندارد ---
        # (نیاز به اقدام خاص ندارد، فقط در شرط بالا رد نمی‌شود)

        # تصمیم نهایی:
        cmd = None

        # اگر کندل سوم هم‌جهت با دو تای قبل باشد
        if third_confirms:
            cmd = 0 if both_bull else (1 if both_bear else None)

        # اگر شرط بالا برقرار نبود، از قواعد شدو استفاده شود
        if cmd is None:
            if shadow_sell:
                cmd = 1
            elif shadow_buy:
                cmd = 0

        return cmd

# ---------------------------------------------
# 🚀 تست مستقل ماژول StrategyFiveSec
# ---------------------------------------------
if __name__ == "__main__":
    # کلاس ساده برای شبیه‌سازی کندل‌ها
    class DummyCandle:
        def __init__(self, open_p, close_p, high, low):
            self.open = open_p
            self.close = close_p
            self.high = high
            self.low = low

        @property
        def body(self):
            return abs(self.close - self.open)

        @property
        def range(self):
            return self.high - self.low

        @property
        def is_bullish(self):
            return self.close > self.open

        @property
        def is_bearish(self):
            return self.close < self.open

        def upper_wick(self):
            return self.high - max(self.open, self.close)

        def lower_wick(self):
            return min(self.open, self.close) - self.low

    # نمونه‌سازی استراتژی
    strategy = StrategyFiveSec(config={})

    # تعریف دو کندل تستی
    c1 = DummyCandle(100, 101, 101.2, 99.8)
    c2 = DummyCandle(101, 101.5, 101.8, 100.9)
    current_open = 101.5
    current_price = 101.7

    # اجرای تست
    result = strategy.decide_trade(c1, c2, current_open, current_price)
    if result == 0:
        print("🚀 سیگنال BUY (خرید)")
    elif result == 1:
        print("🚀 سیگنال SELL (فروش)")
    else:
        print("⏸ عدم ترید - شرایط برقرار نیست")