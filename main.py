import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DATA_FILE = "weather_data.json"


class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("980x650")
        self.root.resizable(False, False)
        self.records = []
        self.build_ui()
        self.load_data()

    def build_ui(self):
        title = ttk.Label(self.root, text="Weather Diary", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        form = ttk.LabelFrame(self.root, text="Новая запись")
        form.pack(fill="x", padx=10, pady=8)

        ttk.Label(form, text="Дата (YYYY-MM-DD):").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.date_entry = ttk.Entry(form, width=20)
        self.date_entry.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(form, text="Температура (°C):").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.temp_entry = ttk.Entry(form, width=20)
        self.temp_entry.grid(row=0, column=3, padx=6, pady=6)

        ttk.Label(form, text="Описание погоды: ").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.desc_entry = ttk.Entry(form, width=55)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=6, pady=6, sticky="we")

        ttk.Label(form, text="Осадки:").grid(row=2, column=0, padx=6, pady=6, sticky="w")
        self.precip_var = tk.StringVar(value="нет")
        self.precip_combo = ttk.Combobox(form, textvariable=self.precip_var, values=["да", "нет"], state="readonly", width=18)
        self.precip_combo.grid(row=2, column=1, padx=6, pady=6, sticky="w")

        ttk.Button(form, text="Добавить запись", command=self.add_record).grid(row=2, column=3, padx=6, pady=6, sticky="e")

        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация")
        filter_frame.pack(fill="x", padx=10, pady=8)

        ttk.Label(filter_frame, text="Дата:").grid(row=0, column=0, padx=6, pady=6)
        self.filter_date_entry = ttk.Entry(filter_frame, width=18)
        self.filter_date_entry.grid(row=0, column=1, padx=6, pady=6)

        ttk.Button(filter_frame, text="Показать по дате", command=self.filter_by_date).grid(row=0, column=2, padx=6, pady=6)

        ttk.Label(filter_frame, text="Температура выше:").grid(row=0, column=3, padx=6, pady=6)
        self.filter_temp_entry = ttk.Entry(filter_frame, width=18)
        self.filter_temp_entry.grid(row=0, column=4, padx=6, pady=6)

        ttk.Button(filter_frame, text="Показать по температуре", command=self.filter_by_temp).grid(row=0, column=5, padx=6, pady=6)
        ttk.Button(filter_frame, text="Показать все", command=self.refresh_table).grid(row=0, column=6, padx=6, pady=6)

        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16)
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")

        self.tree.column("date", width=120, anchor="center")
        self.tree.column("temperature", width=120, anchor="center")
        self.tree.column("description", width=500, anchor="w")
        self.tree.column("precipitation", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=10)

        ttk.Button(bottom, text="Сохранить", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(bottom, text="Загрузить", command=self.load_data).pack(side="left", padx=5)
        ttk.Button(bottom, text="Очистить форму", command=self.clear_form).pack(side="left", padx=5)

    def validate_input(self, date_text, temp_text, desc_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате YYYY-MM-DD.")
            return False
        try:
            float(temp_text)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом.")
            return False
        if not desc_text.strip():
            messagebox.showerror("Ошибка", "Описание не должно быть пустым.")
            return False
        return True

    def add_record(self):
        date_text = self.date_entry.get().strip()
        temp_text = self.temp_entry.get().strip()
        desc_text = self.desc_entry.get().strip()
        precip_text = self.precip_var.get().strip()

        if not self.validate_input(date_text, temp_text, desc_text):
            return

        record = {
            "date": date_text,
            "temperature": float(temp_text),
            "description": desc_text,
            "precipitation": precip_text
        }
        self.records.append(record)
        self.refresh_table()
        self.clear_form()
        messagebox.showinfo("Успех", "Запись добавлена.")

    def refresh_table(self, data=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        data = self.records if data is None else data
        for record in data:
            self.tree.insert("", "end", values=(
                record["date"],
                record["temperature"],
                record["description"],
                record["precipitation"]
            ))

    def filter_by_date(self):
        date_text = self.filter_date_entry.get().strip()
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите дату в формате YYYY-MM-DD.")
            return
        filtered = [r for r in self.records if r["date"] == date_text]
        self.refresh_table(filtered)

    def filter_by_temp(self):
        temp_text = self.filter_temp_entry.get().strip()
        try:
            temp_value = float(temp_text)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число для фильтрации.")
            return
        filtered = [r for r in self.records if r["temperature"] > temp_value]
        self.refresh_table(filtered)

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", "Данные сохранены в JSON.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.records = []
        self.refresh_table()

    def clear_form(self):
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set("нет")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()
