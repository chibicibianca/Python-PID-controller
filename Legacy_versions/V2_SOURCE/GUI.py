from datetime import datetime
from enum import Enum
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
import serial.tools.list_ports
from pathlib import Path
import customtkinter



class DefaultOptionValue(Enum):
    PORT = "Choose COM port"
    BAUDRATE = " Choose baudrate "


class GUI(tk.Tk):

    BACKGROUND_COLOR = '#DCDCDC'
    CANVAS_WIDTH = 510
    CANVAS_HEIGHT = 300
    OBJECT_POSITION_X = 250
    OBJECT_POSITION_Y = 150
    CANVAS_COLOR = 'white'
    COMMON_X = 0.97  # Many graphical elements share the same relative X position

    ANIMATION_STARTED = False


    ARDUINO = None
    ARDUINO_COORDINATES = None
    ARDUINO_READING_THREAD = None

    # Arduino parameters
    ARDUINO_BAUDRATE_OPTIONS = ["9600", "19200", "38400", "57600", "115200"]
    ARDUINO_BAUDRATE_VALUE = None

    ARDUINO_PORT_OPTIONS = serial.tools.list_ports.comports()
    ARDUINO_PORT_VALUE = None


    def __init__(self, title='GUI - 2D ARM', min_size=(550, 600)):
        super().__init__()

        self.file_exists = False  # A flag for whether the file has been loaded or not
        self.changed = True  # A flag used to only redraw the object when a change occured
        self._geometry_handler = geometry.GEOMETRY(
            self.CANVAS_WIDTH, self.CANVAS_HEIGHT, self.OBJECT_POSITION_X, self.OBJECT_POSITION_Y)
        self._initialise_window(title, min_size)
        self._create_widgets()

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
        self._create_labels_and_entry()
        self._create_arduino_config_dropdowns()
        self._create_save_button()
        self._create_t_buttons()
        self._create_a_buttons()

    def _create_save_button(self):
        customtkinter.CTkButton(self, text="Set PID", text_font="Calibri 11 bold", text_color="black",
                                fg_color=("gray80"), command=self._save_record) \
            .place(relx=self.COMMON_X, rely=0.85, relheight=0.05, relwidth=0.20, anchor="ne")

    def _save_record(self):
        self._create_save_button()

    def _set_port(self, selectedChoice):
        self.ARDUINO_PORT_VALUE.set(selectedChoice)

    def _set_baudrate(self, selectedChoice):
        self.ARDUINO_BAUDRATE_VALUE.set(selectedChoice)

    def _create_arduino_config_dropdowns(self):
        # Create labels for dropdowns
        ttk.Label(self, text="Port ", foreground="#000000", background="#DCDCDC", font="Calibri 11 bold") \
            .place(relx=self.COMMON_X - 0.75, rely=0.63, relheight=0.055, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="Baudrate ", foreground="#000000", background="#DCDCDC", font="Calibri 11 bold") \
            .place(relx=self.COMMON_X - 0.75, rely=0.67, relheight=0.060, relwidth=0.2, anchor="ne")

        # Prepare reactive variables for dropdowns
        self.ARDUINO_PORT_VALUE = tk.StringVar()
        self.ARDUINO_BAUDRATE_VALUE = tk.StringVar()

        self.ARDUINO_PORT_VALUE.set(DefaultOptionValue.PORT.value)
        self.ARDUINO_BAUDRATE_VALUE.set(DefaultOptionValue.BAUDRATE.value)

        # Create dropdowns
        tk.OptionMenu(self, self.ARDUINO_PORT_VALUE, *self.ARDUINO_PORT_OPTIONS, command=self._set_port) \
            .place(relx=self.COMMON_X - 0.84, rely=0.63, relheight=0.05, anchor="nw")

        tk.OptionMenu(self, self.ARDUINO_BAUDRATE_VALUE, *self.ARDUINO_BAUDRATE_OPTIONS, command=self._set_baudrate) \
            .place(relx=self.COMMON_X - 0.84, rely=0.67, relheight=0.05, anchor="nw")

    def _create_canvas(self):
        self.canvas_color = tk.StringVar()
        self.canvas_color.set("#87CEFA")

        self.canvas = tk.Canvas(self, width=self.CANVAS_WIDTH,
                                height=self.CANVAS_HEIGHT,
                                bg=self.canvas_color.get())
        self.canvas.place(relx=0.03, rely=0.052)
        
        #self.background_image = ImageTk.PhotoImage(Image.open(r"\imagine.png"))
        #self.image = self.canvas.create_image(0.03, 0.052, image = self.background_image, anchor="nw")

    def _create_labels_and_entry(self):
        # Labels

        ttk.Label(self, text="KP", foreground="#912CEE", background="#DCDCDC", font="Calibri 11 bold") \
            .place(relx=self.COMMON_X - 0.05, rely=0.65, relheight=0.05, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="KI", foreground="#9370DB", background="#DCDCDC", font="Calibri 11 bold") \
            .place(relx=self.COMMON_X - 0.05, rely=0.70, relheight=0.05, relwidth=0.2, anchor="ne")

        ttk.Label(self, text="KD", foreground="#551A8B", background="#DCDCDC", font="Calibri 11 bold") \
            .place(relx=self.COMMON_X - 0.05, rely=0.75, relheight=0.05, relwidth=0.2, anchor="ne")

        customtkinter.CTkEntry(self, foreground="#DCDCDC", background="#DCDCDC") \
            .place(relx=self.COMMON_X, rely=0.65, relheight=0.05, relwidth=0.2, anchor="ne")

        customtkinter.CTkEntry(self, foreground="#DCDCDC", background="#DCDCDC") \
            .place(relx=self.COMMON_X, rely=0.70, relheight=0.05, relwidth=0.2, anchor="ne")

        customtkinter.CTkEntry(self, foreground="#DCDCDC", background="#DCDCDC") \
            .place(relx=self.COMMON_X, rely=0.75, relheight=0.05, relwidth=0.2, anchor="ne")

    def _create_zoom_slider(self):
        ttk.Label(self, text="Zoom:", foreground="#000000", background="#DCDCDC") \
            .place(relx=self.COMMON_X, rely=0.92, relheight=0.035, relwidth=0.2, anchor="ne")

        self.zoom_slider = customtkinter.CTkSlider(
            self, from_=20, to=5, orient="horizontal", command=self._changed)
        self.zoom_slider.set(self._geometry_handler._zoom)
        self.zoom_slider.place(relx=self.COMMON_X, rely=0.92, relheight=0.03, relwidth=0.12, anchor="ne")

    def _create_import_file_button(self):
        self.FILE_NAME = tk.StringVar()
        customtkinter.CTkButton(self, text="Import file", text_font="Calibri 12 bold", text_color="black",
                                fg_color=("lavenderblush1"), hover=False, command=self._read_file) \
            .place(relx=self.COMMON_X, rely=0.57, relheight=0.05, relwidth=0.2, anchor="ne")


    def _create_color_pickers(self):

        # FILL
        self.fill_color = tk.StringVar()
        self.fill_color.set("#000000")

        ttk.Label(self, text="Fill color:", foreground="#000000", background="#DCDCDC") \
            .place(relx=self.COMMON_X-0.85, rely=0.56, relheight=0.025, anchor="ne")

        self._fill_btn = customtkinter.CTkButton(
            self, text="", command=self._pick_color_fill, relief='flat')
        self._fill_btn.place(relx=self.COMMON_X-0.83, rely=0.572, relheight=0.015, relwidth=0.05)
        self._fill_btn['bg'] = self.fill_color.get()

        # LINE
        self.line_color = tk.StringVar()
        self.line_color.set("#0000FF")

        ttk.Label(self, text="Line color:", foreground="#000000", background="#DCDCDC") \
            .place(relx=self.COMMON_X-0.66, rely=0.56, relheight=0.025, anchor="ne")

        self._line_btn = customtkinter.CTkButton(
            self, text="", command=self._pick_color_line, relief='flat')
        self._line_btn.place(relx=self.COMMON_X-0.64, rely=0.572
                            , relheight=0.015, relwidth=0.05)
        self._line_btn['bg'] = self.line_color.get()

        # CANVAS' BACKGROUND
        ttk.Label(self, text="Canvas color:", foreground="#000000", background="#DCDCDC") \
            .place(relx=self.COMMON_X-0.44, rely=0.56, relheight=0.025, anchor="ne")

        self._canvas_btn = customtkinter.CTkButton(
            self, text="", command=self._pick_color_canvas, relief='flat')
        self._canvas_btn.place(relx=self.COMMON_X-0.42, rely=0.572, relheight=0.015, relwidth=0.05)

    def _create_fill_check(self):
        self._check_no_fill = tk.IntVar()

        customtkinter.CTkCheckBox(self, text="Fill", variable=self._check_no_fill, command=self._changed, onvalue=True,
                        offvalue=False) \
            .place(relx=self.COMMON_X-0.10, rely=0.955, relheight=0.048)

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


    def _set_colors(self):
        self._geometry_handler.change_fill_color(
            self.fill_color.get(), self._check_no_fill.get())
        self._geometry_handler.change_line_color(self.line_color.get())

    def _create_t_buttons(self):
        customtkinter.CTkButton(self, text="T+", text_font="Calibri 11 bold", text_color="black",
                                fg_color=("red"), command=self._save_record) \
            .place(relx=self.COMMON_X - 0.80, rely=0.75, relheight=0.1, relwidth=0.1, anchor="ne")

        customtkinter.CTkButton(self, text="T-", text_font="Calibri 11 bold", text_color="black",
                                fg_color=("green"), command=self._save_record) \
            .place(relx=self.COMMON_X - 0.60, rely=0.75, relheight=0.1, relwidth=0.1, anchor="ne")

    def _create_a_buttons(self):
        customtkinter.CTkButton(self, text="A+", text_font="Calibri 11 bold", text_color="black",
                                fg_color=("green"), command=self._save_record) \
            .place(relx=self.COMMON_X - 0.80, rely=0.9, relheight=0.06, relwidth=0.1, anchor="ne")

        customtkinter.CTkButton(self, text="A-", text_font="Calibri 11 bold", text_color="black",
                                fg_color=("green"), command=self._save_record) \
            .place(relx=self.COMMON_X - 0.60, rely=0.9, relheight=0.06, relwidth=0.1, anchor="ne")