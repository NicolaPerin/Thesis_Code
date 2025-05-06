from nomad.config.models.ui import (
    App,
    Column,
    SearchQuantities,
    Menu,
    MenuItemTerms,
    MenuItemCustomQuantities,
    MenuItemHistogram,
    Axis,
    MenuItemVisibility,
)


dir_mbe = "nomad_plugin_mbe.schema_packages.mbe_schema.MBESynthesis"

sample_search_app = App(
    label="MBE Sample Search",
    path="sample_search",
    category="MBE Growth",
    description="Search and filter MBE growth samples based on process parameters or metadata.",
    readme="""
    This app allows users to search for MBE samples by filtering key growth parameters,
    characterisitcs of the substrate and several metadata.
    """,
    search_quantities=SearchQuantities(include=[f'*#{dir_mbe}']),
    columns=[
        Column(quantity="entry_name", selected=True),
        Column(quantity="entry_type"),
        Column(quantity="upload_create_time", selected=True),
        Column(quantity=f"data.title#{dir_mbe}", selected=True),
        Column(quantity=f"data.sample.thickness#{dir_mbe}", selected=True),
        Column(quantity=f"data.duration#{dir_mbe}", selected=True),
    ],
    filters_locked={"section_defs.definition_qualified_name": dir_mbe},
    menu=Menu(
        items=[
            Menu(title="User Info",
                    items=[
                        MenuItemTerms(
                            title="User Name",
                            type="terms",
                            search_quantity=f"data.user.name#{dir_mbe}",
                        ),
                        MenuItemTerms(
                            title="User ORCID",
                            type="terms",
                            search_quantity=f"data.user.ORCID#{dir_mbe}",
                        ),
            ]),
            Menu(title="Sample Info",
                    items=[
                        MenuItemTerms(
                            title="Sample Name",
                            type="terms",
                            search_quantity=f"data.sample.name#{dir_mbe}",
                        ),
                        MenuItemTerms(
                            title="Sample Type",
                            type="terms",
                            search_quantity=f"data.sample.type#{dir_mbe}",
                        ),
                        MenuItemHistogram(
                            title="Sample Thickness",
                            type="histogram",
                            n_bins=10,
                            x=Axis(
                                search_quantity=f"data.sample.thickness#{dir_mbe}",
                                title="Sample Thickness",
                                unit="µm"
                            ),
                        ),
                        MenuItemHistogram(
                            title="Sample Growth Time",
                            type="histogram",
                            n_bins=10,
                            x=Axis(
                                search_quantity=f"data.duration#{dir_mbe}",
                                title="Sample Growth Time",
                                unit="hour"
                            ),
                        ),
            ]),
            Menu(title="Layers Info",
                    items=[
                        MenuItemTerms(
                            title="Layer Name",
                            type="terms",
                            search_quantity=f"data.sample.layer.name#{dir_mbe}"
                        ),
                        MenuItemTerms(
                            title="Layer Material",
                            type="terms",
                            search_quantity=f"data.sample.layer.chemical_formula#{dir_mbe}"
                        ),
                        MenuItemHistogram(
                            title="Layer Doping",
                            type="histogram",
                            n_bins=10,
                            x=Axis(
                                search_quantity=f"data.sample.layer.doping#{dir_mbe}",
                                title="Layer Thickness",
                                unit="cm^-3"
                            ),
                        ),
                        MenuItemHistogram(
                            title="Layer Thickness",
                            type="histogram",
                            n_bins=10,
                            x=Axis(
                                search_quantity=f"data.sample.layer.thickness#{dir_mbe}",
                                title="Layer Thickness",
                                unit="angstrom"
                            ),
                        ),
                        MenuItemHistogram(
                            title="Layer Growth Temperature",
                            type="histogram",
                            n_bins=10,
                            x=Axis(
                                search_quantity=f"data.sample.layer.growth_temperature#{dir_mbe}",
                                title="Layer Growth Temperature",
                                unit="celsius"
                            ),
                        ),
                        MenuItemHistogram(
                            title="Layer Growth Time",
                            type="histogram",
                            n_bins=10,
                            x=Axis(
                                search_quantity=f"data.sample.layer.growth_time#{dir_mbe}",
                                title="Layer Growth Time",
                                unit="s"
                            ),
                        ),
                        MenuItemHistogram(
                            title="Layer Total Growth Rate",
                            type="histogram",
                            n_bins=10,
                            x=Axis(
                                search_quantity=f"data.sample.layer.growth_rate#{dir_mbe}",
                                title="Layer Total Growth Rate",
                                unit="angstrom/s"
                            ),
                        ),
                        MenuItemHistogram(
                            title="Layer Alloy Fraction",
                            type="histogram",
                            n_bins=10,
                            x=Axis(
                                search_quantity=f"data.sample.layer.alloy_fraction#{dir_mbe}",
                                title="Layer Alloy Fraction",
                            ),
                        ),
                        MenuItemHistogram(
                            title="Layer Rotational Frequency",
                            type="histogram",
                            n_bins=10,
                            x=Axis(
                                search_quantity=f"data.sample.layer.rotational_frequency#{dir_mbe}",
                                title="Layer Rotational Frequency",
                                unit="rpm"
                            ),
                        ),
            ]),
            Menu(title="Substrate Info",
                    items=[
                        MenuItemTerms(
                            title="Substrate Model",
                            type="terms",
                            search_quantity=f"data.sample.substrate.name#{dir_mbe}"
                        ),
                        MenuItemTerms(
                            title="Substrate Doping",
                            type="terms",
                            search_quantity=f"data.sample.substrate.doping#{dir_mbe}"
                        ),
                        MenuItemHistogram(
                            title="Substrate Area",
                            type="histogram",
                            n_bins=10,
                            x=Axis(
                                search_quantity=f"data.sample.substrate.area#{dir_mbe}",
                                title="Area",
                                unit="mm^2"
                            ),
                        ),
                        MenuItemTerms(
                            title="Substrate Flat Convention",
                            type="terms",
                            search_quantity=f"data.sample.substrate.flat_convention#{dir_mbe}"
                        ),
                        MenuItemTerms(
                            title="Substrate Holder Model",
                            type="terms",
                            search_quantity=f"data.sample.substrate.holder#{dir_mbe}"
                        ),
            ]),
            MenuItemCustomQuantities(
                title="Custom Filter",
                type="custom_quantities",
            ),
            MenuItemVisibility(
                title="Visibility Filter",
                type="visibility"
            ),
        ],
    ),
)