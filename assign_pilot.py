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

def assign_pilot():
    try:
        values = (
            fields["flightID"].get(),
            fields["personID"].get()
        )
        cursor.callproc("assign_pilot", values)
        conn.commit()
        messagebox.showinfo("Success", "Pilot assigned (if input was valid).")
        print("Processing with values:", values)

        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to assign pilot:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Make sure all fields are valid.")

def show_available_pilots():
    try:
        cursor.execute("""
            SELECT pi.personID, p.first_name, p.last_name, pi.experience,
                  GROUP_CONCAT(l.license_type) as licenses,
                  a.airportID, a.airport_name
            FROM pilot pi
            JOIN person p ON pi.personID = p.personID
            JOIN airport a ON p.locationID = a.locationID
            LEFT JOIN license l ON pi.personID = l.personID
            LEFT JOIN flight_crew fc ON pi.personID = fc.personID
            WHERE fc.personID IS NULL
            GROUP BY pi.personID
        """)
        rows = cursor.fetchall()
        result = "Available Pilots:\n\n"
        result += "\n".join([f"{row[0]} - {row[1]} {row[2] or ''} (Exp: {row[3]}, Licenses: {row[4] or 'None'}, At: {row[5]})" for row in rows]) or "No available pilots found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch pilots: {err}")

def show_flight_crew():
    flight_id = fields["flightID"].get()
    if not flight_id:
        messagebox.showerror("Error", "Please enter a Flight ID.")
        return
        
    try:
        cursor.execute("""
            SELECT p.personID, p.first_name, p.last_name, pi.experience,
                  GROUP_CONCAT(l.license_type) as licenses
            FROM flight_crew fc
            JOIN person p ON fc.personID = p.personID
            JOIN pilot pi ON p.personID = pi.personID
            LEFT JOIN license l ON pi.personID = l.personID
            WHERE fc.flightID = %s
            GROUP BY p.personID
        """, (flight_id,))
        
        rows = cursor.fetchall()

        cursor.execute("""
            SELECT f.support_airline, f.support_tail, a.airplane_type
            FROM flight f
            JOIN airplane a ON f.support_airline = a.airline_id AND f.support_tail = a.tail_num
            WHERE f.flightID = %s
        """, (flight_id,))
        
        flight_row = cursor.fetchone()
        
        if flight_row:
            result = f"Flight {flight_id} ({flight_row[0]} {flight_row[1]}, Type: {flight_row[2]}):\n\n"
            
            if rows:
                result += "Current Flight Crew:\n"
                result += "\n".join([f"{row[0]} - {row[1]} {row[2] or ''} (Exp: {row[3]}, Licenses: {row[4] or 'None'})" for row in rows])
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
root.title("Assign Pilot")
root.geometry("450x350")
root.resizable(True, True)

fields = {
    "flightID": tk.StringVar(),
    "personID": tk.StringVar()
}

tk.Label(root, text="Assign Pilot", font=("Helvetica", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

for label, var in fields.items():
    row = tk.Frame(frame)
    tk.Label(row, text=f"{label}:", width=15, anchor='w', font=("Helvetica", 11)).pack(side=tk.LEFT)
    entry = tk.Entry(row, textvariable=var, width=25)
    entry.pack(side=tk.LEFT)
    row.pack(pady=4)

btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Assign", command=assign_pilot, width=10).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='w')
result_label.pack(pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
