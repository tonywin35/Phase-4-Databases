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

def recycle_crew():
    try:
        values = (
            fields["flightID"].get(),
        )
        cursor.callproc("recycle_crew", values)
        conn.commit()
        messagebox.showinfo("Success", "Crew recycled (if input was valid).")
        print("Processing with values:", values)
        
        # Try printing the outcome
        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to recycle crew:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Make sure the flight ID is valid.")

def show_completed_flights():
    try:
        cursor.execute("""
            SELECT f.flightID, f.support_airline, f.support_tail, r.routeID, f.progress,
                  COUNT(rp.sequence) as total_legs
            FROM flight f
            JOIN route_path rp ON f.routeID = rp.routeID
            JOIN route r ON f.routeID = r.routeID
            WHERE f.airplane_status = 'on_ground'
            GROUP BY f.flightID
            HAVING f.progress >= total_legs
            ORDER BY f.next_time
        """)
        rows = cursor.fetchall()
        result = "Completed Flights (ready for crew recycling):\n\n"
        result += "\n".join([f"{row[0]} - {row[1]} {row[2]}, Route: {row[3]}, Progress: {row[4]}/{row[5]}" for row in rows]) or "No completed flights found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch completed flights: {err}")

def show_flight_crew():
    flight_id = fields["flightID"].get()
    if not flight_id:
        messagebox.showerror("Error", "Please enter a Flight ID.")
        return
        
    try:
        cursor.execute("""
            SELECT p.personID, p.first_name, p.last_name, pi.experience
            FROM flight_crew fc
            JOIN person p ON fc.personID = p.personID
            JOIN pilot pi ON p.personID = pi.personID
            WHERE fc.flightID = %s
        """, (flight_id,))
        
        rows = cursor.fetchall()
        
        # Get flight details
        cursor.execute("""
            SELECT f.support_airline, f.support_tail, a.airportID, a.airport_name,
                   f.progress, COUNT(rp.sequence) as total_legs
            FROM flight f
            JOIN airplane ap ON f.support_airline = ap.airline_id AND f.support_tail = ap.tail_num
            JOIN airport a ON ap.locationID = a.locationID
            JOIN route_path rp ON f.routeID = rp.routeID
            WHERE f.flightID = %s
            GROUP BY f.flightID
        """, (flight_id,))
        
        flight_row = cursor.fetchone()
        
        if flight_row:
            result = f"Flight {flight_id} ({flight_row[0]} {flight_row[1]}):\n"
            result += f"Currently at: {flight_row[2]} ({flight_row[3]})\n"
            result += f"Progress: {flight_row[4]}/{flight_row[5]} legs\n\n"
            
            if rows:
                result += "Current Flight Crew:\n"
                result += "\n".join([f"{row[0]} - {row[1]} {row[2] or ''} (Exp: {row[3]})" for row in rows])
            else:
                result += "No pilots assigned to this flight."
        else:
            result = f"Flight {flight_id} not found."
        
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch flight crew: {err}")

def cancel():
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Recycle Crew")
root.geometry("450x350")
root.resizable(True, True)

fields = {
    "flightID": tk.StringVar()
}

# Heading
tk.Label(root, text="Recycle Crew", font=("Helvetica", 16, "bold")).pack(pady=10)

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
tk.Button(btn_frame, text="Recycle Crew", command=recycle_crew, width=12).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Show Completed", command=show_completed_flights, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Show Crew", command=show_flight_crew, width=10).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='w')
result_label.pack(pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
