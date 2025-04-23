import tkinter as tk
from tkinter import messagebox
import mysql.connector

def run_simulation_cycle():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Linkshane12!",
            database="flight_tracking"
        )
        cursor = conn.cursor()

        # Call the procedure
        cursor.callproc("simulation_cycle")
        conn.commit()

        messagebox.showinfo("Simulation Complete", "✅ Simulation cycle executed successfully.")
        print("Simulation cycle executed.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"❌ Failed to run simulation cycle:\n{err}")
        print("Error running simulation cycle:", err)
    finally:
        cursor.close()
        conn.close()

def run_gui():
    root = tk.Tk()
    root.title("Simulation Cycle")
    root.geometry("300x200")

    tk.Label(root, text="Run Simulation Cycle", font=("Helvetica", 14, "bold")).pack(pady=20)
    tk.Button(root, text="Run", command=run_simulation_cycle, width=20).pack(pady=10)
    tk.Button(root, text="Back to Menu", command=root.destroy, width=20).pack(pady=5)

    root.mainloop()

# Automatically run when imported
run_gui()
