from datetime import datetime
from enum import Enum
from unittest import defaultTestLoader

from pyparsing import Regex
from arduino import read_line, coordinateColumns
from PIL import ImageTk, Image
import threading
import time
import obj_files_handler
import geometry
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from tkinter.filedialog import asksaveasfile
import pandas as pd
import serial
from pathlib import Path
import customtkinter
import serial.tools.list_ports



class DefaultOptionValue(Enum):
    PORT = "Choose COM port"
    BAUDRATE = " Choose baudrate "


class GUI(tk.Tk):

    BACKGROUND_COLOR = '#9F79EE'
    CANVAS_WIDTH = 811
    CANVAS_HEIGHT = 560
    OBJECT_POSITION_X = 400
    OBJECT_POSITION_Y = 280
    CANVAS_COLOR = 'white'
    COMMON_X = 0.97  # Many graphical elements share the same relative X position
    MOVING_STEP = 10

    ANIMATION_STARTED = False


    ARDUINO = None
    ARDUINO_COORDINATES = None
    ARDUINO_READING_THREAD = None

    # Arduino parameters
    ARDUINO_BAUDRATE_OPTIONS = ["9600", "19200", "38400", "57600", "115200"]
    ARDUINO_BAUDRATE_VALUE = None

    ARDUINO_PORT_OPTIONS = serial.tools.list_ports.comports()
    ARDUINO_PORT_VALUE = None

    DATA_FRAME_PARAMETERS = pd.DataFrame(columns=coordinateColumns)

    gxValue = None
    gyValue = None
    gzValue = None
    axValue = None
    ayValue = None
    azValue = None
    mxValue = None
    myValue = None
    mzValue = None
    hValue = None
    tValue = None
    bvValue = None
    faValue = None
    fbValue = None
    fcValue = None
    fdValue = None

    OFFSET_X = 7.5
    OFFSET_Y = 0
    OFFSET_Z = 0

    def __init__(self, title='Drone Movement', min_size=(1165, 680)):
        super().__init__()

        self.file_exists = False  # A flag for whether the file has been loaded or not
        self.changed = True  # A flag used to only redraw the object when a change occured
        self._geometry_handler = geometry.GEOMETRY(
            self.CANVAS_WIDTH, self.CANVAS_HEIGHT, self.OBJECT_POSITION_X, self.OBJECT_POSITION_Y)
        self._initialise_window(title, min_size)
        self._create_widgets()

    def _set_coordinates(self):
        count = 0

        while True:
            if (self.ANIMATION_STARTED == False):
                time.sleep(1)
                continue

            self.ARDUINO_COORDINATES = read_line(self.ARDUINO)
            count += 1

            if ("Gx" in self.ARDUINO_COORDINATES):
                self.gxValue.set(self.ARDUINO_COORDINATES["Gx"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Gx"] = self.ARDUINO_COORDINATES["Gx"]

            if ("Gy" in self.ARDUINO_COORDINATES):
                self.gyValue.set(self.ARDUINO_COORDINATES["Gy"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Gy"] = self.ARDUINO_COORDINATES["Gy"]

            if ("Gz" in self.ARDUINO_COORDINATES):
                self.gzValue.set(self.ARDUINO_COORDINATES["Gz"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Gz"] = self.ARDUINO_COORDINATES["Gz"]

            if ("Ax" in self.ARDUINO_COORDINATES):
                self.axValue.set(self.ARDUINO_COORDINATES["Ax"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Ax"] = self.ARDUINO_COORDINATES["Ax"]

            if ("Ay" in self.ARDUINO_COORDINATES):
                self.ayValue.set(self.ARDUINO_COORDINATES["Ay"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Ay"] = self.ARDUINO_COORDINATES["Ay"]

            if ("Az" in self.ARDUINO_COORDINATES):
                self.azValue.set(self.ARDUINO_COORDINATES["Az"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Az"] = self.ARDUINO_COORDINATES["Az"]

            if ("Mx" in self.ARDUINO_COORDINATES):
                self.mxValue.set(self.ARDUINO_COORDINATES["Mx"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Mx"] = self.ARDUINO_COORDINATES["Mx"]

            if ("My" in self.ARDUINO_COORDINATES):
                self.myValue.set(self.ARDUINO_COORDINATES["My"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "My"] = self.ARDUINO_COORDINATES["My"]

            if ("Mz" in self.ARDUINO_COORDINATES):
                self.mzValue.set(self.ARDUINO_COORDINATES["Mz"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Mz"] = self.ARDUINO_COORDINATES["Mz"]

            if ("H" in self.ARDUINO_COORDINATES):
                self.hValue.set(self.ARDUINO_COORDINATES["H"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "H"] = self.ARDUINO_COORDINATES["H"]

            if ("T" in self.ARDUINO_COORDINATES):
                self.tValue.set(self.ARDUINO_COORDINATES["T"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "T"] = self.ARDUINO_COORDINATES["T"]

            if ("Bv" in self.ARDUINO_COORDINATES):
                self.bvValue.set(self.ARDUINO_COORDINATES["Bv"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Bv"] = self.ARDUINO_COORDINATES["Bv"]

            if ("Fa" in self.ARDUINO_COORDINATES):
                self.faValue.set(self.ARDUINO_COORDINATES["Fa"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Fa"] = self.ARDUINO_COORDINATES["Fa"]

            if ("Fb" in self.ARDUINO_COORDINATES):
                self.fbValue.set(self.ARDUINO_COORDINATES["Fb"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Fb"] = self.ARDUINO_COORDINATES["Fb"]

            if ("Fc" in self.ARDUINO_COORDINATES):
                self.fcValue.set(self.ARDUINO_COORDINATES["Fc"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Fc"] = self.ARDUINO_COORDINATES["Fc"]

            if ("Fd" in self.ARDUINO_COORDINATES):
                self.fdValue.set(self.ARDUINO_COORDINATES["Fd"])
                self.DATA_FRAME_PARAMETERS.loc[count,
                                               "Fd"] = self.ARDUINO_COORDINATES["Fd"]
            time.sleep(1)

    def _initialise_window(self, title, min_size):
        self.title(title)
        self.minsize(*min_size)
        self['bg'] = self.BACKGROUND_COLOR

    def _create_widgets(self):
        self._create_canvas()
        self._create_zoom_slider()
        self._create_import_file_button()
        self._create_color_pickers()
        self._create_fill_check()
        self._create_stop_button()
        self._create_start_button()
        self._create_labels_and_entry()
        self._create_coordinate_values_shown()
        self._create_arduino_config_dropdowns()
        self._create_export_button()

    def _create_export_button(self):
        customtkinter.CTkButton(self, text="Export parameters",text_font="Calibri 12 bold", text_color="black",
                            fg_color=("lavenderblush1"), hover=False, command=self._export_parameters) \
            .place(relx=self.COMMON_X, rely=0.8, relheight=0.05, relwidth=0.2, anchor="ne")

    def _export_parameters(self):
        if (self.DATA_FRAME_PARAMETERS.shape[0] == 0):
            messagebox.showinfo(
                message='Can\'t export data with no parameters collected.', title="WARNING")
            return

        directory_path = filedialog.askdirectory(mustexist=tk.TRUE)
        if (directory_path is ""):
            return

        file_name = "/" + datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + \
            "__DroneMovement.csv"
        export_path = directory_path + file_name
        file = Path(export_path)
        self.DATA_FRAME_PARAMETERS.to_csv(file)
        messagebox.showinfo(
            message='Data exported to CSV', title="SUCCESS")

    def _set_port(self, selectedChoice):
        self.ARDUINO_PORT_VALUE.set(selectedChoice)

    def _set_baudrate(self, selectedChoice):
        self.ARDUINO_BAUDRATE_VALUE.set(selectedChoice)

    def _create_arduino_config_dropdowns(self):
        # Create labels for dropdowns
        ttk.Label(self, text="Port ", foreground="#000000", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X - 0.238, rely=0.89, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Baudrate ", foreground="#000000", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X - 0.25, rely=0.93, relheight=0.036, relwidth=0.2, anchor="ne")

        # Prepare reactive variables for dropdowns
        self.ARDUINO_PORT_VALUE = tk.StringVar()
        self.ARDUINO_BAUDRATE_VALUE = tk.StringVar()

        self.ARDUINO_PORT_VALUE.set(DefaultOptionValue.PORT.value)
        self.ARDUINO_BAUDRATE_VALUE.set(DefaultOptionValue.BAUDRATE.value)

        # Create dropdowns
        tk.OptionMenu(self, self.ARDUINO_PORT_VALUE, *self.ARDUINO_PORT_OPTIONS, command=self._set_port) \
            .place(relx=self.COMMON_X - 0.38, rely=0.89, relheight=0.036, anchor="nw")

        tk.OptionMenu(self, self.ARDUINO_BAUDRATE_VALUE, *self.ARDUINO_BAUDRATE_OPTIONS, command=self._set_baudrate) \
            .place(relx=self.COMMON_X - 0.38, rely=0.93, relheight=0.036, anchor="nw")

    def _create_canvas(self):
        self.canvas_color = tk.StringVar()
        self.canvas_color.set("#87CEFA")

        self.canvas = tk.Canvas(self, width=self.CANVAS_WIDTH,
                                height=self.CANVAS_HEIGHT,
                                bg=self.canvas_color.get())
        self.canvas.place(relx=0.03, rely=0.052)
        
        #self.background_image = ImageTk.PhotoImage(Image.open(r"\imagine.png"))
        #self.image = self.canvas.create_image(0.03, 0.052, image = self.background_image, anchor="nw")

    def _create_coordinate_values_shown(self):
        valueRelx = self.COMMON_X + 0.03

        self.gxValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.gxValue, foreground="#76EE00", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.05, relheight=0.036, relwidth=0.1, anchor="ne")

        self.gyValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.gyValue, foreground="#76EE00", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.08, relheight=0.036, relwidth=0.1, anchor="ne")

        self.gzValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.gzValue, foreground="#76EE00", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.11, relheight=0.036, relwidth=0.1, anchor="ne")

        self.axValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.axValue, foreground="#FFD700", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.14, relheight=0.036, relwidth=0.1, anchor="ne")

        self.ayValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.ayValue, foreground="#FFD700", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.17, relheight=0.036, relwidth=0.1, anchor="ne")

        self.azValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.azValue, foreground="#FFD700", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.20, relheight=0.036, relwidth=0.1, anchor="ne")

        self.mxValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.mxValue, foreground="#3A5FCD", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.23, relheight=0.036, relwidth=0.1, anchor="ne")

        self.myValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.myValue, foreground="#3A5FCD", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.26, relheight=0.036, relwidth=0.1, anchor="ne")

        self.mzValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.mzValue, foreground="#3A5FCD", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.29, relheight=0.036, relwidth=0.1, anchor="ne")

        self.hValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.hValue, foreground="#FFA54F", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.32, relheight=0.036, relwidth=0.1, anchor="ne")

        self.tValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.tValue, foreground="#FF3030", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.35, relheight=0.036, relwidth=0.1, anchor="ne")

        self.bvValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.bvValue, foreground="#4876FF", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.38, relheight=0.036, relwidth=0.1, anchor="ne")

        self.faValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.faValue, foreground="#228B22", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.41, relheight=0.036, relwidth=0.1, anchor="ne")

        self.fbValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.fbValue, foreground="#228B22", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.44, relheight=0.036, relwidth=0.1, anchor="ne")

        self.fcValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.fcValue, foreground="#228B22", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.47, relheight=0.036, relwidth=0.1, anchor="ne")

        self.fdValue = tk.StringVar(self)
        tk.Label(self, textvariable=self.fdValue, foreground="#228B22", background="#9F79EE", font="Calibri 13 bold") \
            .place(relx=valueRelx, rely=0.50, relheight=0.036, relwidth=0.1, anchor="ne")

        customtkinter.CTkEntry(self, foreground="#9F79EE", background="#9F79EE") \
            .place(relx=valueRelx, rely=0.42, relheight=0.03, relwidth=0.1, anchor="ne")

        customtkinter.CTkEntry(self, foreground="#9F79EE", background="#9F79EE") \
            .place(relx=valueRelx, rely=0.45, relheight=0.03, relwidth=0.1, anchor="ne")

        customtkinter.CTkEntry(self, foreground="#9F79EE", background="#9F79EE") \
            .place(relx=valueRelx, rely=0.48, relheight=0.03, relwidth=0.1, anchor="ne")

        customtkinter.CTkEntry(self, foreground="#9F79EE", background="#9F79EE") \
            .place(relx=valueRelx, rely=0.51, relheight=0.03, relwidth=0.1, anchor="ne")

    def _create_labels_and_entry(self):
        # Labels

        ttk.Label(self, text="Gyroscope_x [°/s]", foreground="#76EE00", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.05, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Gyroscope_y [°/s]", foreground="#76EE00", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.08, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Gyroscope_z [°/s]", foreground="#76EE00", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.11, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Accelerometer_x [g]", foreground="#FFD700", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.14, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Accelerometer_y [g]", foreground="#FFD700", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.17, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Accelerometer_z [g]", foreground="#FFD700", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.20, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Pitch_angle [°]", foreground="#3A5FCD", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.23, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Roll_angle [°]", foreground="#3A5FCD", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.26, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Yaw_angle [°]", foreground="#3A5FCD", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.29, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Altitude [m]", foreground="#FFA54F", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.32, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Temperature [°C]", foreground="#FF3030", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.35, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Battery voltage [V]", foreground="#4876FF", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.38, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Free parameter", foreground="#228B22", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.41, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Free parameter", foreground="#228B22", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.44, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Free parameter", foreground="#228B22", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.47, relheight=0.036, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Free parameter", foreground="#228B22", background="#9F79EE", font="Calibri 12 bold") \
            .place(relx=self.COMMON_X, rely=0.50, relheight=0.036, relwidth=0.2, anchor="ne")

    def _create_zoom_slider(self):
        COMM_Y = 0.92
        ttk.Label(self, text="Zoom:", foreground="#000000", background="#9F79EE") \
            .place(relx=0.235, rely=COMM_Y + 0.02, relheight=0.035, relwidth=0.2, anchor="ne")

        self.zoom_slider = customtkinter.CTkSlider(
            self, from_=20, to=5, orient="horizontal", command=self._changed)
        self.zoom_slider.set(self._geometry_handler._zoom)
        self.zoom_slider.place(relx=0.2, rely=COMM_Y + 0.023, relheight=0.03, relwidth=0.12, anchor="ne")

    def _create_import_file_button(self):
        self.FILE_NAME = tk.StringVar()
        ttk.Label(self, textvariable=self.FILE_NAME, foreground="#ffffff", background="#9F79EE") \
            .place(relx=0.86, rely=0.817, relheight=0.035, relwidth=0.09, anchor="ne")

        customtkinter.CTkButton(self, text="Import file", text_font="Calibri 12 bold", text_color="black",
                                fg_color=("lavenderblush1"), hover=False, command=self._read_file) \
            .place(relx=self.COMMON_X, rely=0.72, relheight=0.05, relwidth=0.2, anchor="ne")

    def _create_stop_button(self):
        self.FILE_NAME = tk.StringVar()
        customtkinter.CTkButton(self, text="Stop", text_font="Calibri 12 bold", text_color="red",
                                fg_color=("lavenderblush1"), hover=False, command=self._stop) \
            .place(relx=self.COMMON_X, rely=0.6, relheight=0.07, relwidth=0.09, anchor="ne")

    def _create_start_button(self):
        customtkinter.CTkButton(self, text="Start", text_font="Calibri 12 bold", text_color="springgreen3",
                            fg_color=("lavenderblush1"), hover=False, command=self._start) \
        .place(relx=self.COMMON_X - 0.11, rely=0.60, relheight=0.07, relwidth=0.09, anchor="ne")

    def _create_color_pickers(self):

        COMM_Y = 0.92

        # FILL
        self.fill_color = tk.StringVar()
        self.fill_color.set("#000000")

        ttk.Label(self, text="Fill color:", foreground="#000000", background="#9F79EE") \
            .place(relx=0.08, rely=COMM_Y - 0.027, relheight=0.035, anchor="ne")

        self._fill_btn = customtkinter.CTkButton(
            self, text="", command=self._pick_color_fill, relief='flat')
        self._fill_btn.place(relx=0.085, rely=COMM_Y -
                             0.015, relheight=0.015, relwidth=0.05)
        self._fill_btn['bg'] = self.fill_color.get()

        # LINE
        self.line_color = tk.StringVar()
        self.line_color.set("#0000FF")

        ttk.Label(self, text="Line color:", foreground="#000000", background="#9F79EE") \
            .place(relx=0.20, rely=COMM_Y - 0.027, relheight=0.035, anchor="ne")

        self._line_btn = customtkinter.CTkButton(
            self, text="", command=self._pick_color_line, relief='flat')
        self._line_btn.place(relx=0.205, rely=COMM_Y -
                             0.015, relheight=0.015, relwidth=0.05)
        self._line_btn['bg'] = self.line_color.get()

        # CANVAS' BACKGROUND
        ttk.Label(self, text="Canvas color:", foreground="#000000", background="#9F79EE") \
            .place(relx=0.33, rely=COMM_Y - 0.027, relheight=0.035, anchor="ne")

        self._canvas_btn = customtkinter.CTkButton(
            self, text="", command=self._pick_color_canvas, relief='flat')
        self._canvas_btn.place(relx=0.335, rely=COMM_Y -
                               0.015, relheight=0.015, relwidth=0.05)

    def _create_fill_check(self):
        self._check_no_fill = tk.IntVar()

        customtkinter.CTkCheckBox(self, text="Fill", variable=self._check_no_fill, command=self._changed, onvalue=True,
                        offvalue=False) \
            .place(relx=0.25, rely=0.94, relheight=0.035)

    def _pick_color_fill(self):
        self._pick_color("f")

    def _pick_color_line(self):
        self._pick_color("l")

    def _pick_color_canvas(self):
        self._pick_color("c")

    def _pick_color(self, picker):
        if(picker == "f"):
            col = colorchooser.askcolor(initialcolor=self.fill_color.get())

            if(col[1]):
                self.fill_color.set(col[1])
                self._fill_btn['bg'] = col[1]
        elif(picker == "c"):
            col = colorchooser.askcolor(initialcolor=self.canvas_color.get())

            if(col[1]):
                self.canvas_color.set(col[1])
                self._canvas_btn['bg'] = col[1]
                self.canvas['bg'] = self.canvas_color.get()
        else:
            col = colorchooser.askcolor(initialcolor=self.line_color.get())

            if(col[1]):
                self.line_color.set(col[1])
                self._line_btn['bg'] = col[1]
        self._changed()

    def _changed(self, *args):
        self.changed = True

    def _read_file(self):
        messagebox.showinfo(
            message='Only .obj files are compatible!', title="WARNING")

        file_path = filedialog.askopenfilename(defaultextension=".obj",
                                               filetypes=(("OBJ Files", "*.obj"),
                                                          ("All Files", "*.*")))

        if len(file_path) and file_path[-4:] != ".obj":
            messagebox.showinfo(
                message="Incompatible file format", title="ERROR")

        elif len(file_path):
            self.FILE_NAME.set(file_path.split('/')[-1])
            with open(file_path) as file:
                verticies, faces = obj_files_handler.extract_data(file)
                self._geometry_handler._verticies, self._geometry_handler._faces = verticies, faces
                self.file_exists = True

    def draw(self):
        if(self.ANIMATION_STARTED is True):
            objectDrew = self.draw_based_on_coords()
            if (objectDrew is False):
                return

        self._get_zoom()
        if(self.file_exists and self.changed):
            # Delete all the previous points and lines in order to draw new ones
            self.canvas.delete("all")

            self._set_colors()
            self.canvas = self._geometry_handler.draw_object(self.canvas)
            self.changed = False

    def _get_zoom(self):
        self._geometry_handler._zoom = self.zoom_slider.get()

    def draw_based_on_coords(self):
        coordinatesChanged = False
        coordinates = self.ARDUINO_COORDINATES

        # Set angle
        if (coordinates is not None and "Mx" in coordinates and "My" in coordinates and "Mz" in coordinates):
            # Get x,y,z coords
            xAngleCoord, yAngleCoord, zAngleCoord = coordinates[
                "Mx"], coordinates["My"], coordinates["Mz"]

            # Set object coords
            self._geometry_handler._angle_x = xAngleCoord + self.OFFSET_X
            self._geometry_handler._angle_y = yAngleCoord + self.OFFSET_Y
            self._geometry_handler._angle_z = zAngleCoord + self.OFFSET_Z

            # Mark coordinates changed
            coordinatesChanged = True
            print("Changed angle coordinates (x,y,z) to : (",
                  xAngleCoord, " : ", yAngleCoord, " : ", zAngleCoord, ")")

        # # Set position
        # if (coordinates is not None and "Ax" in coordinates and "Ay" in coordinates):
        #         # Get x,y acceleration values
        #         xPositionAcceleration, yPositionAcceleration = coordinates["Ax"], coordinates["Ay"]

        #         # Get current object corrds
        #         currentObjectXCoordinate, currentObjectYCoordinate = self._geometry_handler.OBJECT_POSITION

        #         # Accelerate object based on current coords and acceleration values
        #         self._geometry_handler.OBJECT_POSITION = [currentObjectXCoordinate + xPositionAcceleration, currentObjectYCoordinate + yPositionAcceleration]

        #         # Mark coordinates changed
        #         coordinatesChanged = True
        #         print("Changed position coordinates (x,y) to : (", xPositionAcceleration, " : ", yPositionAcceleration, ")")

        if (coordinatesChanged is False):
            # No change in coordinates, so no reason to redraw
            return False

        self.canvas.delete("all")
        self._set_colors()
        self.canvas = self._geometry_handler.draw_object(self.canvas)
        return True

    def _set_colors(self):
        self._geometry_handler.change_fill_color(
            self.fill_color.get(), self._check_no_fill.get())
        self._geometry_handler.change_line_color(self.line_color.get())

    def _stop(self):
        if (self.ANIMATION_STARTED == False):
            messagebox.showinfo(
                message='Can\'t stop the animation because it\'s already stopped', title="WARNING")
            return

        self.ANIMATION_STARTED = False

    def _start(self):
        if (self.ANIMATION_STARTED == True):
            messagebox.showinfo(
                message='Can\'t start the animation because it\'s already started', title="WARNING")
            return

        if (self.file_exists is False):
            messagebox.showinfo(
                message='Can\'t start the animation if no object is loaded', title="WARNING")
            return

        BAUDRATE_VALUE = self.ARDUINO_BAUDRATE_VALUE.get()
        PORT_VALUE = self.ARDUINO_PORT_VALUE.get().split()[0]

        if (BAUDRATE_VALUE == DefaultOptionValue.BAUDRATE.value or PORT_VALUE == DefaultOptionValue.PORT.value):
            messagebox.showinfo(
                message='Can\'t start the animation if no port and / or baudrate is selected', title="WARNING")
            return

        # Mark the animation start
        self.ANIMATION_STARTED = True

        if (self.ARDUINO is not None):
            # Close already opened socket
            self.ARDUINO = self.ARDUINO.close()

        self.ARDUINO = serial.Serial(PORT_VALUE, int(BAUDRATE_VALUE))

        if (self.ARDUINO_READING_THREAD is None):
            # Start reading thread if not already started
            self.ARDUINO_READING_THREAD = threading.Thread(
                target=self._set_coordinates)
            self.ARDUINO_READING_THREAD.setDaemon(True)
            self.ARDUINO_READING_THREAD.start()
