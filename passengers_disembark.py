import tkinter as tk
from tkinter import messagebox
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

def passengers_disembark():
    try:
        values = (
            fields["flightID"].get(),
        )
        cursor.callproc("passengers_disembark", values)
        conn.commit()
        messagebox.showinfo("Success", "Passengers disembarked (if input was valid).")
        print("Processing with values:", values)

        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to disembark passengers:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Make sure the flight ID is valid.")

def show_landed_flights():
    try:
        cursor.execute("""
            SELECT f.flightID, f.support_airline, f.support_tail, 
                   a.airportID, a.airport_name
            FROM flight f
            JOIN airplane ap ON f.support_airline = ap.airline_id AND f.support_tail = ap.tail_num
            JOIN airport a ON ap.locationID = a.locationID
            WHERE f.airplane_status = 'on_ground'
            ORDER BY f.next_time
        """)
        rows = cursor.fetchall()
        result = "\n".join([f"{row[0]} - {row[1]} {row[2]} at {row[3]} ({row[4]})" for row in rows]) or "No landed flights found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch flights: {err}")

def show_passengers_on_flight():
    flight_id = fields["flightID"].get()
    if not flight_id:
        messagebox.showerror("Error", "Please enter a Flight ID.")
        return
        
    try:
        cursor.execute("""
            SELECT p.personID, p.first_name, p.last_name
            FROM person p
            JOIN airplane ap ON p.locationID = ap.locationID
            JOIN flight f ON ap.airline_id = f.support_airline AND ap.tail_num = f.support_tail
            WHERE f.flightID = %s
        """, (flight_id,))
        
        rows = cursor.fetchall()
        
        if rows:
            result = f"Passengers on flight {flight_id}:\n\n"
            result += "\n".join([f"{row[0]} - {row[1]} {row[2] or ''}" for row in rows])
        else:
            result = f"No passengers found on flight {flight_id}."
        
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch passengers: {err}")

def cancel():
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Passengers Disembark")
root.geometry("400x350")
root.resizable(True, True)

fields = {
    "flightID": tk.StringVar()
}

tk.Label(root, text="Passengers Disembark", font=("Helvetica", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

for label, var in fields.items():
    row = tk.Frame(frame)
    tk.Label(row, text=f"{label}:", width=15, anchor='w', font=("Helvetica", 11)).pack(side=tk.LEFT)
    entry = tk.Entry(row, textvariable=var, width=25)
    entry.pack(side=tk.LEFT)
    row.pack(pady=4)

btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Disembark", command=passengers_disembark, width=10).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='w')
result_label.pack(pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
