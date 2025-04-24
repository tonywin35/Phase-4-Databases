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
    print("Connected to MySQL Tables found:")
    for table in tables:
        print(" -", table[0])
except mysql.connector.Error as err:
    print("Error:", err)
    messagebox.showerror("Database Error", f"MySQL Error: {err}")

def show_route_summary():
    try:
        cursor.execute("SELECT * FROM route_summary")
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
            messagebox.showinfo("Info", "No routes found in the system.")
            
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to retrieve route summary:\n{err}")

def refresh():
    show_route_summary()

def show_route_details():
    if not tree.selection():
        messagebox.showinfo("Selection Required", "Please select a route from the list.")
        return
        
    selected_item = tree.selection()[0]
    route_id = tree.item(selected_item)['values'][0]
    
    try:

        cursor.execute("""
            SELECT rp.sequence, l.legID, l.departure, l.arrival, l.distance
            FROM route_path rp
            JOIN leg l ON rp.legID = l.legID
            WHERE rp.routeID = %s
            ORDER BY rp.sequence
        """, (route_id,))
        
        legs = cursor.fetchall()

        cursor.execute("""
            SELECT f.flightID, f.support_airline, f.support_tail, 
                   f.airplane_status, f.progress, f.next_time
            FROM flight f
            WHERE f.routeID = %s
        """, (route_id,))
        
        flights = cursor.fetchall()

        details_text = f"Route: {route_id}\n\n"
        
        if legs:
            details_text += "Legs:\n"
            details_text += "-----\n"
            total_distance = 0
            
            for leg in legs:
                details_text += f"Leg #{leg[0]}: {leg[1]} - {leg[2]} → {leg[3]} ({leg[4]} miles)\n"
                total_distance += leg[4]
                
            details_text += f"\nTotal Distance: {total_distance} miles\n\n"
        else:
            details_text += "No legs found for this route.\n\n"
            
        if flights:
            details_text += "Flights using this route:\n"
            details_text += "------------------------\n"
            for f in flights:
                details_text += f"Flight {f[0]}: {f[1]} {f[2]}\n"
                details_text += f"  Status: {f[3]}, Progress: {f[4]}, Next Time: {f[5]}\n\n"
        else:
            details_text += "No flights currently using this route.\n"
        
        details_label.config(text=details_text)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch route details: {err}")

def exit_program():
    conn.close()
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Route Summary")
root.geometry("1000x600")
root.resizable(True, True)

tk.Label(root, text="Route Summary", font=("Helvetica", 16, "bold")).pack(pady=10)

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

details_label = tk.Label(right_frame, text="Select a route to see details", justify="left", font=("Courier", 10), anchor='nw')
details_label.pack(fill=tk.BOTH, expand=True)

btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Refresh", command=refresh, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Route Details", command=show_route_details, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Exit", command=exit_program, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

show_route_summary()

tree.bind('<<TreeviewSelect>>', lambda e: show_route_details())

root.protocol("WM_DELETE_WINDOW", exit_program)
root.mainloop()
