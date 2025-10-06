import random, os, json, socket, threading, tkinter as tk
from tkinter import filedialog as fd, messagebox
from datetime import datetime
from imu_win import open_imu_window
from motor_win import open_motor_window
from LC_win import open_lc_window

import socket
import json
import threading

class PiClient:
    def __init__(self, host="10.55.0.1", port=5050, callback=None): # Pi static IP: 192.168.1.2
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.callback = callback  # function to call with each sample

    def start(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        if self.callback:
            self.callback({"status": "PiClient thread started..."})
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)  # timeout so it doesn't hang forever
            self.sock.connect((self.host, self.port))
            self.callback({"status": "Pi Connected."})
            self.sock.sendall(b"SUBSCRIBE\n")

            buffer = ""
            while self.running:
                data = self.sock.recv(4096).decode("utf-8")
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    sample = json.loads(line)
                    if self.callback:
                        self.callback(sample)
        except Exception as e:
            if self.callback:
                self.callback({"status": f"Not connected to Pi: {e}"})
        finally:
            if self.sock:
                self.sock.close()


    def stop(self):
        self.running = False

class GUI:
    FONTCOLOR="#E0E0E0"
    BUTTONCOLOR="#444444"
    WINDOWCOLOR="#121212"
    CONFIG_FILE = "config.json"

    def __init__(self, root):
        self.root=root
        self.canvas=tk.Canvas(root, 
                   width=1280, 
                   height=720, 
                   bg=self.WINDOWCOLOR, 
                   highlightthickness=0) 

        # StringVars
        self.static_motor_direction=tk.StringVar(value="extension") 
        self.dynamic_motor_direction=tk.StringVar(value="extension")
        self.anticipation=tk.StringVar(value="anticipated") 
        self.static_file_name=tk.StringVar()
        self.dynamic_file_name=tk.StringVar()
        self.pulltime_val=tk.StringVar() 
        self.time_window_val=tk.StringVar()
        self.log_time_pre_val=tk.StringVar()
        self.log_time_post_val=tk.StringVar()
        self.pull_accel_val=tk.StringVar()
        self.pull_decel_val=tk.StringVar()
        self.pull_rot_val=tk.StringVar()
        self.pull_speed_val=tk.StringVar()
        self.avg_force=tk.StringVar(value='-') 
        self.max_force=tk.StringVar(value='-')
        self.ang_disp_x=tk.StringVar(value='-')
        self.ang_disp_y=tk.StringVar(value='-')
        self.ang_disp_z=tk.StringVar(value='-')
        self.max_vel_x=tk.StringVar(value='-')
        self.max_vel_y=tk.StringVar(value='-')
        self.max_vel_z=tk.StringVar(value='-')
        self.max_accel_x=tk.StringVar(value='-')
        self.max_accel_y=tk.StringVar(value='-')
        self.max_accel_z=tk.StringVar(value='-')

        # declare dictionaries for storing element configs
        self.rects={} 
        self.lines={} 
        self.texts={}
        self.widgets={}
        self.entries={}
        self.labels={}
        self.imuButtons={}
        self.imuLabels={}
        self.imuTexts={}
        self.motorButtons={}
        self.motorLabels={}
        self.lcButtons={}
        self.lcLabels={}
        self.lcTexts={}

        self.imuWindow=None
        self.imuCanvas=None
        self.motorWindow=None
        self.motorCanvas=None
        self.lcWindow=None
        self.lcCanvas=None
        self.staticWindow=None
        self.staticCanvas=None
        self.dynamicWindow=None
        self.dynamicCanvas=None

        # initialize status colors to be empty, user can then reload connections to check status
        self.imu_color=self.BUTTONCOLOR
        self.motor_color=self.BUTTONCOLOR
        self.lc_color=self.BUTTONCOLOR

        self.dark=True # start program in dark mode

        self.initialize()

    #=========================misc. functions=========================

    def disable_close(self): # disable closing with [x]
        messagebox.showinfo("Notice", "Please use the Exit button to close this window.")
    
    def setup(self):
        self.root.title("NSAT Prototype 3a")
        self.root.geometry("1280x720")
        self.root.resizable(width=False, height=False)
        self.root.configure(bg=self.WINDOWCOLOR)
        self.canvas.pack() # pack canvas onto window
        self.root.protocol("WM_DELETE_WINDOW", self.disable_close)
    
    def exit_function(self):
        # TODO Release all comm ports, send whatever is needed to each device to power down, close windows etc.
        self.root.destroy()

    def create_window(self, title, width, height):
            window=tk.Toplevel()
            window.title(f"{title}")
            window.geometry(f"{width}x{height}")
            window.resizable(width=False, height=False)
            window.configure(bg=self.WINDOWCOLOR)
            canvas=tk.Canvas(window,
                width=width, 
                height=height, 
                bg=self.WINDOWCOLOR, 
                highlightthickness=3)
            
            canvas.pack()
            def disable_close():
                pass

            window.protocol("WM_DELETE_WINDOW", disable_close)

            return window, canvas

    def create_button(self, parent, text, command, width=10, height=1, relief="solid", 
                    bd=1, bg=BUTTONCOLOR, activebackground=WINDOWCOLOR, 
                    activeforeground=FONTCOLOR, font=("Courier", 14)):
        
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            relief=relief,
            bd=bd,
            bg=bg,
            fg=self.FONTCOLOR,
            activebackground=activebackground,
            activeforeground= activeforeground,
            font=font,
            cursor="hand2"
        )

    def create_radiobutton(self, parent, text, variable, value, width=10,
                        bg=WINDOWCOLOR, activebackground=WINDOWCOLOR,
                        activeforeground="white", fg=FONTCOLOR,
                        selectcolor=BUTTONCOLOR, font=("Courier", 14), command=None):

        return tk.Radiobutton(
            parent,
            text=text,
            variable=variable,
            value=value,
            width=width,
            bg=bg,
            activebackground=activebackground,
            activeforeground=activeforeground,
            fg=fg,
            selectcolor=selectcolor,
            font=font,
            cursor="hand2",
            command=command
        )

    def create_entry(self, parent, textvar, width, font=("Courier", 14)):
        return tk.Entry(
                master=parent, 
                textvariable=textvar, 
                width=width, 
                font=font, 
                bg=self.BUTTONCOLOR, 
                fg=self.FONTCOLOR, 
                insertbackground=self.FONTCOLOR, 
                relief="solid", 
                bd=1
            )
    def write_results(self, test):
        if test == "static":
            if self.static_file_name.get(): # if user has entered static_file_name
                with open(f"{self.generate_file_name('static')}.csv", "w") as static_result:
                    static_result.write("example static results")

        elif test == "dynamic":
            if self.dynamic_file_name.get(): # if user has entered dynamic_file_name
                with open(f"{self.generate_file_name('dynamic')}.csv", "w") as dynamic_result:
                    dynamic_result.write("example dynamic results")

    def generate_file_name(self, test_type):
        now = datetime.now()

        # timestamp formatted as: YYYY-MM-DD-HHMMSS
        timestamp = ( 
                    f"{now.year}-{now.month:02}-{now.day:02}-{now.hour:02}"
                    f"{now.minute:02}{now.second:02}"
        )

        if hasattr(self, "folder_path"):
            # need some check to see if user has entered something
            name = ''
            if test_type == "static":
                    # set preset name: YYYY-MM-DD-HHMMSS-<motor_direction>
                    preset_name = f"{timestamp}-{self.static_motor_direction.get()}" 
                    self.static_file_name.set(preset_name)
                    # join root path + name of static result file    
                    name = os.path.join(self.folder_path, self.static_file_name.get())
                    
            elif test_type == "dynamic":
                    # set preset name: YYYY-MM-DD-HHMMSS-<anticipation>-<motor_direction>
                    preset_name = f"{timestamp}-{self.anticipation.get()}-{self.dynamic_motor_direction.get()}" 
                    self.dynamic_file_name.set(preset_name)
                    # join root path + name of dynamic result file
                    name = os.path.join(self.folder_path, self.dynamic_file_name.get()) 
            return name

    def imu_status(self): # imu connection confirmation TODO: implement
        return random.choice([True, False])
    def motor_status(self):# motor connection confirmation TODO: implement
        return random.choice([True, False])
    def lc_status(self):# load cell connection confirmation TODO: implement
        return random.choice([True, False])

    def anticipated(self):
        if (self.dynamicWindow is None or not self.dynamicWindow.winfo_exists()) and (self.staticWindow is None or not self.staticWindow.winfo_exists()): # if staticWindow / dynamicWindow aren't open 
                # configure window
                try:
                    time_window = int(self.time_window_val.get())
                    post_log = int(self.log_time_post_val.get())
                    pre_log = int(self.log_time_pre_val.get())
                except: # TODO: need to catch for non-entered motor controls too
                    messagebox.showerror("Error", "Enter integer values into \n\"Countdown\", \"Log Time Pre\", and \"Log Time Post\".")
                    return
                
                if pre_log > time_window:
                    messagebox.showerror("Error", "\"Log Time Pre\" must be less than \"Countdown\".")
                    return
                

                dynamicWindow, dynamicCanvas = self.create_window("Dynamic Anticipated", 500, 500)

                self.texts["dynamic_header"] = dynamicCanvas.create_text(250, 70, text="Pull In:", font=("Courier", 30, "bold underline"), fill=self.FONTCOLOR)
                self.texts["dynamic_timer"] = dynamicCanvas.create_text(250, 250, font=("Courier", 50, "bold"), fill=self.FONTCOLOR)
                
                def countdown():
                    nonlocal time_window
                    if time_window > 0 and dynamicWindow.winfo_exists(): 
                        dynamicCanvas.itemconfig(self.texts["dynamic_timer"], text=str(time_window))
                        print(time_window)
                        if time_window == pre_log: # start logging data after pre_log seconds
                            self.start_anticipated_log = True #TODO: implement to start reading data
                            print("ran")
                            self.texts["recording"] = dynamicCanvas.create_text(260, 330, text="Recording...", font=("Courier", 20, "bold"), fill=self.FONTCOLOR)
                        time_window -= 1
                        dynamicWindow.after(1000, countdown)
                    else: # after countdown
                        dynamicCanvas.itemconfig(self.texts["dynamic_header"], text="Pull!")
                        post_log_time()

                def post_log_time():
                    nonlocal post_log
                    if post_log > 0 and dynamicWindow.winfo_exists(): 
                        dynamicCanvas.itemconfig(self.texts["dynamic_timer"], text=str(post_log))
                        post_log -= 1
                        dynamicWindow.after(1000, post_log_time)
                    else: # after countdown
                        dynamicWindow.destroy()         

                countdown()
    
    def unanticipated(self):
        count_to_rand=0  # start random pull counter at 0
        post_counter=1   # start counting at 1 after random pull

        if (
            (self.dynamicWindow is None or not self.dynamicWindow.winfo_exists())
            and
            (self.staticWindow is None or not self.staticWindow.winfo_exists())
        ):
            # configure window
            try:
                time_window=int(self.time_window_val.get())
                post_log=int(self.log_time_post_val.get())
                pre_log=int(self.log_time_pre_val.get())
            except ValueError: # TODO: need to catch for non-entered motor controls too
                messagebox.showerror("Error", "Enter integer values into \n\"Time Window\", \"Log Time Pre\", and \"Log Time Post\".")
                return
                    
            if pre_log + post_log > time_window:
                messagebox.showerror("Error", "The sum of \"Log Time Post\" and \"Log Time Pre\" are greater than \"Time Window\".")
                return
                    
            dynamicWindow, dynamicCanvas=self.create_window("Dynamic Unanticipated", 500, 500)
            rand_pulltime=random.randint(0, time_window)
            self.texts["dynamic_timer"]=dynamicCanvas.create_text(250, 250, font=("Courier", 50, "bold"), fill=self.FONTCOLOR)
            self.texts["recording"]=dynamicCanvas.create_text(260, 350, text="Recording...", font=("Courier", 20, "bold"), fill=self.FONTCOLOR)
                
            def post_countup(): # count up to post_log after motor acuates
                nonlocal post_counter
                if post_counter <= post_log:
                    dynamicCanvas.itemconfig(self.texts["dynamic_timer"], text=post_counter)
                    post_counter += 1
                    dynamicWindow.after(1000, post_countup)  
                else:
                    dynamicWindow.destroy()

            def random_count():
                nonlocal count_to_rand
        
                if count_to_rand < rand_pulltime + pre_log:
                    dynamicCanvas.itemconfig(self.texts["dynamic_timer"], text="Relax")
                    count_to_rand += 1
                    dynamicWindow.after(1000, random_count)
                else:
                    post_countup()
            
            random_count()    

    def handle_pi_messages(self, sample):
        if "status" in sample: # status will be in sample data when booting up & when not connected
            # Update a Label on the canvas
            self.canvas.itemconfig(self.texts["pi_status"], text=sample["status"])
        else: # when only sensor data is coming through
            self.latest_sample = sample # Save the latest sample
            self.reload_connections() # Update statuses on the canvas

    #=========================button functions=========================

    def dark_light(self): # change visual mode
        self.dark=not self.dark # toggle boolean 

        if self.dark:  
            self.FONTCOLOR="#E0E0E0"
            self.BUTTONCOLOR="#444444"
            self.WINDOWCOLOR="#121212"
            self.widgets["darkButton"].config(text="⏾")
        else:
            self.FONTCOLOR="black"
            self.BUTTONCOLOR="#ffffff"
            self.WINDOWCOLOR="#eeeeee"
            self.widgets["darkButton"].config(text="☀")

        # update window and canvas
        self.root.configure(bg=self.WINDOWCOLOR)
        self.canvas.configure(bg=self.WINDOWCOLOR)

        # update IMU window's elements
        if self.imuWindow is not None and self.imuWindow.winfo_exists():

            self.imuWindow.configure(bg=self.WINDOWCOLOR)
            self.imuCanvas.configure(bg=self.WINDOWCOLOR)

            for button in self.imuButtons.values():
                button.config(bg=self.WINDOWCOLOR, activebackground=self.BUTTONCOLOR, fg=self.FONTCOLOR, activeforeground=self.FONTCOLOR)
                
            for label in self.imuLabels.values():
                    label.config(fg=self.FONTCOLOR, bg=self.BUTTONCOLOR)

            for text in self.imuTexts.values():
                self.imuCanvas.itemconfig(text, fill=self.FONTCOLOR)

        # update motor window's elements
        if self.motorWindow is not None and self.motorWindow.winfo_exists():
            self.motorWindow.configure(bg=self.WINDOWCOLOR)
            self.motorCanvas.configure(bg=self.WINDOWCOLOR)

            for name, button in self.motorButtons.items():
                if name not in ("accel_entry", "decel_entry", "speed_entry", "rotation_entry"):
                    button.config(bg=self.WINDOWCOLOR, activebackground=self.BUTTONCOLOR, fg=self.FONTCOLOR, activeforeground=self.FONTCOLOR)
                else:
                    button.config(bg=self.WINDOWCOLOR, fg=self.FONTCOLOR, insertbackground=self.FONTCOLOR)

            for label in self.motorLabels.values():
                label.config(fg=self.FONTCOLOR, bg=self.BUTTONCOLOR)

            for text in self.motorTexts.values():
                self.motorCanvas.itemconfig(text, fill=self.FONTCOLOR)
        
        # update load cell window's elements
        if self.lcWindow is not None and self.lcWindow.winfo_exists():
            self.lcWindow.configure(bg=self.WINDOWCOLOR)
            self.lcCanvas.configure(bg=self.WINDOWCOLOR)

            for button in self.lcButtons.values():
                button.config(bg=self.WINDOWCOLOR, activebackground=self.BUTTONCOLOR, fg=self.FONTCOLOR, activeforeground=self.FONTCOLOR)
                
            for label in self.lcLabels.values():
                label.config(fg=self.FONTCOLOR, bg=self.BUTTONCOLOR)

            for text in self.lcTexts.values():
                self.lcCanvas.itemconfig(text, fill=self.FONTCOLOR)

        # update static window's elements
        if self.staticWindow is not None and self.staticWindow.winfo_exists():
            self.staticWindow.configure(bg=self.WINDOWCOLOR)
            self.staticCanvas.configure(bg=self.WINDOWCOLOR, highlightbackground=self.FONTCOLOR)
            self.staticCanvas.itemconfig(self.texts["static_timer"], fill=self.FONTCOLOR)
            self.staticCanvas.itemconfig(self.texts["timer_header"], fill=self.FONTCOLOR)
            try:
                self.staticCanvas.itemconfig(self.texts["recording"], fill=self.FONTCOLOR)
            except:
                pass

        # update buttons, reloadbutton, entries, and radiobuttons need separate updates
        for name, button in self.widgets.items():
            if name == "reloadButton": # reload button should have transparent background
                button.config(bg=self.WINDOWCOLOR, activebackground=self.WINDOWCOLOR, fg=self.FONTCOLOR, activeforeground=self.BUTTONCOLOR)
            elif name.endswith("Entry"):
                button.config(bg=self.BUTTONCOLOR, fg=self.FONTCOLOR, insertbackground=self.FONTCOLOR)
            elif name.endswith("_r"):
                button.config(bg=self.WINDOWCOLOR, activebackground=self.WINDOWCOLOR, activeforeground=self.FONTCOLOR, fg=self.FONTCOLOR, selectcolor=self.BUTTONCOLOR)
            else:
                button.config(bg=self.BUTTONCOLOR, fg=self.FONTCOLOR, activebackground=self.WINDOWCOLOR, activeforeground=self.FONTCOLOR)
        
        # update rectangles
        for name, rect in self.rects.items(): 
            if name in ("imu", "motor", "lc"):
                continue # skip the status rectangles
            self.canvas.itemconfig(rect, fill=self.BUTTONCOLOR)

        # update texts
        for text in self.texts.values():
            self.canvas.itemconfig(text, fill=self.FONTCOLOR)
        
        #update labels
        for name, label in self.labels.items():
            if name == "load_prev":
                label.config(fg=self.FONTCOLOR, bg=self.WINDOWCOLOR)
            else:
                label.config(fg=self.FONTCOLOR, bg=self.BUTTONCOLOR)

        for line in self.lines.values():
            self.canvas.itemconfig(line, fill=self.FONTCOLOR)

    def reload_connections(self): # update each rectangle's fill color depending on connection status
        sample = getattr(self, "latest_sample", None) # sample = self.latest_sample, return none if doesn't exist
        if not sample:
            return  # no data yet

        # IMU check: are accel values non-zero-ish?
        imu_ok = any(abs(sample.get(k, 0)) > 0.001 for k in ["ax", "ay", "az"])
        self.canvas.itemconfig(self.rects["imu"], fill="green" if imu_ok else "red")

        # Load cell check: is Newtons value changing?
        lc_ok = abs(sample.get("Newtons", 0)) > 0.001
        self.canvas.itemconfig(self.rects["lc"], fill="green" if lc_ok else "red")


    def standalone_imu(self): # open IMU window  #TODO create IMU graph, make start button work, read IMU data correctly
        if self.canvas.itemcget(self.rects["imu"], "fill") == "green": # if IMU is connected
            if (self.imuWindow is None or not self.imuWindow.winfo_exists()): # if imu window isn't open
                # unpack + pass current color for its colors
                self.imuWindow, self.imuCanvas, self.imuButtons, self.imuLabels, self.imuTexts = (
                    open_imu_window(self.WINDOWCOLOR, self.BUTTONCOLOR, self.FONTCOLOR)
                 ) 
            else:
                self.imuWindow.lift() 
        else:
            messagebox.showerror("IMU Error", "IMU not connected.")

    def standalone_motor(self):# open motor window, #TODO direct control
        if self.canvas.itemcget(self.rects["motor"], "fill") == "green": # if motor is connected
            if self.motorWindow is None or not self.motorWindow.winfo_exists(): # if motor window isn't open
                # unpack + pass current color for its colors
                self.motorWindow, self.motorCanvas, self.motorButtons, self.motorTexts = ( 
                    open_motor_window(self.WINDOWCOLOR, self.BUTTONCOLOR, self.FONTCOLOR) 
                )
            else:
                self.motorWindow.lift() 
        else:
            messagebox.showerror("Motor Error", "Motor not connected.")

    def standalone_lc(self): # open load cell window    #TODO live readings
        if self.canvas.itemcget(self.rects["lc"], "fill") == "green": # if load cell isn't connected
            if self.lcWindow is None or not self.lcWindow.winfo_exists(): # if lcwindow isn't open
                # unpack + pass current color for its colors
                self.lcWindow, self.lcCanvas, self.lcButtons, self.lcLabels, self.lcTexts = (
                    open_lc_window(self.WINDOWCOLOR, self.BUTTONCOLOR, self.FONTCOLOR)
                )
            else:
                self.lcWindow.lift() 
        else:
            messagebox.showerror("Load Cell Error", "Load cell not connected.")

    def choose_folder(self, choose=True):  # choose root folder
        if choose: # if being called from button, prompt user to choose folder
            self.folder_path = fd.askdirectory(title="Select a Root Folder", initialdir='/') 

            # only save if user actually chose something
            if self.folder_path: 
                with open(self.CONFIG_FILE, "w") as file: # write chosen folder into json
                    json.dump({"folder_path": self.folder_path}, file)

        if not self.folder_path:  # user cancelled
            return

        # truncate path if too long
        if len(self.folder_path) > 31:
            self.formatted_path = self.folder_path[:31] + "..."
        else:
            self.formatted_path = self.folder_path

        if "path" not in self.texts:  # if first time
            self.texts["path"] = self.canvas.create_text(
                800, 81,
                text=self.formatted_path.replace("/", "\\"),
                font=("Courier", 11),
                fill=self.FONTCOLOR,
                anchor="nw"
            )
        else:
            self.canvas.itemconfig(
                self.texts["path"],
                text=self.formatted_path.replace("/", "\\")
            )

        # Bind tooltip to the "path" canvas text
        self.canvas.tag_bind(
            self.texts["path"], "<Enter>",
            lambda e: self.show_tooltip(e, text_type="root_folder")
        )
        self.canvas.tag_bind(self.texts["path"], "<Leave>", self.hide_tooltip)

    def show_prev_folder(self):
        if os.path.exists(self.CONFIG_FILE):
            # if json file has been created, read it and set folder path to be the previous stored path.
            with open(self.CONFIG_FILE, "r") as file:
                try:
                    data = json.load(file)
                    self.folder_path = data.get("folder_path")
                except json.JSONDecodeError:
                    self.folder_path = None
        else:
            self.folder_path = None

        self.choose_folder(choose=False) # run choose_folder but skip choosing (only updates UI)

    def start_static(self): #TODO: implement data output
        time_left_down = 5
        time_left_up = 1

        if hasattr(self, "folder_path"):
            try:
                pulltime = int(self.pulltime_val.get())
            except ValueError:
                messagebox.showerror("Error", "Enter an integer value into \"Pull Time\".")
                return
            if (
                (self.staticWindow is None or not self.staticWindow.winfo_exists())
                and 
                (self.dynamicWindow is None or not self.dynamicWindow.winfo_exists())
                ): # if staticWindow and dynamicWindow isn't open:

                self.staticWindow, self.staticCanvas = self.create_window("Static Test", 500, 500) # create window

                # create text
                self.texts["static_header"] = self.staticCanvas.create_text(250, 70, text="Starting in:", font=("Courier", 30, "bold underline"), fill=self.FONTCOLOR)
                self.texts["static_timer"] = self.staticCanvas.create_text(250, 250, font=("Courier", 50, "bold"), fill=self.FONTCOLOR)

                def countdown_pre(): # countdown from 5, display amt. of time left on screen
                    nonlocal time_left_down
                    if time_left_down > 0 and self.staticWindow.winfo_exists(): 
                        self.staticCanvas.itemconfig(self.texts["static_timer"], text=str(time_left_down))
                        time_left_down -=  1
                        self.staticWindow.after(1000, countdown_pre)
                    else: # after countdown
                        self.staticCanvas.itemconfig(self.texts["static_header"], text="Start Pull:")
                        self.texts["recording"] = self.staticCanvas.create_text(257, 330, text="Recording...", font=("Courier", 20, "bold"), fill=self.FONTCOLOR)
                        countdown_post()

                def countdown_post(): # count up to pulltime, close window
                    nonlocal pulltime
                    if pulltime > 0:
                        self.staticCanvas.itemconfig(self.texts["static_timer"], text=pulltime)
                        pulltime -=  1
                        self.staticWindow.after(1000, countdown_post)
                    else: # after count up
                        self.staticWindow.destroy()

                countdown_pre()

                self.static_file_path = self.generate_file_name("static")
                self.write_results("static") 
        else:
            messagebox.showerror("Error", "Choose root folder before running tests.")
            
    def start_dynamic(self): #TODO: implement data output
        if hasattr(self, "folder_path"):
            # run anticipated test
            if self.anticipation.get() == "anticipated": 
                self.anticipated()

            # run unanticipated test
            elif self.anticipation.get() == "unanticipated":
                self.unanticipated()
        else:
            messagebox.showerror("Error", "Choose root folder before running tests.")

        self.dynamic_file_path = self.generate_file_name("dynamic")
        self.write_results("dynamic") 

    #=========================text/widget related functions=========================

    def canvas_elements(self): # define and place all canvas elements
        # pi related:
        self.texts["pi_status"] = self.canvas.create_text(15, 693, font=("Courier", 14), fill=self.FONTCOLOR, anchor = "w")
        # lines
        self.lines[1] = self.canvas.create_line(10, 150, 1270, 150, fill=self.FONTCOLOR, width=2)
        self.lines[2] = self.canvas.create_line(300, 10, 300, 140, fill=self.FONTCOLOR, width=1)
        self.lines[3] = self.canvas.create_line(780, 10, 780, 140, fill=self.FONTCOLOR, width=1)
        self.lines[4] = self.canvas.create_line(780, 160, 780, 325, fill=self.FONTCOLOR, width=1) 
        self.lines[5] = self.canvas.create_line(10, 335, 1270, 335, fill=self.FONTCOLOR, width=2)
        self.lines[6] = self.canvas.create_line(381, 400, 381, 465, fill=self.FONTCOLOR, width=1)
        self.lines[7] = self.canvas.create_line(780, 345, 780, 655, fill=self.FONTCOLOR, width=1)
        self.lines[8] = self.canvas.create_line(10, 665, 1270, 665, fill = self.FONTCOLOR, width = 2)
        # connection info
        self.texts["connection_info"] = self.canvas.create_text(125, 24, text="Component Status", font=("Courier", 16, "underline"), fill=self.FONTCOLOR)
        self.texts["imu_status"] = self.canvas.create_text(88, 60, text="IMU", font=("Courier", 14), fill=self.FONTCOLOR) 
        self.rects["imu"] = self.canvas.create_rectangle(40, 53, 55, 68, fill=self.imu_color, outline = "black", width=2) # imu_color = red/green depending on connection
        self.texts["motor_status"] = self.canvas.create_text(100, 90, text="Motor", font=("Courier", 14), fill=self.FONTCOLOR) 
        self.rects["motor"] = self.canvas.create_rectangle(40, 83, 55, 98, fill=self.motor_color, outline = "black", width=2) # motor_color = red/green depending on connection
        self.texts["load_cell_status"] = self.canvas.create_text(122, 120, text="Load Cell", font=("Courier", 14), fill=self.FONTCOLOR) 
        self.rects["lc"] = self.canvas.create_rectangle(40, 113, 55, 128, fill=self.lc_color, outline = "black", width=2) # lc_color = red/green depending on connection

        # standalone tests
        self.texts["component_testing"] = self.canvas.create_text(535, 24, text="Component Testing", font=("Courier", 16, "underline"), fill=self.FONTCOLOR)

        # choose directory
        self.texts["choose_directory"] = self.canvas.create_text(1010, 24, text="Choose Directory", font=("Courier", 16, "underline"), fill=self.FONTCOLOR)
        self.rects["path_rect"] = self.canvas.create_rectangle(795, 74, 1140, 103, fill=self.BUTTONCOLOR, width=1)
        self.texts["folder_symbol"] = self.canvas.create_text(1126, 88, text="📁", font=("Courier", 16), fill=self.FONTCOLOR)
        self.labels["load_prev"] = tk.Label(root, text="(Click here to load previous chosen folder)", font=("Courier", 9), fg=self.FONTCOLOR, bg=self.WINDOWCOLOR, cursor="hand2")
        self.labels["load_prev"].place(x=811, y=105)
        # static assessment
        self.texts["static_assessment"] = self.canvas.create_text(20, 165, text="Static Assessment", font=("Courier", 16, "underline"), fill=self.FONTCOLOR, anchor="nw")
        self.texts["pull_time"] = self.canvas.create_text(120, 232, text="Pull time (sec):", font=("Courier", 14), fill=self.FONTCOLOR)

        # static results
        self.texts["static_results"] = self.canvas.create_text(800, 165, text="Static Results", font=("Courier", 16, "underline"), fill=self.FONTCOLOR, anchor="nw")
        self.texts["avg_force"] = self.canvas.create_text(883, 230, text="Avg. Force (N):", font=("Courier", 14), fill=self.FONTCOLOR)
        self.texts["max_force"] = self.canvas.create_text(1130, 230, text="Max Force (N):", font=("Courier", 14), fill=self.FONTCOLOR)
        self.texts["static_log_file"] = self.canvas.create_text(877, 280, text="Log File Name:", font=("Courier", 14), fill=self.FONTCOLOR)
        self.labels["static_log_label"] = tk.Label(root, textvariable=self.static_file_name, font=("Courier", 11), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=34, height=1, anchor="w", padx=3)
        self.labels["static_log_label"].place(x=964, y=270)
        self.texts["static_log_hint"] = self.canvas.create_text(984, 300, text="(Hover over name for full address)", font=("Courier", 10), fill=self.FONTCOLOR, anchor="w")
        self.labels["avg_force"] = tk.Label(root, textvariable=self.avg_force, font=("Courier", 14), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=5, height=1)
        self.labels["avg_force"].place(x=976, y=218)
        self.labels["max_force"] = tk.Label(root, textvariable=self.max_force, font=("Courier", 14), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=5, height=1)
        self.labels["max_force"].place(x=1215, y=218)

        # dynamic assessment
        self.texts["dynamic_assessment"] = self.canvas.create_text(136, 370, text="Dynamic Assessment", font=("Courier", 16, "underline"), fill=self.FONTCOLOR)
        self.texts["time_window"] = self.canvas.create_text(264, 500, text="Countdown (sec):", font=("Courier", 14), fill=self.FONTCOLOR)
        self.texts["log_time_pre"] = self.canvas.create_text(247, 540, text="Log Time Pre (sec):", font=("Courier", 14), fill=self.FONTCOLOR)
        self.texts["log_time_post"] = self.canvas.create_text(242, 580, text="Log Time Post (sec):", font=("Courier", 14), fill=self.FONTCOLOR)
        self.texts["pull_accel"] = self.canvas.create_text(570, 500, text="Pull Accel. (m/sec^2):", font=("Courier", 14), fill=self.FONTCOLOR)
        self.texts["pull_decel"] = self.canvas.create_text(570, 540, text="Pull Decel. (m/sec^2):", font=("Courier", 14), fill=self.FONTCOLOR)
        self.texts["pull_rot"] = self.canvas.create_text(604, 580, text="Pull Rot. (deg):", font=("Courier", 14), fill=self.FONTCOLOR)
        self.texts["pull_speed"] = self.canvas.create_text(598, 620, text="Pull Speed (RPM):", font=("Courier", 14), fill=self.FONTCOLOR)

        # dynamic results
        self.texts["dynamic_results"] = self.canvas.create_text(896, 350, text="Dynamic Results", font=("Courier", 16, "underline"), fill=self.FONTCOLOR)
        self.texts["dynamic_log_file"] = self.canvas.create_text(877, 408, text="Log File Name:", font=("Courier", 14), fill=self.FONTCOLOR)
        self.labels["dynamic_log_label"] = tk.Label(root, textvariable=self.dynamic_file_name, font=("Courier", 11), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=34, height=1, anchor="w", padx=3)
        self.labels["dynamic_log_label"].place(x=964, y=397)
        self.texts["dynamic_log_hint"] = self.canvas.create_text(984, 427, text="(Hover over name for full address)", font=("Courier", 10), fill=self.FONTCOLOR, anchor="w")
        self.texts["ang_disp"] = self.canvas.create_text(916, 500, text="Max Ang. Disp. (deg):", font=("Courier", 14), fill=self.FONTCOLOR)
        self.texts["max_vel"] = self.canvas.create_text(938, 540, text="Max Vel. (m/sec):", font=("Courier", 14), fill=self.FONTCOLOR)
        self.texts["max_accel"] = self.canvas.create_text(916, 580, text="Max Accel. (m/sec^2):", font=("Courier", 14), fill=self.FONTCOLOR)
        self.texts['x'] = self.canvas.create_text(1077, 470, text="X", font=("Courier", 14,), fill=self.FONTCOLOR)
        self.texts['y'] = self.canvas.create_text(1151, 470, text="Y", font=("Courier", 14), fill=self.FONTCOLOR)
        self.texts['z'] = self.canvas.create_text(1227, 470, text="Z", font=("Courier", 14), fill=self.FONTCOLOR)
        self.labels["ang_disp_x"] = tk.Label(root, textvariable=self.ang_disp_x, font=("Courier", 14), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=5, height=1)
        self.labels["ang_disp_x"].place(x=1045, y=487)
        self.labels["ang_disp_y"] = tk.Label(root, textvariable=self.ang_disp_y, font=("Courier", 14), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=5, height=1)
        self.labels["ang_disp_y"].place(x=1045, y=527)
        self.labels["ang_disp_z"] = tk.Label(root, textvariable=self.ang_disp_z, font=("Courier", 14), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=5, height=1)
        self.labels["ang_disp_z"].place(x=1045, y=567)
        self.labels["max_vel_x"] = tk.Label(root, textvariable=self.max_vel_x, font=("Courier", 14), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=5, height=1)
        self.labels["max_vel_x"].place(x=1120, y=487)
        self.labels["max_vel_y"] = tk.Label(root, textvariable=self.max_vel_y, font=("Courier", 14), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=5, height=1)
        self.labels["max_vel_y"].place(x=1120, y=527)
        self.labels["max_vel_z"] = tk.Label(root, textvariable=self.max_vel_z, font=("Courier", 14), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=5, height=1)
        self.labels["max_vel_z"].place(x=1120, y=567)
        self.labels["max_accel_x"] = tk.Label(root, textvariable=self.max_accel_x, font=("Courier", 14), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=5, height=1)
        self.labels["max_accel_x"].place(x=1195, y=487)
        self.labels["max_accel_y"] = tk.Label(root, textvariable=self.max_accel_y, font=("Courier", 14), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=5, height=1)
        self.labels["max_accel_y"].place(x=1195, y=527)
        self.labels["max_accel_z"] = tk.Label(root, textvariable=self.max_accel_z, font=("Courier", 14), fg=self.FONTCOLOR, bg=self.BUTTONCOLOR, bd=1, relief="solid", width=5, height=1)
        self.labels["max_accel_z"].place(x=1195, y=567)
    
    def switch_text(self): # switch between time window or countdown depending on chosen test
        if self.anticipation.get() == "unanticipated": 
            self.canvas.itemconfig(self.texts["time_window"], text="Time Window (sec):")
            self.canvas.coords(self.texts["time_window"], 253, 500)
        elif self.anticipation.get() == "anticipated":
            self.canvas.itemconfig(self.texts["time_window"], text="Countdown (sec):")
            self.canvas.coords(self.texts["time_window"], 264, 500)

    def widget_setup(self):
        # define button names, configs
        self.button_configs = {
        "reloadButton": {"text": "↻", "command": self.reload_connections, "width": 1, "height": 1, "relief": "flat", "bd": 0, "bg": self.WINDOWCOLOR, "activebackground": self.WINDOWCOLOR, "activeforeground": self.BUTTONCOLOR, "font": ("Times New Roman", 20)},
        "standaloneIMUbutton": {"text": "IMU", "command": self.standalone_imu},
        "standaloneMotorButton": {"text": "Motor", "command": self.standalone_motor},
        "standaloneLCButton": {"text": "Load Cell", "command": self.standalone_lc},
        "fileLocationButton": {"text": "Choose Folder", "command": self.choose_folder, "width": 13, "font": ("Courier", 11)},
        "exitButton": {"text": "Exit", "command": self.exit_function, "width": 5, "font": ("Courier", 10)},
        "startStatic": {"text": "Start Static", "command": self.start_static, "width": 14},
        "startDynamic": {"text": "Start Dynamic", "command": self.start_dynamic, "width": 14},
        "darkButton": {"text": "⏾", "command": self.dark_light, "width": 3, "font": ("Courier", 16)},
        }
        # unpack, create buttons
        for name, cfg in self.button_configs.items():
            self.widgets[name] = self.create_button(self.root, **cfg) 

        # define radio button names, configs
        self.radio_configs = {
        "staticExtension_r": {"text": "Extension", "variable": self.static_motor_direction, "value": "extension", "width": 8},
        "staticLeftLateral_r": {"text": "Left Lateral", "variable": self.static_motor_direction, "value": "left_lateral", "width": 11},
        "staticFlexion_r": {"text": "Flexion", "variable": self.static_motor_direction, "value": "flexion", "width": 8},
        "staticRightLateral_r": {"text": "Right Lateral", "variable": self.static_motor_direction, "value": "right_lateral", "width": 12},
        "dynamicExtension_r": {"text": "Extension", "variable": self.dynamic_motor_direction, "value": "extension", "width": 8},
        "dynamicLeftLateral_r": {"text": "Left Lateral", "variable": self.dynamic_motor_direction, "value": "left_lateral", "width": 11},
        "dynamicFlexion_r": {"text": "Flexion", "variable": self.dynamic_motor_direction, "value": "flexion", "width": 8},
        "dynamicRightLateral_r": {"text": "Right Lateral", "variable": self.dynamic_motor_direction, "value": "right_lateral", "width": 12},
        "anticipated_r": {"text": "Anticipated", "variable": self.anticipation, "value": "anticipated", "width": 10, "command": self.switch_text},
        "unanticipated_r": {"text": "Unanticipated", "variable": self.anticipation, "value": "unanticipated", "width": 13, "command": self.switch_text},
        }
        # unpack, create radio buttons
        for name, cfg in self.radio_configs.items():
            self.widgets[name] = self.create_radiobutton(self.root, **cfg)

        # define entry names, configs
        self.entry_configs = {
        "pulltimeEntry": {"textvar": self.pulltime_val, "width": 4},
        "timeWindowEntry": {"textvar": self.time_window_val, "width": 4},
        "logTimePreEntry": {"textvar": self.log_time_pre_val, "width": 4},
        "logTimePostEntry": {"textvar": self.log_time_post_val, "width": 4},
        "pullAccelEntry": {"textvar": self.pull_accel_val, "width": 4},
        "pullDecelEntry": {"textvar": self.pull_decel_val, "width": 4},
        "pullRotEntry": {"textvar": self.pull_rot_val, "width": 4},
        "pullSpeedEntry": {"textvar": self.pull_speed_val, "width": 4},
        }
        # unpack, create entries
        for name, cfg in self.entry_configs.items():
            self.widgets[name] = self.create_entry(self.root, **cfg)

        # bind a left-click and underline to the load previous folder label:
        self.labels["load_prev"].bind("<Button-1>", lambda e: self.show_prev_folder())
        self.labels["load_prev"].bind("<Enter>", lambda e: self.labels["load_prev"].config(font=("Courier", 9, "underline")))
        self.labels["load_prev"].bind("<Leave>", lambda e: self.labels["load_prev"].config(font=("Courier", 9)))
        
        # Bind tooltips to entries
        try:
            self.labels["static_log_label"].bind(
                "<Enter>",
                lambda e: self.show_tooltip(e, text_type = "static_entry")
            )
            self.labels["static_log_label"].bind("<Leave>", self.hide_tooltip)

            self.labels["dynamic_log_label"].bind(
                "<Enter>",
                lambda e: self.show_tooltip(e, text_type = "dynamic_entry")
            )
            self.labels["dynamic_log_label"].bind("<Leave>", self.hide_tooltip)
        except:
            pass

    def place_widgets(self): # place all widgets
        self.widgets["reloadButton"].place(x=260, y=3)
        self.widgets["standaloneIMUbutton"].place(x=325, y=70)
        self.widgets["standaloneMotorButton"].place(x=475, y=70)
        self.widgets["standaloneLCButton"].place(x=625, y=70)
        self.widgets["fileLocationButton"].place(x=1150, y=75)
        self.widgets["exitButton"].place(x=1225, y=8)
        self.widgets["pulltimeEntry"].place(x=215, y=220)
        self.widgets["staticExtension_r"].place(x=310, y=205)
        self.widgets["staticLeftLateral_r"].place(x=460, y=205)
        self.widgets["staticFlexion_r"].place(x=300, y=235)
        self.widgets["staticRightLateral_r"].place(x=460, y=235)
        self.widgets["startStatic"].place(x=30, y=280)
        self.widgets["darkButton"].place(x=1225, y=675)
        self.widgets["anticipated_r"].place(x=20, y=400) 
        self.widgets["unanticipated_r"].place(x=190, y=400)
        self.widgets["dynamicExtension_r"].place(x=400, y=400)
        self.widgets["dynamicLeftLateral_r"].place(x=560, y=400)
        self.widgets["dynamicFlexion_r"].place(x=390, y=430)
        self.widgets["dynamicRightLateral_r"].place(x=560, y=430)
        self.widgets["timeWindowEntry"].place(x=370, y=487)
        self.widgets["logTimePreEntry"].place(x=370, y=527)
        self.widgets["logTimePostEntry"].place(x=370, y=567)
        self.widgets["pullAccelEntry"].place(x=710, y=487)
        self.widgets["pullDecelEntry"].place(x=710, y=527)
        self.widgets["pullRotEntry"].place(x=710, y=567)
        self.widgets["pullSpeedEntry"].place(x=710, y=607)
        self.widgets["startDynamic"].place(x=30, y=610)

    def show_tooltip(self, event, text_type = None, text=None):
        if text is None:
            if text_type == "static_entry":
                # Only show tooltip if folder_path and filename both exist
                if getattr(self, 'folder_path', None) and self.static_file_name.get():
                    text = os.path.join(self.folder_path, self.static_file_name.get()) + ".csv"
                    text = text.replace("/", "\\")  # convert backslashes to forward slashes
                else:
                    return
            elif text_type == "dynamic_entry":
                if getattr(self, 'folder_path', None) and self.dynamic_file_name.get():
                    text = os.path.join(self.folder_path, self.dynamic_file_name.get()) + ".csv"
                    text = text.replace("/", "\\")  # convert backslashes to forward slashes
                else:
                    return
            elif text_type == "root_folder":
                text = self.folder_path.replace("/", "\\")

        # Create tooltip window
        x, y = event.x_root, event.y_root
        tooltip = tk.Toplevel(self.root)
        tooltip.overrideredirect(True)
        tooltip.config(bg="#FFFFE0", bd=1, relief="solid")
        label = tk.Label(
            tooltip,
            text=text,
            bg="#FFFFE0",
            fg="black",
            font=("Courier", 10),
            bd=0,
            padx =5,
            pady=2,
            anchor="e"
        )
        label.pack()
        # Place tooltip so top-right corner is at pointer
        tooltip.update_idletasks()
        tooltip_width = tooltip.winfo_width()
        tooltip.geometry(f"+{x - tooltip_width}+{y}")
        self.tooltip = tooltip  # store reference

    def hide_tooltip(self, event = None):
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()
            del self.tooltip

    def initialize(self):
        self.setup()
        self.canvas_elements()
        self.imu_status()
        self.motor_status()
        self.lc_status()
        self.widget_setup()
        self.place_widgets()
        #=====Pi Client=====
        self.client = PiClient(callback=self.handle_pi_messages)
        self.client.start()

# run GUI
root = tk.Tk()
gui = GUI(root)
root.mainloop()

