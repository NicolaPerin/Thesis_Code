import re
import sys
import numpy as np
from datetime import datetime

def parse_wri(file_path):
    with open(file_path, "r", encoding="latin1") as file:
        lines = file.readlines()

    date = ""
    starting_time = ""
    duration = ""
    sample = ""
    flux = np.nan
    Tdeox = np.nan
    rot = np.nan

    # Track which values have already been set to avoid problems with multiple process files
    got_date = got_duration = got_thickness = got_flux = got_Tdeox = got_rot = False

    for line in lines:
        # Date and time of the growth
        if not got_date and ("Grown" in line or "Last" in line):
            match_d = re.search(r"\d{2}[-_/]\d{2}[-_/]\d{2,4}", line)
            match_t = re.search(r"\d{2}:\d{2}:\d{2}", line)
            if match_t:
                starting_time = match_t.group(0)
            if match_d:
                raw_date = match_d.group(0)
                # Convert different date formats into US format (MM-DD-YYYY)
                try:
                    if "_" in raw_date and len(raw_date) == 8:
                        date = datetime.strptime(raw_date, "%m_%d_%y").strftime("%m-%d-%Y")
                    elif "/" in raw_date:
                        if len(raw_date.split("/")[-1]) == 4:  # 4-digit year
                            date = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%m-%d-%Y")
                        else:
                            date = datetime.strptime(raw_date, "%d/%m/%y").strftime("%m-%d-%Y")
                    elif "-" in raw_date:
                        date = datetime.strptime(raw_date, "%m-%d-%Y").strftime("%m-%d-%Y")
                    else:
                        date = raw_date
                    got_date = True
                except Exception as e:
                    print(f"Error parsing date: {raw_date} -> {e}")

        # Growth total time
        if not got_duration and "Total time" in line:
            match = re.search(r"\d{2}:\d{2}:\d{2}", line)
            if match:
                duration = match.group(0)
                got_duration = True

        # Sample total thickness
        if not got_thickness and "Total thickness" in line:
            match = re.search(r"(\d+(\.\d+)?|\.\d+)", line)
            if match:
                sample = float(match.group(0))
                got_thickness = True

        # Arsenic partial pressure
        if not got_flux:
            if line.strip().lower().startswith("as"):
                match_as = re.search(r'(?:flux~|~)\s*([\dEe\+\-\.]+)', line)
                if match_as:
                    flux = match_as.group(1)
                    got_flux = True

        # Deoxidation temperature
        if not got_Tdeox:
            match_deox = re.search(r"(?:Tdeox|deox|Pdeox)\s*=?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)(?=[^0-9.]|$)", line)
            if match_deox:
                Tdeox = float(match_deox.group(1))
                got_Tdeox = True

        # Nominal rotation frequency
        if not got_rot:
            match_rot = re.search(r"(?:rot|rotation)\s*[:=]?\s*(\d+)\s*rpm", line)
            if match_rot:
                rot = int(match_rot.group(1) or match_rot.group(2))
                got_rot = True

    return date, starting_time, duration, sample, flux, Tdeox, rot

# ----------------------------------

