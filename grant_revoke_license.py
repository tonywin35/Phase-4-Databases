import tkinter as tk
from tkinter import messagebox
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Phase4sucksballs",
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

def grant_revoke_license():
    try:
        values = (
            fields["personID"].get(),
            fields["license"].get()
        )
        cursor.callproc("grant_or_revoke_pilot_license", values)
        conn.commit()
        messagebox.showinfo("Success", "License granted or revoked (if input was valid).")
        print("Processing with values:", values)

        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to process license:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Make sure all fields are valid.")

def show_licenses():
    try:
        cursor.execute("""
            SELECT p.personID, p.first_name, p.last_name, l.license_type 
            FROM pilot pi
            JOIN person p ON pi.personID = p.personID
            LEFT JOIN license l ON pi.personID = l.personID
        """)
        rows = cursor.fetchall()
        result = "\n".join([f"{row[0]} - {row[1]} {row[2] or ''}: {row[3] or 'No license'}" for row in rows]) or "No pilots found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch licenses: {err}")

def show_pilots():
    try:
        cursor.execute("""
            SELECT p.personID, p.first_name, p.last_name, pi.experience
            FROM pilot pi
            JOIN person p ON pi.personID = p.personID
        """)
        rows = cursor.fetchall()
        result = "\n".join([f"{row[0]} - {row[1]} {row[2] or ''} (Exp: {row[3]})" for row in rows]) or "No pilots found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch pilots: {err}")

def cancel():
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Grant or Revoke Pilot License")
root.geometry("350x300")
root.resizable(True, True)

fields = {
    "personID": tk.StringVar(),
    "license": tk.StringVar()
}

tk.Label(root, text="Grant or Revoke Pilot License", font=("Helvetica", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

for label, var in fields.items():
    row = tk.Frame(frame)
    tk.Label(row, text=f"{label}:", width=15, anchor='w', font=("Helvetica", 11)).pack(side=tk.LEFT)
    entry = tk.Entry(row, textvariable=var, width=25)
    entry.pack(side=tk.LEFT)
    row.pack(pady=4)

help_text = "Common licenses: A320, A380, B737, B747, B777, B787"
tk.Label(root, text=help_text, font=("Helvetica", 9), justify=tk.LEFT).pack()

btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Add/Revoke", command=grant_revoke_license, width=10).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Show Pilots", command=show_pilots, width=10).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='w')
result_label.pack(pady=10)

root.mainloop()
