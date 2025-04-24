import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import mysql.connector
import sys

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Phase4sucksballs",
        database="flight_tracking"
    )
    cursor = conn.cursor()
    
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    print("Tables found:")
    for table in tables:
        print(" -", table[0])
    db_connected = True
except mysql.connector.Error as err:
    print("Error:", err)
    db_connected = False

def launch_module(module_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.join(current_dir, f"{module_name}.py")
    
    if os.path.exists(module_path):
        try:
            subprocess.Popen([sys.executable, module_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {module_name}:\n{e}")
    else:
        messagebox.showwarning("Module Not Found", f"The module {module_name}.py was not found.")

def exit_program():
    if 'conn' in globals() and conn.is_connected():
        conn.close()
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Simple Airline Management System (SAMS)")
root.geometry("800x600")
root.resizable(True, True)

header_frame = tk.Frame(root, bg="#3a7ebf", padx=10, pady=10)
header_frame.pack(fill=tk.X)

tk.Label(
    header_frame, 
    text="Simple Airline Management System", 
    font=("Helvetica", 20, "bold"),
    bg="#3a7ebf",
    fg="white"
).pack()

status_frame = tk.Frame(root, bg="#f0f0f0", padx=10, pady=5)
status_frame.pack(fill=tk.X)

status_label = tk.Label(
    status_frame,
    text="Database: " + ("✅ Connected" if db_connected else "❌ Not Connected"),
    font=("Helvetica", 10),
    fg="green" if db_connected else "red"
)
status_label.pack(side=tk.RIGHT)

content_frame = tk.Frame(root, padx=20, pady=20)
content_frame.pack(fill=tk.BOTH, expand=True)

sections = {
    "Entity Management": [
        ("Add Airplane", "updated_add_airplane"),
        ("Add Airport", "add_airport"),
        ("Add Person", "add_person"),
        ("Grant/Revoke License", "grant_revoke_license")
    ],
    "Flight Operations": [
        ("Offer Flight", "offer_flight"),
        ("Flight Landing", "flight_landing"),
        ("Flight Takeoff", "updated_flight_takeoff"),
        ("Passengers Board", "passengers_board"),
        ("Passengers Disembark", "passengers_disembark")
    ],
    "Flight Management": [
        ("Assign Pilot", "assign_pilot"),
        ("Recycle Crew", "recycle_crew"),
        ("Retire Flight", "retire_flight"),
        ("Simulation Cycle", "simulation_cycle")
    ],
    "System Views": [
        ("Flights in the Air", "updated_flights_in_air"),
        ("Flights on the Ground", "flights_on_ground"),
        ("People in the Air", "people_in_air"),
        ("People on the Ground", "people_on_ground"),
        ("Route Summary", "route_summary"),
        ("Alternate Airports", "alternate_airports")
    ]
}

row = 0
for section_title, buttons in sections.items():

    tk.Label(
        content_frame,
        text=section_title,
        font=("Helvetica", 14, "bold"),
        anchor="w"
    ).grid(row=row, column=0, columnspan=3, sticky="w", pady=(20, 10))
    row += 1

    col = 0
    for button_text, module_name in buttons:
        tk.Button(
            content_frame,
            text=button_text,
            width=20,
            height=2,
            command=lambda m=module_name: launch_module(m)
        ).grid(row=row, column=col, padx=10, pady=5)
        
        col += 1
        if col >= 3:
            col = 0
            row += 1
    
    if col > 0:
        row += 1

footer_frame = tk.Frame(root, bg="#f0f0f0", padx=10, pady=10)
footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

tk.Button(
    footer_frame,
    text="Exit",
    width=15,
    command=exit_program
).pack(side=tk.RIGHT)

root.protocol("WM_DELETE_WINDOW", exit_program)

if __name__ == "__main__":
    root.mainloop()
