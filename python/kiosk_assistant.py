import tkinter as tk
import subprocess

def run_script(script_name):
    print(f"{script_name} button clicked")
    subprocess.Popen(["python", script_name])

def close_app():
    root.destroy()

# Initialize the main window
root = tk.Tk()
root.geometry("480x320")
root.overrideredirect(True)  # Make the window borderless
root.title("Kiosk Assistant")

# Create a darker gradient background
canvas = tk.Canvas(root, width=480, height=320)
canvas.pack(fill="both", expand=True)

gradient = canvas.create_rectangle(0, 0, 480, 320, fill="#2c2f33", outline="")
canvas.lower(gradient)

# Add "X" button to close the app
close_button = tk.Button(
    root, text="X", command=close_app, bg="#ff5555", fg="#ffffff", relief="flat", width=3
)
close_button.place(x=450, y=0)

# Create buttons with rounded edges and a glass-like look
buttons = [
    ("Light Control", "light_control.py"),
    ("Temperature Control", "temperature_control.py"),
    ("Assistant", "assistant.py"),
    ("Music Player", "music_player.py"),
    ("Settings", "settings.py"),
    ("Exit", "exit.py")
]

# Function to create rounded buttons
def create_rounded_button(parent, text, command, x, y):
    button = tk.Button(
        parent, text=text, command=command,
        height=2, width=12, bg="#ffffff", fg="#000000", relief="flat",
        highlightbackground="#ffffff", highlightthickness=1
    )
    button.place(x=x, y=y)
    button.configure(font=("Arial", 10, "bold"))
    button.bind("<Enter>", lambda e: button.config(bg="#e0e0e0"))
    button.bind("<Leave>", lambda e: button.config(bg="#ffffff"))

# Arrange buttons in two rows (3 buttons per row)
for i, (text, script) in enumerate(buttons):
    row = i // 3
    col = i % 3
    create_rounded_button(
        root, text=text, command=lambda s=script: run_script(s),
        x=20 + col * 150, y=100 + row * 100
    )

# Start the GUI loop
root.mainloop()
