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

def add_person():
    try:

        tax_id = fields["taxID"].get() or None
        experience = fields["experience"].get()
        experience = int(experience) if experience else None
        miles = fields["miles"].get()
        miles = int(miles) if miles else None
        funds = fields["funds"].get()
        funds = int(funds) if funds else None
        
        values = (
            fields["personID"].get(),
            fields["first_name"].get(),
            fields["last_name"].get() or None,
            fields["locationID"].get(),
            tax_id,
            experience,
            miles,
            funds
        )
        cursor.callproc("add_person", values)
        conn.commit()
        messagebox.showinfo("Success", "Person added (if input was valid).")
        print("Inserting values:", values)

        for result in cursor.stored_results():
            print("Stored procedure result:", result.fetchall())
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to add person:\n{err}")
    except ValueError:
        messagebox.showerror("Input Error", "Make sure numeric fields are valid numbers.")

def show_people():
    try:
        cursor.execute("""
            SELECT p.personID, p.first_name, p.last_name, 
                   CASE WHEN pilot.personID IS NOT NULL THEN 'Pilot' ELSE 'Passenger' END as role
            FROM person p
            LEFT JOIN pilot ON p.personID = pilot.personID
            LEFT JOIN passenger ON p.personID = passenger.personID
        """)
        rows = cursor.fetchall()
        result = "\n".join([f"{row[0]} - {row[1]} {row[2] or ''} ({row[3]})" for row in rows]) or "No people found."
        result_label.config(text=result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not fetch people: {err}")

def cancel_add():
    root.destroy()

def launch_main_menu():
    root.destroy()
    import main_menu

root = tk.Tk()
root.title("Add Person")
root.geometry("350x400")
root.resizable(True, True)

fields = {
    "personID": tk.StringVar(),
    "first_name": tk.StringVar(),
    "last_name": tk.StringVar(),
    "locationID": tk.StringVar(),
    "taxID": tk.StringVar(),
    "experience": tk.StringVar(),
    "miles": tk.StringVar(),
    "funds": tk.StringVar()
}

tk.Label(root, text="Add Person", font=("Helvetica", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

for label, var in fields.items():
    row = tk.Frame(frame)
    tk.Label(row, text=f"{label}:", width=15, anchor='w', font=("Helvetica", 11)).pack(side=tk.LEFT)
    entry = tk.Entry(row, textvariable=var, width=25)
    entry.pack(side=tk.LEFT)
    row.pack(pady=4)

help_text = """
For Pilot: Fill in taxID and experience
For Passenger: Fill in miles and funds
Last name is optional.
"""
tk.Label(root, text=help_text, font=("Helvetica", 9), justify=tk.LEFT).pack()

btn_frame = tk.Frame(root)
tk.Button(btn_frame, text="Add Person", command=add_person, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Show People", command=show_people, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Return to Main Menu", command=launch_main_menu, width=15).pack(side=tk.LEFT, padx=10)
btn_frame.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), anchor='w')
result_label.pack(pady=10)

root.mainloop()
