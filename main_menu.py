import tkinter as tk
from tkinter import messagebox

def launch_add_airplane():
    root.destroy()
    import GUI  # This would be your existing GUI refactored into a module

def launch_add_airport():
    root.destroy()
    # import add_airport_gui

def launch_add_person():
    root.destroy()
    # import add_person_gui

root = tk.Tk()
root.title("Flight System - Main Menu")
root.geometry("400x400")

tk.Label(root, text="Select Stored Procedure", font=("Helvetica", 16, "bold")).pack(pady=20)

# Add one button per procedure
tk.Button(root, text="Add Airplane", width=25, command=launch_add_airplane).pack(pady=5)
tk.Button(root, text="Add Airport", width=25, command=launch_add_airport).pack(pady=5)
tk.Button(root, text="Add Person", width=25, command=launch_add_person).pack(pady=5)
tk.Button(root, text="Quit", width=25, command=root.destroy).pack(pady=20)

root.mainloop()
