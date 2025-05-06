import os
from pathlib import Path
import h5py
import numpy as np

from parser import *
from utils import *

sample_id_list, number_list = file_searcher("./growths/processes/")

for sample_id, number in zip(sample_id_list, number_list):

    try:
        wri_path = f"./growths/processes/{sample_id}.wri"

        ep_path = None
        for ext in ["ep4", "ep3", "ep2"]:
            ep_path_candidate = f"./growths/processes/{sample_id}.{ext}"
            if os.path.exists(ep_path_candidate):
                ep_path = ep_path_candidate
                break

        refl_path = f"./growths/logs/hm{number}refl.txt"
        pyro_path = f"./growths/logs/hm{number}temp.txt"
        log_path = f"./growths/logs/{sample_id}.log"

        # Required files
        if not os.path.exists(wri_path):
            print(f"Error: Missing {sample_id} wri file, skipping this iteration.")
            continue  
        if ep_path is None:
            print(f"Error: Missing {sample_id} ep file, skipping this iteration.")
            continue

        # Parsing the files
        date, starting_time, duration, sample_th, As_pp, Tdeox, rot = parse_wri(wri_path)

        ending_time = time_calculator(starting_time, duration)
        starting_time = time_converter(date, starting_time)
        ending_time = time_converter(date, ending_time)
        h, m, s = map(int, duration.split(":"))
        duration = h + (m / 60) + (s / 3600)
        if isinstance(As_pp, str):
            As_pp = arsenic_ranges(As_pp)

        substrate_data = parse_substrate(wri_path)

        _, rpm, g_temp, Si_curr, C_curr = parse_wri_layer(wri_path, Tdeox)

        layer_index, loop, r_step, material, dop_element, thickness, g_time, g_rate, x, shutters, pg_rates = parse_layer(ep_path)

        timestamp_r  = dayfraction_r = calib_950 = calib_470 = None
        timestamp_p = dayfraction_p = t_ratio = t_emiss = None
        timestamp_l = time_l = pressure_l = None
        # Optional files
        if os.path.exists(refl_path):
            timestamp_r, dayfraction_r, calib_950, calib_470 = parse_reflectometer(refl_path)
        else:
           print(f"Warning: Missing {refl_path}, skipping sensor parsing.")
        if os.path.exists(pyro_path):
            timestamp_p, dayfraction_p, t_ratio, t_emiss = parse_pyrometer(pyro_path)
        else:
           print(f"Warning: Missing {pyro_path}, skipping sensor parsing.")
        if os.path.exists(log_path):
            timestamp_l, time_l, pressure_l = parse_log(log_path)
        else:
           print(f"Warning: Missing {log_path}, skipping sensor parsing.")

        # Path of the file
        output_directory = Path("./nexus_files/")  
        output_directory.mkdir(parents=True, exist_ok=True)
        # File name
        filename = f"{sample_id}.nxs"
        file_path = output_directory / filename

        # Creation of the file
        with h5py.File(file_path, "w") as hdf:

            # NeXus Structure

            # NXentry: /entry
            hdf.create_group("entry")
            entry = hdf['/entry']
            entry.attrs["NX_class"] = "NXentry"
            entry.attrs["default"] = "entry"
            # /entry/definition
            entry.create_dataset('definition',data='NXepitaxy') # application definition
            # /entry/title
            entry.create_dataset('title', data=f'Growth {sample_id} {date}')
            # /entry/experiment_description
            entry.create_dataset('experiment_description', data='High Mobility Molecular Beam Epitaxy Growth')
            entry['experiment_description'].attrs["description"] = "Deposition technique involved"
            # /entry/start_time
            entry.create_dataset('start_time', data=starting_time)
            # /entry/end_time
            entry.create_dataset('end_time', data=ending_time)
            # /entry/duration
            entry.create_dataset('duration', data=duration)
            entry['duration'].attrs["description"] = 'Total time of growth'
            entry['duration'].attrs["units"] = 'hour'

            date = datetime.strptime(date, "%m-%d-%Y")
            if date < datetime(2023,11,2):

                # NXuser: /entry/user
                entry.create_group("user")
                user = entry['user']
                user.attrs["NX_class"] = "NXuser"
                # /entry/user/name
                user.create_dataset('name',data='Giorgio Biasiol')
                # /entry/user/affiliation
                user.create_dataset('affiliation',data='CNR-IOM')
                # /entry/user/role
                user.create_dataset('role',data='Technology Director')
                # /entry/user/email
                user.create_dataset('email',data='giorgio.biasiol@cnr.it')
                # /entry/user/ORCID
                user.create_dataset('ORCID',data='https://orcid.org/0000-0001-7974-5459')

            else:

                # NXuser: /entry/user_1
                entry.create_group("user_1")
                user_1 =  entry['user_1']
                user_1.attrs["NX_class"] = "NXuser"
                # /entry/user/name
                user_1.create_dataset('name',data='Giorgio Biasiol')
                # /entry/user/affiliation
                user_1.create_dataset('affiliation',data='CNR-IOM')
                # /entry/user/role
                user_1.create_dataset('role',data='Technology Director')
                # /entry/user/email
                user_1.create_dataset('email',data='giorgio.biasiol@cnr.it')
                # /entry/user/ORCID
                user_1.create_dataset('ORCID',data='https://orcid.org/0000-0001-7974-5459')

                # NXuser: /entry/user_2
                entry.create_group("user_2")
                user_2 =  entry['user_2']
                user_2.attrs["NX_class"] = "NXuser"
                # /entry/user/name
                user_2.create_dataset('name',data='Davide Curcio')
                # /entry/user/affiliation
                user_2.create_dataset('affiliation',data='CNR-IOM')
                # /entry/user/role
                user_2.create_dataset('role',data='Research technologist')
                # /entry/user/email
                user_2.create_dataset('email',data='curcio@iom.cnr.it')
                # /entry/user/ORCID
                user_2.create_dataset('ORCID',data='https://orcid.org/0000-0003-2488-3840')


            # NXsample: /entry/sample
            entry.create_group("sample")
            sample = entry['sample']
            sample.attrs["NX_class"] = "NXsample"
            # /entry/sample/name
            sample.create_dataset('name', data=f'{sample_id}')
            # /entry/sample/thickness
            sample.create_dataset('thickness', data=sample_th)
            sample['thickness'].attrs['units'] = 'μm'

            # NXsample: /entry/sample/substrate
            sample.create_group("substrate")
            substrate = sample['substrate']
            substrate.attrs["NX_class"] = "NXsample_component"
            # /entry/sample/substrate/name
            substrate.create_dataset('name', data=substrate_data['name'])
            substrate['name'].attrs["description"] = 'Wafer model'
            # /entry/sample/substrate/chemical_formula
            substrate.create_dataset('chemical_formula', data='GaAs')
            # /entry/sample/substrate/thickness
            if np.isnan(substrate_data['thickness']):
                substrate.create_dataset('thickness', data=500)
            else:
                substrate.create_dataset('thickness', data=substrate_data['thickness'])
            substrate['thickness'].attrs["description"] = 'Thickness of the substrate'
            substrate['thickness'].attrs['units'] = 'μm'
            # /entry/sample/substrate/area
            substrate.create_dataset('area', data=area_converter(substrate_data['area']))
            substrate['area'].attrs['description'] = 'Area of the substrate'
            substrate['area'].attrs['units'] = 'mm^2'
            # /entry/sample/substrate/diameter
            substrate.create_dataset('diameter', data=substrate_data['diameter'])
            substrate['diameter'].attrs['description'] = 'Wafer diameter'
            substrate['diameter'].attrs['units'] = 'in'
            # /entry/sample/substrate/crystal_orientation
            substrate.create_dataset('crystal_orientation', data=substrate_data['orientation'])
            substrate['crystal_orientation'].attrs['description'] = 'Crystallographic direction of the material'
            # /entry/sample/substrate/flat_convention
            substrate.create_dataset('flat_convention', data=substrate_data['convention'])
            substrate['flat_convention'].attrs['description'] = 'Flat convention of the wafer, value accepted are EJ or US' 
            # /entry/sample/substrate/doping
            substrate.create_dataset('doping', data=substrate_data['doping'])
            substrate['doping'].attrs['description'] = 'Doping type and level of the substrate (e.g., p+, n, SI)'
            # /entry/sample/substrate/holder
            substrate.create_dataset('holder', data=substrate_data['holder'])
            substrate['holder'].attrs['description'] = 'Type of substrate holder used in the process' 
            # /entry/sample/substrate/crystalline_structure
            substrate.create_dataset('crystalline_structure', data='single crystal')
            substrate['crystalline_structure'].attrs['description'] = 'Crystalline structure of the material'

            # Initialize the current layer counter
            current_layer = 0

            # Iterate through each layer
            for i in range(len(layer_index)):
                layer_name = f"layer{current_layer + 1:02d}"
                # NXsample_component: /entry/sample/layer
                sample.create_group(f"{layer_name}")
                layer = sample[f'{layer_name}']
                layer.attrs["NX_class"] = "NXsample_component"
                # /entry/sample/layer/name
                layer.create_dataset('name', data=layer_name)
                layer['name'].attrs["description"] = 'Name of the layer'
                # /entry/sample/layer/chemical_formula
                layer.create_dataset('chemical_formula', data=material[i])
                layer['chemical_formula'].attrs["description"] = 'Chemical formula of the layer'
                # /entry/sample/layer/doping
                if material[i] == "Si":
                    layer.create_dataset('doping', data=g_time[i]*10e11)
                    layer['doping'].attrs["description"] = 'Doping value of the layer'
                    layer['doping'].attrs["units"] = 'cm^-2'
                else:
                    layer.create_dataset('doping', data=doping_calculator(dop_element[i],Si_curr[i],C_curr[i],g_rate[i]))
                    layer['doping'].attrs["description"] = 'Doping value of the layer'
                    layer['doping'].attrs["units"] = 'cm^-3'
                # /entry/sample/layer/thickness
                layer.create_dataset('thickness', data=thickness[i])
                layer['thickness'].attrs["units"] = 'Å'
                # /entry/sample/layer/growth_temperature
                layer.create_dataset('growth_temperature', data=g_temp[i])
                layer['growth_temperature'].attrs["description"] = 'Growing temperature of the layer'
                layer['growth_temperature'].attrs["units"] = '°C'
                # /entry/sample/layer/growth_time
                layer.create_dataset('growth_time', data=g_time[i])
                layer['growth_time'].attrs["description"] = 'Growing time of the layer'
                layer['growth_time'].attrs["units"] = 's'
                # /entry/sample/layer/growth_rate
                layer.create_dataset('growth_rate', data=g_rate[i])
                layer['growth_rate'].attrs["description"] = 'Rate at which the layer is grown'
                layer['growth_rate'].attrs["units"] = 'Å/s'
                # /entry/sample/layer/alloy_fraction
                layer.create_dataset('alloy_fraction', data=x[i])
                layer['alloy_fraction'].attrs["description"] = 'Fraction of the first element in a ternary alloy'
                # /entry/sample/layer/rotational_frequency
                if sum(rpm) == 0 and not np.isnan(rot):
                    layer.create_dataset('rotational_frequency', data=rot)
                else:
                    layer.create_dataset('rotational_frequency', data=rpm[i])
                layer['rotational_frequency'].attrs["description"] = 'Rotational frequency of the sample for the current layer'
                layer['rotational_frequency'].attrs["units"] = 'rpm'

                cell_material = ["Gallium", "Gallium", "Aluminium", "Indium"]
                cell_names = ["First Gallium Cell", "Second Gallium Cell", "Aluminium Cell", "Indium Cell"]
                cell_number = 0
                for k, open in enumerate(shutters[i]):
                    if open:
                        cell_number += 1

                        # NXmaterial_source: /entry/sample/layer/material_source
                        layer.create_group(f"cell_{cell_number}")
                        cell = layer[f'cell_{cell_number}']
                        cell.attrs["NX_class"] = "NXmaterial_source"
                        # /entry/sample/layer/cell/name
                        cell.create_dataset('name', data=cell_names[k])
                        cell['name'].attrs["description"] = 'Name of the material source device'
                        # /entry/sample/layer/cell/model
                        cell.create_dataset('model', data='')
                        cell['model'].attrs["description"] = 'Model of the material source device'
                        # /entry/sample/layer/cell/type
                        cell.create_dataset('type', data='effusion_cell')
                        cell['type'].attrs["description"] = 'Type of material source device'
                        # /entry/sample/layer/cell/shutter_status
                        cell.create_dataset('shutter_status', data='open')
                        cell['shutter_status'].attrs["description"] = 'Status of the shutter during this layer growth step'
                        # /entry/sample/layer/cell/material
                        cell.create_dataset('material', data=cell_material[k])
                        cell['material'].attrs["description"] = 'Material of the cell'
                        # /entry/sample/layer/cell/partial_growth_rate
                        cell.create_dataset('partial_growth_rate', data=pg_rates[i][k])
                        cell.attrs["description"] = 'Partial growth rate of the cell'
                        cell.attrs["units"] = 'Å/s'

                if material[i] != "Si" or material[i] != "C":
                    # NXmaterial_source: /entry/sample/layer/material_source
                    layer.create_group(f"cell_{cell_number+1}")
                    cell_as = layer[f'cell_{cell_number+1}']
                    cell_as.attrs["NX_class"] = "NXmaterial_source"
                    # /entry/sample/layer/cell/name
                    cell_as.create_dataset('name', data='Arsenic Cell')
                    cell_as['name'].attrs["description"] = 'Name of the material source device'
                    # /entry/sample/layer/cell/model
                    cell_as.create_dataset('model', data='')
                    cell_as['model'].attrs["description"] = 'Model of the material source device'
                    # /entry/sample/layer/cell/type
                    cell_as.create_dataset('type', data='effusion_cell')
                    cell_as['type'].attrs["description"] = 'Type of material source device'
                    # /entry/sample/layer/cell/shutter_status
                    cell_as.create_dataset('shutter_status', data='open')
                    cell_as['shutter_status'].attrs["description"] = 'Status of the shutter during this layer growth step'
                    # /entry/sample/layer/cell/material
                    cell_as.create_dataset('material', data='Arsenic')
                    cell_as['material'].attrs["description"] = 'Material of the cell'
                    # /entry/sample/layer/cell/partial_pressure
                    cell_as.create_dataset('partial_pressure', data=As_pp)
                    cell_as.attrs["description"] = 'Partial pressure of the cell'
                    cell_as.attrs["units"] = 'Torr'

                current_layer += 1

                # Handle repetition of block of layers 
                if loop[i] > 1 and i > 0:  
                    repeat_count = loop[i] - 1  # Until now there is already an occurence of the layers to repeat
                    for repeat in range(repeat_count):
                        # Repeat layers starting from the return step r_step[i]
                        for j in range(r_step[i]-1, i+1):
                            layer_name = f"layer{current_layer + 1:02d}"
                            # NXsample_component: /entry/sample/layer
                            sample.create_group(f"{layer_name}")
                            layer = sample[f'{layer_name}']
                            layer.attrs["NX_class"] = "NXsample_component"
                            # /entry/sample/layer/name
                            layer.create_dataset('name', data=layer_name)
                            # /entry/sample/layer/chemical_formula
                            layer.create_dataset('chemical_formula', data=material[j])
                            if material[j] == "Si":
                                layer.create_dataset('doping', data=g_time[j]*10e11)
                                layer['doping'].attrs["description"] = 'Doping value of the layer'
                                layer['doping'].attrs["units"] = 'cm^-2'
                            else:
                                layer.create_dataset('doping', data=doping_calculator(dop_element[j],Si_curr[j],C_curr[j],g_rate[j]))
                                layer['doping'].attrs["description"] = 'Doping value of the layer'
                                layer['doping'].attrs["units"] = 'cm^-3'
                            # /entry/sample/layer/thickness
                            layer.create_dataset('thickness', data=thickness[j])
                            layer['thickness'].attrs["units"] = 'Å'
                            # /entry/sample/layer/growth_temperature
                            layer.create_dataset('growth_temperature', data=g_temp[j])
                            layer['growth_temperature'].attrs["description"] = 'Growing temperature of the layer'
                            layer['growth_temperature'].attrs["units"] = '°C'
                            # /entry/sample/layer/growth_time
                            layer.create_dataset('growth_time', data=g_time[j])
                            layer['growth_time'].attrs["description"] = 'Growing time of the layer'
                            layer['growth_time'].attrs["units"] = 's'
                            # /entry/sample/layer/growth_rate
                            layer.create_dataset('growth_rate', data=g_rate[j])
                            layer['growth_rate'].attrs["description"] = 'Rate at which the layer is grown'
                            layer['growth_rate'].attrs["units"] = 'Å/s'
                            # /entry/sample/layer/alloy_fraction
                            layer.create_dataset('alloy_fraction', data=x[j])
                            layer['alloy_fraction'].attrs["description"] = 'Fraction of the first element in a ternary alloy'
                            # /entry/sample/layer/rotational_frequency
                            if sum(rpm) == 0 and not np.isnan(rot):
                                layer.create_dataset('rotational_frequency', data=rot)
                            else:
                                layer.create_dataset('rotational_frequency', data=rpm[j])
                            layer['rotational_frequency'].attrs["description"] = 'Rotational frequency of the sample for the current layer'
                            layer['rotational_frequency'].attrs["units"] = 'rpm'
                            
                            cell_material = ["Gallium", "Gallium", "Aluminium", "Indium"]
                            cell_names = ["First Gallium Cell", "Second Gallium Cell", "Aluminium Cell", "Indium Cell"]
                            cell_number = 0
                            for k, open in enumerate(shutters[j]):
                                if open:
                                    cell_number += 1

                                    # NXmaterial_source: /entry/sample/layer/material_source
                                    layer.create_group(f"cell_{cell_number}")
                                    cell = layer[f'cell_{cell_number}']
                                    cell.attrs["NX_class"] = "NXmaterial_source"
                                    # /entry/sample/layer/cell/name
                                    cell.create_dataset('name', data=cell_names[k])
                                    cell['name'].attrs["description"] = 'Name of the material source device'
                                    # /entry/sample/layer/cell/model
                                    cell.create_dataset('model', data='')
                                    cell['model'].attrs["description"] = 'Model of the material source device'
                                    # /entry/sample/layer/cell/type
                                    cell.create_dataset('type', data='effusion_cell')
                                    cell['type'].attrs["description"] = 'Type of material source device'
                                    # /entry/sample/layer/cell/shutter_status
                                    cell.create_dataset('shutter_status', data='open')
                                    cell['shutter_status'].attrs["description"] = 'Status of the shutter during this layer growth step'
                                    # /entry/sample/layer/cell/material
                                    cell.create_dataset('material', data=cell_material[k])
                                    cell['material'].attrs["description"] = 'Material of the cell'
                                    # /entry/sample/layer/cell/partial_growth_rate
                                    cell.create_dataset('partial_growth_rate', data=pg_rates[j][k])
                                    cell.attrs["description"] = 'Partial growth rate of the cell'
                                    cell.attrs["units"] = 'Å/s'

                            # NXmaterial_source: /entry/sample/layer/material_source
                            layer.create_group(f"cell_{cell_number+1}")
                            cell_as = layer[f'cell_{cell_number+1}']
                            cell_as.attrs["NX_class"] = "NXmaterial_source"
                            # /entry/sample/layer/cell/name
                            cell_as.create_dataset('name', data='Arsenic Cell')
                            cell_as['name'].attrs["description"] = 'Name of the material source device'
                            # /entry/sample/layer/cell/model
                            cell_as.create_dataset('model', data='')
                            cell_as['model'].attrs["description"] = 'Model of the material source device'
                            # /entry/sample/layer/cell/type
                            cell_as.create_dataset('type', data='effusion_cell')
                            cell_as['type'].attrs["description"] = 'Type of material source device'
                            # /entry/sample/layer/cell/shutter_status
                            cell_as.create_dataset('shutter_status', data='open')
                            cell_as['shutter_status'].attrs["description"] = 'Status of the shutter during this layer growth step'
                            # /entry/sample/layer/cell/material
                            cell_as.create_dataset('material', data='Arsenic')
                            cell_as['material'].attrs["description"] = 'Material of the cell'
                            # /entry/sample/layer/cell/partial_pressure
                            cell_as.create_dataset('partial_pressure', data=As_pp)
                            cell_as.attrs["description"] = 'Partial pressure of the cell'
                            cell_as.attrs["units"] = 'Torr'

                            current_layer += 1

            # NXinstrument: /entry/instrument
            entry.create_group("instrument")
            instrument = entry['instrument']
            instrument.attrs["NX_class"] = "NXinstrument"

            # /entry/instrument/chamber
            instrument.create_group("chamber")
            chamber = instrument['chamber']
            chamber.attrs["NX_class"] = "NXenvironment"
            # /entry/instrument/chamber/name
            chamber.create_dataset('name',data='Veeco Gen II')
            chamber['name'].attrs['description'] = 'Model of the growing chamber'
            # /entry/instrument/chamber/type
            chamber.create_dataset('type',data='Ultra High Vacuum (UHV) Chamber')
            chamber['type'].attrs['description'] = 'Type of growing chamber'
            # /entry/instrument/chamber/description
            chamber.create_dataset('description',data='High mobility III-V MBE system, equipped with As (2X), Ga (2X), Al, In effusion cells and Si and C doping sources.')
            chamber['description'].attrs['description'] = 'Information of the chamber'
            # /entry/instrument/chamber/program
            chamber.create_dataset('program',data='LabView program developed in-house')
            chamber['program'].attrs['description'] = 'Program controlling the apparatus'

            # /entry/instrument/chamber/sensor_1
            chamber.create_group(f"sensor_1")
            chamber['sensor_1'].attrs["NX_class"] = "NXsensor"
            # /entry/instrument/chamber/sensor_1/name
            chamber['sensor_1'].create_dataset('name', data='Reflectometer 950')
            chamber['sensor_1/name'].attrs['description'] = 'Name of sensor'
            # /entry/instrument/chamber/sensor_1/model
            chamber['sensor_1'].create_dataset('model', data='')
            chamber['sensor_1/model'].attrs['description'] = 'Model of sensor'
            # /entry/instrument/chamber/sensor_1/measurement
            chamber['sensor_1'].create_dataset('measurement', data='reflectivity')
            chamber['sensor_1/measurement'].attrs['description'] = 'Physical quantity being measured'
            if os.path.exists(refl_path):
                # /entry/instrument/chamber/sensor_1/value
                chamber['sensor_1'].create_dataset('value',data=np.mean(calib_950))
                chamber['sensor_1/value'].attrs['description'] = 'Average value of the signal'
                # /entry/instrument/chamber/sensor_1/value_log
                chamber['sensor_1'].create_group("value_log")
                chamber['sensor_1/value_log'].attrs["NX_class"] = "NXlog"
                # /entry/instrument/chamber/sensor_1/value_log/time
                chamber['sensor_1/value_log'].create_dataset('time', data=dayfraction_converter(dayfraction_r))
                chamber['sensor_1/value_log/time'].attrs['start'] = starting_time
                chamber['sensor_1/value_log/time'].attrs['unit'] = 's'
                chamber['sensor_1/value_log/time'].attrs['target'] = '/entry/instrument/chamber/sensor_1/value_log/time'
                # /entry/instrument/chamber/sensor_1/value_log/value
                chamber['sensor_1/value_log'].create_dataset('value', data=calib_950)
                chamber['sensor_1/value_log/value'].attrs['description'] = 'Reflectivity of the sample'
                chamber['sensor_1/value_log/value'].attrs['target'] = '/entry/instrument/chamber/sensor_1/value_log/value'

                # /entry/950_reflectivity_log
                entry.create_group('950_reflectivity_log')
                refl950_log = entry['950_reflectivity_log']
                refl950_log.attrs["NX_class"] = "NXdata"
                refl950_log["value"] = chamber['sensor_1/value_log/value']
                refl950_log["time"] = chamber['sensor_1/value_log/time']
                refl950_log.attrs["signal"] = "value"
                refl950_log.attrs["axes"] = "time"
                refl950_log.attrs["title"] = "950 nm Reflectivity Log"

            # /entry/instrument/chamber/sensor_2
            chamber.create_group(f"sensor_2")
            chamber['sensor_2'].attrs["NX_class"] = "NXsensor"
            # /entry/instrument/chamber/sensor_2/name
            chamber['sensor_2'].create_dataset('name', data='Reflectometer 470')
            chamber['sensor_2/name'].attrs['description'] = 'Name of sensor'
            # /entry/instrument/chamber/sensor_2/model
            chamber['sensor_2'].create_dataset('model', data='')
            chamber['sensor_2/model'].attrs['description'] = 'Model of sensor'
            # /entry/instrument/chamber/sensor_2/measurement
            chamber['sensor_2'].create_dataset('measurement', data='reflectivity')
            chamber['sensor_2/measurement'].attrs['description'] = 'Physical quantity being measured'
            if os.path.exists(refl_path):
                # /entry/instrument/chamber/sensor_2/value
                chamber['sensor_2'].create_dataset('value',data=np.mean(calib_470))
                chamber['sensor_2/value'].attrs['description'] = 'Average value of the signal'
                # /entry/instrument/chamber/sensor_2/value_log
                chamber['sensor_2'].create_group("value_log")
                chamber['sensor_2/value_log'].attrs["NX_class"] = "NXlog"
                # /entry/instrument/chamber/sensor_2/value_log/time
                chamber['sensor_2/value_log'].create_dataset('time', data=dayfraction_converter(dayfraction_r))
                chamber['sensor_2/value_log/time'].attrs['start'] = starting_time
                chamber['sensor_2/value_log/time'].attrs['unit'] = 's'
                chamber['sensor_2/value_log/time'].attrs['target'] = '/entry/instrument/chamber/sensor_2/value_log/time'
                # /entry/instrument/chamber/sensor_2/value_log/value
                chamber['sensor_2/value_log'].create_dataset('value', data=calib_470)
                chamber['sensor_2/value_log/value'].attrs['description'] = 'Reflectivity of the sample'
                chamber['sensor_2/value_log/value'].attrs['target'] = '/entry/instrument/chamber/sensor_2/value_log/value'

                # /entry/470_reflectivity_log
                entry.create_group('470_reflectivity_log')
                refl470_log = entry['470_reflectivity_log']
                refl470_log.attrs["NX_class"] = "NXdata"
                refl470_log["value"] = chamber['sensor_2/value_log/value']
                refl470_log["time"] = chamber['sensor_2/value_log/time']
                refl470_log.attrs["signal"] = "value"
                refl470_log.attrs["axes"] = "time"
                refl470_log.attrs["title"] = "470 nm Reflectivity Log"
                

            # /entry/instrument/chamber/sensor_3
            chamber.create_group("sensor_3")
            chamber['sensor_3'].attrs["NX_class"] = "NXsensor"
            # /entry/instrument/chamber/sensor_3/name
            chamber['sensor_3'].create_dataset('name', data='One-channel pyrometer')
            chamber['sensor_3/name'].attrs['description'] = 'Name of the sensor'
            # /entry/instrument/chamber/sensor_3/model
            chamber['sensor_3'].create_dataset('model', data='')
            chamber['sensor_3/model'].attrs['description'] = 'Model of the sensor'
            # /entry/instrument/chamber/sensor_3/measurement
            chamber['sensor_3'].create_dataset('measurement', data='rate_temperature')
            chamber['sensor_3/measurement'].attrs['description'] = 'Physical quantity being measured'
            if os.path.exists(pyro_path):
                # /entry/instrument/chamber/sensor_3/value
                chamber['sensor_3'].create_dataset('value',data=np.mean(t_ratio))
                chamber['sensor_3/value'].attrs['description'] = 'Average value of the signal'
                # /entry/instrument/chamber/sensor_3/value_log
                chamber['sensor_3'].create_group("value_log")
                chamber['sensor_3/value_log'].attrs["NX_class"] = "NXlog"
                # /entry/instrument/chamber/sensor_3/value_log/time
                chamber['sensor_3/value_log'].create_dataset('time', data=dayfraction_converter(dayfraction_p))
                chamber['sensor_3/value_log/time'].attrs['start'] = starting_time
                chamber['sensor_3/value_log/time'].attrs['unit'] = 's'
                chamber['sensor_3/value_log/time'].attrs['target'] = '/entry/instrument/chamber/sensor_3/value_log/time'
                # /entry/instrument/chamber/sensor_3/value_log/value
                chamber['sensor_3/value_log'].create_dataset('value', data=t_ratio)
                chamber['sensor_3/value_log/value'].attrs['description'] = 'Rate temperature'
                chamber['sensor_3/value_log/value'].attrs['target'] = '/entry/instrument/chamber/sensor_3/value_log/value'

                # /entry/rate_temperature_log
                entry.create_group('rate_temperature_log')
                rate_log = entry['rate_temperature_log']
                rate_log.attrs["NX_class"] = "NXdata"
                rate_log["value"] = chamber['sensor_3/value_log/value']
                rate_log["time"] = chamber['sensor_3/value_log/time']
                rate_log.attrs["signal"] = "value"
                rate_log.attrs["axes"] = "time"
                rate_log.attrs["title"] = "Rate Temperature Log"

            # /entry/instrument/chamber/sensor_4
            chamber.create_group("sensor_4")
            chamber['sensor_4'].attrs["NX_class"] = "NXsensor"
            # /entry/instrument/chamber/sensor_4/name
            chamber['sensor_4'].create_dataset('name', data='Two-channel pyrometer')
            chamber['sensor_4/name'].attrs['description'] = 'Name of the sensor'
            # /entry/instrument/chamber/sensor_4/model
            chamber['sensor_4'].create_dataset('model', data='')
            chamber['sensor_4/model'].attrs['description'] = 'Model of the sensor'
            # /entry/instrument/chamber/sensor_4/measurement
            chamber['sensor_4'].create_dataset('measurement', data='emissivity_temperature')
            chamber['sensor_4/measurement'].attrs['description'] = 'Physical quantity being measured'
            if os.path.exists(pyro_path):
                # /entry/instrument/chamber/sensor_4/value
                chamber['sensor_4'].create_dataset('value',data=np.mean(t_emiss))
                chamber['sensor_4/value'].attrs['description'] = 'Average value of the signal'
                chamber['sensor_4/value'].attrs['unit'] = '°C'
                # /entry/instrument/chamber/sensor_4/value_log
                chamber['sensor_4'].create_group("value_log")
                chamber['sensor_4/value_log'].attrs["NX_class"] = "NXlog"
                # /entry/instrument/chamber/sensor_4/value_log/time
                chamber['sensor_4/value_log'].create_dataset('time', data=dayfraction_converter(dayfraction_p))
                chamber['sensor_4/value_log/time'].attrs['start'] = starting_time
                chamber['sensor_4/value_log/time'].attrs['unit'] = 's'
                chamber['sensor_4/value_log/time'].attrs['target'] = '/entry/instrument/chamber/sensor_4/value_log/time'
                # /entry/instrument/chamber/sensor_4/value_log/value
                chamber['sensor_4/value_log'].create_dataset('value', data=t_emiss)
                chamber['sensor_4/value_log/value'].attrs['description'] = 'Emissivity temperature'
                chamber['sensor_4/value_log/value'].attrs['unit'] = '°C'
                chamber['sensor_4/value_log/value'].attrs['target'] = '/entry/instrument/chamber/sensor_4/value_log/value'

                # /entry/emissivity_temperature_log
                entry.create_group('emissivity_temperature_log')
                emiss_log = entry['emissivity_temperature_log']
                emiss_log.attrs["NX_class"] = "NXdata"
                emiss_log["value"] = chamber['sensor_4/value_log/value']
                emiss_log["time"] = chamber['sensor_4/value_log/time']
                emiss_log.attrs["signal"] = "value"
                emiss_log.attrs["axes"] = "time"
                emiss_log.attrs["title"] = "Emissivity Temperature Log (°C)"

            # /entry/instrument/chamber/sensor_5
            chamber.create_group("sensor_5")
            chamber['sensor_5'].attrs['NX_class'] = "NXsensor" 
            # /entry/instrument/chamber/sensor_5/name
            chamber['sensor_5'].create_dataset('name',data='Ion gauge')
            chamber['sensor_5/name'].attrs['description'] = 'Name of the ion gauge'
            # /entry/instrument/chamber/sensor_5/model
            chamber['sensor_5'].create_dataset('model',data='')
            chamber['sensor_5/model'].attrs['description'] = 'Model of the ion gauge' 
            # /entry/instrument/chamber/sensor_5/measurement
            chamber['sensor_5'].create_dataset('measurement',data='pressure')
            chamber['sensor_5/measurement'].attrs['description'] = 'Physical quantity being measured'
            # /entry/instrument/chamber/sensor_5/value
            chamber['sensor_5'].create_dataset('value',data=1e-12)
            chamber['sensor_5/value'].attrs['description'] = 'Nominal value of the signal'
            chamber['sensor_5/value'].attrs['unit'] = 'mbar'
            if os.path.exists(log_path):
                # /entry/instrument/chamber/sensor_5/temperature
                chamber['sensor_5'].create_group("value_log")
                chamber['sensor_5/value_log'].attrs["NX_class"] = "NXlog"
                # /entry/instrument/chamber/sensor_5/temperature/time
                chamber['sensor_5/value_log'].create_dataset('time', data=log_time_converter(time_l))
                chamber['sensor_5/value_log/time'].attrs['start'] = starting_time
                chamber['sensor_5/value_log/time'].attrs['unit'] = 's'
                chamber['sensor_5/value_log/time'].attrs['target'] = '/entry/instrument/chamber/sensor_5/temperature/time'
                # /entry/instrument/chamber/sensor_5/temperature/value
                chamber['sensor_5/value_log'].create_dataset('value', data=pressure_l)
                chamber['sensor_5/value_log/value'].attrs['description'] = 'Pressure'
                chamber['sensor_5/value_log/value'].attrs['unit'] = 'Torr'
                chamber['sensor_5/value_log/value'].attrs['target'] = '/entry/instrument/chamber/sensor_5/temperature/value'

                # /entry/pressure_log
                entry.create_group('pressure_log')
                pressure_log = entry['pressure_log']
                pressure_log.attrs["NX_class"] = "NXdata"
                pressure_log["value"] = chamber['sensor_5/value_log/value']
                pressure_log["time"] = chamber['sensor_5/value_log/time']
                pressure_log.attrs["signal"] = "value"
                pressure_log.attrs["axes"] = "time"
                pressure_log.attrs["title"] = "Pressure Log (Torr)"

            # NXcooling_device: /entry/instrument/chamber/cooling_device
            chamber.create_group("cooling_device")
            cooling_device = chamber['cooling_device']
            cooling_device.attrs["NX_class"] = "NXcooling_device"
            # /entry/instrument/chamber/cooling_device/name
            cooling_device.create_dataset('name',data='Cooling shroud')
            cooling_device['name'].attrs['description'] = 'Name of the cooling system'
            # /entry/instrument/chamber/cooling_device/model
            cooling_device.create_dataset('model',data='')
            cooling_device['model'].attrs['description'] = 'Model of the cooling system'
            # /entry/instrument/chamber/cooling_device/cooling_mode
            cooling_device.create_dataset('cooling_mode',data='liquid_nitrogen')
            cooling_device['cooling_mode'].attrs['description'] = 'Mode used to cool the chamber'
            # /entry/instrument/chamber/cooling_device/temperature
            cooling_device.create_dataset('temperature',data=77)
            cooling_device['temperature'].attrs['description'] = 'Nominal temperature of the system'
            cooling_device['temperature'].attrs['units'] = 'K'

            
        if os.path.exists(file_path):
            print(f"Success: File {filename} created successfully at {file_path}.")
        else:
            print(f"Error: Failed to create {filename}.")

    except Exception as e:
        print(f"Error processing {sample_id}: {e}")