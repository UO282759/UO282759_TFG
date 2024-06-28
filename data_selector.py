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
Data Selector Tool

This script provides a graphical user interface (GUI) for selecting specific columns 
from a tab-separated values (TSV) file based on user-defined masses. The selected columns 
can be saved to new files. The tool supports handling large files by processing them in chunks.

Modules:
    - tkinter: Provides the GUI components.
    - ttk: Extends tkinter with themed widgets.
    - filedialog: Provides file selection dialogs.
    - messagebox: Provides message box dialogs.
    - threading: Allows running tasks in separate threads.
    - mmap: Provides memory-mapped file support.
    - pandas: Provides data manipulation and analysis tools.
    - math: Provides mathematical functions.

Functions:
    - line_count(infile): Count the number of lines in a file.
    - data_selector(masses, infile, outfile): Select specific columns from a file and save to a new file.
    - save_selection(): Save the selected numbers to the output file(s).
    - long_running_function(selected_numbers, paths, save_path): Execute the data selection process for each file in a separate thread.
    - clear_selection(): Clear all selections.
    - cancel_thread(): Cancel the currently running thread.
    - select_file(): Open a file dialog to select input files and enable buttons based on available masses.
    - enable_buttons(available_masses): Enable the checkbuttons based on available masses.
    - disable_buttons(): Disable all checkbuttons.
    