def parse_substrate(file_path):
    with open(file_path, "r", encoding="latin1") as file:
        lines = file.readlines()

    substrate_lines = []

    for i, line in enumerate(lines):
        if "Substrate" in line:
            substrate_lines.append(line.strip())
            substrate_lines.append(lines[i + 1].strip())

    substrate_text = " ".join(substrate_lines)

    pattern = re.compile(r"""
        Substrate:\s+
        (?P<orientation>\(?\d{3}\)[AB]?)                    # Crystal orientation
        (?:\s+\d+deg\s+off(?:\s+to\s+[-\d]+)?)?             # Optional miscut
        \s*
        (?P<doping>SI|p\+|p-|n\+|n-)                        # Doping
        (?:\s+(?P<convention>EJ|US))?                       # Optional convention
        (?:\s+(?P<thickness>\d+)um)?                        # Optional thickness 
        (?:\s+\w+)*
        [\s;]*                                              # Space or ;
        #(?P<area>\d+/\d+|\d+)?\s*(?:di|of)?\s*             
        (?:~\s*)?(?P<area>\d+/\d+|\d+|\bpiece\b)?\s*        # Area (fraction or int) 
        (?:[^'\d]*?)?                                       # Ignore optional noise 
        (?:di|of)?\s*
        (?P<diameter>\d+)(?:''|' ?'|")\s*                   # Diameter
        \s*
        (?P<name>[^;]+?)\s*;\s*                             # Name
        (?:(?P<holder>(Ta|Mo)[A-Za-z0-9]*))?                # Holder 
    """, re.VERBOSE)

    pattern_special = re.compile(r"""
        Substrate:\s+
        (?P<orientation>\(\d{3}\)[AB]?)\s+
        (?P<doping>SI|p\+|p-|n\+|n-)\s+
        (?P<convention>EJ|US)?\s*
        (?P<name>[^;]+?)\s*;\s*
        (?P<area>piece|\d+/\d+|\d+)?\s*
        (?:of\s*)?
        (?P<diameter>\d+)''\s*
        ;?\s*
        (?P<holder>(Ta|Mo)[A-Za-z0-9]+)
    """, re.VERBOSE)

    pattern_NIL = re.compile(r"""
        Substrate:\s+
        (?P<orientation>\(\d{3}\)[AB]?)\s+
        (?P<doping>SI|p\+|p-|n\+|n-)\s*
        (?: (?P<convention>EJ|US) \s* )?     
        (?: (?P<area>\d+X\d+cm\^2) )? \s* ;\s*  
        (?P<name>(?:NIL\s+)?pattern\s+\d+(?:-\d+)?(?:\s*[\+\-]?\s*\w+)?)
        \s*;\s*
        (?P<holder>(Ta|Mo)[A-Za-z0-9]+)
    """, re.VERBOSE)


    match = (
        pattern.search(substrate_text)
        or pattern_special.search(substrate_text)
        or pattern_NIL.search(substrate_text)
    )

    if not match:
        raise ValueError(f"Substrate parsing failed for text: {substrate_text}")

    substrate = {
        "orientation": "",
        "doping": "",
        "convention": "",
        "area": "",
        "diameter": np.nan,
        "thickness": np.nan,
        "name": "",
        "holder": ""
    }

    if match:
        data = match.groupdict()
        substrate["orientation"] = data.get("orientation") or ""
        substrate["doping"] = data.get("doping") or ""
        substrate["convention"] = data.get("convention") or ""
        substrate["area"] = data.get("area") or ""
        substrate["diameter"] = int(data["diameter"]) if data.get("diameter") else np.nan
        substrate["thickness"] = int(data["thickness"]) if data.get("thickness") else np.nan
        substrate["name"] = data.get("name", "").strip()
        substrate["holder"] = data.get("holder") or ""

    return substrate

# ----------------------------------

def parse_wri_layer(file_path, Tdeox):

    with open(file_path, "r", encoding="latin1") as file:
        lines = file.readlines()
        file_content = "".join(lines)

    rpm_dict = {}  # Store values per layer
    rpm_value = 0.0  # Default value before finding any match
    rpm_counter = 0  # Track layer number

    Si_dict = {}  
    Si_value = 0 
    Si_counter = 0

    C_dict = {}  
    C_value = 0 
    C_counter = 0

    temp_dict = {}  
    temp_value = 0 
    temp_counter = 0

    # Capture all control types
    control_matches = re.findall(r"%\s*control|T\s*control|power\s*control", file_content, re.IGNORECASE)
    control = control_matches[0] if control_matches else None
    
    for line in lines:
        # Detect the start of a new layer
        if re.match(r'^\d+\s+\d+\s+\d+\s+\w+', line):  
            rpm_counter += 1  
            rpm_dict[rpm_counter] = rpm_value  # Assign last known  value
            Si_counter += 1  
            Si_dict[Si_counter] = Si_value
            C_counter += 1  
            C_dict[C_counter] = C_value
            temp_counter += 1  
            temp_dict[temp_counter] = temp_value

        # Find rotational frequency values in the line
        match_rpm = re.search(r'(CAR rot|CAR rpm)\s*([\d.]+)', line)
        if match_rpm:
            rpm_value = float(match_rpm.group(2))  
            rpm_dict[rpm_counter] = rpm_value      # Update last known value

        # Find Si current values in the line
        match_Si = re.search(r'(Si)\s*([\d.]+),', line)
        if match_Si:
            Si_value = float(match_Si.group(2))
            Si_dict[Si_counter] = Si_value

        # Find C current values in the line
        match_C = re.search(r'(C)\s*([\d.]+),', line)
        if match_C:
            C_value = float(match_C.group(2))
            C_dict[C_counter] = C_value

        # Find growth temperature values in the line
        match_temp = re.search(r'Substr\s*([\d.]+)', line)
        if match_temp:
            if Tdeox == 0.0:
                temp_value = float(match_temp.group(1))
            else:    
                # Adjust temperature based on Tdeox
                if control == "% control" or control == "T control":
                    temp_value = float(match_temp.group(1)) - (Tdeox - 580) 
                else:
                    temp_value = float(match_temp.group(1))  
            
            temp_dict[temp_counter] = temp_value

    rpm_data = [value for key, value in sorted(rpm_dict.items())]
    Si_current_data = [value for key, value in sorted(Si_dict.items())]
    C_current_data = [value for key, value in sorted(C_dict.items())]
    temp_data = [value for key, value in sorted(temp_dict.items())]
    
    return control, rpm_data, temp_data, Si_current_data, C_current_data

# ----------------------------------

