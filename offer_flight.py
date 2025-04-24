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

def offer_flight():
    try:
        values = (
            fields["flightID"].get(),
            fields["routeID"].get(),
            fields["support_airline"].get(),
            fields["support_tail"].get(),
            int(fields["progress"].get()),
            fields["next_time"].get(),
            int(fields["cost"].get())
        )
        cursor.callproc("offer_flight", values)
        conn.commit()
        messagebox.showinfo("Success", "Flight offered (if input was valid).")
        print("Inserting values:", values)

        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to offer flight:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Make sure numeric fields are valid numbers.")

def show_flights():
    try:
        cursor.execute("SELECT flightID, routeID, support_airline, support_tail, progress, next_time, cost FROM flight")
        rows = cursor.fetchall()
        result = "\n".join([f"{row[0]} - Route: {row[1]}, Plane: {row[2]} {row[3]}, Next: {row[5]}" for row in rows]) or "No flights found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch flights: {err}")

def show_airplanes():
    try:
        cursor.execute("SELECT airline_id, tail_num FROM airplane")
        rows = cursor.fetchall()
        result = "Available Airplanes:\n" + "\n".join([f"{row[0]} {row[1]}" for row in rows]) or "No airplanes found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch airplanes: {err}")
        
def show_routes():
    try:
        cursor.execute("SELECT routeID FROM route")
        rows = cursor.fetchall()
        result = "Available Routes:\n" + "\n".join([f"{row[0]}" for row in rows]) or "No routes found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch routes: {err}")

def cancel():
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Offer Flight")
root.geometry("400x450")
root.resizable(True, True)

fields = {
    "flightID": tk.StringVar(),
    "routeID": tk.StringVar(),
    "support_airline": tk.StringVar(),
    "support_tail": tk.StringVar(),
    "progress": tk.StringVar(),
    "next_time": tk.StringVar(),
    "cost": tk.StringVar()
}

fields["progress"].set("0")

tk.Label(root, text="Offer Flight", font=("Helvetica", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

for label, var in fields.items():
    row = tk.Frame(frame)
    tk.Label(row, text=f"{label}:", width=15, anchor='w', font=("Helvetica", 11)).pack(side=tk.LEFT)
    entry = tk.Entry(row, textvariable=var, width=25)
    entry.pack(side=tk.LEFT)
    row.pack(pady=4)

help_text = """
Next time format: HH:MM:SS (24-hour format)
Progress: Starting leg sequence (usually 0)
Cost: Flight fare in currency units
"""
tk.Label(root, text=help_text, font=("Helvetica", 9), justify=tk.LEFT).pack()

btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Add Flight", command=offer_flight, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Show Flights", command=show_flights, width=15).pack(side=tk.LEFT, padx=5)
btn_frame.pack(pady=10)

btn_frame2 = tk.Frame(root)
tk.Button(btn_frame2, text="Show Airplanes", command=show_airplanes, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame2, text="Show Routes", command=show_routes, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
btn_frame2.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='w')
result_label.pack(pady=10)

root.mainloop()
