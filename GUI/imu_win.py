import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

# start in dark mode
FONTCOLOR = "#E0E0E0" 
BUTTONCOLOR = "#444444"
WINDOWCOLOR = "#121212"

# declare dictionaries for storing configs
imuTexts = {}
imuButtons = {}
imuLabels = {}


def open_imu_window(window_color = WINDOWCOLOR, button_color = BUTTONCOLOR, font_color = FONTCOLOR):
    imuWindow = tk.Toplevel()
    imuWindow.title("IMU Data")
    imuWindow.geometry("720x620")
    imuWindow.resizable(width = False, height = False)
    imuWindow.configure(bg = window_color)

    imuCanvas = tk.Canvas(imuWindow,
                           width = 720, 
                           height = 620, 
                           bg = window_color, 
                           highlightthickness = 0) # create canvas
    imuCanvas.pack() # pack canvas onto window

    # disable closing with [x]
    def disable_close():
        pass
    imuWindow.protocol("WM_DELETE_WINDOW", disable_close)
    
    # ==========imu values==========
    ang_x = tk.StringVar(value = "-")
    ang_y = tk.StringVar(value = "-")
    ang_z = tk.StringVar(value = "-")

    vel_x = tk.StringVar(value = "-")
    vel_y = tk.StringVar(value = "-")
    vel_z = tk.StringVar(value = "-")

    acc_x = tk.StringVar(value = "-")
    acc_y = tk.StringVar(value = "-")
    acc_z = tk.StringVar(value = "-")

    # ==========function definitions=========
    def exitFunction():
        imuWindow.destroy()

    def startFunction():
        pass

    # ==========button definition + placement==========
    imuButtons["imu_exit"] = tk.Button(
    imuWindow,
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
    imuButtons["imu_exit"].place(x = 656, y = 580)

    imuButtons["imu_start"] = tk.Button(
    imuWindow,
    text = "Start",
    command = startFunction,
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
    imuButtons["imu_start"].place(x = 15, y = 580)

    # ==========text==========
    imuTexts["angular_displacement"] = imuCanvas.create_text(215, 80, text = "Angular Displacement (deg):", font = ("Courier", 14), fill = font_color)
    imuTexts["velocity"] = imuCanvas.create_text(270, 120, text = "Velocity (m/sec):", font = ("Courier", 14), fill = font_color)
    imuTexts["acceleration"] = imuCanvas.create_text(237, 160, text = "Acceleration (m/sec^2):", font = ("Courier", 14), fill = font_color)
    imuTexts["x"] = imuCanvas.create_text(460, 50, text = "X", font = ("Courier", 14), fill = font_color)
    imuTexts["y"] = imuCanvas.create_text(534, 50, text = "Y", font = ("Courier", 14), fill = font_color)
    imuTexts["z"] = imuCanvas.create_text(608, 50, text = "Z", font = ("Courier", 14), fill = font_color)

    # ==========label define==========
    imuLabels["ang_x_label"] = tk.Label(imuWindow, textvariable = ang_x, font = ("Courier", 14), fg = font_color, bg = button_color, bd = 1, relief = "solid", width = 5, height = 1) 
    imuLabels["ang_y_label"] = tk.Label(imuWindow, textvariable = ang_y, font = ("Courier", 14), fg = font_color, bg = button_color, bd = 1, relief = "solid", width = 5, height = 1)
    imuLabels["ang_z_label"] = tk.Label(imuWindow, textvariable = ang_z, font = ("Courier", 14), fg = font_color, bg = button_color, bd = 1, relief = "solid", width = 5, height = 1)
    imuLabels["vel_x_label"] = tk.Label(imuWindow, textvariable = vel_x, font = ("Courier", 14), fg = font_color, bg = button_color, bd = 1, relief = "solid", width = 5, height = 1) 
    imuLabels["vel_y_label"] = tk.Label(imuWindow, textvariable = vel_y, font = ("Courier", 14), fg = font_color, bg = button_color, bd = 1, relief = "solid", width = 5, height = 1)
    imuLabels["vel_z_label"] = tk.Label(imuWindow, textvariable = vel_z, font = ("Courier", 14), fg = font_color, bg = button_color, bd = 1, relief = "solid", width = 5, height = 1)
    imuLabels["acc_x_label"] = tk.Label(imuWindow, textvariable = acc_x, font = ("Courier", 14), fg = font_color, bg = button_color, bd = 1, relief = "solid", width = 5, height = 1) 
    imuLabels["acc_y_label"] = tk.Label(imuWindow, textvariable = acc_y, font = ("Courier", 14), fg = font_color, bg = button_color, bd = 1, relief = "solid", width = 5, height = 1)
    imuLabels["acc_z_label"] = tk.Label(imuWindow, textvariable = acc_z, font = ("Courier", 14), fg = font_color, bg = button_color, bd = 1, relief = "solid", width = 5, height = 1)
    
    # ==========label place==========
    imuLabels["ang_x_label"].place(x = 430, y = 67)
    imuLabels["ang_y_label"].place(x = 505, y = 67)
    imuLabels["ang_z_label"].place(x = 580, y = 67)
    imuLabels["vel_x_label"].place(x = 430, y = 107)
    imuLabels["vel_y_label"].place(x = 505, y = 107)
    imuLabels["vel_z_label"].place(x = 580, y = 107)
    imuLabels["acc_x_label"].place(x = 430, y = 147)
    imuLabels["acc_y_label"].place(x = 505, y = 147)
    imuLabels["acc_z_label"].place(x = 580, y = 147)

    #===========rectangle (temp graph)===========
    imuCanvas.create_rectangle(190, 230, 540, 580, fill = button_color, outline = "black", width = 2)
    imuCanvas.create_text(360, 415, text = "graph", font = ("Courier, 20"), fill = font_color)

    return imuWindow, imuCanvas, imuButtons, imuLabels, imuTexts
