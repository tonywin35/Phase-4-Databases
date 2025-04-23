import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="!",
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

def show_alternate_airports():
    try:
        cursor.execute("SELECT * FROM alternative_airports")
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
            messagebox.showinfo("Info", "No alternate airports found in the system.")
            
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to retrieve alternate airports:\n{err}")

def refresh():
    show_alternate_airports()

def show_city_details():
    if not tree.selection():
        messagebox.showinfo("Selection Required", "Please select a city from the list.")
        return
        
    selected_item = tree.selection()[0]
    values = tree.item(selected_item)['values']
    
    city = values[0]
    state = values[1]
    country = values[2]
    
    try:
        # Get all airports in this city
        cursor.execute("""
            SELECT a.airportID, a.airport_name, a.locationID,
                   COUNT(DISTINCT f.flightID) as num_flights,
                   COUNT(DISTINCT p.personID) as num_people
            FROM airport a
            LEFT JOIN airplane ap ON a.locationID = ap.locationID
            LEFT JOIN flight f ON ap.airline_id = f.support_airline AND ap.tail_num = f.support_tail
            LEFT JOIN person p ON a.locationID = p.locationID
            WHERE a.city = %s AND a.state = %s AND a.country = %s
            GROUP BY a.airportID
        """, (city, state, country))
        
        airports = cursor.fetchall()
        
        if not airports:
            messagebox.showinfo("Info", f"No airports found in {city}, {state}, {country}.")
            return
            
        # Prepare details text
        details_text = f"City: {city}, {state}, {country}\n\n"
        details_text += "Airports in this city:\n"
        details_text += "---------------------\n\n"
        
        for airport in airports:
            details_text += f"Airport ID: {airport[0]}\n"
            details_text += f"Name: {airport[1]}\n"
            details_text += f"Location ID: {airport[2]}\n"
            details_text += f"Current Flights: {airport[3]}\n"
            details_text += f"People at Airport: {airport[4]}\n\n"
            
            # Get flights at this airport
            cursor.execute("""
                SELECT f.flightID, f.support_airline, f.support_tail, 
                       f.airplane_status, f.next_time
                FROM flight f
                JOIN airplane ap ON f.support_airline = ap.airline_id AND f.support_tail = ap.tail_num
                JOIN airport a ON ap.locationID = a.locationID
                WHERE a.airportID = %s
            """, (airport[0],))
            
            flights = cursor.fetchall()
            
            if flights:
                details_text += "Current Flights:\n"
                for flight in flights:
                    details_text += f" - {flight[0]} ({flight[1]} {flight[2]}): {flight[3]}, Next: {flight[4]}\n"
                details_text += "\n"
            else:
                details_text += "No flights currently at this airport.\n\n"
        
        details_label.config(text=details_text)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch city details: {err}")

def exit_program():
    conn.close()
    root.destroy()

root = tk.Tk()
root.title("Alternate Airports")
root.geometry("1000x600")
root.resizable(True, True)

# Heading
tk.Label(root, text="Alternate Airports", font=("Helvetica", 16, "bold")).pack(pady=10)

# Split into left and right panels
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Create left frame for table
left_frame = tk.Frame(main_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create treeview for data display
tree = ttk.Treeview(left_frame)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add vertical scrollbar
v_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=tree.yview)
v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=v_scrollbar.set)

# Add horizontal scrollbar
h_frame = tk.Frame(left_frame)
h_frame.pack(fill=tk.X, expand=False, side=tk.BOTTOM)
h_scrollbar = ttk.Scrollbar(h_frame, orient="horizontal", command=tree.xview)
h_scrollbar.pack(fill=tk.X)
tree.configure(xscrollcommand=h_scrollbar.set)

# Create right frame for details
right_frame = tk.Frame(main_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

details_label = tk.Label(right_frame, text="Select a city to see alternate airports", justify="left", font=("Courier", 10), anchor='nw')
details_label.pack(fill=tk.BOTH, expand=True)

# Buttons
btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Refresh", command=refresh, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="City Details", command=show_city_details, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Exit", command=exit_program, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

# Load initial data
show_alternate_airports()

# Bind selection event
tree.bind('<<TreeviewSelect>>', lambda e: show_city_details())

root.protocol("WM_DELETE_WINDOW", exit_program)
root.mainloop()
