# Photoluminescence GUI

This repository contains the code for the Guided User Interface (GUI) developed for the Photoluminescence beamline @ EuroFEL Support Laboratory (CNR-ISM, Rome).

## Overview

The GUI allows to generate .nxs files directly from .spc files. Since the executable files are too large to be uploaded to GitHub, you can download the source code and generate your own executable using PyInstaller.

### .spc File Output

The `.spc` files are the output of a **Horiba iHR320 - Jobin Yvon** spectrometer. We modified certain parameters in the spectrometer's acquisition software to associate the following metadata dictionary entries with experiment-specific information:
- `PROJECT`: Sample name  
- `SITE`: Temperature at which the experiment was conducted  
- `TITLE`: Title of the experiment

A sample `.spc` file is also provided to allow testing of the GUI.

### NeXus Format Integration for Transient Absorption Beamline

A proposed **NeXus file** is also included in the repository. This file served as the starting point for modifying the LabVIEW acquisition interface to support NeXus-compatible metadata output.

## Getting Started

To use the GUI:
1. Download the code.
2. use PyInstaller to generate a platform-specific executable from the source code.
3. Download the sample .spc and play with the GUI's features!

## Contact

For questions or contributions, feel free to open an issue!

