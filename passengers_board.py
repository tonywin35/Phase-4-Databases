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

def passengers_board():
    try:
        values = (
            fields["flightID"].get(),
        )
        cursor.callproc("passengers_board", values)
        conn.commit()
        messagebox.showinfo("Success", "Passengers boarded (if input was valid).")
        print("Processing with values:", values)

        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to board passengers:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Make sure the flight ID is valid.")

def show_available_flights():
    try:
        cursor.execute("""
            SELECT f.flightID, f.support_airline, f.support_tail, f.next_time, f.cost
            FROM flight f
            WHERE f.airplane_status = 'on_ground'
            ORDER BY f.next_time
        """)
        rows = cursor.fetchall()
        result = "\n".join([f"{row[0]} - {row[1]} {row[2]}, Departure: {row[3]}, Cost: ${row[4]}" for row in rows]) or "No available flights found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch flights: {err}")

def show_potential_passengers():
    flight_id = fields["flightID"].get()
    if not flight_id:
        messagebox.showerror("Error", "Please enter a Flight ID.")
        return
        
    try:

        cursor.execute("""
            SELECT a.airportID, a.airport_name
            FROM flight f
            JOIN airplane ap ON f.support_airline = ap.airline_id AND f.support_tail = ap.tail_num
            JOIN airport a ON ap.locationID = a.locationID
            WHERE f.flightID = %s AND f.airplane_status = 'on_ground'
        """, (flight_id,))
        
        airport_row = cursor.fetchone()
        if not airport_row:
            messagebox.showerror("Error", "Flight not found or not on ground.")
            return
            
        airport_id, airport_name = airport_row

        cursor.execute("""
            SELECT p.personID, p.first_name, p.last_name, pas.funds
            FROM person p
            JOIN passenger pas ON p.personID = pas.personID
            JOIN airport a ON p.locationID = a.locationID
            WHERE a.airportID = %s
        """, (airport_id,))
        
        rows = cursor.fetchall()

        cursor.execute("SELECT cost FROM flight WHERE flightID = %s", (flight_id,))
        cost_row = cursor.fetchone()
        flight_cost = cost_row[0] if cost_row else 0
        
        result = f"Passengers at {airport_id} ({airport_name}):\n"
        result += f"Flight cost: ${flight_cost}\n\n"
        result += "\n".join([f"{row[0]} - {row[1]} {row[2] or ''} (Funds: ${row[3]})" for row in rows]) if rows else "No passengers at this airport."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch passengers: {err}")

def cancel():
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Passengers Board")
root.geometry("400x350")
root.resizable(True, True)

fields = {
    "flightID": tk.StringVar()
}

tk.Label(root, text="Passengers Board", font=("Helvetica", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

for label, var in fields.items():
    row = tk.Frame(frame)
    tk.Label(row, text=f"{label}:", width=15, anchor='w', font=("Helvetica", 11)).pack(side=tk.LEFT)
    entry = tk.Entry(row, textvariable=var, width=25)
    entry.pack(side=tk.LEFT)
    row.pack(pady=4)

btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Board", command=passengers_board, width=10).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Available Flights", command=show_available_flights, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='w')
result_label.pack(pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
