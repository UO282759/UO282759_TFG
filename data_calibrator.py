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
Calibration Application

This module provides a graphical user interface (GUI) for performing
calibrations using weighted least squares regression. The application 
allows users to select files containing signal data, input the corresponding 
concentrations, and perform the calibration to determine the regression 
parameters.

The application uses the following modules:
- tkinter: For creating the GUI.
- numpy: For numerical operations.
- matplotlib: For plotting the calibration results.

Functions:
- m(x, w): Calculate the weighted mean.
- cov(x, y, w): Calculate the weighted covariance.
- corr(x, y, w): Calculate the weighted correlation.
- wls(x, y, w): Perform weighted least squares regression.

Classes:
- CalibrationApp: Main class for the calibration application.

Usage:
Run this script to launch the calibration application GUI.

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
from matplotlib import pyplot as plt


def m(x, w):
    """
    Calculate the weighted mean.

    Parameters:
    x (array-like): Values.
    w (array-like): Weights.

    Returns:
    float: Weighted mean of x.
    """
    return np.sum(x * w) / np.sum(w)


def cov(x, y, w):
    """
    Calculate the weighted covariance.

    Parameters:
    x (array-like): Values of the first variable.
    y (array-like): Values of the second variable.
    w (array-like): Weights.

    Returns:
    float: Weighted covariance of x and y.
    """
    return np.sum(w * (x - m(x, w)) * (y - m(y, w))) / np.sum(w)


def corr(x, y, w):
    """
    Calculate the weighted correlation.

    Parameters:
    x (array-like): Values of the first variable.
    y (array-like): Values of the second variable.
    w (array-like): Weights.

    Returns:
    float: Weighted correlation of x and y.
    """
    return cov(x, y, w) / np.sqrt(cov(x, x, w) * cov(y, y, w))


def wls(x, y, w):
    """
    Perform weighted least squares regression.

    Parameters:
    x (array-like): Independent variable values.
    y (array-like): Dependent variable values.
    w (array-like): Weights.

    Returns:
    tuple: (slope, intercept, r_squared) of the regression line.
    """
    c = corr(x, y, w)
    slope = c * np.std(y) / np.std(x)
    intercept = m(y, w) - m(x, w) * slope
    return slope, intercept, c**2


