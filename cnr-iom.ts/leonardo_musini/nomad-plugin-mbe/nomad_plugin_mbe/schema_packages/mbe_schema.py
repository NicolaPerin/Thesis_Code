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

from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
    )

import re
from nomad.units import ureg
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.metainfo import Section, SubSection, Package, Quantity, Datetime, MEnum

m_package = Package(name='mbe_sample_growth')


class User(ArchiveSection):

    m_def = Section(
        a_eln=ELNAnnotation(
            properties={
                'order': [
                    'name',
                    'ORCID',
                    'email',
                    'role',
                    'affiliation',
                ]
            }
        )
    )

    name = Quantity(
        type=str,
        description="Name and Surname of the operator",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    role = Quantity(
        type=str,
        description="Role of the operator",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    affiliation = Quantity(
        type=str,
        description="Affiliated institution of the operator",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    ORCID = Quantity(
        type=str,
        description="ORCID identifier of the operator",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    email = Quantity(
        type=str,
        description="Email of the operator",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

# ----------------------------------

class CoolingDevice(ArchiveSection):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties={
                'order': [
                    'name',
                    'model',
                    'cooling_mode',
                    'temperature'
                ]
            }
        )
    )

    name = Quantity(
        type=str,
        description="Name of the cooling device in the chamber",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    model = Quantity(
        type=str,
        description="Model of the cooling device in the chamber",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    cooling_mode = Quantity(
        type=MEnum([
            'liquid_nitrogen',
            'gaseous_nitrogen',
            'water',
            'air',
            'other',
            'off'
        ]),
        description="Mode used to cool the chamber",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.EnumEditQuantity
        )
    )

    temperature = Quantity(
        type=float,
        unit='kelvin',
        description="Nominal temperature of the apparatus",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='kelvin'
        )
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

# ----------------------------------

class MaterialSource(ArchiveSection):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties={
                'order': [
                    'name',
                    'model',
                    'type',
                    'shutter_status',
                    'partial_growth_rate',
                    'partial_pressure'

                ]
            }
        )
    )

    name = Quantity(
        type=str,
        description="Name of the material source device in the chamber",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    model = Quantity(
        type=str,
        description="Model of the material source device in the chamber",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    type = Quantity(
        type=MEnum([
            'effusion_cell',
            'cracker_cell',
            'filament',
        ]),
        description="Type of material source used in the chamber",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.EnumEditQuantity
        )
    )

    shutter_status = Quantity(
        type=MEnum([
            'open',
            'closed',
        ]),
        description="Status of the shutter during the deposition of the current layer",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.EnumEditQuantity
        )
    )

    partial_growth_rate = Quantity(
        type=float,
        unit='angstrom/s',
        description="Partial growth rate of the cell during the deposition of the current layer",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='angstrom/s'
        )
    )

    partial_pressure = Quantity(
        type=float,
        unit='torr',
        description="Partial pressure of the cell during the deposition of the current layer",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='torr'
        )
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

# ----------------------------------

class SubstrateDescription(ArchiveSection):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties={
                'order': [
                    'name',
                    'chemical_formula',
                    'crystalline_structure',
                    'crystal_orientation',
                    'doping',
                    'diameter',
                    'thickness',
                    'area',
                    'flat_convention',
                    'holder'
                ]
            }
        )
    )

    name = Quantity(
        type=str,
        description="Identifier of the wafer from which the substrate was derived",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    chemical_formula = Quantity(
        type=str,
        description="Chemical formula of the substrate material",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    thickness = Quantity(
        type=float,
        unit='µm',
        description="Thickness of the substrate",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='µm'
        )
    )

    area = Quantity(
        type=float,
        unit='mm**2',
        description="Area of the substrate",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='mm**2'
        )
    )

    diameter = Quantity(
        type=int,
        unit='inches',
        description="Diameter of the wafer from which the substrate was derived",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='inches'
        )
    )

    crystal_orientation = Quantity(
        type=str,
        description="Crystallographic direction of the material",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    flat_convention = Quantity(
        type=MEnum([
            'EJ',
            'US',
            ''
        ]),
        description="Flat convention of the wafer",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.EnumEditQuantity
        )
    )

    doping = Quantity(
        type=str,
        description="Doping type and level of the substrate",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    holder = Quantity(
        type=str,
        description="Type of substrate holder used in the process",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    crystalline_structure = Quantity(
        type=MEnum([
            'single crystal',
            'polycrystal',
            'semi-crystal',
            'amorphous crystal'
        ]),
        description="Crystalline structure type of the material",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.EnumEditQuantity
        )
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

# ----------------------------------

class LayerDescription(ArchiveSection):

    m_def = Section(
        a_eln=ELNAnnotation(
            properties={
                'order': [
                    'name',
                    'chemical_formula',
                    'doping',
                    'thickness',
                    'growth_temperature',
                    'growth_time',
                    'growth_rate',
                    'alloy_fraction',
                    'rotational_frequency'
                ]
            }
        )
    )

    name = Quantity(
        type=str,
        description="Name of the layer",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    chemical_formula = Quantity(
        type=str,
        description="Chemical composition of the layer",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    doping = Quantity(
        type=float,
        unit='1 / cm ** 3',
        description="Doping level of the layer",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='1/ cm ** 3'
        )
    )

    thickness = Quantity(
        type=float,
        unit='angstrom',
        description="Thickness of the layer",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='angstrom'
        )
    )

    growth_temperature = Quantity(
        type=float,
        unit='celsius',
        description="Growing temperature of the layer",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='celsius'
        )
    )

    growth_time = Quantity(
        type=float,
        unit='s',
        description="Growing time of the layer",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='s'
        )
    )

    growth_rate = Quantity(
        type=float,
        unit='angstrom/s',
        description="Growing rate of the layer",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='angstrom/s'
        )
    )

    alloy_fraction = Quantity(
        type=float,
        description="Fraction of the first element in a ternary alloy",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity
        )
    )

    rotational_frequency = Quantity(
        type=float,
        unit='rpm',
        description="Rotational frequency of the sample during the deposition of the current layer",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='rpm'
        )
    )

    cell = SubSection(section_def=MaterialSource, repeats=True)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

