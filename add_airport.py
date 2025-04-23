import tkinter as tk
from tkinter import messagebox
import mysql.connector

def run_add_airport():
    def add_airport():
        try:
            # Gather and validate inputs
            values = (
                fields["airportID"].get().strip().upper(),
                fields["airport_name"].get().strip(),
                fields["city"].get().strip(),
                fields["state"].get().strip(),
                fields["country"].get().strip().upper(),
                fields["locationID"].get().strip()
            )

            if len(values[0]) != 3 or len(values[4]) != 3:
                raise ValueError("AirportID and Country must be 3 characters.")

            cursor.callproc("add_airport", values)
            conn.commit()
            messagebox.showinfo("Success", " Airport added successfully (if input was valid).")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f" MySQL error:\n{err}")
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))

    def cancel_add():
        conn.close()
        root.destroy()

    # MySQL connection
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Linkshane12!",
        database="flight_tracking"
    )
    cursor = conn.cursor()

    root = tk.Tk()
    root.title("Add Airport")
    root.geometry("400x450")

    tk.Label(root, text="Add Airport", font=("Helvetica", 16, "bold")).pack(pady=10)

    frame = tk.Frame(root)
    frame.pack(pady=10)

    # Field setup
    fields = {
        "airportID": tk.StringVar(),
        "airport_name": tk.StringVar(),
        "city": tk.StringVar(),
        "state": tk.StringVar(),
        "country": tk.StringVar(),
        "locationID": tk.StringVar()
    }

    for label, var in fields.items():
        row = tk.Frame(frame)
        tk.Label(row, text=f"{label}:", width=15, anchor='w', font=("Helvetica", 11)).pack(side=tk.LEFT)
        tk.Entry(row, textvariable=var, width=30).pack(side=tk.LEFT)
        row.pack(pady=5)

    # Buttons
    btn_frame = tk.Frame(root)
    tk.Button(btn_frame, text="Add Airport", command=add_airport, width=15).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Cancel", command=cancel_add, width=15).pack(side=tk.LEFT, padx=10)
    btn_frame.pack(pady=20)

    root.mainloop()

# Run when imported
run_add_airport()
