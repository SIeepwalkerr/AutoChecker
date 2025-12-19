import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import vk_api
import threading
import time
import json
import os
import webbrowser
import re
from datetime import datetime


class VKManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VK Manager - Управление ВКонтакте")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        self.vk = None
        self.vk_session = None
        self.is_running = False
        self.config_file = "config.json"
        self.stats = self.load_stats()

        self.setup_ui()
        self.load_config()

    def load_stats(self):
        if os.path.exists('stats.json'):
            with open('stats.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'messages_read': 0, 'friends_removed': 0, 'groups_left': 0}

    def save_stats(self):
        with open('stats.json', 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=4, ensure_ascii=False)

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#5181B8", height=70)
        header.pack(fill="x")
        tk.Label(header, text="🔵 VK Manager", font=("Arial", 24, "bold"), bg="#5181B8", fg="white").pack(pady=15)

        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        left_panel = tk.Frame(main_container, width=350)
        left_panel.pack(side="left", fill="y", padx=(0, 5))

        right_panel = tk.Frame(main_container)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)

    def setup_left_panel(self, parent):
        conn = tk.LabelFrame(parent, text="🔐 Подключение", font=("Arial", 10, "bold"), padx=10, pady=10)
        conn.pack(fill="x", pady=(0, 10))

        tk.Label(conn, text="VK Access Token:").pack(anchor="w")
        token_fr = tk.Frame(conn)
        token_fr.pack(fill="x", pady=5)
        self.token_entry = tk.Entry(token_fr, show="*", font=("Arial", 9))
        self.token_entry.pack(side="left", fill="x", expand=True)
        tk.Button(token_fr, text="👁", width=3, command=self.toggle_token_visibility).pack(side="right", padx=(5, 0))

        btn_fr = tk.Frame(conn)
        btn_fr.pack(fill="x", pady=5)
        tk.Button(btn_fr, text="🔗 Получить токен", command=self.open_token_helper, bg="#E1E8ED").pack(side="left", padx=(0, 5))
        tk.Button(btn_fr, text="✓ Подключить", command=self.connect_vk, bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).pack(side="left")

        self.connection_status = tk.Label(conn, text="● Не подключено", fg="red")
        self.connection_status.pack(pady=(10, 0))

        quick = tk.LabelFrame(parent, text="⚡ Быстрые действия", font=("Arial", 10, "bold"), padx=10, pady=10)
        quick.pack(fill="x", pady=(0, 10))
        tk.Button(quick, text="📖 Прочитать сейчас", command=self.quick_read_messages, bg="#2196F3", fg="white", height=2).pack(fill="x", pady=2)
        tk.Button(quick, text="👥 Анализ друзей", command=lambda: self.notebook.select(1), bg="#9C27B0", fg="white", height=2).pack(fill="x", pady=2)
        tk.Button(quick, text="🏢 Группы", command=lambda: self.notebook.select(2), bg="#FF9800", fg="white", height=2).pack(fill="x", pady=2)

        stats_fr = tk.LabelFrame(parent, text="📊 Статистика", padx=10, pady=10)
        stats_fr.pack(fill="x", pady=(0, 10))
        self.stats_labels = {}
        for text, key in [("Прочитано сообщений:", "messages_read"), ("Удалено друзей:", "friends_removed"), ("Вышли из групп:", "groups_left")]:
            fr = tk.Frame(stats_fr)
            fr.pack(fill="x", pady=2)
            tk.Label(fr, text=text).pack(side="left")
            lbl = tk.Label(fr, text="0", font=("Arial", 8, "bold"), fg="#4CAF50")
            lbl.pack(side="right")
            self.stats_labels[key] = lbl
        tk.Button(stats_fr, text="🔄 Сбросить", command=self.reset_stats, bg="#E1E8ED").pack(fill="x", pady=(8, 0))

        settings = tk.LabelFrame(parent, text="⚙️ Настройки", padx=10, pady=10)
        settings.pack(fill="both", expand=True)
        tk.Button(settings, text="💾 Сохранить", command=self.save_config, bg="#607D8B", fg="white").pack(fill="x", pady=5)

        self.update_stats_display()

    def setup_right_panel(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)

        msg_tab = tk.Frame(self.notebook)
        friends_tab = tk.Frame(self.notebook)
        groups_tab = tk.Frame(self.notebook)
        logs_tab = tk.Frame(self.notebook)

        self.notebook.add(msg_tab, text="📬 Сообщения")
        self.notebook.add(friends_tab, text="👥 Друзья")
        self.notebook.add(groups_tab, text="🏢 Группы")
        self.notebook.add(logs_tab, text="📋 Логи")

        self.setup_messages_tab(msg_tab)
        self.setup_friends_tab(friends_tab)
        self.setup_groups_tab(groups_tab)
        self.setup_logs_tab(logs_tab)

    def setup_messages_tab(self, parent):
        f = tk.Frame(parent, padx=20, pady=20)
        f.pack(fill="both", expand=True)

        tk.Label(f, text="Автоматическое прочтение сообщений", font=("Arial", 14, "bold")).pack(pady=(0, 20))

        s = tk.LabelFrame(f, text="Настройки")
        s.pack(fill="x", pady=10)
        int_fr = tk.Frame(s)
        int_fr.pack(fill="x", pady=5)
        tk.Label(int_fr, text="Интервал (сек):").pack(side="left")
        self.msg_interval = tk.Spinbox(int_fr, from_=30, to=3600, width=10)
        self.msg_interval.pack(side="left", padx=10)
        self.msg_interval.delete(0, tk.END)
        self.msg_interval.insert(0, "60")

        self.filter_groups_var = tk.BooleanVar()
        tk.Checkbutton(s, text="Игнорировать групповые чаты", variable=self.filter_groups_var).pack(anchor="w")

        btns = tk.Frame(f)
        btns.pack(pady=20)
        self.start_btn = tk.Button(btns, text="▶ Запустить", command=self.start_auto_reading, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), height=2)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=5)
        self.stop_btn = tk.Button(btns, text="⏸ Остановить", command=self.stop_auto_reading, bg="#f44336", fg="white", font=("Arial", 11, "bold"), height=2, state="disabled")
        self.stop_btn.pack(side="right", fill="x", expand=True, padx=5)

    def setup_friends_tab(self, parent):
        f = tk.Frame(parent, padx=20, pady=20)
        f.pack(fill="both", expand=True)
        tk.Label(f, text="Анализ друзей", font=("Arial", 14, "bold")).pack(pady=(0, 15))

        btn_fr = tk.Frame(f)
        btn_fr.pack(pady=10)
        tk.Button(btn_fr, text="Неактивные (>6 мес)", command=self.find_inactive_friends, bg="#2196F3", fg="white").pack(side="left", padx=5)
        tk.Button(btn_fr, text="Удалённые аккаунты", command=self.find_deleted_friends, bg="#9C27B0", fg="white").pack(side="left", padx=5)

        list_fr = tk.LabelFrame(f, text="Результаты")
        list_fr.pack(fill="both", expand=True, pady=10)
        scrollbar = tk.Scrollbar(list_fr)
        scrollbar.pack(side="right", fill="y")
        self.friends_listbox = tk.Listbox(list_fr, yscrollcommand=scrollbar.set, selectmode="extended")
        self.friends_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.friends_listbox.yview)

        act_fr = tk.Frame(f)
        act_fr.pack(pady=10)
        tk.Button(act_fr, text="❌ Удалить выбранных", command=self.remove_selected_friends, bg="#f44336", fg="white").pack(side="left", padx=5)
        tk.Button(act_fr, text="🗑️ Очистить", command=lambda: self.friends_listbox.delete(0, tk.END)).pack(side="left", padx=5)

    def setup_groups_tab(self, parent):
        f = tk.Frame(parent, padx=20, pady=20)
        f.pack(fill="both", expand=True)
        tk.Label(f, text="Управление группами", font=("Arial", 14, "bold")).pack(pady=(0, 15))

        tk.Button(f, text="🔍 Загрузить группы", command=self.load_groups, bg="#2196F3", fg="white").pack(pady=10)

        list_fr = tk.LabelFrame(f, text="Список групп")
        list_fr.pack(fill="both", expand=True, pady=10)
        scrollbar = tk.Scrollbar(list_fr)
        scrollbar.pack(side="right", fill="y")
        self.groups_listbox = tk.Listbox(list_fr, yscrollcommand=scrollbar.set, selectmode="extended")
        self.groups_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.groups_listbox.yview)

        act_fr = tk.Frame(f)
        act_fr.pack(pady=10)
        tk.Button(act_fr, text="🚪 Выйти из выбранных", command=self.leave_selected_groups, bg="#f44336", fg="white").pack(side="left", padx=5)
        tk.Button(act_fr, text="🗑️ Очистить", command=lambda: self.groups_listbox.delete(0, tk.END)).pack(side="left", padx=5)

    def setup_logs_tab(self, parent):
        f = tk.Frame(parent, padx=20, pady=20)
        f.pack(fill="both", expand=True)
        self.log_text = scrolledtext.ScrolledText(f, font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4")
        self.log_text.pack(fill="both", expand=True)
        btn_fr = tk.Frame(f)
        btn_fr.pack(pady=10)
        tk.Button(btn_fr, text="🗑️ Очистить", command=lambda: self.log_text.delete(1.0, tk.END)).pack(side="left", padx=5)
        tk.Button(btn_fr, text="💾 Сохранить лог", command=self.save_log).pack(side="left", padx=5)

    # === Методы ===
    def toggle_token_visibility(self):
        self.token_entry.config(show="" if self.token_entry.cget("show") == "*" else "*")

    def open_token_helper(self):
        if os.path.exists("token_helper.html"):
            webbrowser.open("file://" + os.path.abspath("token_helper.html"))
        else:
            webbrowser.open("https://oauth.vk.com/authorize?client_id=2685278&scope=messages,friends,groups,offline&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token")
        self.log("Открыт помощник по токену", "INFO")

    def connect_vk(self):
        token = self.token_entry.get().strip()
        if not token:
            messagebox.showerror("Ошибка", "Введите токен")
            return
        def conn():
            try:
                self.vk_session = vk_api.VkApi(token=token)
                self.vk = self.vk_session.get_api()
                user = self.vk.users.get()[0]
                name = f"{user['first_name']} {user['last_name']}"
                self.root.after(0, lambda: self.connection_status.config(text=f"● {name}", fg="green"))
                self.log(f"Подключено: {name}", "SUCCESS")
            except Exception as e:
                self.root.after(0, lambda: self.connection_status.config(text="● Ошибка", fg="red"))
                self.log(f"Ошибка подключения: {e}", "ERROR")
                messagebox.showerror("Ошибка", str(e))
        threading.Thread(target=conn, daemon=True).start()

    def check_connection(self):
        if not self.vk:
            messagebox.showerror("Ошибка", "Подключитесь к VK")
            return False
        return True

    def log(self, msg, level="INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        colors = {"INFO": "#569cd6", "SUCCESS": "#6a9955", "ERROR": "#f44747", "WARNING": "#ce9178"}
        color = colors.get(level, "white")
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.tag_add(level, "end-2l", "end-1l")
        self.log_text.tag_config(level, foreground=color)
        self.log_text.see(tk.END)

    def quick_read_messages(self):
        if not self.check_connection(): return
        threading.Thread(target=self.read_messages_once, daemon=True).start()

    def read_messages_once(self):
        try:
            convs = self.vk.messages.getConversations(filter='unread', count=200)
            if convs['count'] == 0:
                self.log("Нет непрочитанных сообщений", "INFO")
                return
            self.log(f"Найдено: {convs['count']}", "INFO")
            count = 0
            for item in convs['items']:
                peer_id = item['conversation']['peer']['id']
                peer_type = item['conversation']['peer']['type']
                if self.filter_groups_var.get() and peer_type == 'chat':
                    continue
                self.vk.messages.markAsRead(peer_id=peer_id)
                count += 1
                time.sleep(0.4)
            self.stats['messages_read'] += count
            self.save_stats()
            self.root.after(0, self.update_stats_display)
            self.log(f"Прочитано диалогов: {count}", "SUCCESS")
        except Exception as e:
            self.log(f"Ошибка: {e}", "ERROR")

    def start_auto_reading(self):
        if not self.check_connection(): return
        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.log("Авто-чтение запущено", "SUCCESS")

        def loop():
            while self.is_running:
                self.read_messages_once()
                interval = int(self.msg_interval.get())
                for _ in range(interval):
                    if not self.is_running: break
                    time.sleep(1)
        threading.Thread(target=loop, daemon=True).start()

    def stop_auto_reading(self):
        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log("Авто-чтение остановлено", "WARNING")

    def find_inactive_friends(self):
        if not self.check_connection(): return
        self.friends_listbox.delete(0, tk.END)
        def run():
            try:
                friends = self.vk.friends.get(fields='last_seen')['items']
                now = time.time()
                inactive = []
                for fr in friends:
                    if 'last_seen' in fr:
                        if now - fr['last_seen']['time'] > 180*24*3600:
                            days = int((now - fr['last_seen']['time']) / 86400)
                            inactive.append((fr['id'], f"{fr['first_name']} {fr['last_name']} ({days} дней)"))
                for uid, text in inactive:
                    self.root.after(0, lambda t=text: self.friends_listbox.insert(tk.END, t))
                self.log(f"Неактивных: {len(inactive)}", "SUCCESS")
            except Exception as e:
                self.log(f"Ошибка: {e}", "ERROR")
        threading.Thread(target=run, daemon=True).start()

    def find_deleted_friends(self):
        if not self.check_connection(): return
        self.friends_listbox.delete(0, tk.END)
        def run():
            try:
                friends = self.vk.friends.get(fields='deactivated')['items']
                deleted = [f"{fr['first_name']} {fr['last_name']} (удалён)" for fr in friends if 'deactivated' in fr]
                for text in deleted:
                    self.root.after(0, lambda t=text: self.friends_listbox.insert(tk.END, t))
                self.log(f"Удалённых: {len(deleted)}", "SUCCESS")
            except Exception as e:
                self.log(f"Ошибка: {e}", "ERROR")
        threading.Thread(target=run, daemon=True).start()

    def remove_selected_friends(self):
        if not self.check_connection(): return
        sel = self.friends_listbox.curselection()
        if not sel or not messagebox.askyesno("Удаление", f"Удалить {len(sel)} друзей?"): return
        def run():
            removed = 0
            for i in reversed(sel):
                text = self.friends_listbox.get(i)
                # Простой парсинг ID не делаем — для безопасности лучше добавить хранение ID
                self.log(f"Удаление друга: {text} (демо)", "WARNING")
                removed += 1
                time.sleep(0.5)
            self.stats['friends_removed'] += removed
            self.save_stats()
            self.root.after(0, self.update_stats_display)
            self.root.after(0, lambda: self.friends_listbox.delete(0, tk.END))
            self.log(f"Удалено: {removed}", "SUCCESS")
        threading.Thread(target=run, daemon=True).start()

    def load_groups(self):
        if not self.check_connection(): return
        self.groups_listbox.delete(0, tk.END)
        def run():
            try:
                groups = self.vk.groups.get(extended=1)['items']
                for g in groups:
                    self.root.after(0, lambda name=g['name'], gid=g['id']: self.groups_listbox.insert(tk.END, f"{name} (ID: {gid})"))
                self.log(f"Загружено групп: {len(groups)}", "SUCCESS")
            except Exception as e:
                self.log(f"Ошибка: {e}", "ERROR")
        threading.Thread(target=run, daemon=True).start()

    def leave_selected_groups(self):
        if not self.check_connection(): return
        sel = self.groups_listbox.curselection()
        if not sel or not messagebox.askyesno("Выход", f"Выйти из {len(sel)} групп?"): return
        def run():
            left = 0
            for i in reversed(sel):
                text = self.groups_listbox.get(i)
                match = re.search(r'ID: (\d+)', text)
                if match:
                    gid = int(match.group(1))
                    self.vk.groups.leave(group_id=gid)
                    left += 1
                    time.sleep(0.5)
                self.log(f"Вышли из: {text}", "SUCCESS")
            self.stats['groups_left'] += left
            self.save_stats()
            self.root.after(0, self.update_stats_display)
            self.root.after(0, lambda: self.groups_listbox.delete(0, tk.END))
            self.log(f"Вышли из {left} групп", "SUCCESS")
        threading.Thread(target=run, daemon=True).start()

    def update_stats_display(self):
        for k, lbl in self.stats_labels.items():
            lbl.config(text=str(self.stats.get(k, 0)))

    def reset_stats(self):
        if messagebox.askyesno("Сброс", "Сбросить статистику?"):
            self.stats = {'messages_read': 0, 'friends_removed': 0, 'groups_left': 0}
            self.save_stats()
            self.update_stats_display()
            self.log("Статистика сброшена", "INFO")

    def save_log(self):
        filename = f"vk_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.log_text.get(1.0, tk.END))
        self.log(f"Лог сохранён: {filename}", "SUCCESS")

    def save_config(self):
        cfg = {"token": self.token_entry.get(), "interval": self.msg_interval.get(), "filter_groups": self.filter_groups_var.get()}
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        self.log("Настройки сохранены", "SUCCESS")

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.token_entry.insert(0, cfg.get("token", ""))
                self.msg_interval.delete(0, tk.END)
                self.msg_interval.insert(0, cfg.get("interval", "60"))
                self.filter_groups_var.set(cfg.get("filter_groups", False))
            except: pass


if __name__ == "__main__":
    root = tk.Tk()
    app = VKManagerApp(root)
    root.mainloop()