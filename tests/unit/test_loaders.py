# SADS Loaders Unit Tests
import pytest
from libraries.components.loader import ComponentLibraryLoader
from libraries.materials.loader import MaterialsLibraryLoader

def test_component_library_loader():
    loader = ComponentLibraryLoader()
    all_comps = loader.get_all()
    assert "solar_panels" in all_comps
    
    thrusters = loader.get_category("thrusters")
    assert len(thrusters) > 0
    
    # Filter thrusters by Isp > 1000s (electric propulsion)
    electric = loader.filter_components("thrusters", lambda x: x["isp_s"] > 1000)
    assert len(electric) == 2
    assert electric[0]["name"] == "Busek BHT-200"

def test_materials_library_loader():
    loader = MaterialsLibraryLoader()
    mats = loader.get_all()
    assert len(mats) == 5
    
    al = loader.get_material("Aluminum 6061-T6")
    assert al is not None
    assert al["density_kg_m3"] == 2700.0
    assert al["yield_strength_mpa"] == 276.0
