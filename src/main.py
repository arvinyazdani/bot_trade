"""
Bot Trade Project - Offline Simulation Mode
-------------------------------------------
اجرای ربات در حالت آفلاین با داده‌های تست (شبیه‌سازی کندل‌های ۵ ثانیه‌ای)
"""

from core.candle_engine import CandleEngine
from core.strategy_five_sec import StrategyFiveSec
from core.martingale_manager import MartingaleManager
from core.trade_executor import TradeExecutorMock
from core.trade_logger import TradeLogger

def main():
    """
    اجرای کامل تست ربات در حالت آفلاین
    شامل ساخت کندل‌ها، تصمیم‌گیری استراتژی و اجرای ماک تریدها
    """
    print("🔷 شروع اجرای حالت شبیه‌سازی...\n")

    # ⚙️ پیکربندی پایه
    cfg = {
        "five_second_mode": True,
        "max_trades": 10,
        "martingale_factor": 2,
        "continue_after_loss": True
    }

    # 🧩 ایجاد ماژول‌ها
    engine = CandleEngine(mode="sim")              # موتور شبیه‌سازی کندل‌ها
    strategy = StrategyFiveSec(cfg)                # منطق تصمیم‌گیری
    logger = TradeLogger()                         # ثبت وقایع
    martingale = MartingaleManager(base_amount=1.0, factor=2.0, max_steps=3)
    executor = TradeExecutorMock(logger=logger)    # اجرای ترید ماک

    # اجرای شبیه‌سازی و تولید کندل‌های تست
    engine.run_simulation(duration=60)

    # ✅ شبیه‌سازی ترید بر اساس سیگنال تصادفی استراتژی
    import random
    for i in range(cfg["max_trades"]):
        direction = random.choice(["buy", "sell"])
        amount = martingale.current_amount()
        print(f"\n🕓 ترید شماره {i+1} | جهت: {direction.upper()} | حجم: {amount}")
        win = executor.place_trade(direction, amount)
        result = "win" if win else "loss"
        logger.log_trade(direction, amount, result=result)
        if win:
            martingale.on_win()
        else:
            martingale.on_loss()

    # 📊 نمایش آمار نهایی
    stats = logger.stats()
    print("\n📈 نتایج شبیه‌سازی:")
    print(f"تعداد کل معاملات: {stats['total']}")
    print(f"بردها: {stats['wins']} | باخت‌ها: {stats['losses']}")
    print(f"درصد برد: {stats['winrate']}%")

if __name__ == "__main__":
    main()