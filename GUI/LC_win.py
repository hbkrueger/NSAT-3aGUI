import tkinter as tk

# start in dark mode
FONTCOLOR = "#E0E0E0" 
BUTTONCOLOR = "#444444"
WINDOWCOLOR = "#121212"

# declare dictionaries for storing configs
lcTexts = {}
lcButtons = {}
lcLabels = {}

def open_lc_window(window_color = WINDOWCOLOR, button_color = BUTTONCOLOR, font_color = FONTCOLOR): 
    lcWindow = tk.Toplevel()
    lcWindow.title("Load Cell Control")
    lcWindow.geometry("300x200")
    lcWindow.resizable(width = False, height = False)
    lcWindow.configure(bg = window_color)
    
    lcCanvas = tk.Canvas(lcWindow,
                           width = 300, 
                           height = 200, 
                           bg = window_color, 
                           highlightthickness = 0) # create canvas
    lcCanvas.pack() # pack canvas onto window

    # disable closing with [x]
    def disable_close():
        pass  
    lcWindow.protocol("WM_DELETE_WINDOW", disable_close)

    # TODO: load cell value
    force_val = tk.StringVar(value = "-")

    # ==========function definitions=========
    def exitFunction():
        lcWindow.destroy()

    def startFunction():
        pass
    
    # ==========button/entry definition + placement==========   
    lcButtons["lc_exit"] = tk.Button(
    lcWindow,
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
    lcButtons["lc_exit"].place(x = 242, y = 165)

    lcButtons["lc_start"] = tk.Button(
    lcWindow,
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

    lcButtons["lc_start"].place(x = 10, y = 165)


    # ==========text==========
    lcTexts["force"] = lcCanvas.create_text(116, 83, text = "Force (N):", font = ("Courier", 14), fill = font_color)

    # ==========label define + place==========
    lcLabels["newtons"] = tk.Label(lcWindow, textvariable = force_val, font = ("Courier", 14), fg = font_color, bg = button_color, bd = 1, relief = "solid", width = 5, height = 1) 
    lcLabels["newtons"].place(x = 186, y = 70)
    return lcWindow, lcCanvas, lcButtons, lcLabels, lcTexts
