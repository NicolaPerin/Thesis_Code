# MBE-Growth-NeXus-Converter

This repository contains a Python tool designed to convert legacy text files into standardized **NeXus** files, tailored for the **HMMBE Laboratory** at **CNR-IOM** in Trieste, specialized in **Molecular Beam Epitaxy (MBE)** for the synthesis of high-quality III/V semiconductor samples.

The conversion of raw laboratory files into structured NeXus format helps to support the adoption of the **FAIR data principles**, ensuring that scientific experimental data are **Findable**, **Accessible**, **Interoperable**, and **Reusable** for long-term use, collaboration, and reproducibility.

## Structure of the directory

- **`custom_schemas/`**: directory containing the custom NeXus application definition and base classes used.
    - **`applications/NXepitaxy.nxdl.xml`**: XML documentation of the **NXepitaxy** application definition.
    - **`base_classes/NXcooling_device.nxdl.xml`**: XML documentation of the **NXcooling_device** base class.
    - **`base_classes/NXmaterial_source.nxdl.xml`**: XML documentation of the **NXmaterial_source** base class.

- **`growths/`**: directory containing the text files from which the data is retrieved.
    - **`processes/`**: directory of the `.wri` and `.ep` files containing the MBE deposition process data and metadata.
    - **`logs/`**: directory of the others optional log files.

- **`nexus_files/`**: directory where the new converted NeXus files will be saved.

- **`nexus_converter.py`**: main script executing the NeXus file creation.
- **`parser.py`**: parsing functions to retrieve data from the text files.
- **`utils.py`**: several useful functions for data conversion, transformation and more.

- **`parser_testing.ipynb`**: Jupyter notebook where test the parsing functions.
- **`file_validations.ipynb`**: Jupyter notebook to visualize and validate the NeXus files and plot graphs.

## How to Run

To use the scripts, first clone this repository:

```sh
git clone https://github.com/leonardomusini/MBE-Growth-NeXus-Converter.git
cd MBE-Growth-NeXus-Converter
```
Then, in a Python virtual environment (recommended), install all the necessary libraries and dipendencies:

```sh
pip install -r requirements.txt
```

Finally, run the following command:

```sh
python nexus_converter.py
```

The script will convert all the text growth files in the  `growths/` directory into NeXus files, which will be saved in the `nexus_files/` folder.

To **visualize and validate** the generated files, you can:

- Use the `file_validation.ipynb` notebook 
- Or upload them to the free web service [myHDF5](https://myhdf5.hdfgroup.org/).