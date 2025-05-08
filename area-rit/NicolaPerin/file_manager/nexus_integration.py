"""
nexus_integration.py  ·  2025‑04‑17

Two instrument flavours supported:

* TEM‑EDS  (generic microscope + EDS detector)
* TVIPS    (TVIPS camera files you debugged earlier)

Both writers build on the same “common” scaffolding and then patch in the
few groups that are mandatory for NXem *but not* present in the TIFF
header.

If you add more instruments, just copy‑and‑tweak the ‘populate_…’
function.
"""
import json
import numpy as np
import tifffile
from nexusformat.nexus import (
    NXroot,
    NXentry,
    NXsample,
    NXdata,
    NXfield,
    NXgroup,
    NXnote,
)

# ----------------------------------------------------------------------
# helpers (unchanged)
# ----------------------------------------------------------------------
def flatten_dict(d, parent_key="", sep="."):
    items = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_dict(v, new_key, sep=sep).items())
    elif isinstance(d, list):
        for i, v in enumerate(d):
            new_key = f"{parent_key}[{i}]"
            items.extend(flatten_dict(v, new_key, sep=sep).items())
    else:
        items.append((parent_key, d))
    return dict(items)


def load_tiff_metadata_flat(tiff_path):
    meta = {}
    with tifffile.TiffFile(tiff_path) as tif:
        for tag in tif.pages[0].tags.values():
            name, value = tag.name, tag.value
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    meta.update(
                        {f"{name}.{k}": v for k, v in flatten_dict(parsed).items()}
                    )
                except json.JSONDecodeError:
                    meta[name] = value
            elif isinstance(value, dict):
                meta.update(
                    {f"{name}.{k}": v for k, v in flatten_dict(value).items()}
                )
            else:
                meta[name] = value
    return meta


def dotted_path_to_list(path):
    return path.strip().replace("/", ".").split(".")


def _nxgroup(parent, name, nx_class=None):
    if name not in parent:
        parent[name] = NXgroup()
    if nx_class:
        parent[name].attrs["NX_class"] = nx_class
    return parent[name]


# ----------------------------------------------------------------------
# 0. Common scaffold – used by every writer
# ----------------------------------------------------------------------
def _build_scaffold(tiff_path, mapping_json, out_file, extra_fields, hdr_meta):
    """Return (nxroot, nxentry) with image + mapping already inserted."""
    meta_flat = load_tiff_metadata_flat(tiff_path)

    with open(mapping_json) as f:
        mapping = json.load(f)

    nxroot = NXroot()
    nxroot.attrs["file_name"] = out_file

    nxentry = NXentry()
    nxentry["definition"] = "NXem"
    nxroot["NXentry"] = nxentry

    # --- sample placeholder (will be adjusted by instrument‑specific code)
    sample = NXsample()
    sample["name"] = "UNKNOWN_SAMPLE"
    sample["identifier_sample"] = "unknown_id"
    sample["physical_form"] = "bulk"
    sample["is_simulation"] = NXfield(np.uint8(0), attrs={"units": "NX_BOOLEAN"})

    if extra_fields:
        if "sample_identifier" in extra_fields:
            sample["identifier_sample"] = NXfield(extra_fields["sample_identifier"])
            sample["identifier_sample"].attrs["type"] = "NX_CHAR"  # validator requirement
        if "preparation_date" in extra_fields:
            prep = extra_fields["preparation_date"].strip()
            if len(prep) == 10:
                prep += "T00:00:00Z"
            sample["preparation_date"] = prep

        if "atom_types" in extra_fields:
            sample["atom_types"] = extra_fields["atom_types"]
    nxentry["SAMPLE"] = sample            # MUST be ‘SAMPLE’, upper‑case!

    # --- coordinate system placeholder (mandatory minOccurs=1)
    cs = NXgroup()
    cs.attrs["NX_class"] = "NXcoordinate_system"
    cs["type"] = "cartesian"
    cs["handedness"] = "right"
    cs["origin"] = "front_top_left"
    nxentry["coordinate_system_1"] = cs

    # --- start_time (if TIFF header didn’t supply one via mapping)
    if "start_time" not in nxentry:
        nxentry["start_time"] = "1970-01-01T00:00:00Z"

    # --- TIFF header → NXfields
    for key, val in meta_flat.items():
        if key not in mapping:
            continue
        pieces = dotted_path_to_list(mapping[key])
        target = nxroot
        for part in pieces[:-1]:
            target = _nxgroup(target, part)
        target[pieces[-1]] = NXfield(val)

    # --- store the image itself
    img = tifffile.imread(tiff_path)
    nxdata = NXdata()
    nxdata.signal = "data"
    nxdata["data"] = NXfield(img, name="data")
    nxentry["image_2d"] = nxdata

    # --- extra manual fields from the web form
    for k, v in (extra_fields or {}).items():
        nxentry[k] = v

    # --- full TIFF header (optional, JSON dump) for provenance
    if hdr_meta:
        note = NXnote()
        note["type"] = "text/plain"
        note["data"] = json.dumps(hdr_meta, indent=2)
        nxentry["hdr_metadata"] = note

    return nxroot, nxentry


