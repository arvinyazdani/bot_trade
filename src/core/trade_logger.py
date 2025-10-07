import json
from pathlib import Path
from datetime import datetime

class TradeLogger:
    def __init__(self, path: str = "logs/trades.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def log_trade(self, direction: str, amount: float, result: str):
        ts = datetime.now().isoformat(timespec="seconds")
        rec = {"time": ts, "direction": direction, "amount": amount, "result": result}
        data = self._read_all()
        data.append(rec)
        self._write_all(data)

    def log_event(self, name: str, payload: dict):
        ts = datetime.now().isoformat(timespec="seconds")
        rec = {"time": ts, "event": name, "payload": payload}
        data = self._read_all()
        data.append(rec)
        self._write_all(data)

    def stats(self):
        data = self._read_all()
        trades = [d for d in data if "result" in d]
        wins = sum(1 for t in trades if t["result"] == "win")
        losses = sum(1 for t in trades if t["result"] == "loss")
        total = len(trades)
        wr = (wins / total * 100) if total else 0.0
        return {"total": total, "wins": wins, "losses": losses, "winrate": round(wr, 2)}

    def _read_all(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write_all(self, data):
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")