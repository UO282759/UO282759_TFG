#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 Dario Bagues Castro
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

"""
This module provides a GUI application for selecting and plotting data.

The application allows users to:
- Select a file containing mass data.
- Choose specific mass numbers to plot from the file.
- Generate a plot of the selected mass data using matplotlib.

The GUI is built using Tkinter and includes functionalities for file selection,
data parsing, and plot generation using Matplotlib.

Author: Dario Bagues Castro
"""

__author__ = "Dario Bagues Castro"
__copyright__ = "Copyright (C) 2024, Dario Bagues Castro"
__license__ = "GPLv3-or-later"
__version__ = "0.0.1"
__maintainer__ = "Dario Bagues Castro"
__email__ = "dariobc@inventati.org"
__status__ = "Prototype"

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle


def generate_plot():
    """
    Generate a plot of the selected mass data from the file.

    This function reads the file specified in the path_var variable, extracts
    the data corresponding to the selected mass numbers, and plots it using
    matplotlib. If no file is selected or no mass numbers are selected, it shows
    an error message.
    """
    selected_numbers = [number for number, var in number_vars.items() if var.get()]
    if path_var.get() == "":
        messagebox.showerror("Error", "No file selected.")
        return

    if not selected_numbers:
        messagebox.showerror("Error", "No numbers selected.")
        return

    with open(path_var.get(), encoding="utf-8") as f:
        available = [int(m) for m in f.readline()[:-1].split("\t")[1:]]
        masses = dict(zip(available, list(range(1, len(available) + 1))))

    try:
        ar = np.loadtxt(
            path_var.get(),
            delimiter="\t",
            skiprows=1,
            usecols=[masses[m] for m in selected_numbers],
        )
    except OSError as e:
        messagebox.showerror("Error", f"An error occurred while reading the file:\n{e}")
        return

    plt.plot(range(1, ar.shape[0] + 1), ar, label=selected_numbers)
    plt.legend(loc=1)

    # Show the plot in a regular pyplot window
    plt.show()


def clear_selection():
    """
    Clear all mass number selections.

    This function resets all mass number checkbuttons to an unchecked state.
    """
    for n in number_vars.values():
        n.set(False)


def select_file():
    """
    Open a file dialog to select a file and enable relevant checkbuttons.

    This function opens a file dialog for the user to select a file. It then reads
    the available mass numbers from the file and enables the corresponding checkbuttons.
    If an error occurs while reading the file, it shows an error message and disables
    all checkbuttons.
    """
    file_path = filedialog.askopenfilename()
    if file_path:
        available_masses = range(75, 210)
        file_path_label.config(text="")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline()
                new_masses = [int(x) for x in first_line.split()[2:]]
                available_masses = [i for i in available_masses if i in new_masses]
        except OSError as e:
            messagebox.showerror(
                "Error", f"An error occurred while reading the file:\n{e}"
            )
            disable_buttons()
        else:
            enable_buttons(available_masses)
            # Display each selected file path in the label
            path_var.set(file_path)
            file_path_label.config(text=path_var.get())
    else:
        messagebox.showerror("Error", "No file selected.")


def enable_buttons(available_masses):
    """
    Enable checkbuttons for the available mass numbers.

    This function enables the checkbuttons for the mass numbers that are available
    in the selected file and disables the others.

    Args:
        available_masses (list): List of available mass numbers.
    """
    for n in range(75, 210):
        if n in available_masses:
            number_vars[n].set(False)  # Uncheck by default
            number_buttons[n].state(["!disabled"])
        else:
            number_vars[n].set(False)
            number_buttons[n].state(["disabled"])


def disable_buttons():
    """
    Disable all mass number checkbuttons.

    This function disables all mass number checkbuttons and sets their state to unchecked.
    """
    for n in range(75, 210):
        number_vars[n].set(False)
        number_buttons[n].state(["disabled"])


def on_closing():
    """
    Handle the window closing event.

    This function quits the Tkinter main loop and destroys the root window when the
    user attempts to close the application window.
    """
    root.quit()
    root.destroy()


mplstyle.use("fast")

# Create main window
root = tk.Tk()
root.title("Data Selector")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Create a frame for the file selector
file_frame = tk.Frame(root)
file_frame.pack(padx=10, pady=10, anchor="w")

# Create a label to display the file path
path_var = tk.StringVar()
file_path_label = ttk.Label(
    file_frame,
    textvariable=path_var,
    width=50,
    anchor="w",
    relief="sunken",
    justify="left",
)
file_path_label.grid(row=0, column=1)

# Create file selector button
file_button = ttk.Button(file_frame, text="Select Files", command=select_file)
file_button.grid(row=0, column=0, padx=5)

# Create mass selection checkbuttons for numbers 75 to 209
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Create checkable buttons
number_vars = {}
number_buttons = {}
for num in range(75, 210):
    var = tk.BooleanVar()
    chk = ttk.Checkbutton(frame, text=str(num), variable=var, state="disabled")
    chk.grid(row=(num - 75) // 10, column=(num - 75) % 10, padx=5, pady=5, sticky="w")
    number_vars[num] = var
    number_buttons[num] = chk

# Create view and clear buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
save_button = ttk.Button(button_frame, text="View", command=generate_plot)
save_button.pack(side=tk.LEFT, padx=5)
clear_button = ttk.Button(button_frame, text="Clear", command=clear_selection)
clear_button.pack(side=tk.LEFT, padx=5)

# Start GUI event loop
root.mainloop()