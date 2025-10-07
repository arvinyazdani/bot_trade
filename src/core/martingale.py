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
ماژول MartingaleManager
------------------------
مدیریت پله‌های مارتینگل، ضریب رشد و بازگشت پس از برد.
"""

class MartingaleManager:
    def __init__(self, config):
        # مقدار پایه معامله (اولین پله)
        self.base_amount = 1
        # ضریب رشد (۲ = دو برابر در هر باخت)
        self.multiplier = config.get("martingale_step", 2)
        # آیا مارتینگل بعد از باخت ادامه دارد؟
        self.continue_after_loss = config.get("continue_after_loss", True)

    def next_step(self, current_amount):
        """
        در صورت باخت، مبلغ مرحله بعدی را بر اساس ضریب رشد برمی‌گرداند.
        """
        if not self.continue_after_loss:
            return self.base_amount
        next_amount = current_amount * self.multiplier
        print(f"🔁 مارتینگل فعال: مبلغ بعدی = {next_amount}")
        return next_amount

    def reset_amount(self):
        """
        بازگشت به مبلغ پایه در صورت برد یا شروع جدید.
        """
        return self.base_amount