# nomad-plugin-mbe

This repository contains the main scripts for the custom plugin developed for the HMMBE Laboratory data. To check the complete version of `nomad-plugin-mbe`, please see my personal [GitHub repository](https://github.com/leonardomusini/nomad-plugin-mbe).

## Main scripts

- **`schema_packages/`**
    - **`mbe_schema.py`**: definition of the NOMAD custom schema `MBESynthesis`.
    - **`__init__.py`**: NOMAD entry point for the schema.

- **`parsers/`**
    - **`mbe_parser.py`**: parser to map the NXepitaxy-based NeXus files into the NOMAD schema.
    - **`__init__.py`**: NOMAD entry point for the parser.

- **`apps/`**
    - **`mbe_app.py`**: NOMAD app `MBE Sample Search` to enhance findability and accessibility.
    - **`__init__.py`**: NOMAD entry point for the app.