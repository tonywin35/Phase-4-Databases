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
    print("✅ Connected to MySQL! Tables found:")
    for table in tables:
        print(" -", table[0])
except mysql.connector.Error as err:
    print("❌ Error:", err)
    messagebox.showerror("Database Error", f"MySQL Error: {err}")

def add_airplane():
    try:
        values = (
            fields["airlineID"].get(),
            fields["tail_num"].get(),
            int(fields["seat_capacity"].get()),
            int(fields["speed"].get()),
            fields["locationID"].get(),
            fields["plane_type"].get(),
            bool(int(fields["maintenanced"].get())),
            fields["model"].get(),
            bool(int(fields["neo"].get()))
        )
        cursor.callproc("add_airplane", values)
        conn.commit()
        messagebox.showinfo("Success", "Airplane added (if input was valid).")
        print("Inserting values:", values)
        
        # Try printing the outcome
        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to add airplane:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Make sure numeric fields are valid integers (0 or 1 for booleans).")

def show_airplanes():
    try:
        cursor.execute("SELECT airline_id, tail_num, airplane_type FROM airplane")
        rows = cursor.fetchall()
        result = "\n".join([f"{row[0]} - {row[1]} ({row[2]})" for row in rows]) or "No airplanes found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch airplanes: {err}")

def cancel_add():
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Add Airplane")
root.geometry("350x400")
root.resizable(True, True)

fields = {
    "airlineID": tk.StringVar(),
    "tail_num": tk.StringVar(),
    "seat_capacity": tk.StringVar(),
    "speed": tk.StringVar(),
    "locationID": tk.StringVar(),
    "plane_type": tk.StringVar(),
    "maintenanced": tk.StringVar(),
    "model": tk.StringVar(),
    "neo": tk.StringVar(),
}

# Heading
tk.Label(root, text="Add Airplane", font=("Helvetica", 16, "bold")).pack(pady=10)

# Display each field and its value
frame = tk.Frame(root)
frame.pack(pady=10)

for label, var in fields.items():
    row = tk.Frame(frame)
    tk.Label(row, text=f"{label}:", width=15, anchor='w', font=("Helvetica", 11)).pack(side=tk.LEFT)
    entry = tk.Entry(row, textvariable=var, width=25)
    entry.pack(side=tk.LEFT)
    row.pack(pady=4)

# Buttons
btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Add Airplane", command=add_airplane, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Show Airplanes", command=show_airplanes, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='w')
result_label.pack(pady=10)

root.mainloop()
