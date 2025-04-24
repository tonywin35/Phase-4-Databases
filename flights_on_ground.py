import tkinter as tk
from tkinter import ttk, messagebox
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

def show_flights_on_ground():
    try:
        cursor.execute("SELECT * FROM flights_on_the_ground")
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
            messagebox.showinfo("Info", "No flights currently on the ground.")
            
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to retrieve flights on ground:\n{err}")

def refresh():
    show_flights_on_ground()

def show_airport_details():
    if not tree.selection():
        messagebox.showinfo("Selection Required", "Please select an airport from the list.")
        return
        
    selected_item = tree.selection()[0]
    airport_id = tree.item(selected_item)['values'][0]
    
    try:
        cursor.execute("""
            SELECT a.airport_id, a.airport_name, a.city, a.state, a.country,
                   COUNT(DISTINCT p.personID) as people_count
            FROM airport a
            LEFT JOIN person p ON a.locationID = p.locationID
            WHERE a.airportID = %s
            GROUP BY a.airportID
        """, (airport_id,))
        
        result = cursor.fetchone()
        
        if result:
            details_text = f"Airport: {result[0]} - {result[1]}\n"
            details_text += f"Location: {result[2]}, {result[3]}, {result[4]}\n"
            details_text += f"People at this airport: {result[5]}\n\n"
            
            # Also get flights at this airport
            cursor.execute("""
                SELECT f.flightID, f.support_airline, f.support_tail, f.next_time
                FROM flight f
                JOIN airplane a ON f.support_airline = a.airline_id AND f.support_tail = a.tail_num
                JOIN airport ap ON a.locationID = ap.locationID
                WHERE ap.airportID = %s AND f.airplane_status = 'on_ground'
            """, (airport_id,))
            
            flights = cursor.fetchall()
            
            if flights:
                details_text += "Flights at this airport:\n"
                for flight in flights:
                    details_text += f" - {flight[0]} ({flight[1]} {flight[2]}), Next: {flight[3]}\n"
            else:
                details_text += "No flights at this airport."
                
            details_label.config(text=details_text)
        else:
            details_label.config(text=f"No details found for airport {airport_id}")
            
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch airport details: {err}")

def exit_program():
    conn.close()
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Flights on the Ground")
root.geometry("1000x600")
root.resizable(True, True)

# Heading
tk.Label(root, text="Flights on the Ground", font=("Helvetica", 16, "bold")).pack(pady=10)

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
tk.Button(btn_frame, text="Airport Details", command=show_airport_details, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Exit", command=exit_program, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

# Load initial data
show_flights_on_ground()

root.protocol("WM_DELETE_WINDOW", exit_program)
root.mainloop()
