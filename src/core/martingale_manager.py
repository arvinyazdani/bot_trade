class MartingaleManager:
    """
    مدیریت مارتینگل منظم (مثلاً ضریب 2x) تا n مرحله.
    """
    def __init__(self, base_amount: float = 1.0, factor: float = 2.0, max_steps: int = 5):
        self.base_amount = base_amount
        self.factor = factor
        self.max_steps = max_steps
        self.step = 0

    def current_amount(self) -> float:
        return self.base_amount * (self.factor ** self.step)

    def on_win(self):
        """در صورت برد، مارتینگل ریست می‌شود."""
        self.step = 0

    def on_loss(self):
        """در صورت باخت، اگر جا دارد به مرحله بعد می‌رویم."""
        if self.step < self.max_steps:
            self.step += 1

    def reset(self):
        self.step = 0