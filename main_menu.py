import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("Flight System - Main Menu")
root.geometry("450x700")

tk.Label(root, text="Select Stored Procedure", font=("Helvetica", 16, "bold")).pack(pady=10)

# === HANDLERS FOR EACH PROCEDURE ===
def launch_add_airplane():
    root.destroy()
    import add_airplane

def launch_add_airport():
    root.destroy()
    import add_airport

def launch_add_person():
    root.destroy()
    import add_person

def launch_grant_or_revoke_license():
    root.destroy()
    import grant_or_revoke_license

def launch_offer_flight():
    root.destroy()
    import offer_flight

def launch_flight_landing():
    root.destroy()
    import flight_landing

def launch_flight_takeoff():
    root.destroy()
    import flight_takeoff

def launch_passengers_board():
    root.destroy()
    import passengers_board

def launch_passengers_disembark():
    root.destroy()
    import passengers_disembark

def launch_assign_pilot():
    root.destroy()
    import assign_pilot

def launch_recycle_crew():
    root.destroy()
    import recycle_crew

def launch_retire_flight():
    root.destroy()
    import retire_flight

def launch_sim_cycle():
    root.destroy()
    import simulation_cycle

# === BUTTONS FOR EACH PROCEDURE ===
button_config = {"width": 30, "font": ("Helvetica", 11)}

tk.Button(root, text="Add Airplane", command=launch_add_airplane, **button_config).pack(pady=3)
tk.Button(root, text="Add Airport", command=launch_add_airport, **button_config).pack(pady=3)
tk.Button(root, text="Add Person", command=launch_add_person, **button_config).pack(pady=3)
tk.Button(root, text="Grant/Revoke Pilot License", command=launch_grant_or_revoke_license, **button_config).pack(pady=3)
tk.Button(root, text="Offer Flight", command=launch_offer_flight, **button_config).pack(pady=3)
tk.Button(root, text="Flight Landing", command=launch_flight_landing, **button_config).pack(pady=3)
tk.Button(root, text="Flight Takeoff", command=launch_flight_takeoff, **button_config).pack(pady=3)
tk.Button(root, text="Passengers Board", command=launch_passengers_board, **button_config).pack(pady=3)
tk.Button(root, text="Passengers Disembark", command=launch_passengers_disembark, **button_config).pack(pady=3)
tk.Button(root, text="Assign Pilot", command=launch_assign_pilot, **button_config).pack(pady=3)
tk.Button(root, text="Recycle Crew", command=launch_recycle_crew, **button_config).pack(pady=3)
tk.Button(root, text="Retire Flight", command=launch_retire_flight, **button_config).pack(pady=3)
tk.Button(root, text="Simulation Cycle", command=launch_sim_cycle, **button_config).pack(pady=3)

# === Quit Button ===
tk.Button(root, text="Quit", width=30, command=root.destroy, font=("Helvetica", 11, "bold")).pack(pady=15)

root.mainloop()
