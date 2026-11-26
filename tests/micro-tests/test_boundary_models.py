# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Test the pydantic property classes for odpi/egeria#9465 (SolutionBoundary, DesignModelBoundary).
"""
from pydantic import ValidationError
import pytest
from pyegeria.models import SolutionBoundaryProperties, DesignModelBoundaryProperties, SolutionBlueprintProperties


def test_solution_boundary_round_trips_with_its_class_name():
    model = SolutionBoundaryProperties(**{'class': 'SolutionBoundaryProperties', 'qualifiedName': 'Boundary::A', 'displayName': 'A', 'description': 'd'})
    assert model.model_dump(by_alias=True, exclude_none=True) == {'class': 'SolutionBoundaryProperties', 'qualifiedName': 'Boundary::A', 'displayName': 'A', 'description': 'd'}


def test_design_model_boundary_round_trips_with_its_class_name():
    model = DesignModelBoundaryProperties(**{'class': 'DesignModelBoundaryProperties', 'qualifiedName': 'Boundary::B', 'displayName': 'B', 'description': 'e'})
    assert model.model_dump(by_alias=True, exclude_none=True) == {'class': 'DesignModelBoundaryProperties', 'qualifiedName': 'Boundary::B', 'displayName': 'B', 'description': 'e'}


def test_each_class_refuses_the_other_class_name():
    with pytest.raises(ValidationError):
        SolutionBoundaryProperties(**{'class': 'DesignModelBoundaryProperties', 'qualifiedName': 'x', 'displayName': 'y'})
    with pytest.raises(ValidationError):
        DesignModelBoundaryProperties(**{'class': 'SolutionBoundaryProperties', 'qualifiedName': 'x', 'displayName': 'y'})


def test_a_solution_boundary_is_a_design_model_boundary():
    assert issubclass(SolutionBoundaryProperties, DesignModelBoundaryProperties)


def test_boundaries_add_no_fields_beyond_a_blueprint():
    assert set(SolutionBoundaryProperties.model_fields) == set(SolutionBlueprintProperties.model_fields)
    assert set(DesignModelBoundaryProperties.model_fields) == set(SolutionBlueprintProperties.model_fields)


def test_class_name_is_required():
    with pytest.raises(ValidationError):
        SolutionBoundaryProperties(qualifiedName='x', displayName='y')


def test_both_classes_are_exported_from_pyegeria_models():
    import pyegeria.models as m
    for name in ("SolutionBoundaryProperties", "DesignModelBoundaryProperties"):
        assert name in m.__all__ and getattr(m, name) is not None