class CalibrationApp:
    """Application for performing calibration using weighted least squares regression."""

    def __init__(self, root):
        """
        Initialize the CalibrationApp.

        Parameters:
        root (tk.Tk): Root window of the Tkinter application.
        """
        self.root = root
        self.root.title("Calibration")

        self.rows = []
        self.create_widgets()

    def create_widgets(self):
        """Create and layout the widgets for the application."""
        # Container frame for rows
        self.frame = ttk.Frame(self.root)
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create initial rows
        for _ in range(3):
            self.add_row()

        # Bottom row with "Add Row" and "Calibrate" buttons
        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.pack(padx=10, pady=10, fill=tk.X)

        self.add_button = ttk.Button(
            self.bottom_frame, text="Add Row", command=self.add_row
        )
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.calibrate_button = ttk.Button(
            self.bottom_frame, text="Calibrate", command=self.calibrate
        )
        self.calibrate_button.pack(side=tk.LEFT, padx=5)

        self.mass_label = ttk.Label(self.bottom_frame)
        self.mass_label.configure(text="Mass:")
        self.mass_label.pack(side=tk.LEFT, padx=5)

        validate_mass = (self.frame.register(str.isdigit), "%P")
        self.mass_entry = ttk.Entry(
            self.bottom_frame, width=4, validate="key", validatecommand=validate_mass
        )
        self.mass_entry.insert(0, "")
        self.mass_entry.pack(side=tk.LEFT, padx=5)

    def add_row(self):
        """Add a new row to the application for selecting files and entering concentrations."""
        row_frame = ttk.Frame(self.frame)
        row_frame.pack(fill=tk.X, pady=2)

        delete_button = ttk.Button(
            row_frame, text="Delete", command=lambda rf=row_frame: self.delete_row(rf)
        )
        delete_button.pack(side=tk.LEFT, padx=5)

        file_button = ttk.Button(
            row_frame, text="Select File", command=lambda: self.select_file(row_frame)
        )
        file_button.pack(side=tk.LEFT, padx=5)

        file_label = ttk.Entry(row_frame, state="readonly", width=30)
        file_label.pack(side=tk.LEFT, padx=5)

        validate_concentration = (
            self.frame.register(self.validate_calibration_number),
            "%P",
        )

        concentration_entry = ttk.Entry(
            row_frame, width=10, validate="key", validatecommand=validate_concentration
        )
        concentration_entry.insert(0, "0.0e00")
        concentration_entry.pack(side=tk.LEFT, padx=5)

        mass_label = ttk.Label(row_frame)
        mass_label.configure(text="ppb")
        mass_label.pack(side=tk.LEFT)

        self.rows.append((row_frame, file_label, concentration_entry))

    def delete_row(self, row_frame):
        """
        Delete a specified row from the application.

        Parameters:
        row_frame (ttk.Frame): Frame of the row to be deleted.
        """
        for widget in row_frame.winfo_children():
            widget.destroy()
        row_frame.destroy()
        self.rows = [row for row in self.rows if row[0] != row_frame]

    def select_file(self, row_frame):
        """
        Open a file dialog to select a file and update the corresponding row's file label.

        Parameters:
        row_frame (ttk.Frame): Frame of the row where the file was selected.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            for row in self.rows:
                if row[0] == row_frame:
                    row[1].config(state=tk.NORMAL)
                    row[1].delete(0, tk.END)
                    row[1].insert(0, file_path)
                    row[1].config(state="readonly")

    def calibrate(self):
        """Perform calibration using the selected files and entered concentrations."""
        x = []
        y = []
        s = []
        if not (self.mass_entry.get()):
            messagebox.showerror("Error", "No mass selected for the calibration.")
            return
        mass = int(self.mass_entry.get())
        if len(self.rows) < 3:
            messagebox.showerror(
                "Error", "At least three points are needed for the calibration."
            )
            return
        for _, file_label, concentration_entry in self.rows:
            try:
                file_path = file_label.get()
                with open(file_path, "r", encoding="utf-8") as f:
                    first_line = f.readline()
                    new_masses = [int(x) for x in first_line.split()[2:]]
                    if mass not in new_masses:
                        messagebox.showerror(
                            "Error",
                            f"Mass {mass} not in available masses {new_masses} in file {file_path}.",
                        )
                        return
                    else:
                        signal = np.loadtxt(
                            file_path,
                            delimiter="\t",
                            skiprows=1,
                            usecols=[new_masses.index(mass) + 1],
                        )
            except OSError as e:
                messagebox.showerror(
                    "Error", f"An error occurred while reading the file:\n{e}"
                )
                return
            x.append(float(concentration_entry.get()))
            y.append(np.mean(signal))
            s.append(np.std(signal))

        x = np.array(x)
        y = np.array(y)
        s = np.array(s)
        w = 1 / s**2

        slope, intercept, r2 = wls(x, y, w)
        xp = [x.min(), x.max()]
        pred = np.array([intercept + x.min() * slope, intercept + x.max() * slope])

        plt.figure()
        
        # Plot the results
        plt.errorbar(
            x,
            y,
            yerr=s,
            linestyle="none",
            marker=".",
            color="b",
            capsize=5,
            label="calibration points \pm SD",
        )
        plt.plot(
            xp,
            pred,
            "r--",
            label=f"regression: I = {slope:.4f} * [C] + {intercept:.4f}   (r^2 = {r2:.3f})",
        )
        plt.grid(linestyle=":")
        plt.ylabel("intensity (arbitrary units)")
        plt.xlabel("concentration (ppb)")
        plt.legend()
        plt.show()

    def validate_calibration_number(self, mass):
        """
        Validate if the input string can be converted to a float.

        Parameters:
        mass (str): Input string to validate.

        Returns:
        bool: True if valid float, False otherwise.
        """
        try:
            float(mass)
            return True
        except ValueError:
            self.frame.bell()
            return False


if __name__ == "__main__":
    root = tk.Tk()
    app = CalibrationApp(root)
    root.mainloop()
