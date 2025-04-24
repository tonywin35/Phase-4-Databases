import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="cs4400_2025",
    database="flight_tracking"
)
cursor = conn.cursor()

try:
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    print("Tables found:")
    for table in tables:
        print(" -", table[0])
except mysql.connector.Error as err:
    print("Error:", err)
    messagebox.showerror("Database Error", f"MySQL Error: {err}")

def show_flights_in_air():
    try:
        cursor.execute("SELECT * FROM flights_in_the_air")
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()

        for item in tree.get_children():
            tree.delete(item)

        tree["columns"] = columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for row in data:
            tree.insert("", "end", values=row)
            
        if not data:
            messagebox.showinfo("Info", "No flights currently in the air.")
            
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to retrieve flights in air:\n{err}")

def refresh():
    show_flights_in_air()

def exit_program():
    conn.close()
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Flights in the Air")
root.geometry("900x500")
root.resizable(True, True)

tk.Label(root, text="Flights in the Air", font=("Helvetica", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10, fill=tk.BOTH, expand=True)

tree = ttk.Treeview(frame)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=v_scrollbar.set)

h_frame = tk.Frame(root)
h_frame.pack(fill=tk.X, expand=False)
h_scrollbar = ttk.Scrollbar(h_frame, orient="horizontal", command=tree.xview)
h_scrollbar.pack(fill=tk.X)
tree.configure(xscrollcommand=h_scrollbar.set)

btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Refresh", command=refresh, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Exit", command=exit_program, width=15).pack(side=tk.LEFT, padx=10)

btn_frame.pack(pady=20)

show_flights_in_air()

root.protocol("WM_DELETE_WINDOW", exit_program)
root.mainloop()
