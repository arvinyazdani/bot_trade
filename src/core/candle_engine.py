import random
import time
from dataclasses import dataclass
from core.strategy_five_sec import StrategyFiveSec

# ---------------------------------------------
# 🧩 کلاس Candle - نمایش ساختار هر کندل ۵ ثانیه‌ای
# ---------------------------------------------
@dataclass
class Candle:
    open_price: float
    close_price: float
    high: float
    low: float

    @property
    def open(self) -> float:
        """معادل open_price برای سازگاری با استراتژی"""
        return self.open_price

    @property
    def close(self) -> float:
        """معادل close_price برای سازگاری با استراتژی"""
        return self.close_price

    @property
    def direction(self) -> str:
        """
        تشخیص جهت کندل (صعودی / نزولی / دوجی)
        اگر اختلاف قیمت باز و بسته کمتر از ۰.۰۰۰۱ باشد دوجی است.
        """
        if abs(self.close_price - self.open_price) < 0.0001:
            return "doji"
        return "bullish" if self.close_price > self.open_price else "bearish"

    @property
    def upper_shadow(self) -> float:
        """
        طول سایه بالایی کندل (فاصله بیشترین قیمت تا بدنه فوقانی)
        """
        return self.high - max(self.open_price, self.close_price)

    @property
    def lower_shadow(self) -> float:
        """
        طول سایه پایینی کندل (فاصله کمترین قیمت تا بدنه پایینی)
        """
        return min(self.open_price, self.close_price) - self.low

    @property
    def range(self) -> float:
        """
        محدوده‌ی کلی کندل (فاصله بین بیشترین و کمترین قیمت)
        """
        return self.high - self.low

    @property
    def body(self) -> float:
        """طول بدنهٔ کندل (اختلاف قیمت باز و بسته)"""
        return abs(self.close_price - self.open_price)

    @property
    def is_bullish(self) -> bool:
        """صعودی بودن کندل"""
        return self.close_price > self.open_price

    @property
    def is_bearish(self) -> bool:
        """نزولی بودن کندل"""
        return self.close_price < self.open_price

    def upper_wick(self) -> float:
        """alias برای سایهٔ بالایی (مطابق نام مورد انتظار در استراتژی)"""
        return self.upper_shadow

    def lower_wick(self) -> float:
        """alias برای سایهٔ پایینی (مطابق نام مورد انتظار در استراتژی)"""
        return self.lower_shadow


