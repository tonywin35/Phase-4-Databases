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

def retire_flight():
    try:
        values = (
            fields["flightID"].get(),
        )
        cursor.callproc("retire_flight", values)
        conn.commit()
        messagebox.showinfo("Success", "Flight retired (if input was valid).")
        print("Processing with values:", values)
        
        # Try printing the outcome
        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to retire flight:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Make sure the flight ID is valid.")

def show_completed_flights():
    try:
        cursor.execute("""
            SELECT f.flightID, f.support_airline, f.support_tail, r.routeID, f.progress,
                  COUNT(rp.sequence) as total_legs, 
                  CASE 
                    WHEN COUNT(p.personID) = 0 THEN 'Empty'
                    ELSE 'Has passengers/crew'
                  END as status
            FROM flight f
            JOIN route_path rp ON f.routeID = rp.routeID
            JOIN route r ON f.routeID = r.routeID
            JOIN airplane a ON f.support_airline = a.airline_id AND f.support_tail = a.tail_num
            LEFT JOIN person p ON a.locationID = p.locationID
            WHERE f.airplane_status = 'on_ground'
            GROUP BY f.flightID
            HAVING f.progress >= total_legs
            ORDER BY f.next_time
        """)
        rows = cursor.fetchall()
        result = "Completed Flights (ready for retirement):\n\n"
        result += "\n".join([f"{row[0]} - {row[1]} {row[2]}, Route: {row[3]}, Progress: {row[4]}/{row[5]}, Status: {row[6]}" for row in rows]) or "No completed flights found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch completed flights: {err}")

def show_flight_details():
    flight_id = fields["flightID"].get()
    if not flight_id:
        messagebox.showerror("Error", "Please enter a Flight ID.")
        return
        
    try:
        cursor.execute("""
            SELECT f.flightID, f.support_airline, f.support_tail, f.routeID, 
                   f.airplane_status, f.progress, f.next_time, f.cost,
                   a.airportID, a.airport_name
            FROM flight f
            JOIN airplane ap ON f.support_airline = ap.airline_id AND f.support_tail = ap.tail_num
            JOIN airport a ON ap.locationID = a.locationID
            WHERE f.flightID = %s
        """, (flight_id,))
        
        flight_row = cursor.fetchone()
        
        if not flight_row:
            result_label.config(text=f"Flight {flight_id} not found.")
            return
            
        # Count people on board
        cursor.execute("""
            SELECT COUNT(p.personID) as total,
                   COUNT(pi.personID) as pilots,
                   COUNT(pa.personID) as passengers
            FROM airplane a
            LEFT JOIN person p ON a.locationID = p.locationID
            LEFT JOIN pilot pi ON p.personID = pi.personID
            LEFT JOIN passenger pa ON p.personID = pa.personID
            WHERE a.airline_id = %s AND a.tail_num = %s
        """, (flight_row[1], flight_row[2]))
        
        count_row = cursor.fetchone()
        
        # Count legs in route
        cursor.execute("""
            SELECT COUNT(*) FROM route_path WHERE routeID = %s
        """, (flight_row[3],))
        
        route_legs = cursor.fetchone()[0]
        
        result = f"Flight {flight_row[0]} Details:\n\n"
        result += f"Airline: {flight_row[1]}\n"
        result += f"Tail Number: {flight_row[2]}\n"
        result += f"Route: {flight_row[3]}\n"
        result += f"Status: {flight_row[4]}\n"
        result += f"Progress: {flight_row[5]}/{route_legs} legs\n"
        result += f"Next Time: {flight_row[6]}\n"
        result += f"Cost: ${flight_row[7]}\n"
        result += f"Current Location: {flight_row[8]} ({flight_row[9]})\n\n"
        
        result += f"People on Board: {count_row[0]} total\n"
        result += f"  - Pilots: {count_row[1]}\n"
        result += f"  - Passengers: {count_row[2]}\n\n"
        
        if flight_row[4] == 'on_ground' and flight_row[5] >= route_legs and count_row[0] == 0:
            result += "This flight can be retired."
        else:
            result += "This flight cannot be retired yet."
            
            if flight_row[4] != 'on_ground':
                result += "\n  - Flight must be on the ground."
            
            if flight_row[5] < route_legs:
                result += f"\n  - Flight must complete all legs ({flight_row[5]}/{route_legs})."
            
            if count_row[0] > 0:
                result += "\n  - All passengers and crew must disembark."
        
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch flight details: {err}")

def cancel():
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Retire Flight")
root.geometry("450x400")
root.resizable(True, True)

fields = {
    "flightID": tk.StringVar()
}

# Heading
tk.Label(root, text="Retire Flight", font=("Helvetica", 16, "bold")).pack(pady=10)

# Display each field and its value
frame = tk.Frame(root)
frame.pack(pady=10)

for label, var in fields.items():
    row = tk.Frame(frame)
    tk.Label(row, text=f"{label}:", width=15, anchor='w', font=("Helvetica", 11)).pack(side=tk.LEFT)
    entry = tk.Entry(row, textvariable=var, width=25)
    entry.pack(side=tk.LEFT)
    row.pack(pady=4)

# Add help text
help_text = """
A flight can be retired when:
1. It is on the ground
2. It has completed all legs of its route
3. All passengers and crew have disembarked
"""
tk.Label(root, text=help_text, font=("Helvetica", 9), justify=tk.LEFT).pack()

# Buttons
btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Retire", command=retire_flight, width=10).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Show Completed", command=show_completed_flights, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Flight Details", command=show_flight_details, width=12).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='w')
result_label.pack(pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
