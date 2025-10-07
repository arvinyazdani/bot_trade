import time
from datetime import datetime

class TradeExecutorMock:
    """
    اکسکیوتور ماک: به‌جای کلیک واقعی، فقط لاگ و خروجی ترمینال می‌دهد.
    """
    def __init__(self, logger=None):
        self.logger = logger

    def place_trade(self, direction: str, amount: float, expiry_seconds: int = 5):
        """
        ثبت معامله فرضی و برگرداندن نتیجه‌ی شبیه‌سازی (تصادفی یا بر اساس منطق تست).
        """
        ts = datetime.now().isoformat(timespec="seconds")
        print(f"🧾 [{ts}] ثبت معامله {direction.upper()} مبلغ={amount} زمان={expiry_seconds}s")
        if self.logger:
            self.logger.log_event("place_trade", {
                "time": ts, "direction": direction, "amount": amount, "expiry": expiry_seconds
            })
        # نتیجه را فعلا تصادفی یا الگوی ساده برگردان (در فاز گزارش‌گیری دقیق‌تر می‌کنیم)
        # اینجا می‌توانیم بر اساس حرکت کندل بعدی نتیجه بدهیم؛ موقتاً random:
        import random
        win = random.random() > 0.5
        return win