# ---------------------------------------------
# ⚙️ کلاس CandleEngine - موتور اصلی کندل در حالت تستی
# ---------------------------------------------
class CandleEngine:
    def __init__(self, mode="sim", live_reader=None):
        # حالت اجرای موتور (شبیه‌سازی یا زنده)
        self.mode = mode
        # خواننده داده زنده (اگر در حالت زنده استفاده شود)
        self.live_reader = live_reader
        # لیست آخرین کندل‌ها (حداکثر ۳ عدد)
        self.candles = []
        self.running = False
        self.strategy = StrategyFiveSec(config={})

    def generate_candle(self, last_close: float) -> Candle:
        """
        شبیه‌سازی تولید کندل تصادفی بر اساس قیمت قبلی
        - قیمت باز: همان قیمت بسته کندل قبلی
        - قیمت بسته: با تغییر تصادفی
        - high، low: کمی بالاتر/پایین‌تر از باز و بسته
        """
        change = random.uniform(-0.5, 0.5)  # تغییر تصادفی قیمت
        open_price = last_close
        close_price = last_close + change
        high = max(open_price, close_price) + random.uniform(0.05, 0.3)
        low = min(open_price, close_price) - random.uniform(0.05, 0.3)
        return Candle(open_price, close_price, high, low)

    def add_candle(self, candle: Candle):
        """
        افزودن کندل جدید و نگه‌داشتن فقط ۳ کندل آخر
        """
        self.candles.append(candle)
        if len(self.candles) > 3:
            self.candles.pop(0)

    def analyze(self):
        """
        بررسی شرایط معاملاتی با استفاده از الگوریتم StrategyFiveSec
        """
        if len(self.candles) < 3:
            return None

        c1, c2, c3 = self.candles
        current_open = c3.open_price
        current_price = c3.close_price

        # فراخوانی منطق تصمیم‌گیری از StrategyFiveSec
        result = self.strategy.decide_trade(c1, c2, current_open, current_price)

        if result == 0:
            return "BUY"
        elif result == 1:
            return "SELL"
        else:
            return None

    def run_simulation(self, duration: int = 30, fast: bool = False):
        self.running = True
        last_close = 100.0  # قیمت شروع فرضی
        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                # تولید کندل جدید
                candle = self.generate_candle(last_close)
                self.add_candle(candle)
                last_close = candle.close_price

                # نمایش اطلاعات کندل جدید
                print(f"\n🕔 کندل جدید:")
                print(f"Open={candle.open_price:.2f}  Close={candle.close_price:.2f}  "
                      f"High={candle.high:.2f}  Low={candle.low:.2f}  Dir={candle.direction}")

                # تحلیل و بررسی صدور سیگنال معاملاتی
                signal = self.analyze()
                if signal:
                    print(f"🚀 سیگنال معاملاتی: {signal}")

                # اگر fast برابر False باشد، ۵ ثانیه صبر کن، در غیر این صورت بدون تأخیر ادامه بده
                if not fast:
                    time.sleep(5)  # فاصله ۵ ثانیه‌ای بین کندل‌ها (شبیه‌سازی)

        except KeyboardInterrupt:
            print("\n⏹ شبیه‌سازی به‌صورت دستی متوقف شد.")
        finally:
            self.running = False
            print("\n✅ شبیه‌سازی به پایان رسید.")

    def run_live(self, duration: int = 60):
        """
        اجرای خواندن داده زنده از live_reader و ساخت کندل ۵ ثانیه‌ای
        هر ۵ ثانیه یک کندل ساخته شده و تحلیل می‌شود.
        """
        if self.live_reader is None:
            print("❌ live_reader تنظیم نشده است.")
            return

        self.running = True
        open_price = None
        high = None
        low = None
        close_price = None
        start_time = time.time()

        prices = []

        while self.running and time.time() - start_time < duration:
            # خواندن قیمت زنده از مرورگر از طریق LiveDataReader
            price = self.live_reader.get_live_price()
            current_time = time.time()

            # بررسی اینکه قیمت None نباشد تا از خطا جلوگیری شود
            # این بررسی برای جلوگیری از خطا هنگام خواندن قیمت از مرورگر است.
            if price is None:
                print("⚠️ قیمت هنوز بارگذاری نشده، عبور از این مرحله...")
                time.sleep(1)
                continue

            if open_price is None:
                open_price = price
                high = price
                low = price

            # بروزرسانی high و low
            if price > high:
                high = price
            if price < low:
                low = price

            close_price = price
            prices.append(price)

            # اگر ۵ ثانیه گذشته باشد، کندل ساخته و تحلیل شود
            if current_time - start_time >= 5:
                candle = Candle(open_price=open_price, close_price=close_price, high=high, low=low)
                self.add_candle(candle)

                # نمایش اطلاعات کندل جدید
                print(f"\n🕔 کندل زنده جدید:")
                print(f"Open={candle.open_price:.2f}  Close={candle.close_price:.2f}  "
                      f"High={candle.high:.2f}  Low={candle.low:.2f}  Dir={candle.direction}")

                # تحلیل و بررسی صدور سیگنال معاملاتی
                signal = self.analyze()
                if signal:
                    print(f"🚀 سیگنال معاملاتی زنده: {signal}")

                # آماده‌سازی برای کندل بعدی
                open_price = None
                high = None
                low = None
                close_price = None
                prices = []
                start_time = current_time

            time.sleep(1)  # فاصله ۱ ثانیه‌ای خواندن داده زنده

        self.running = False
        print("\n✅ حالت زنده پایان یافت.")