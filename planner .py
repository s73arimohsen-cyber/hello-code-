import tkinter as tk
from tkinter import scrolledtext, messagebox
import sqlite3
from datetime import datetime
from tkcalendar import Calendar

class DailyPlannerApp:
    def __init__(self, master): # master لێرەدا پێناسە کراوە
        self.master = master
        master.title("دەفتەری ڕۆژانەی من")
        master.geometry("800x600")
        master.configure(bg="#F0F8FF") # رەنگی پاشخان

        self.conn = sqlite3.connect('planner.db')
        self.create_table()

        # چوارچێوەی سەرەوە (بۆ بەروار و ناونیشان)
        self.top_frame = tk.Frame(master, bg="#ADD8E6", bd=2, relief="raised")
        self.top_frame.pack(pady=10, padx=10, fill="x")

        self.date_label = tk.Label(self.top_frame, text=self.get_current_date(), font=("Arial", 16, "bold"), bg="#ADD8E6", fg="white")
        self.date_label.pack(side="left", padx=10)

        self.title_label = tk.Label(self.top_frame, text="پلانەکانی ئەمڕۆ", font=("Arial", 20, "bold"), bg="#ADD8E6", fg="white")
        self.title_label.pack(side="right", padx=10)

        # چوارچێوەی تەقویم
        # ئەم بەشانە دەبێت لێرەدا بن، لەناو فانکشنی __init__ و دوای self.title_label.pack()
        self.calendar_frame = tk.Frame(master, bg="#F0F8FF")
        self.calendar_frame.pack(pady=5, padx=10, fill="x")

        self.cal = Calendar(self.calendar_frame, selectmode='day',
                             year=datetime.now().year, month=datetime.now().month,
                             day=datetime.now().day,
                             date_pattern='y-mm-dd',
                             font="Arial 10", background="#E0FFFF",
                             foreground="#333333", selectbackground="#4CAF50",
                             selectforeground="white", headersbackground="#ADD8E6",
                             headersforeground="white", weekendbackground="#F0F8FF",
                             weekendforeground="#FF5722")
        self.cal.pack(padx=10, pady=5)
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)

        # چوارچێوەی ناوەڕاست (بۆ شوێنی نووسین)
        self.text_frame = tk.Frame(master, bg="#E6E6FA", bd=2, relief="sunken")
        self.text_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.planner_text = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, font=("Calibri", 12), width=70, height=20, bg="#FFFFFF", fg="#333333", insertbackground="black")
        self.planner_text.pack(pady=10, padx=10, fill="both", expand=True)

        # چوارچێوەی خوارەوە (بۆ دوگمەکان)
        self.button_frame = tk.Frame(master, bg="#F0F8FF")
        self.button_frame.pack(pady=10, padx=10, fill="x")

        self.save_button = tk.Button(self.button_frame, text="پاشکەوتکردن", command=self.save_plan, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", padx=10, pady=5)
        self.save_button.pack(side="left", padx=10)

        self.load_button = tk.Button(self.button_frame, text="بارکردنی پلان", command=lambda: self.load_plan(self.current_selected_date), font=("Arial", 12, "bold"), bg="#2196F3", fg="white", padx=10, pady=5)
        self.load_button.pack(side="left", padx=10)

        self.clear_button = tk.Button(self.button_frame, text="سڕینەوە", command=self.clear_text, font=("Arial", 12, "bold"), bg="#FF5722", fg="white", padx=10, pady=5)
        self.clear_button.pack(side="right", padx=10)
        
        # بۆ هەڵگرتنی بەرواری هەڵبژێردراو
        self.current_selected_date = self.get_current_date()

        # بارکردنی پلانی ئەمڕۆ کاتێک ئەپلیکەیشنەکە دەکرێتەوە
        self.load_plan(self.current_selected_date)

    def get_current_date(self):
        return datetime.now().strftime("%Y-%m-%d")

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY,
                date TEXT UNIQUE,
                plan TEXT
            )
        ''')
        self.conn.commit()

    def on_date_select(self, event):
        selected_date = self.cal.get_date()
        self.date_label.config(text=selected_date) # گۆڕینی بەرواری نمایشکراو
        self.load_plan(selected_date) # بارکردنی پلانی ڕۆژی هەڵبژێردراو
        self.current_selected_date = selected_date # نوێکردنەوەی بەرواری هەڵبژێردراو

    def save_plan(self):
        plan_date = self.current_selected_date
        plan_content = self.planner_text.get(1.0, tk.END).strip()

        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO plans (date, plan) VALUES (?, ?)", (plan_date, plan_content))
        except sqlite3.IntegrityError:
            cursor.execute("UPDATE plans SET plan = ? WHERE date = ?", (plan_content, plan_date))
        self.conn.commit()
        messagebox.showinfo("سەرکەوتوو بوو", f"پلانی {plan_date} بە سەرکەوتوویی پاشکەوت کرا!")

    def load_plan(self, selected_date=None):
        if selected_date is None:
            current_date_to_load = self.get_current_date()
        else:
            current_date_to_load = selected_date

        cursor = self.conn.cursor()
        cursor.execute("SELECT plan FROM plans WHERE date = ?", (current_date_to_load,))
        result = cursor.fetchone()

        self.planner_text.delete(1.0, tk.END)
        if result:
            self.planner_text.insert(tk.END, result[0])
        else:
            self.planner_text.insert(tk.END, f"هیچ پلانێک بۆ {current_date_to_load} نییە. دەستبکە بە نووسین!")

        self.current_selected_date = current_date_to_load

    def clear_text(self):
        self.planner_text.delete(1.0, tk.END)

# دروستکردنی پەنجەرەی سەرەکی
root = tk.Tk()
app = DailyPlannerApp(root)
root.mainloop()

# دوای داخستنی ئەپلیکەیشنەکە، پەیوەندی بنکەدراوەکە دابخە
app.conn.close()