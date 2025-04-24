import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Linkshane12!",
    database="flight_tracking"
)
cursor = conn.cursor()

try:
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    print("Connected to MySQL! Tables found:")
    for table in tables:
        print(" -", table[0])
except mysql.connector.Error as err:
    print("Error:", err)
    messagebox.showerror("Database Error", f"MySQL Error: {err}")

def show_people_on_ground():
    try:
        cursor.execute("SELECT * FROM people_on_the_ground")
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        
        for item in tree.get_children():
            tree.delete(item)
            
        tree["columns"] = columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        for row in data:
            tree.insert("", "end", values=row)
            
        if not data:
            messagebox.showinfo("Info", "No people currently on the ground.")
            
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to retrieve people on ground:\n{err}")

def refresh():
    show_people_on_ground()

def show_airport_details():
    if not tree.selection():
        messagebox.showinfo("Selection Required", "Please select an airport from the list.")
        return
        
    selected_item = tree.selection()[0]
    airport_id = tree.item(selected_item)['values'][0]
    
    try:
        cursor.execute("""
            SELECT airport_name, city, state, country
            FROM airport
            WHERE airportID = %s
        """, (airport_id,))
        
        airport = cursor.fetchone()
        
        if not airport:
            messagebox.showinfo("Info", f"No details found for airport {airport_id}.")
            return
            
        cursor.execute("""
            SELECT p.personID, p.first_name, p.last_name,
                  CASE 
                    WHEN pi.personID IS NOT NULL THEN 'Pilot'
                    WHEN pa.personID IS NOT NULL THEN 'Passenger'
                    ELSE 'Unknown'
                  END as role,
                  COALESCE(pi.experience, 0) as experience,
                  COALESCE(pa.miles, 0) as miles,
                  COALESCE(pa.funds, 0) as funds
            FROM person p
            JOIN airport a ON p.locationID = a.locationID
            LEFT JOIN pilot pi ON p.personID = pi.personID
            LEFT JOIN passenger pa ON p.personID = pa.personID
            WHERE a.airportID = %s
        """, (airport_id,))
        
        people = cursor.fetchall()

        cursor.execute("""
            SELECT f.flightID, f.support_airline, f.support_tail, f.next_time
            FROM flight f
            JOIN airplane a ON f.support_airline = a.airline_id AND f.support_tail = a.tail_num
            JOIN airport ap ON a.locationID = ap.locationID
            WHERE ap.airportID = %s AND f.airplane_status = 'on_ground'
            ORDER BY f.next_time
        """, (airport_id,))
        
        flights = cursor.fetchall()
        
        details_text = f"Airport: {airport_id} - {airport[0]}\n"
        details_text += f"Location: {airport[1]}, {airport[2]}, {airport[3]}\n\n"
        
        if people:
            details_text += "People at this airport:\n"
            details_text += "-----------------------\n"
            
            pilots = [p for p in people if p[3] == 'Pilot']
            passengers = [p for p in people if p[3] == 'Passenger']
            
            if pilots:
                details_text += "Pilots:\n"
                for p in pilots:
                    details_text += f" - {p[0]}: {p[1]} {p[2] or ''} (Exp: {p[4]})\n"
                details_text += "\n"
                
            if passengers:
                details_text += "Passengers:\n"
                for p in passengers:
                    details_text += f" - {p[0]}: {p[1]} {p[2] or ''} (Miles: {p[5]}, Funds: ${p[6]})\n"
                details_text += "\n"
        else:
            details_text += "No people at this airport.\n\n"
            
        if flights:
            details_text += "Departing Flights:\n"
            details_text += "-----------------\n"
            for f in flights:
                details_text += f" - {f[0]}: {f[1]} {f[2]}, Departure: {f[3]}\n"
        else:
            details_text += "No departing flights at this airport.\n"
        
        details_label.config(text=details_text)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch airport details: {err}")

def exit_program():
    conn.close()
    root.destroy()

root = tk.Tk()
root.title("People on the Ground")
root.geometry("1000x600")
root.resizable(True, True)

tk.Label(root, text="People on the Ground", font=("Helvetica", 16, "bold")).pack(pady=10)

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

left_frame = tk.Frame(main_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

tree = ttk.Treeview(left_frame)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

v_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=tree.yview)
v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=v_scrollbar.set)

h_frame = tk.Frame(left_frame)
h_frame.pack(fill=tk.X, expand=False, side=tk.BOTTOM)
h_scrollbar = ttk.Scrollbar(h_frame, orient="horizontal", command=tree.xview)
h_scrollbar.pack(fill=tk.X)
tree.configure(xscrollcommand=h_scrollbar.set)

right_frame = tk.Frame(main_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

details_label = tk.Label(right_frame, text="Select an airport to see details", justify="left", font=("Courier", 10), anchor='nw')
details_label.pack(fill=tk.BOTH, expand=True)

btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Refresh", command=refresh, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Exit", command=exit_program, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

show_people_on_ground()

tree.bind('<<TreeviewSelect>>', lambda e: show_airport_details())

root.protocol("WM_DELETE_WINDOW", exit_program)
root.mainloop()
