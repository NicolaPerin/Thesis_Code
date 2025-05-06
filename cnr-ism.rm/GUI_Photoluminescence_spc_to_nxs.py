import wx
import os
import threading
import h5py
import spc
from pathlib import Path
from datetime import datetime

class ConversionApp(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(600, 500))

        self.SetSizeHints(600, 500, 600, 500)

        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Select the folder containing .spc files
        self.select_folder_btn = wx.Button(self.panel, label="Select folder with .spc files")
        self.select_folder_btn.Bind(wx.EVT_BUTTON, self.on_select_folder)
        self.sizer.Add(self.select_folder_btn, 0, wx.ALL, 10)

        self.file_listbox = wx.CheckListBox(self.panel, size=(600, 150))
        self.sizer.Add(self.file_listbox, 0, wx.ALL, 10)

        # Select all button
        self.select_all_btn = wx.Button(self.panel, label="Select all files")
        self.select_all_btn.Bind(wx.EVT_BUTTON, self.on_select_all)
        self.sizer.Add(self.select_all_btn, 0, wx.ALL, 10)

        #  Select the output folder
        self.select_output_btn = wx.Button(self.panel, label="Select output folder")
        self.select_output_btn.Bind(wx.EVT_BUTTON, self.on_select_output_folder)
        self.sizer.Add(self.select_output_btn, 0, wx.ALL, 10)
       
        #  Create a text control to show the output folder path
        self.output_folder_text = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE, size=(300, 35))
        self.sizer.Add(self.output_folder_text, 0, wx.ALL | wx.EXPAND, 10)

        #  Progress bar
        self.progress_bar = wx.Gauge(self.panel, range=100, size=(600, 25))
        self.sizer.Add(self.progress_bar, 0, wx.ALL, 10)

        #  Start the conversion
        self.convert_btn = wx.Button(self.panel, label="Start Conversion")
        self.convert_btn.Bind(wx.EVT_BUTTON, self.on_convert)
        self.sizer.Add(self.convert_btn, 0, wx.ALL, 10)

        self.panel.SetSizer(self.sizer)
        
        self.Show()

        # Variables for selected folders
        self.input_folder = ""
        self.output_folder = ""
        self.update_output_folder_text()
        self.files_to_convert = []

    def on_select_folder(self, event):
        """Select the folder containing .spc files"""
        dialog = wx.DirDialog(self, "Select a folder", style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.input_folder = dialog.GetPath()
            # List .spc files
            self.files_to_convert = [f for f in os.listdir(self.input_folder) if f.endswith('.spc')]
            self.file_listbox.Clear()
            self.file_listbox.Append(self.files_to_convert)

        dialog.Destroy()

    def on_select_output_folder(self, event):
        """Select the output folder"""
        dialog = wx.DirDialog(self, "Select output folder", style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.output_folder = dialog.GetPath()
            # Update the output folder path in the GUI
            self.update_output_folder_text()
        dialog.Destroy()

    def update_output_folder_text(self):
        """Update the output folder path in the text control"""
        self.output_folder_text.SetValue(self.output_folder if self.output_folder else "No output folder selected")

    def on_convert(self, event):
        """Start the conversion of the files"""
        # Get selected files
        selected_files = [self.files_to_convert[i] for i in range(len(self.files_to_convert)) if self.file_listbox.IsChecked(i)]

        if not selected_files:
            wx.MessageBox("Select at least one file to convert", "Error", wx.OK | wx.ICON_ERROR)
            return

        if not self.output_folder:
            wx.MessageBox("Select an output folder", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Start conversion in a separate thread to avoid blocking the GUI
        
        self.convert_btn.Disable()
        self.thread = threading.Thread(target=self.convert_files, args=(selected_files,))
        self.thread.start()

    def convert_files(self, selected_files):
        """Converts .spc files to neXus (HDF5) format"""
        total_files = len(selected_files)
        for i, file in enumerate(selected_files):
            input_file_path = os.path.join(self.input_folder, file)
            # Generate a unique output file name for each file
            output_file_name = f"{Path(file).stem}.nxs"
            output_file_path = os.path.join(self.output_folder, output_file_name)

            # Convert each file (call conversion function)
            try:
                self.convert_spc_to_nexus(input_file_path, output_file_path)
            except Exception as e:
                wx.CallAfter(self.show_error, str(e))
                return

            # Update progress bar and text
            wx.CallAfter(self.update_progress, i + 1, total_files)

        wx.CallAfter(self.on_conversion_complete)

    def convert_spc_to_nexus(self, input_file, output_file):
        """Converts an individual .spc file to neXus (HDF5) format"""
        file = spc.File(input_file)

        # Create the neXus file using h5py
        with h5py.File(output_file, "w") as f:
            f.attrs['default'] = 'entry'
            f.create_group("entry")
            f['/entry'].attrs["NX_class"] = "NXentry"
            f['/entry'].attrs["default"] = "data"
            f['/entry'].create_dataset('definition', data='NXoptical_spectroscopy')
            f['/entry/definition'].attrs["version"] = 'v2024.02'
            f['/entry/definition'].attrs["URL"] = 'https://github.com/FAIRmat-NFDI/nexus_definitions/blob/fd58c03d6c1be6469c2aff92ae7649fe5ad38a63/contributed_definitions/NXoptical_spectroscopy.nxdl.xml'

            # Add metadata from the .spc file
            
            f['/entry'].create_dataset('end_time', data=file.log_dict[b'DATE '])
            f['/entry'].create_dataset('title', data=file.log_dict[b'TITLE '])
            f['/entry'].create_dataset('experiment_type', data='Photoluminescence')
            
            # Instrument group 
            
            f['/entry'].create_group("instrument")
            f['/entry/instrument'].attrs['NX_class'] = "NXinstrument"
           
            # Source group
            
            f['/entry/instrument'].create_group("source_excitation")
            f['/entry/instrument/source_excitation'].attrs["NX_class"] = "NXsource"
            f['/entry/instrument/source_excitation'].create_dataset('type', data='Laser')
            f['/entry/instrument/source_excitation'].create_dataset('wavelength', data=file.log_dict[b'EXCIT_LINE '])
            f['/entry/instrument/source_excitation/wavelength'].attrs['units'] = 'nm'

            # Beam group
           
            f['/entry/instrument'].create_group("beam_excitation")
            f['/entry/instrument/beam_excitation'].attrs["NX_class"] = 'NXbeam'
            f['/entry/instrument/beam_excitation'].create_dataset('type', data = 'Laser')
            f['/entry/instrument/beam_excitation'].create_dataset('wavelength', data = file.log_dict[b'EXCIT_LINE '])
            f['/entry/instrument/beam_excitation/wavelength'].attrs['units'] = 'nm'
            f['/entry/instrument/beam_excitation'].create_dataset('fluence', data = file.log_dict[b'REMARK '])

            # Detector group
            
            f['/entry/instrument'].create_group("detector")
            f['/entry/instrument/detector'].attrs["NX_class"] = 'NXdetector'
            f['/entry/instrument/detector'].create_dataset('detector_type', data='CCD')
            f['/entry/instrument/detector'].create_dataset('count_time', data=file.log_dict[b'ACQ. TIME (S) '])
            f['/entry/instrument/detector/count_time'].attrs['units'] = "s"

            # Monochromator group
            
            f['/entry/instrument'].create_group("monochromator")
            f['/entry/instrument/monochromator'].attrs['NX_class'] = "NXmonochromator"
            f['/entry/instrument/monochromator'].create_dataset('entrance_slit', data=file.log_dict[b'FRONT ENTRANCE SLIT '])
            f['/entry/instrument/monochromator'].create_dataset('exit_slit', data=file.log_dict[b'FRONT EXIT SLIT '])
            f['/entry/instrument/monochromator'].create_dataset('wavelength', data=file.x)
            f['/entry/instrument/monochromator/wavelength'].attrs['units'] = 'nm'

            # Sample group
            
            f['/entry'].create_group("sample")
            f['/entry/sample'].attrs['NX_class'] = "NXsample"
            f['/entry/sample'].create_dataset('sample_name', data=file.log_dict[b'PROJECT '])
            #f['/entry/sample'].create_dataset('chemical_formula', data=file.log_dict[b'PROJECT '])
            f['/entry/sample'].create_dataset('temperature', data=file.log_dict[b'SITE '])

            # User group

            f['/entry'].create_group("user")
            f['/entry/user'].attrs['NXclass'] = "NXuser"
            f['/entry/user'].create_dataset('name', data = 'EFSL Staff')
            f['/entry/user'].create_dataset('e-mail', data = 'efsl@ism.cnr.it')
            f['/entry/user'].create_dataset('affiliation', data = 'CNR-ISM - Roma Tor Vergata  - EuroFEL Support Laboratory - http://efsl.ism.cnr.it/en/')

            # Data group
            
            f['/entry'].create_group("data")
            f['/entry/data'].attrs['NX_class'] = "NXdata"
            f['/entry/data'].create_dataset("intensity", data=file.sub[0].y)
            f['/entry/data'].create_dataset("wavelength", data=file.x)
            f['/entry/data'].attrs["signal"] = "intensity"
            f['/entry/data/intensity'].attrs["units"] = "arbitrary units"
            f['/entry/data/wavelength'].attrs["units"] = "nm"

    def update_progress(self, current, total):
        """Update the progress bar and status"""
        progress = (current * 100) // total
        self.progress_bar.SetValue(progress)
        wx.CallAfter(self.SetStatusText, f"Converting file {current}/{total}...")

    def show_error(self, error_message):
        """Show an error message"""
        wx.MessageBox(f"Error during conversion: {error_message}", "Error", wx.OK | wx.ICON_ERROR)

    def on_conversion_complete(self):
        """Complete the conversion and reset the GUI"""
        wx.MessageBox("Conversion completed successfully!", "Completed", wx.OK | wx.ICON_INFORMATION)
        self.convert_btn.Enable()
        self.progress_bar.SetValue(0)

    def on_select_all(self, event):
        """Select all files in the checklist"""
        for i in range(len(self.files_to_convert)):
            self.file_listbox.Check(i, True)

if __name__ == "__main__":
    app = wx.App(False)  # Initialize wxPython application
    frame = ConversionApp(None, "Convert .spc Files to NeXus")
    app.MainLoop()  # Start the wxPython event loop