# ----------------------------------------------------------------------
# 1. Instrument‑specific population helpers
# ----------------------------------------------------------------------

# a one‑liner for creating a field only if it is missing
def _maybe_set_field(group: NXgroup, name: str, value):
    if name not in group:
        group[name] = value

# ──────────────────────────────────────────────────────────────
# 1) TEM‑EDS population
# ──────────────────────────────────────────────────────────────
def _populate_tem_eds(nxentry: NXgroup):
    # ── dynamic branch -------------------------------------------------
    meas   = _nxgroup(nxentry, "measurement", "NXobject")
    events = _nxgroup(meas,     "events",     "NXobject")
    ev     = _nxgroup(events,   "event_data", "NXevent_data_em")

    inst   = _nxgroup(ev, "instrument", "NXinstrument_em")

    ebeam  = _nxgroup(inst, "ebeam_column", "NXebeam_column")
    _maybe_set_field(ebeam, "operation_mode", "unknown")

    # electron source with mandatory fields
    esrc = _nxgroup(ebeam, "electron_source", "NXsource")
    _maybe_set_field(esrc, "emitter_type", "unknown")
    _maybe_set_field(esrc, "voltage", 0.0)

    _nxgroup(ebeam, "filter", "NXfilter")

    det = _nxgroup(inst, "detector", "NXdetector")
    _maybe_set_field(det, "mode", "unknown")

    stage = _nxgroup(inst, "stage", "NXmanipulator")
    for fld in ("tilt1", "tilt2", "rotation", "position"):
        _maybe_set_field(stage, fld, 0.0)

    # ── static microscope branch --------------------------------------
    inst_static = _nxgroup(meas, "instrument", "NXinstrument_em")
    _maybe_set_field(inst_static, "name",     "generic TEM")
    _maybe_set_field(inst_static, "location", "unknown")
    _maybe_set_field(inst_static, "type",     "TEM")

    # required fabrication group
    fabr = _nxgroup(inst_static, "fabrication", "NXfabrication")
    _maybe_set_field(fabr, "vendor",        "unknown")
    _maybe_set_field(fabr, "model",         "unknown")
    _maybe_set_field(fabr, "serial_number", "unknown")

    ebeam_static = _nxgroup(inst_static, "ebeam_column", "NXebeam_column")
    esrc_static  = _nxgroup(ebeam_static, "electron_source", "NXsource")
    _maybe_set_field(esrc_static, "emitter_type", "unknown")

# ──────────────────────────────────────────────────────────────
# 2) TVIPS population
# ──────────────────────────────────────────────────────────────
def _populate_tvips(nxentry: NXgroup):
    _populate_tem_eds(nxentry)  # dynamic branch and basics

    meas = _nxgroup(nxentry, "measurement", "NXobject")
    inst = _nxgroup(meas, "instrument", "NXinstrument_em")
    _maybe_set_field(inst, "name",     "TVIPS‑microscope")
    _maybe_set_field(inst, "location", "unknown")
    _maybe_set_field(inst, "type",     "TEM")

    ebeam = _nxgroup(inst, "ebeam_column", "NXebeam_column")
    esrc  = _nxgroup(ebeam, "electron_source", "NXsource")
    _maybe_set_field(esrc, "emitter_type", "unknown")

    # fabrication is already created in _populate_tem_eds()

# ----------------------------------------------------------------------
# 2. Public builder functions
# ----------------------------------------------------------------------
def build_nexus_from_tiff_TEM_ED(
    tiff_path,
    mapping_json_path,
    out_nxs="TEM_ED.nxs",
    extra_fields=None,
    hdr_metadata=None,
):
    root, entry = _build_scaffold(
        tiff_path, mapping_json_path, out_nxs, extra_fields, hdr_metadata
    )
    _populate_tem_eds(entry)
    root.save(out_nxs, mode="w")
    print("✓ NXem file (TEM‑EDS) →", out_nxs)
    return root


def build_nexus_from_tiff_TVIPS(
    tiff_path,
    mapping_json_path,
    out_nxs="TVIPS.nxs",
    extra_fields=None,
    hdr_metadata=None,
):
    root, entry = _build_scaffold(
        tiff_path, mapping_json_path, out_nxs, extra_fields, hdr_metadata
    )
    _populate_tvips(entry)
    root.save(out_nxs, mode="w")
    print("✓ NXem file (TVIPS) →", out_nxs)
    return root
