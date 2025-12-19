import tkinter as tk
from tkinter import messagebox, scrolledtext
import vk_api
import threading
import time

class VKAutoReadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VK Auto Read")
        self.root.geometry("600x500")
        self.is_running = False
        self.setup_ui()

    def setup_ui(self):
        # Заголовок
        header = tk.Frame(self.root, bg="#5181B8", height=50)
        header.pack(fill="x")
        tk.Label(header, text="VK Auto Read", font=("Arial", 18, "bold"), 
                bg="#5181B8", fg="white").pack(pady=10)

        main = tk.Frame(self.root, padx=20, pady=20)
        main.pack(fill="both", expand=True)

        # Токен
        tk.Label(main, text="VK Access Token:", font=("Arial", 10)).pack(anchor="w")
        self.token_entry = tk.Entry(main, width=60, show="*")
        self.token_entry.pack(fill="x", pady=5)

        # Интервал
        interval_frame = tk.Frame(main)
        interval_frame.pack(fill="x", pady=10)
        tk.Label(interval_frame, text="Интервал (сек):").pack(side="left")
        self.interval = tk.Spinbox(interval_frame, from_=30, to=3600, value=60, width=10)
        self.interval.pack(side="left", padx=10)

        # Кнопки
        btn_frame = tk.Frame(main)
        btn_frame.pack(fill="x", pady=10)

        self.start_btn = tk.Button(btn_frame, text="▶ Запустить", 
                                   command=self.start, bg="#4CAF50", fg="white",
                                   font=("Arial", 11, "bold"), width=15)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = tk.Button(btn_frame, text="⏸ Остановить",
                                  command=self.stop, bg="#f44336", fg="white",
                                  font=("Arial", 11, "bold"), width=15, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        tk.Button(btn_frame, text="📖 Сейчас", command=self.read_once,
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"), 
                 width=12).pack(side="left", padx=5)

        # Лог
        tk.Label(main, text="Лог:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10,5))
        self.log = scrolledtext.ScrolledText(main, height=15, bg="#F5F5F5")
        self.log.pack(fill="both", expand=True)

    def log_msg(self, msg):
        self.log.insert("end", f"{msg}\n")
        self.log.see("end")

    def read_messages(self):
        token = self.token_entry.get().strip()
        if not token:
            messagebox.showerror("Ошибка", "Введите токен!")
            return 0

        try:
            vk = vk_api.VkApi(token=token).get_api()
            convs = vk.messages.getConversations(filter='unread', count=200)

            if convs['count'] == 0:
                self.log_msg("Нет непрочитанных")
                return 0

            self.log_msg(f"Найдено: {convs['count']}")

            for item in convs['items']:
                if not self.is_running:
                    break
                peer_id = item['conversation']['peer']['id']
                vk.messages.markAsRead(peer_id=peer_id)
                self.log_msg(f"✓ Диалог {peer_id}")
                time.sleep(0.5)

            return convs['count']
        except Exception as e:
            self.log_msg(f"✗ Ошибка: {e}")
            messagebox.showerror("Ошибка", str(e))
            return 0

    def read_once(self):
        threading.Thread(target=self.read_messages, daemon=True).start()

    def start(self):
        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.log_msg("▶ Запущен")

        def loop():
            while self.is_running:
                self.read_messages()
                interval = int(self.interval.get())
                self.log_msg(f"⏰ Ожидание {interval}с...")
                for _ in range(interval):
                    if not self.is_running:
                        break
                    time.sleep(1)

        threading.Thread(target=loop, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log_msg("⏸ Остановлен")

if __name__ == "__main__":
    root = tk.Tk()
    app = VKAutoReadApp(root)
    root.mainloop()
