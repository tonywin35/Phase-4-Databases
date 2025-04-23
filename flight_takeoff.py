import tkinter as tk
from tkinter import messagebox
import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="!",
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

def flight_takeoff():
    try:
        values = (
            fields["flightID"].get(),
        )
        cursor.callproc("flight_takeoff", values)
        conn.commit()
        messagebox.showinfo("Success", "Flight took off (if input was valid).")
        print("Processing with values:", values)
        
        # Try printing the outcome
        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to process takeoff:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Make sure the flight ID is valid.")

def show_flights_on_ground():
    try:
        cursor.execute("""
            SELECT f.flightID, f.support_airline, f.support_tail 
            FROM flight f
            WHERE f.airplane_status = 'on_ground'
        """)
        rows = cursor.fetchall()
        result = "\n".join([f"{row[0]} - Airline: {row[1]}, Plane: {row[2]}" for row in rows]) or "No flights on the ground."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch flights: {err}")

def show_pilot_info():
    try:
        cursor.execute("""
            SELECT f.flightID, f.support_airline, f.support_tail, 
                   COUNT(fc.personID) as pilot_count
            FROM flight f
            LEFT JOIN flight_crew fc ON f.flightID = fc.flightID
            WHERE f.airplane_status = 'on_ground'
            GROUP BY f.flightID
        """)
        rows = cursor.fetchall()
        result = "\n".join([f"{row[0]} - Pilots assigned: {row[3]}" for row in rows]) or "No flights found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch pilot info: {err}")

def cancel():
    root.destroy()

root = tk.Tk()
root.title("Flight Takeoff")
root.geometry("350x300")
root.resizable(True, True)

fields = {
    "flightID": tk.StringVar()
}

# Heading
tk.Label(root, text="Flight Takeoff", font=("Helvetica", 16, "bold")).pack(pady=10)

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
tk.Button(btn_frame, text="Takeoff", command=flight_takeoff, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Show Grounded", command=show_flights_on_ground, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Show Pilots", command=show_pilot_info, width=15).pack(side=tk.LEFT, padx=5)
btn_frame.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='w')
result_label.pack(pady=10)

root.mainloop()
