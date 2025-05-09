import tkinter as tk
from tkinter import ttk, messagebox
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
    print("✅ Connected to MySQL! Tables found:")
    for table in tables:
        print(" -", table[0])
except mysql.connector.Error as err:
    print("❌ Error:", err)
    messagebox.showerror("Database Error", f"MySQL Error: {err}")

def show_people_in_air():
    try:
        cursor.execute("SELECT * FROM people_in_the_air")
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
            
        # Insert column names
        tree["columns"] = columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Insert data
        for row in data:
            tree.insert("", "end", values=row)
            
        if not data:
            messagebox.showinfo("Info", "No people currently in the air.")
            
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to retrieve people in air:\n{err}")

def refresh():
    show_people_in_air()

def show_flight_details():
    if not tree.selection():
        messagebox.showinfo("Selection Required", "Please select a row from the list.")
        return
        
    selected_item = tree.selection()[0]
    selected_values = tree.item(selected_item)['values']
    
    # Get departure and arrival airports
    dep_airport = selected_values[0]
    arr_airport = selected_values[1]
    
    # Get flight IDs as comma-separated list
    flight_list = selected_values[4] if len(selected_values) > 4 else ""
    flights = flight_list.split(',') if flight_list else []
    
    if not flights:
        messagebox.showinfo("Info", "No flight information available.")
        return
    
    # Get details for the first flight
    try:
        flight_details_text = "Flight Details:\n\n"
        
        for flight_id in flights:
            cursor.execute("""
                SELECT f.flightID, f.support_airline, f.support_tail, 
                       f.routeID, f.airplane_status, f.progress, f.next_time
                FROM flight f
                WHERE f.flightID = %s
            """, (flight_id,))
            
            flight = cursor.fetchone()
            
            if flight:
                flight_details_text += f"Flight ID: {flight[0]}\n"
                flight_details_text += f"Airline: {flight[1]}, Tail: {flight[2]}\n"
                flight_details_text += f"Route: {flight[3]}\n"
                flight_details_text += f"Status: {flight[4]}, Progress: {flight[5]}\n"
                flight_details_text += f"Next Event: {flight[6]}\n\n"
                
                # Get passenger details
                cursor.execute("""
                    SELECT p.personID, p.first_name, p.last_name,
                          CASE WHEN pi.personID IS NOT NULL THEN 'Pilot' ELSE 'Passenger' END as role
                    FROM person p
                    JOIN airplane a ON p.locationID = a.locationID
                    LEFT JOIN pilot pi ON p.personID = pi.personID
                    LEFT JOIN passenger pa ON p.personID = pa.personID
                    WHERE a.airline_id = %s AND a.tail_num = %s
                """, (flight[1], flight[2]))
                
                people = cursor.fetchall()
                
                if people:
                    flight_details_text += "People on board:\n"
                    for person in people:
                        flight_details_text += f" - {person[0]}: {person[1]} {person[2] or ''} ({person[3]})\n"
                else:
                    flight_details_text += "No people on board this flight.\n"
                
                flight_details_text += "---------------------------\n\n"
        
        details_label.config(text=flight_details_text)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch flight details: {err}")

def exit_program():
    conn.close()
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("People in the Air")
root.geometry("1000x600")
root.resizable(True, True)

# Heading
tk.Label(root, text="People in the Air", font=("Helvetica", 16, "bold")).pack(pady=10)

# Create top frame for table
top_frame = tk.Frame(root)
top_frame.pack(pady=10, fill=tk.BOTH, expand=True)

# Create treeview for data display
tree = ttk.Treeview(top_frame)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add vertical scrollbar
v_scrollbar = ttk.Scrollbar(top_frame, orient="vertical", command=tree.yview)
v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=v_scrollbar.set)

# Add horizontal scrollbar
h_frame = tk.Frame(root)
h_frame.pack(fill=tk.X, expand=False)
h_scrollbar = ttk.Scrollbar(h_frame, orient="horizontal", command=tree.xview)
h_scrollbar.pack(fill=tk.X)
tree.configure(xscrollcommand=h_scrollbar.set)

# Create bottom frame for details
bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=10, fill=tk.X)

details_label = tk.Label(bottom_frame, text="", justify="left", font=("Courier", 10), anchor='w')
details_label.pack(pady=10, fill=tk.X)

# Buttons
btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Refresh", command=refresh, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Exit", command=exit_program, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

# Load initial data
show_people_in_air()

root.protocol("WM_DELETE_WINDOW", exit_program)
root.mainloop()