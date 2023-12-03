#!/usr/bin/env python

"""Tests for `gds_tidy3d` package."""

import pytest
import pya
import os
import numpy as np
from gds_tidy3d import core, lyprocessor


@pytest.fixture
def response_is_point_inside_polygon():
    """Sample pytest fixture that returns a point and polygon."""
    point = [0, 0]
    polygon = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
    return {"point": point, "polygon": polygon}


def test_is_point_inside_polygon(response_is_point_inside_polygon):
    """Sample pytest test function with the pytest fixture as an argument."""
    point = response_is_point_inside_polygon["point"]
    polygon = response_is_point_inside_polygon["polygon"]
    assert core.is_point_inside_polygon(point, polygon)


def test_parse_yaml_tech():
    file_path = os.path.join(os.path.dirname(__file__), "tech.yaml")

    expected_output = {
        "name": "EBeam",
        "substrate": [
            {"z_base": 0.0, "z_span": -2, "material_type": "nk", "material": 1.48}
        ],
        "superstrate": [
            {"z_base": 0.0, "z_span": 3, "material_type": "nk", "material": 1.48}
        ],
        "pinrec": [{"layer": [1, 10]}],
        "devrec": [{"layer": [68, 0]}],
        "device": [
            {
                "layer": [1, 0],
                "z_base": 0.0,
                "z_span": 0.22,
                "material_type": "tidy3d_db",
                "material": ["cSi", "Li1993_293K"],
                "sidewall_angle": 85,
            },
            {
                "layer": [1, 5],
                "z_base": 0.3,
                "z_span": 0.22,
                "material_type": "tidy3d_db",
                "material": ["Si3N4", "Philipp1973Sellmeier"],
                "sidewall_angle": 80,
            },
        ],
    }

    parsed_data = core.parse_yaml_tech(file_path)
    assert parsed_data == expected_output

def test_layout_initialization():
    ly = pya.Layout()
    cell = pya.Cell()
    test_layout = core.layout("TestLayout", ly, cell)

    assert test_layout.name == "TestLayout"
    assert test_layout.ly == ly
    assert test_layout.cell == cell

def test_layout_dbu_property():
    ly = pya.Layout()
    ly.dbu = 0.001  # Set a specific dbu value
    test_layout = core.layout("TestLayout", ly, ly.create_cell("TestCell"))

    assert test_layout.dbu == 0.001

def test_port_initialization():
    test_port = core.port("opt1", [0, 0, 0], .5, "+")

    assert test_port.name == "opt1"
    assert test_port.center == [0, 0, 0]
    assert test_port.width == .5
    assert test_port.direction == "+"
    assert test_port.height is None
    assert test_port.material is None

def test_port_properties():
    test_port = core.port("opt1", [0, 0, 0], .5, "+")

    assert test_port.x == 0
    assert test_port.y == 0
    assert test_port.z == 0

def test_port_idx_property():
    test_port = test_port = core.port("opt1", [0, 0, 0], .5, "+")

    assert test_port.idx == 1  # assuming idx is the reverse of the digits in the name

def test_structure_initialization_with_all_parameters():
    test_polygon = [[0, 0], [1, 1], [2, 2]]
    test_structure = core.structure("structure", test_polygon, .0, .22, "Si", 85)

    assert test_structure.name == "structure"
    assert test_structure.polygon == test_polygon
    assert test_structure.z_base == .0
    assert test_structure.z_span == .22
    assert test_structure.material == "Si"
    assert test_structure.sidewall_angle == 85

def test_structure_initialization_with_default_sidewall_angle():
    test_polygon = [[0, 0], [1, 1], [2, 2]]
    test_structure = core.structure("structure", test_polygon, .0, .22, "Si", 85)

    assert test_structure.sidewall_angle == 85  # Checking default value



def test_dilate_with_default_extension():
    vertices = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
    expected_result = [[-2, -2], [2, -2], [2, 2], [-2, 2]]

    assert lyprocessor.dilate(vertices, extension=1) == expected_result

def test_load_layout_with_single_top_cell():
    test_file = "tests/si_sin_escalator.gds"  # Replace with actual path
    result = lyprocessor.load_layout(test_file)

    assert isinstance(result, core.layout)  # Assuming layout is a class
    assert result.name == "si_sin_escalator"  # Replace with the actual expected cell name
    # Further assertions can be made depending on the properties of the layout and cell

def test_load_layout_with_multiple_top_cells():
    test_file = "tests/bad_topcells.gds"  # Replace with actual path
    
    with pytest.raises(ValueError) as excinfo:
        lyprocessor.load_layout(test_file)
    
    assert "More than one top cell found" in str(excinfo.value)

if __name__ == "__main__":
    pytest.main([__file__])