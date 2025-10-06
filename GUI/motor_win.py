import tkinter as tk
from tkinter import messagebox

# start in dark mode
FONTCOLOR = "#E0E0E0" 
BUTTONCOLOR = "#444444"
WINDOWCOLOR = "#121212"

# declare dictionaries for storing configs
motorTexts = {}
motorButtons = {}

# user's written values
# TODO: allow for actual control
accel_value = None
decel_value = None
speed_value = None
rot_value = None

def open_motor_window(window_color = WINDOWCOLOR, button_color = BUTTONCOLOR, font_color = FONTCOLOR): 
    motorWindow = tk.Toplevel()
    motorWindow.title("Motor Control")
    motorWindow.geometry("250x300")
    motorWindow.resizable(width = False, height = False)
    motorWindow.configure(bg = window_color)

    motorCanvas = tk.Canvas(motorWindow,
                           width = 260, 
                           height = 300, 
                           bg = window_color, 
                           highlightthickness = 0) # create canvas
    motorCanvas.pack() # pack canvas onto window

    # disable closing with [x]
    def disable_close():
        pass
    motorWindow.protocol("WM_DELETE_WINDOW", disable_close)

    # ==========function definitions=========
    def exitFunction():
        motorWindow.destroy()
        # TODO: shuts down the motor

    #TODO: make clockwise/counterclockwise work
    def clockwise():
        pass

    def countClockwise():
        pass 

    # ==========button/entry definition + placement==========
    motorButtons["motor_exit"] = tk.Button(
    motorWindow,
    text = "Exit",
    command = exitFunction,
    width = 5,
    height = 1,
    relief = "solid",
    state = "normal",
    bg = button_color,
    bd = 1,
    fg = font_color,
    activebackground = button_color,
    activeforeground = font_color,
    font = ("Courier", 10),
    cursor = "hand2"
    )
    motorButtons["motor_exit"].place(x = 192, y = 10)

    motorButtons["clockwise"] = tk.Button(
    motorWindow,
    text = "Move CW",
    command = clockwise,
    width = 9,
    height = 1,
    relief = "solid",
    state = "normal",
    bg = button_color,
    bd = 1,
    fg = font_color,
    activebackground = button_color,
    activeforeground = font_color,
    font = ("Courier", 11),
    cursor = "hand2"
    )
    motorButtons["clockwise"].place(x = 150, y = 260)

    motorButtons["count_clockwise"] = tk.Button(
    motorWindow,
    text = "Move CCW",
    command = countClockwise,
    width = 9,
    height = 1,
    relief = "solid",
    state = "normal",
    bg = button_color,
    bd = 1,
    fg = font_color,
    activebackground = button_color,
    activeforeground = font_color,
    font = ("Courier", 11),
    cursor = "hand2"
    )
    motorButtons["count_clockwise"].place(x = 10, y = 260)

    motorButtons["accel_entry"] = tk.Entry(
        master = motorWindow,        # or your Toplevel window
        textvariable = accel_value, # binds the StringVar
        width = 4,   
        fon = ("Courier", 14),
        bg = button_color,
        fg = font_color,
        insertbackground = font_color,  # cursor color for dark mode
        relief = "solid",
        bd = 1
    )
    motorButtons["accel_entry"].place(x = 192, y = 60)

    motorButtons["decel_entry"] = tk.Entry(
        master = motorWindow,        # or your Toplevel window
        textvariable = decel_value, # binds the StringVar
        width = 4,   
        fon = ("Courier", 14),
        bg = button_color,
        fg = font_color,
        insertbackground = font_color,  # cursor color for dark mode
        relief = "solid",
        bd = 1
    )
    motorButtons["decel_entry"].place(x = 192, y = 100)

    motorButtons["speed_entry"] = tk.Entry(
        master = motorWindow,        # or your Toplevel window
        textvariable = speed_value, # binds the StringVar
        width = 4,   
        fon = ("Courier", 14),
        bg = button_color,
        fg = font_color,
        insertbackground = font_color,  # cursor color for dark mode
        relief = "solid",
        bd = 1
    )
    motorButtons["speed_entry"].place(x = 192, y = 140)

    motorButtons["rotation_entry"] = tk.Entry(
        master = motorWindow,        # or your Toplevel window
        textvariable = rot_value, # binds the StringVar
        width = 4,   
        fon = ("Courier", 14),
        bg = button_color,
        fg = font_color,
        insertbackground = font_color,  # cursor color for dark mode
        relief = "solid",
        bd = 1
    )
    motorButtons["rotation_entry"].place(x = 192, y = 180)

    # ==========text==========
    motorTexts["acceleration"] = motorCanvas.create_text(100, 73, text = "Accel. (m/sec^2):", font = ("Courier", 12), fill = font_color)
    motorTexts["deceleration"] = motorCanvas.create_text(100, 113, text = "Decel. (m/sec^2):", font = ("Courier", 12), fill = font_color)
    motorTexts["speed"] = motorCanvas.create_text(125, 153, text = "Speed (RPM):", font = ("Courier", 12), fill = font_color)
    motorTexts["rotation"] = motorCanvas.create_text(131, 193, text = "Rot. (deg):", font = ("Courier", 12), fill = font_color)



    




    return motorWindow, motorCanvas, motorButtons, motorTexts
