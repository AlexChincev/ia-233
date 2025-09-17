import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime, timedelta
import winsound


# ===== БАЗОВЫЙ ТАЙМЕР =====
class BaseTimer:
    def __init__(self, parent, label, font=("Helvetica", 16)):
        self.parent = parent
        self.label = label
        self.font = font
        self.seconds = 0

    def tick(self):
        """Обновление таймера — реализуется в наследниках"""
        pass

    def update_display(self, text):
        """Вывод текста на метку"""
        self.label.config(text=text, font=self.font)

    def to_hhmmss(self, sec):
        """Форматирование секунд в HH:MM:SS"""
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        return f"{h:02}:{m:02}:{s:02}"


# ===== СТАНДАРТНЫЙ ТАЙМЕР =====
class StandardTimer(BaseTimer):
    def tick(self):
        self.seconds += 1
        self.update_display(f"⏳ Standard: {self.to_hhmmss(self.seconds)}")


# ===== ИНТЕРВАЛЬНЫЙ ТАЙМЕР =====
class IntervalTimer(BaseTimer):
    def __init__(self, parent, label, interval=5, font=("Helvetica", 16)):
        super().__init__(parent, label, font)
        self.interval = interval

    def tick(self):
        self.seconds += 1
        if self.seconds >= self.interval:
            self.seconds = 0
            winsound.Beep(1000, 400)  # звук при каждом интервале
        self.update_display(f"🔁 Interval ({self.interval}s): {self.to_hhmmss(self.seconds)}")


# ===== ЦЕЛЕВОЙ ТАЙМЕР =====
class TargetTimer(BaseTimer):
    def __init__(self, parent, label, target_hhmm, font=("Helvetica", 16)):
        super().__init__(parent, label, font)
        self.target_hhmm = target_hhmm
        self.target_seconds = self.compute_seconds_until(target_hhmm)

    def compute_seconds_until(self, hhmm):
        hh = hhmm // 100
        mm = hhmm % 100
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            return 0
        now = datetime.now()
        target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return int((target - now).total_seconds())

    def tick(self):
        if self.target_seconds > 0:
            self.target_seconds -= 1
            if self.target_seconds == 0:
                winsound.Beep(1500, 800)  # длинный звук по окончании
                messagebox.showinfo("Target Timer", "🎯 Целевое время наступило!")
        self.update_display(f"🎯 Target {self.target_hhmm:04}: {self.to_hhmmss(self.target_seconds)}")


# ===== ОСНОВНОЕ ПРИЛОЖЕНИЕ =====
class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("400x250")
        self.root.configure(bg="#20232a")

        font = ("Helvetica", 18, "bold")

        # Получаем целевое время от пользователя
        target_time = simpledialog.askinteger(
            "Target Timer", "Введите целевое время (HHMM):", parent=self.root
        )
        if target_time is None:
            self.root.destroy()
            return

        # Метки
        self.standard_label = tk.Label(root, text="", bg="#20232a", fg="#61dafb", font=font)
        self.interval_label = tk.Label(root, text="", bg="#20232a", fg="#21a366", font=font)
        self.target_label = tk.Label(root, text="", bg="#20232a", fg="#f54291", font=font)

        self.standard_label.pack(pady=10)
        self.interval_label.pack(pady=10)
        self.target_label.pack(pady=10)

        # Таймеры
        self.standard_timer = StandardTimer(root, self.standard_label, font)
        self.interval_timer = IntervalTimer(root, self.interval_label, 5, font)
        self.target_timer = TargetTimer(root, self.target_label, target_time, font)

        # Запускаем цикл обновления
        self.update_all()

    def update_all(self):
        self.standard_timer.tick()
        self.interval_timer.tick()
        self.target_timer.tick()
        self.root.after(1000, self.update_all)

# ===== ЗАПУСК =====
if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()