Author: Dario Bagues Castro
"""

__author__ = "Dario Bagues Castro"
__copyright__ = "Copyright (C) 2024, Dario Bagues Castro"
__license__ = "GPLv3-or-later"
__version__ = "0.0.1"
__maintainer__ = "Dario Bagues Castro"
__email__ = "dariobc@inventati.org"
__status__ = "Prototype"


import mmap
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd


CHUNKSIZE = 1000000


def line_count(infile):
    """
    Count the number of lines in a file.

    Parameters:
    infile (str): The path to the input file.

    Returns:
    int: The number of lines in the file.
    """
    lines = 0
    with open(infile, "r+") as f:
        buf = mmap.mmap(f.fileno(), 0)
        while buf.readline():
            lines += 1
    return lines

def data_selector(masses, infile, outfile):
    """
    Select specific columns from a file based on given masses and save to a new file.

    Parameters:
    masses (list of int): The masses to select.
    infile (str): The path to the input file.
    outfile (str): The path to the output file.

    Yields:
    float: The progress percentage of the operation.
    """
    with open(infile) as infile_r:
        first_line = infile_r.readline().strip()
        available_masses = [int(x) for x in first_line.split()[2:]]
    columns = [0] + [available_masses.index(int(i)) for i in masses]
    lines = line_count(infile)

    with open(outfile, "w") as outfile:
        outfile.write("Push number\t" + "\t".join(str(m) for m in masses) + "\n")
        for chunk in pd.read_csv(infile, delimiter="\t", chunksize=CHUNKSIZE):
            chunk.iloc[:, columns].to_csv(outfile, index=False, header=False, sep="\t")
            yield 100 - (1 - chunk.index[-1] / lines) * 100

def save_selection():
    """
    Save the selected numbers to the output file(s).
    """
    if path_var.get() == "":
        messagebox.showerror("Error", "No file selected.")
        return

    selected_numbers = [number for number, var in number_vars.items() if var.get()]
    if selected_numbers:
        save_path = []
        for path in path_var.get().split("\n"):
            save_path.append(
                filedialog.asksaveasfilename(
                    initialdir=path,
                    initialfile="".join(path.split("/")[-1].split(".")[:-1])
                    + "_modified.txt",
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                )
            )
        if len(save_path) == len(path_var.get().split("\n")):
            save_button.config(state=tk.DISABLED)
            clear_button.config(state=tk.DISABLED)
            cancel_button.config(state=tk.NORMAL)
            global thread_running
            thread_running = True
            threading.Thread(
                target=long_running_function,
                args=(selected_numbers, path_var.get(), save_path),
            ).start()
        else:
            messagebox.showerror(
                "Error", "You need to select a save file for every input file."
            )
    else:
        messagebox.showerror("Error", "No numbers selected.")

def long_running_function(selected_numbers, paths, save_path):
    """
    Execute the data selection process for each file in a separate thread.

    Parameters:
    selected_numbers (list of int): The selected masses.
    paths (str): The input file paths.
    save_path (list of str): The output file paths.
    """
    paths = paths.split("\n")
    for n, path in enumerate(paths):
        if not thread_running:
            break
        progress_var.set(f"File: {n+1}/{len(paths)}\tGetting file size...")
        for progress in data_selector(selected_numbers, path, save_path[n]):
            if not thread_running:
                break
            progress_var.set(f"File: {n+1}/{len(paths)}\tProgress: {progress:.2f} %")
    if thread_running:
        progress_var.set("Modified files saved.")
    else:
        progress_var.set("Operation canceled by user.")

    save_button.config(state=tk.NORMAL)
    clear_button.config(state=tk.NORMAL)
    cancel_button.config(state=tk.DISABLED)

def clear_selection():
    """
    Clear all selections.
    """
    for var in number_vars.values():
        var.set(False)

def cancel_thread():
    """
    Cancel the currently running thread.
    """
    global thread_running
    thread_running = False

def select_file():
    """
    Open a file dialog to select input files and enable buttons based on available masses.
    """
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        available_masses = range(75, 210)
        file_path_label.config(text="")
        for file_path in file_paths:
            try:
                with open(file_path, "r") as f:
                    first_line = f.readline()
                    new_masses = [int(x) for x in first_line.split()[2:]]
                    available_masses = [i for i in available_masses if i in new_masses]
            except Exception as e:
                messagebox.showerror(
                    "Error", f"An error occurred while reading the file:\n{e}"
                )
                disable_buttons()
            else:
                enable_buttons(available_masses)
                path_var.set("\n".join(path for path in file_paths))
                file_path_label.config(text=path_var.get())
    else:
        messagebox.showerror("Error", "No files selected.")

def enable_buttons(available_masses):
    """
    Enable the checkbuttons based on available masses.

    Parameters:
    available_masses (list of int): The masses that are available in the selected file.
    """
    for num in range(75, 210):
        if num in available_masses:
            number_vars[num].set(False)
            number_buttons[num].state(["!disabled"])
        else:
            number_vars[num].set(False)
            number_buttons[num].state(["disabled"])

def disable_buttons():
    """
    Disable all checkbuttons.
    """
    for num in range(75, 210):
        number_vars[num].set(False)
        number_buttons[num].state(["disabled"])

# Create main window
root = tk.Tk()
root.title("Data Selector")

# Create a frame for the file selector
file_frame = tk.Frame(root)
file_frame.pack(padx=10, pady=10, anchor="w")

# Create a Label to display the file path
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

# Create a frame to hold the Checkbuttons
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Create checkable buttons for numbers 75 to 209
number_vars = {}
number_buttons = {}
for num in range(75, 210):
    var = tk.BooleanVar()
    chk = ttk.Checkbutton(frame, text=str(num), variable=var, state="disabled")
    chk.grid(row=(num - 75) // 10, column=(num - 75) % 10, padx=5, pady=5, sticky="w")
    number_vars[num] = var
    number_buttons[num] = chk

# Create save, clear, and cancel buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

save_button = ttk.Button(button_frame, text="Save", command=save_selection)
save_button.pack(side=tk.LEFT, padx=5)

clear_button = ttk.Button(button_frame, text="Clear", command=clear_selection)
clear_button.pack(side=tk.LEFT, padx=5)

# Create a Cancel button for the thread
cancel_button = ttk.Button(
    button_frame, text="Cancel", command=cancel_thread, state="disabled"
)
cancel_button.pack(side=tk.LEFT, padx=5)

# Create a progress label
progress_var = tk.StringVar()
progress_label = ttk.Label(root, textvariable=progress_var)
progress_label.pack()

# Initialize thread flag
thread_running = False

# Start GUI event loop
root.mainloop()
