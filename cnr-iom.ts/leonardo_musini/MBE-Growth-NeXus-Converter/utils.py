import os
import re
from datetime import datetime, timedelta
from fractions import Fraction
import numpy as np


def file_searcher(folder_path):
    """
    Extracts sample IDs and their numeric components from all .wri files in the specified folder.

    Parameters:
        folder_path (str): Path to the folder containing .wri files.

    Returns:
        sample_ids (list of str): List of sample ID strings.
        numbers (list of str): List of numeric parts found within those sample IDs.
    """
    sample_ids = []
    numbers = []

    if not os.path.isdir(folder_path):
        print("Error: The provided folder path does not exist.")
        return [], []

    # Iterate over files in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".wri"):  
            sample_id = filename[0:-4] 
            sample_ids.append(sample_id)

            # Extract numeric part from sample_id
            match = re.search(r"\d+", sample_id)
            if match:
                numbers.append(match.group())

    return sample_ids, numbers

# ----------------------------------

def time_calculator(time_str, time_delta_str):
    """
    Adds a time delta (HH:MM:SS) to a given time string (HH:MM:SS).

    Parameters:
        time_str (str): Base time string.
        time_delta_str (str): Time delta string to add.

    Returns:
        str: Resulting time after addition, formatted as "HH:MM:SS".
    """

    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    h, m, s = map(int, time_delta_str.split(":"))  
    time_delta = timedelta(hours=h, minutes=m, seconds=s) 

    new_time_obj = time_obj + time_delta
    new_time_str = new_time_obj.strftime("%H:%M:%S")

    return new_time_str

# ----------------------------------

def area_converter(area):
    """
    Converts an area value given as a fraction or integer string into mm².

    Parameters:
        area (str): A string representing the area fraction (e.g., "1/4", "1/2", "1").

    Returns:
        float: The area converted to mm². If area is "piece" return 0.0
    """
    base_area = 2000  # "1" = 2000 mm²

    if not area or area.lower() == "piece":
        return 0.0
    
    match = re.match(r"(\d+(?:\.\d+)?)X(\d+(?:\.\d+)?)cm\^2", area)
    if match:
        x1 = float(match.group(1))
        x2 = float(match.group(2))
        return x1 * x2 * 100

    try:
        numeric_value = float(Fraction(area))  
        return numeric_value * base_area
    except ValueError:
        raise ValueError(f"Invalid area format: {area}. Expected fraction or integer as a string.")
    
# ----------------------------------

def time_converter(date_str, time_str):
    """
    Converts date and time strings into an ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SS).
    
    Parameters:
        date_str (str): The date string in MM-DD-YYYY format.
        time_str (str): The time string in HH:MM:SS format.

    Returns:
        str: ISO 8601 formatted timestamp (YYYY-MM-DDTHH:MM:SS).
    """
    try:
        # MM-DD-YYYY
        parsed_date = datetime.strptime(date_str, "%m-%d-%Y")  
        # HH:MM:SS
        parsed_time = datetime.strptime(time_str, "%H:%M:%S").time()

        combined_datetime = datetime.combine(parsed_date.date(), parsed_time)

        return combined_datetime.isoformat()  # Convert to ISO 8601 format

    except ValueError as e:
        raise ValueError(f"Error parsing date or time: {e}")
    
# ----------------------------------

def arsenic_ranges(value):
    """
    Convert a string representing a range in scientific notation, returning the average of the range.

    Parameters:
        value (str): A string representing a number or a range, e.g., "3.0-1.2E-3" or "1.0E-2"

    Returns:
        float: The average of the range or the single float value.
    """

    # Typo in scientific notation
    value = value.strip().replace(".E", "E")
    if value and value.startswith("E-"):
        value = "1" + value

    # Pattern to detect ranges
    match = re.match(r"^(\d+(\.\d+)?)-(\d+(\.\d+)?[Ee][-+]?\d+)$", value)
    
    if match:
        first_match = float(match.group(1))  
        second_match = float(match.group(3))  
        
        # Extract the exponent from the second number 
        exponent_match = re.search(r"[Ee]([-+]?\d+)", match.group(3))
        if exponent_match:
            exponent = int(exponent_match.group(1))  
            first_match = first_match * (10 ** exponent)  
        
        return (first_match + second_match) / 2 
    
    # If it's just a normal float, parse it directly
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid number format: {value}")
    
# ----------------------------------

def doping_calculator(dop_element, Si_curr, C_curr, g_rate):
    """
    Calculates the doping level based on the dopant type and its growth rate.
    
    Parameters:
        dop_element (str): Type of dopant, either 'C' for Carbon or 'Si' for Silicon.
        Si_curr (float): Current Silicon concentration.
        C_curr (float): Current Carbon concentration.
        g_rate (float): Growth rate used for normalization.
    
    Returns:
        float: Calculated doping level, or 0.0 if inputs are invalid or dopant is None.
    """
    
    if dop_element is None:
        return 0.0
    
    elif dop_element == "C":
        if C_curr is None or np.isnan(C_curr):
            return 0.0
        return 9.8653e8 * np.exp(0.41434 * C_curr) * 2.8 / g_rate
    
    elif dop_element == "Si":
        if Si_curr is None or np.isnan(Si_curr):
            return 0.0
        elif Si_curr < 16:
            return 1.0223e7 * np.exp(1.5319 * Si_curr) * 2.8 / g_rate
        else:
            return 3.0471e12 * np.exp(0.68786 * Si_curr) * 2.8 / g_rate
    
    else:
        raise ValueError(f"Unknown dopant: {dop_element}")

# ----------------------------------

def log_time_converter(log_time):
    """
    Converts a list of time strings in HH:MM:SS format to total seconds.

    Parameters:
        log_time (list of str): List of time strings formatted as "HH:MM:SS".

    Returns:
        list of int: List of corresponding times in seconds.
    """
    def time_to_sec(t):
        h, m, s = map(int, t.split(":"))
        return h * 3600 + m * 60 + s
    
    log_time_new = [time_to_sec(t) for t in log_time]

    return log_time_new

# ----------------------------------

def dayfraction_converter(day_fractions):
    """
    Converts a list of day fractions into seconds relative to the first entry.

    Parameters:
        day_fractions (list of float): List of day fractions.

    Returns:
        list of int: List of time differences in seconds relative to the first day fraction.
    """
    if not day_fractions:
        return []

    base = day_fractions[0]

    # Convert each day fraction to seconds relative to the start of the measurement
    log_seconds = [int((df - base) * 86400) for df in day_fractions]

    return log_seconds

# ----------------------------------

def alloy_inserter(material, alloy):
    """
    Inserts alloy composition values into a material name string.
    
    Parameters:
        material (str): A 6-character string representing a material composed of 3 elements with each element is assumed to be 2 characters long.
        alloy (float): A float between 0 and 1 indicating the alloy fraction of the second element.
    
    Returns:
        str: A new string with alloy composition inserted.
    """

    if len(material) == 6:
        el1 = material[:2]
        el2 = material[2:4]
        el3 = material[4:]

        # EL1_(x)EL2_(1-x)EL3
        new_name = f"{el1}$_{{{alloy:.2f}}}${el2}$_{{{1 - alloy:.2f}}}${el3}"

        return new_name

    raise ValueError("Material string must be exactly 6 characters long (3 elements of 2 chars each).")