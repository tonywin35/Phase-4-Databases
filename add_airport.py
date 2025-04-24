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

def add_airport():
    try:
        values = (
            fields["airportID"].get(),
            fields["airport_name"].get(),
            fields["city"].get(),
            fields["state"].get(),
            fields["country"].get(),
            fields["locationID"].get()
        )
        cursor.callproc("add_airport", values)
        conn.commit()
        messagebox.showinfo("Success", "Airport added (if input was valid).")
        print("Inserting values:", values)

        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to add airport:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Make sure all fields have valid values.")

def show_airports():
    try:
        cursor.execute("SELECT airportID, airport_name, city, state, country FROM airport")
        rows = cursor.fetchall()
        result = "\n".join([f"{row[0]} - {row[1]} ({row[2]}, {row[3]}, {row[4]})" for row in rows]) or "No airports found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch airports: {err}")

def cancel_add():
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Add Airport")
root.geometry("350x350")
root.resizable(True, True)

fields = {
    "airportID": tk.StringVar(),
    "airport_name": tk.StringVar(),
    "city": tk.StringVar(),
    "state": tk.StringVar(),
    "country": tk.StringVar(),
    "locationID": tk.StringVar()
}

tk.Label(root, text="Add Airport", font=("Helvetica", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

for label, var in fields.items():
    row = tk.Frame(frame)
    tk.Label(row, text=f"{label}:", width=15, anchor='w', font=("Helvetica", 11)).pack(side=tk.LEFT)
    entry = tk.Entry(row, textvariable=var, width=25)
    entry.pack(side=tk.LEFT)
    row.pack(pady=4)

btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Add Airport", command=add_airport, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Show Airports", command=show_airports, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='w')
result_label.pack(pady=10)

root.mainloop()
