#!/usr/bin/env python
# coding: utf-8

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

# ### IMPORTS

import sys

import numpy as np
import scipy.signal
from matplotlib import pyplot as plt

# ### CONFIGURATION

DATADIR = ...  # set to the directory containing data
DATASET = ...  # set to the filename of the data
LOAD_MASSES = (142, 175, 193, 195)
MIN_EVENT_LENGTH = 10
MAX_EVENT_LENGTH = 150
MASS_FOR_SELECTION = 193
MASS_OF_INTEREST = 175

# ### MAIN

# #### Generate numpy array

with open(DATADIR / DATASET) as f:
    available = [int(m) for m in f.readline()[:-1].split("\t")[1:]]
    masses = dict(zip(available, list(range(1, len(available) + 1))))

for mass in LOAD_MASSES:
    assert (
        mass in masses
    ), f"Mass {mass} not in the available masses:{', '.join(m for m in masses)}"

ar = np.loadtxt(
    DATADIR / DATASET,
    delimiter="\t",
    skiprows=1,
    usecols=[masses[m] for m in LOAD_MASSES],
)

print(
    f"Loadad array with {ar.shape[1]} columns and {ar.shape[0]} rows, with a size of {sys.getsizeof(ar)} bytes."
)

mass_dict = dict(zip(LOAD_MASSES, range(len(LOAD_MASSES))))

# #### Get all peaks

events_by_mass = {}
for i in range(ar.shape[1]):
    peaks = scipy.signal.find_peaks(
        ar[:, i], width=(MIN_EVENT_LENGTH, MAX_EVENT_LENGTH)
    )[0]
    if not peaks.size:
        print("Could,'t detect any event for mass", LOAD_MASSES[i])
    peak_widths = scipy.signal.peak_widths(ar[:, i], peaks, rel_height=1.0)
    left = peak_widths[2]
    right = peak_widths[3]
    events_by_mass[LOAD_MASSES[i]] = list(zip(left.astype(int), right.astype(int)))


# #### Get the integral of every event
sum_I = np.array(
    [
        i
        for i in [
            np.sum(ar[side[0] : side[1], mass_dict[MASS_OF_INTEREST]], axis=0)
            for side in events_by_mass[MASS_FOR_SELECTION]
        ]
    ]
)

#

DT = 13e-6  # 13 us == 13e-6 s
FLOW = 0.5  # 30 uL/min == 0.5 uL/s
TE = 0.1  # 0.1 = 10 %
# 1 ppb == 1 ng/mL == 1 fg/uL

X0 = ...  # insert value from calibrate
X1 = ...  # insert value from calibrate
event_mass_interest = (sum_I - X0) / X1 * DT * FLOW / TE

# ### VALIDATION

icp = ...  # load the icp data as an array-like

plt.figure()
plt.boxplot((icp, event_mass_interest[event_mass_interest < 120]))
plt.gca().set_xticklabels(["SC-ICP-MS", "CyTOF"])
plt.gca().set_ylabel("mass (fg)")
plt.show()
