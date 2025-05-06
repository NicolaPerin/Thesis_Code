from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import App, Column, Columns, FilterMenu, FilterMenus

from nomad_plugin_mbe.apps.mbe_app import sample_search_app

app_entry_point = AppEntryPoint(
    name='NewApp',
    description='New app entry point configuration.',
    app=App(
        label='NewApp',
        path='app',
        category='simulation',
        columns=Columns(
            selected=['entry_id'],
            options={
                'entry_id': Column(),
            },
        ),
        filter_menus=FilterMenus(
            options={
                'material': FilterMenu(label='Material'),
            }
        ),
    ),
)

mbe_app_entry_point = AppEntryPoint(
    name='MBE_searching_app',
    description='App for searching by terms or range in MBE growth',
    app=sample_search_app
)