# ----------------------------------

class SensorDescription(ArchiveSection):

    m_def = Section(
        a_eln=ELNAnnotation(
            properties={
                'order': [
                    'name',
                    'model',
                    'measurement',
                    'value',
                    'value_unit'
                ]
            }
        )
    )

    name = Quantity(
        type=str,
        description="Name of the sensor in the chamber",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    model = Quantity(
        type=str,
        description="Model of the sensor in the chamber",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    measurement = Quantity(
        type=str,
        description="Physical quantity being measured",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    value = Quantity(
        type=float,
        description="Nominal or average value of the signal",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
        )
    )

    value_unit = Quantity(
        type=str,
        description="Unit of the sensor value (used for interpretation)",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        if self.measurement:
            m = self.measurement.lower()
            unit = None

            if m == 'emissivity_temperature':
                unit = 'celsius'
            elif m == 'pressure':
                unit = 'mbar'
            elif m == 'rate_temperature':
                unit = 'unitless'
            elif m == 'reflectivity':
                unit = 'unitless'

            if unit:
                self.value_unit = unit
            else:
                logger.warning(f"Unknown measurement type '{self.measurement}', no unit assigned.")

# ----------------------------------

class SampleGrowingEnvironment(ArchiveSection):

    m_def = Section(
        a_eln=ELNAnnotation(
            properties={
                'order': [
                    'model',
                    'type',
                    'description',
                    'program'
                ]
            }
        )
    )

    model = Quantity(
        type=str,
        description="Model of the growing apparatus",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    type = Quantity(
        type=str,
        description="Type of growing apparatus",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    description = Quantity(
        type=str,
        description="Description of the growing apparatus",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    program = Quantity(
        type=str,
        description="Program controlling the growth process",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    cooling_device = SubSection(section_def=CoolingDevice)
    sensor = SubSection(section_def=SensorDescription, repeats=True)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

# ----------------------------------

class Instruments(ArchiveSection):

    m_def = Section(
        a_eln=ELNAnnotation(
            properties={
                'order': []
            }
        )
    )

    chamber = SubSection(section_def=SampleGrowingEnvironment)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

# ----------------------------------

class SampleRecipe(ArchiveSection):

    m_def = Section(
        a_eln=ELNAnnotation(
            properties={
                'order': [
                    'name',
                    'thickness',
                    'type'
                ]
            }
        )
    )

    name = Quantity(
        type=str,
        description="Identifier name of the sample",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    thickness = Quantity(
        type=float,
        unit='µm',
        description="Total thickness of the sample",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='µm'
        )
    )

    type = Quantity(
        type=str,
        description="Type of sample",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    substrate = SubSection(section_def=SubstrateDescription)
    layer = SubSection(section_def=LayerDescription, repeats=True)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        if self.name and not self.type:
            # Extracting the sample type from the sample name
            match = re.match(r'^hm\d+(.*)$', self.name.strip(), re.IGNORECASE)
            if match:
                self.type = match.group(1)
            else:
                logger.warning(f"Could not extract type from name: {self.name}")

# ----------------------------------

class MBESynthesis(EntryData):

    m_def = Section(
        a_eln=ELNAnnotation(
            properties={
                'order': [
                    'definition',
                    'title',
                    'growth_description',
                    'start_time',
                    'end_time',
                    'duration'
                ]
            }
        )
    )

    definition = Quantity(
        type=str,
        description="Type of metadata format, based on NeXus application definition",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    title = Quantity(
        type=str,
        description="Title of the growth",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    growth_description = Quantity(
        type=str,
        description="Growing technique involved",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity
        )
    )

    start_time = Quantity(
        type=Datetime,
        description="Starting time of the growth process",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.DateTimeEditQuantity
        )
    )

    end_time = Quantity(
        type=Datetime,
        description="Ending time of the growth process",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.DateTimeEditQuantity
        )
    )

    duration = Quantity(
        type=float,
        unit='hour',
        description="Total time of growth",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='hour'
        )
    )

    user = SubSection(section_def=User, repeats=True)
    instrument = SubSection(section_def=Instruments)
    sample = SubSection(section_def=SampleRecipe)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


m_package.__init_metainfo__()