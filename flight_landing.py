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

def flight_landing():
    try:
        values = (
            fields["flightID"].get(),
        )
        cursor.callproc("flight_landing", values)
        conn.commit()
        messagebox.showinfo("Success", "Flight landed (if input was valid).")
        print("Processing with values:", values)

        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to land flight:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Make sure the flight ID is valid.")

def show_flights_in_air():
    try:
        cursor.execute("""
            SELECT flightID, support_airline, support_tail, next_time, airplane_status 
            FROM flight 
            WHERE airplane_status = 'in_flight'
            ORDER BY next_time
        """)
        rows = cursor.fetchall()
        result = "\n".join([f"{row[0]} - {row[1]} {row[2]}, Landing at: {row[3]}" for row in rows]) or "No flights in the air."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch flights: {err}")

def show_flight_status():
    flight_id = fields["flightID"].get()
    if not flight_id:
        messagebox.showerror("Error", "Please enter a Flight ID.")
        return
        
    try:
        cursor.execute("""
            SELECT f.flightID, f.support_airline, f.support_tail, f.airplane_status, f.progress, f.next_time,
                   r.routeID, COUNT(rp.sequence) as total_legs
            FROM flight f
            JOIN route_path rp ON f.routeID = rp.routeID
            JOIN route r ON f.routeID = r.routeID
            WHERE f.flightID = %s
            GROUP BY f.flightID
        """, (flight_id,))
        
        row = cursor.fetchone()
        if row:
            result = f"Flight: {row[0]}\nAirline: {row[1]}\nTail: {row[2]}\nStatus: {row[3]}\nProgress: {row[4]} of {row[7]} legs\nNext time: {row[5]}\nRoute: {row[6]}"

            cursor.execute("""
                SELECT COUNT(p.personID)
                FROM person p
                JOIN airplane a ON p.locationID = a.locationID
                JOIN flight f ON a.airline_id = f.support_airline AND a.tail_num = f.support_tail
                WHERE f.flightID = %s
            """, (flight_id,))
            
            passenger_count = cursor.fetchone()[0]
            result += f"\nPassengers on board: {passenger_count}"
            
            result_label.config(text=result)
        else:
            result_label.config(text=f"Flight {flight_id} not found.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch flight status: {err}")

def cancel():
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Flight Landing")
root.geometry("350x350")
root.resizable(True, True)

fields = {
    "flightID": tk.StringVar()
}

tk.Label(root, text="Flight Landing", font=("Helvetica", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

for label, var in fields.items():
    row = tk.Frame(frame)
    tk.Label(row, text=f"{label}:", width=15, anchor='w', font=("Helvetica", 11)).pack(side=tk.LEFT)
    entry = tk.Entry(row, textvariable=var, width=25)
    entry.pack(side=tk.LEFT)
    row.pack(pady=4)

btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Land Flight", command=flight_landing, width=12).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Show In-Air", command=show_flights_in_air, width=12).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='w')
result_label.pack(pady=10)

root.mainloop()
