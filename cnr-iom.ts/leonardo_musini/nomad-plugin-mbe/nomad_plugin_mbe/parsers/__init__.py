from nomad.config.models.plugins import ParserEntryPoint
from pydantic import Field


class NewParserEntryPoint(ParserEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from nomad_plugin_mbe.parsers.parser import NewParser

        return NewParser(**self.dict())


parser_entry_point = NewParserEntryPoint(
    name='NewParser',
    description='New parser entry point configuration.',
    mainfile_name_re=r'.*\.newmainfilename',
)

class HDF5MBEParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_plugin_mbe.parsers.mbe_parser import HDF5MBEParser
        return HDF5MBEParser()

mbe_parser_entry_point = HDF5MBEParserEntryPoint(
    name="hdf5_mbe_parser",
    description="Parser for HDF5 or NeXus files related to Molecular Beam Epitaxy growth.",
    mainfile_name_re=r'.+\.nxs',
    mainfile_mime_re=r'application/x-hdf5'
)