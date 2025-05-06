from nomad.config.models.plugins import SchemaPackageEntryPoint
from pydantic import Field


class NewSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from nomad_plugin_mbe.schema_packages.schema_package import m_package

        return m_package


schema_package_entry_point = NewSchemaPackageEntryPoint(
    name='NewSchemaPackage',
    description='New schema package entry point configuration.',
)


class MBESchemaEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_plugin_mbe.schema_packages.mbe_schema import m_package

        return m_package


mbe_schema_entry_point = MBESchemaEntryPoint(
    name='mbe_sample_growth',
    description='Schema package for describing a Molecular Beam Epitaxy growth process.',
)