def parse_layer(file_path):

    with open(file_path, 'r', encoding="latin1") as file:
        lines = file.readlines()

    eps = 1e-4    #Necessary for rounding errors

    layer = []
    loop = []
    r_step = []
    material = []
    dop_element = []
    thickness = []
    time = []
    rate = []
    x = []

    shutters = []
    pg_rates = []

    no_elements = ['interruption']
    r_step_adjust = 0

    for i, line in enumerate(lines):
        
        if re.match(r'^\d+\s+\d+\s+\d+\s+\w+', line):
            columns = line.split()
            # Filter columns to keep only the actual layers
            if any(no in columns for no in no_elements):
                r_step_adjust += 1
                continue 

            shutter_status = []
            pgr_layer = []
            # Layer number
            layer.append(int(columns[0]))
            # Number of repetitions of the layer block
            loop.append(int(columns[1]))
            # Layer from where the repetition starts 
            if int(columns[1]) > 1:
                r_step.append(int(columns[2]) - r_step_adjust)
            else:
                r_step.append(int(columns[2]))
            # Material composition and eventual dopant
            if ':' in columns[3]:
                ch_formula, dopant = columns[3].split(':', 1)
            else:
                ch_formula = columns[3]
                dopant = None
            material.append(ch_formula)
            dop_element.append(dopant)
            # Thickness of the layer
            if float(columns[4]) < eps:
                thickness.append(0.00)
            else:
                thickness.append(float(columns[4]))
            # Growth time
            time.append(float(columns[5]))
            # Growth rate
            if float(columns[6]) < eps:
                rate.append(0.00)
            else:
                rate.append(float(columns[6]))
            # Alloy fraction
            if float(columns[7]) < eps:
                x.append(0.00)
            else:
                x.append(float(columns[7]))
            # Shutter statuses
            shutter_status = [(col == 'TRUE' or col == 'O') for col in columns[8:12]]
            shutters.append(shutter_status)
            # Partial growth rates
            if len(columns) == 18:   # Handle case where C shutter is not present in the files
                pgr_layer = list(map(float, columns[14:18]))
            else:
                pgr_layer = list(map(float, columns[13:17]))
            pg_rates.append(pgr_layer)
 
    return layer, loop, r_step, material, dop_element, thickness, time, rate, x, shutters, pg_rates

# ----------------------------------

def parse_reflectometer(file_path):
    with open(file_path, "r", encoding="latin1") as file:
        lines = file.readlines()

    day_fraction = []
    calib_950 = []
    calib_470 = []
    timestamp = ""

    for line in lines:
        line = line.strip()

        # Parse start time
        if "Start" in line and not timestamp:
            match = re.search(r"\b(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})\b", line)
            if match:
                timestamp = match.group(1)

        # Match numerical data lines
        elif re.match(r"^\d+(\.\d+)?\s+\d+(\.\d+)?\s+\d+(\.\d+)?", line):
            columns = line.split()

            try:
                day_fraction.append(float(columns[0]))
                calib_950.append(float(columns[1]))
                calib_470.append(float(columns[2]))
            except (IndexError, ValueError):
                continue

    return timestamp, day_fraction, calib_950, calib_470

# ----------------------------------

def parse_pyrometer(file_path):

    with open(file_path, "r", encoding="latin1") as file:
        lines = file.readlines()

    day_fraction = []
    temp_ratio = []
    temp_emiss = []
    timestamp = ""

    for line in lines:
        
        if "Start" in line:
            match = re.search(r"\b(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})\b", line)
            if match:
                timestamp = match.group(1)

        elif re.match(r"^\d+(\.\d+)?\s+\d+(\.\d+)?\s+\d+(\.\d+)?", line):
            columns = line.split()

            try:
                day_fraction.append(float(columns[0]))
                temp_ratio.append(float(columns[2]))
                temp_emiss.append(float(columns[3]))
            except (IndexError, ValueError):
                continue

    return timestamp, day_fraction, temp_ratio, temp_emiss

# ----------------------------------

def parse_log(file_path):

    with open(file_path, "r", encoding="latin1") as file:
        lines = file.readlines()

    total_times = []
    pressures = []
    timestamp = ""

    log_started = False  # Flag to detect when log section begins

    for line in lines:
        line = line.strip()

        if "Start" in line and not timestamp:
            match = re.search(r"\b(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})\b", line)
            if match:
                timestamp = match.group(1)

        if not log_started and re.match(r"^\d+\s+\d{2}:\d{2}:\d{2}", line):
            log_started = True

        if log_started:
            match = re.match(r"^\d+\s+([\d:]+)\s+([0-9.Ee\-]+)", line)
            if match:
                try:
                    total_time = match.group(1)
                    pressure = match.group(2)
                    total_times.append(total_time)
                    pressures.append(float(pressure))
                except (IndexError, ValueError):
                    continue

    return timestamp, total_times, pressures