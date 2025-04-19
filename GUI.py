import tkinter as tk
from tkinter import messagebox
import sqlite3
import mysql.connector
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="flight_tracking"
)
cursor = conn.cursor()
def add_airplane():
    messagebox.showinfo("Airplane Added", "The airplane has been added to the system!")

def cancel_add():
    root.destroy()

root = tk.Tk()
root.title("Add Airplane")
root.geometry("350x400")
root.resizable(False, False)

fields = {
    "Speed": "345",
    "Maintained": "NULL",
    "Airline ID": "United",
    "Neo": "TRUE",
    "Tail Num": "nk780b",
    "Location ID": "port_190",
    "Model": "NULL",
    "Seat Cap": "120",
    "Plane Type": "Airbus"
}

# Heading
tk.Label(root, text="Add Airplane", font=("Helvetica", 16, "bold")).pack(pady=10)

# Display each field and its value
frame = tk.Frame(root)
frame.pack(pady=10)

for label, value in fields.items():
    row = tk.Frame(frame)
    tk.Label(row, text=f"{label}:", width=15, anchor='w', font=("Helvetica", 11)).pack(side=tk.LEFT)
    tk.Label(row, text=value, width=20, anchor='w', font=("Helvetica", 11, "bold")).pack(side=tk.LEFT)
    row.pack(pady=4)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)
root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

root.mainloop()
