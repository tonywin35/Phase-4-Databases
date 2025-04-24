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

def simulation_cycle():
    try:
        cursor.callproc("simulation_cycle")
        conn.commit()
        messagebox.showinfo("Success", "Simulation cycle executed.")
        print("Simulation cycle processed")
        
        # Try printing the outcome
        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
        
        # Refresh the system status display
        show_system_status()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to run simulation cycle:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Error in simulation cycle.")

def show_system_status():
    try:
        # Count flights by status
        cursor.execute("""
            SELECT airplane_status, COUNT(*) as count
            FROM flight
            GROUP BY airplane_status
        """)
        flight_status = cursor.fetchall()
        
        # Get next event
        cursor.execute("""
            SELECT flightID, airplane_status, next_time, 
                   CASE
                    WHEN airplane_status = 'in_flight' THEN 'Landing'
                    ELSE 'Takeoff'
                   END as next_action
            FROM flight 
            ORDER BY next_time ASC 
            LIMIT 1
        """)
        next_event = cursor.fetchone()
        
        # Count people
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN airplane.locationID IS NOT NULL THEN 1 ELSE 0 END) as in_flights,
                SUM(CASE WHEN airport.locationID IS NOT NULL THEN 1 ELSE 0 END) as in_airports
            FROM person p
            LEFT JOIN airplane ON p.locationID = airplane.locationID
            LEFT JOIN airport ON p.locationID = airport.locationID
        """)
        people_counts = cursor.fetchone()
        
        result = "System Status\n"
        result += "============\n\n"
        
        result += "Flights:\n"
        if flight_status:
            for status in flight_status:
                result += f"  - {status[0]}: {status[1]}\n"
        else:
            result += "  No flights in the system\n"
        
        result += "\nNext Event:\n"
        if next_event:
            result += f"  Flight {next_event[0]} - {next_event[3]} at {next_event[2]}\n"
        else:
            result += "  No events scheduled\n"
        
        result += "\nPeople:\n"
        if people_counts:
            result += f"  - In flights: {people_counts[0] or 0}\n"
            result += f"  - At airports: {people_counts[1] or 0}\n"
        else:
            result += "  No people in the system\n"
        
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch system status: {err}")

def show_next_events():
    try:
        cursor.execute("""
            SELECT f.flightID, f.support_airline, f.support_tail, 
                   f.airplane_status, f.progress, f.next_time,
                   CASE
                    WHEN f.airplane_status = 'in_flight' THEN 'Landing'
                    ELSE 'Takeoff'
                   END as next_action,
                   r.routeID,
                   COUNT(p.personID) as passengers
            FROM flight f
            JOIN route r ON f.routeID = r.routeID
            JOIN airplane a ON f.support_airline = a.airline_id AND f.support_tail = a.tail_num
            LEFT JOIN person p ON a.locationID = p.locationID
            GROUP BY f.flightID
            ORDER BY f.next_time ASC
            LIMIT 5
        """)
        rows = cursor.fetchall()
        
        if rows:
            result = "Upcoming Events (next 5):\n\n"
            for i, row in enumerate(rows):
                result += f"{i+1}. Flight {row[0]} ({row[1]} {row[2]})\n"
                result += f"   Status: {row[3]}, Progress: {row[4]}, Time: {row[5]}\n"
                result += f"   Next action: {row[6]}, Route: {row[7]}, Passengers: {row[8]}\n\n"
        else:
            result = "No events scheduled."
            
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch next events: {err}")

def cancel():
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Simulation Cycle")
root.geometry("500x500")
root.resizable(True, True)

# Heading
tk.Label(root, text="Simulation Cycle", font=("Helvetica", 16, "bold")).pack(pady=10)

# Help text
help_text = """
The simulation cycle executes the next event in the system:
- If a flight is in the air, it will land and passengers will disembark.
- If a flight is on the ground, passengers will board and it will take off.
- If a flight has completed its route, the crew will be recycled.

Click "Next Step" to advance the simulation to the next event.
"""
tk.Label(root, text=help_text, font=("Helvetica", 9), justify=tk.LEFT).pack(padx=20)

# Buttons
btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Next Step", command=simulation_cycle, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Show Next Events", command=show_next_events, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="System Status", command=show_system_status, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

tk.Button(root, text="Cancel", command=cancel, width=15).pack(pady=10)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='nw')
result_label.pack(pady=10, fill=tk.BOTH, expand=True)

# Show initial system status
show_system_status()

root.mainloop()
