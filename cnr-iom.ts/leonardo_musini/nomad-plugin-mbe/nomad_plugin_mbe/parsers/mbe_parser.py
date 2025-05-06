from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.datamodel.datamodel import (
        EntryArchive,
    )
from structlog.stdlib import (
        BoundLogger,
    )

import h5py
from datetime import datetime
from nomad.parsing import MatchingParser
from nomad.datamodel import EntryArchive
from nomad_plugin_mbe.schema_packages.mbe_schema import (
    MBESynthesis, SampleRecipe, SubstrateDescription, User,
    SampleGrowingEnvironment, LayerDescription, SensorDescription,
    Instruments, CoolingDevice, MaterialSource
)


def parse_datetime(hdf5_obj, key):
    """Extracts and converts a datetime string from HDF5 to a Python datetime object."""
    if key in hdf5_obj:
        value = hdf5_obj[key][()]
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


class HDF5MBEParser(MatchingParser):

    def __init__(self):
        super().__init__(
            name='HDF5MBEParser',
            code_name='MyHDF5MBECode',
            mainfile_name_re=r'.+\.nxs',
            mainfile_mime_re=r'application/x-hdf5'
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        """Parses the HDF5/NeXus file and maps it to the NOMAD data schema."""
        logger.info(f"Starting parser for file: {mainfile}")

        with h5py.File(mainfile, "r") as hdf:
            logger.info("HDF5 file opened successfully")

            # Create main metadata structure
            archive.data = MBESynthesis()
            entry = archive.data
            entry_data = hdf["entry"]
            logger.info("Parsing general metadata")

            # Extract general metadata
            entry.definition = entry_data["definition"][()].decode("utf-8") if "definition" in entry_data else None
            entry.title = entry_data["title"][()].decode("utf-8") if "title" in entry_data else None
            entry.growth_description = entry_data["experiment_description"][()].decode("utf-8") if "experiment_description" in entry_data else None

            # Extract timestamps
            entry.start_time = parse_datetime(entry_data, "start_time")
            entry.end_time = parse_datetime(entry_data, "end_time")
            entry.duration = entry_data["duration"][()] if "duration" in entry_data else None

            # Extract user information
            if "user" in entry_data:
                user_data = entry_data["user"]
                user = entry.m_create(User)
                logger.info("Parsing user information")

                user.name = user_data["name"][()].decode("utf-8") if "name" in user_data else None
                user.email = user_data["email"][()].decode("utf-8") if "email" in user_data else None
                user.role = user_data["role"][()].decode("utf-8") if "role" in user_data else None
                user.affiliation = user_data["affiliation"][()].decode("utf-8") if "affiliation" in user_data else None
                user.ORCID = user_data["ORCID"][()].decode("utf-8") if "ORCID" in user_data else None
            else:
                max_user = 5
                user_index = 1
                while user_index < max_user and f"user_{user_index}" in entry_data:
                    user_data = entry_data[f"user_{user_index}"]
                    user = entry.m_create(User)
                    logger.info("Parsing user information")

                    user.name = user_data["name"][()].decode("utf-8") if "name" in user_data else None
                    user.email = user_data["email"][()].decode("utf-8") if "email" in user_data else None
                    user.role = user_data["role"][()].decode("utf-8") if "role" in user_data else None
                    user.affiliation = user_data["affiliation"][()].decode("utf-8") if "affiliation" in user_data else None
                    user.ORCID = user_data["ORCID"][()].decode("utf-8") if "ORCID" in user_data else None

                    user_index += 1

            # Extract apparatus information
            if "instrument" in entry_data:
                instrument_data = entry_data["instrument"]
                instrument = entry.m_create(Instruments)
                logger.info("Parsing instrument information")

                # Extract chamber information
                if "chamber" in instrument_data:
                    chamber_data = instrument_data["chamber"]
                    chamber = instrument.m_create(SampleGrowingEnvironment)
                    logger.info("Parsing chamber information")

                    chamber.model = chamber_data["name"][()].decode("utf-8") if "name" in chamber_data else None
                    chamber.type = chamber_data["type"][()].decode("utf-8") if "type" in chamber_data else None
                    chamber.description = chamber_data["description"][()].decode("utf-8") if "description" in chamber_data else None
                    chamber.program = chamber_data["program"][()].decode("utf-8") if "program" in chamber_data else None

                    # Extract cooling device information
                    if "cooling_device" in chamber_data:
                        device_data = chamber_data["cooling_device"]
                        device = chamber.m_create(CoolingDevice)
                        logger.info("Parsing cooling device information")

                        device.name = device_data["name"][()].decode("utf-8") if "name" in device_data else None
                        device.model = device_data["model"][()].decode("utf-8") if "model" in device_data else None
                        device.cooling_mode = device_data["cooling_mode"][()].decode("utf-8") if "cooling_mode" in device_data else None
                        device.temperature = device_data["temperature"][()] if "temperature" in device_data else None

                    # Extract sensors information
                    max_sensor = 8
                    sensor_index = 1
                    while sensor_index < max_sensor and f"sensor_{sensor_index}" in chamber_data:
                        sensor_data = chamber_data[f"sensor_{sensor_index}"]
                        sensor = chamber.m_create(SensorDescription)
                        logger.info("Parsing sensor information")

                        sensor.name = sensor_data["name"][()].decode("utf-8") if "name" in sensor_data else None
                        sensor.model = sensor_data["model"][()].decode("utf-8") if "model" in sensor_data else None
                        sensor.measurement = sensor_data["measurement"][()].decode("utf-8") if "measurement" in sensor_data else None
                        sensor.value = sensor_data["value"][()] if "value" in sensor_data else None

                        sensor_index += 1

            # Extract sample recipe
            if "sample" in entry_data:
                sample_data = entry_data["sample"]
                sample = entry.m_create(SampleRecipe)
                logger.info("Parsing sample recipe information")

                sample.name = sample_data["name"][()].decode("utf-8") if "name" in sample_data else None
                sample.thickness = sample_data["thickness"][()] if "thickness" in sample_data else None

                # Extract substrate details
                if "substrate" in sample_data:
                    substrate_data = sample_data["substrate"]
                    substrate = sample.m_create(SubstrateDescription)
                    logger.info("Parsing substrate information")

                    substrate.name = substrate_data["name"][()].decode("utf-8") if "name" in substrate_data else None
                    substrate.chemical_formula = substrate_data["chemical_formula"][()].decode("utf-8") if "chemical_formula" in substrate_data else None
                    substrate.crystalline_structure = substrate_data["crystalline_structure"][()].decode("utf-8") if "crystalline_structure" in substrate_data else None
                    substrate.crystal_orientation = substrate_data["crystal_orientation"][()].decode("utf-8") if "crystal_orientation" in substrate_data else None
                    substrate.doping = substrate_data["doping"][()].decode("utf-8") if "doping" in substrate_data else None
                    substrate.diameter = substrate_data["diameter"][()] if "diameter" in substrate_data else None
                    substrate.thickness = substrate_data["thickness"][()] if "thickness" in substrate_data else None
                    substrate.area = substrate_data["area"][()] if "area" in substrate_data else None
                    substrate.flat_convention = substrate_data["flat_convention"][()].decode("utf-8") if "flat_convention" in substrate_data else None
                    substrate.holder = substrate_data["holder"][()].decode("utf-8") if "holder" in substrate_data else None

                # Extract growth layers
                max_layer = 200
                layer_index = 1
                while layer_index < max_layer and f"layer{layer_index:02d}" in sample_data:
                    layer_data = sample_data[f"layer{layer_index:02d}"]
                    layer = sample.m_create(LayerDescription)
                    logger.info("Parsing layer information")

                    layer.name = layer_data["name"][()].decode("utf-8") if "name" in layer_data else None
                    layer.chemical_formula = layer_data["chemical_formula"][()].decode("utf-8") if "chemical_formula" in layer_data else None
                    layer.doping = layer_data["doping"][()] if "doping" in layer_data else None
                    layer.alloy_fraction = layer_data["alloy_fraction"][()] if "alloy_fraction" in layer_data else None
                    layer.thickness = layer_data["thickness"][()] if "thickness" in layer_data else None
                    layer.growth_temperature = layer_data["growth_temperature"][()] if "growth_temperature" in layer_data else None
                    layer.growth_time = layer_data["growth_time"][()] if "growth_time" in layer_data else None
                    layer.growth_rate = layer_data["growth_rate"][()] if "growth_rate" in layer_data else None
                    layer.rotational_frequency = layer_data["rotational_frequency"][()] if "rotational_frequency" in layer_data else None

                    max_cell = 5
                    cell_index = 1
                    while cell_index < max_cell and f"cell_{cell_index}" in layer_data:
                        cell_data = layer_data[f"cell_{cell_index}"]
                        cell = layer.m_create(MaterialSource)
                        logger.info("Parsing cell information")

                        cell.name = cell_data["name"][()].decode("utf-8") if "name" in cell_data else None
                        cell.model = cell_data["model"][()].decode("utf-8") if "model" in cell_data else None
                        cell.type = cell_data["type"][()].decode("utf-8") if "type" in cell_data else None
                        cell.shutter_status = cell_data["shutter_status"][()].decode("utf-8") if "shutter_status" in cell_data else None
                        cell.partial_growth_rate = cell_data["partial_growth_rate"][()] if "partial_growth_rate" in cell_data else None
                        cell.partial_pressure = cell_data["partial_pressure"][()] if "partial_pressure" in cell_data else None

                        cell_index += 1

                    layer_index += 1

            logger.info("HDF5 file successfully parsed into NOMAD schema.")