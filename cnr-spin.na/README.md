## Links of our code's repositories

### Emanuele D'Amico

* [AMORE main branch](https://github.com/PioApocalypse/AMORE): contains fully operational AMORE with only a login BYOK system and a sample creation feature which automatically assigns our Standard-ID ("Na-25-000") to the new sample.
* [AMORE dev branch](https://github.com/PioApocalypse/AMORE/tree/dev): contains development code that's still being tested and frankly currently not even operational; experimental feature: sample tracking.



### Rosario Forlenza
* [eLab_to_NOMAD.py](https://github.com/RosarioForlenza/elab-to-nomad-parser): contains the parser that I developed during the internship to extract from the MODA laboratory's eLabFTW instance the data related to the PLD manufacturing process and the in situ monitoring via RHEED.
The program maps the data in an archive.json file that respects the NOMAD ontologies, converts the RHEED measurement data in a .csv file and allows the sending of these data, including RHEED images, to NOMAD automatically, creating an entry for the PLDProcess schema specifically created within the "nomad-plugin-pld-moda" plugin.

* [pld_schema.py](https://github.com/RosarioForlenza/nomad-plugin-pld-moda/blob/main/src/nomad_plugin_pld_moda/schema_packages/pld_schema.py) contains the main schema of the "nomad-plugin-pld-moda" plugin that I produced during the internship. This schema includes a section for the PLD manufacturing process data, a subsection for loading RHEED images and a subsection for loading intensity data measured by RHEED with interactive graph generation.