"""
Unit tests for pyegeria models module.

These tests cover Pydantic models and data structures.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from pyegeria.models import (
    MembershipStatus, ValidStatusValues, SearchStringRequestBody,
    FilterRequestBody, GetRequestBody, NewElementRequestBody,
    ReferenceableProperties, InitialClassifications, TemplateRequestBody,
    UpdateElementRequestBody, UpdateStatusRequestBody, NewRelationshipRequestBody,
    DeleteRequestBody, UpdateRelationshipRequestBody, ResultsRequestBody,
    PyegeriaModel
)


@pytest.mark.unit
class TestModelsModule:
    """Unit tests for models module."""
    
    def test_membership_status_enum(self):
        """Test MembershipStatus enum values."""
        assert MembershipStatus.UNKNOWN == "UNKNOWN"
        assert MembershipStatus.DISCOVERED == "DISCOVERED"
        assert MembershipStatus.PROPOSED == "PROPOSED"
        assert MembershipStatus.IMPORTED == "IMPORTED"
        assert MembershipStatus.VALIDATED == "VALIDATED"
        assert MembershipStatus.DEPRECATED == "DEPRECATED"
        assert MembershipStatus.OBSOLETE == "OBSOLETE"
        assert MembershipStatus.OTHER == "OTHER"
        
        # Test enum iteration
        statuses = list(MembershipStatus)
        assert len(statuses) == 8
        assert MembershipStatus.UNKNOWN in statuses
        assert MembershipStatus.ACTIVE not in statuses  # Not in this enum
    
    def test_valid_status_values_enum(self):
        """Test ValidStatusValues enum values."""
        assert ValidStatusValues.UNKNOWN == "UNKNOWN"
        assert ValidStatusValues.DRAFT == "DRAFT"
        assert ValidStatusValues.PREPARED == "PREPARED"
        assert ValidStatusValues.PROPOSED == "PROPOSED"
        assert ValidStatusValues.APPROVED == "APPROVED"
        assert ValidStatusValues.REJECTED == "REJECTED"
        assert ValidStatusValues.ACTIVE == "ACTIVE"
        assert ValidStatusValues.FAILED == "FAILED"
        assert ValidStatusValues.DISABLED == "DISABLED"
        assert ValidStatusValues.COMPLETE == "COMPLETE"
        assert ValidStatusValues.DEPRECATED == "DEPRECATED"
        assert ValidStatusValues.OTHER == "OTHER"
        assert ValidStatusValues.DELETED == "DELETED"
        
        # Test enum iteration
        statuses = list(ValidStatusValues)
        assert len(statuses) == 18
        assert ValidStatusValues.ACTIVE in statuses
        assert ValidStatusValues.UNKNOWN in statuses
    
    def test_search_string_request_body(self):
        """Test SearchStringRequestBody model."""
        # Test with minimal data
        request = SearchStringRequestBody(search_string="test")
        assert request.search_string == "test"
        assert request.page_size is None
        assert request.start_from is None
        
        # Test with all fields
        request = SearchStringRequestBody(
            search_string="test search",
            page_size=10,
            start_from=0
        )
        assert request.search_string == "test search"
        assert request.page_size == 10
        assert request.start_from == 0
    
    def test_filter_request_body(self):
        """Test FilterRequestBody model."""
        # Test with minimal data
        request = FilterRequestBody()
        assert request.page_size is None
        assert request.start_from is None
        
        # Test with pagination
        request = FilterRequestBody(page_size=20, start_from=10)
        assert request.page_size == 20
        assert request.start_from == 10
    
    def test_get_request_body(self):
        """Test GetRequestBody model."""
        # Test with minimal data
        request = GetRequestBody()
        assert request.page_size is None
        assert request.start_from is None
        
        # Test with pagination
        request = GetRequestBody(page_size=15, start_from=5)
        assert request.page_size == 15
        assert request.start_from == 5
    
    def test_new_element_request_body(self):
        """Test NewElementRequestBody model."""
        # Test with minimal data
        request = NewElementRequestBody()
        assert request.properties is None
        assert request.initial_classifications is None
        
        # Test with properties
        properties = {"name": "test_element", "description": "test description"}
        request = NewElementRequestBody(properties=properties)
        assert request.properties == properties
        assert request.initial_classifications is None
        
        # Test with classifications
        classifications = [{"classification_name": "test_class"}]
        request = NewElementRequestBody(
            properties=properties,
            initial_classifications=classifications
        )
        assert request.properties == properties
        assert request.initial_classifications == classifications
    
    def test_referenceable_properties(self):
        """Test ReferenceableProperties model."""
        # Test with minimal data
        props = ReferenceableProperties()
        assert props.qualified_name is None
        assert props.display_name is None
        assert props.description is None
        
        # Test with all fields
        props = ReferenceableProperties(
            qualified_name="test.qualified.name",
            display_name="Test Display Name",
            description="Test description"
        )
        assert props.qualified_name == "test.qualified.name"
        assert props.display_name == "Test Display Name"
        assert props.description == "Test description"
    
    def test_initial_classifications(self):
        """Test InitialClassifications model."""
        # Test with minimal data
        classifications = InitialClassifications()
        assert classifications.classification_name is None
        assert classifications.classification_properties is None
        
        # Test with classification name
        classifications = InitialClassifications(classification_name="test_class")
        assert classifications.classification_name == "test_class"
        assert classifications.classification_properties is None
        
        # Test with properties
        properties = {"prop1": "value1", "prop2": "value2"}
        classifications = InitialClassifications(
            classification_name="test_class",
            classification_properties=properties
        )
        assert classifications.classification_name == "test_class"
        assert classifications.classification_properties == properties
    
    def test_template_request_body(self):
        """Test TemplateRequestBody model."""
        # Test with minimal data
        request = TemplateRequestBody()
        assert request.template_guid is None
        assert request.template_properties is None
        
        # Test with template GUID
        request = TemplateRequestBody(template_guid="test-guid-123")
        assert request.template_guid == "test-guid-123"
        assert request.template_properties is None
        
        # Test with properties
        properties = {"prop1": "value1"}
        request = TemplateRequestBody(
            template_guid="test-guid-123",
            template_properties=properties
        )
        assert request.template_guid == "test-guid-123"
        assert request.template_properties == properties
    
    def test_update_element_request_body(self):
        """Test UpdateElementRequestBody model."""
        # Test with minimal data
        request = UpdateElementRequestBody()
        assert request.properties is None
        
        # Test with properties
        properties = {"name": "updated_name"}
        request = UpdateElementRequestBody(properties=properties)
        assert request.properties == properties
    
    def test_update_status_request_body(self):
        """Test UpdateStatusRequestBody model."""
        # Test with minimal data
        request = UpdateStatusRequestBody()
        assert request.status is None
        
        # Test with status
        request = UpdateStatusRequestBody(status=ValidStatusValues.ACTIVE)
        assert request.status == ValidStatusValues.ACTIVE
        
        # Test with string status
        request = UpdateStatusRequestBody(status="ACTIVE")
        assert request.status == "ACTIVE"
    
    def test_new_relationship_request_body(self):
        """Test NewRelationshipRequestBody model."""
        # Test with minimal data
        request = NewRelationshipRequestBody()
        assert request.relationship_properties is None
        
        # Test with properties
        properties = {"relationship_type": "test_type"}
        request = NewRelationshipRequestBody(relationship_properties=properties)
        assert request.relationship_properties == properties
    
    def test_delete_request_body(self):
        """Test DeleteRequestBody model."""
        # Test with minimal data
        request = DeleteRequestBody()
        assert request.force_delete is None
        
        # Test with force delete
        request = DeleteRequestBody(force_delete=True)
        assert request.force_delete is True
        
        request = DeleteRequestBody(force_delete=False)
        assert request.force_delete is False
    
    def test_update_relationship_request_body(self):
        """Test UpdateRelationshipRequestBody model."""
        # Test with minimal data
        request = UpdateRelationshipRequestBody()
        assert request.relationship_properties is None
        
        # Test with properties
        properties = {"updated_prop": "updated_value"}
        request = UpdateRelationshipRequestBody(relationship_properties=properties)
        assert request.relationship_properties == properties
    
    def test_results_request_body(self):
        """Test ResultsRequestBody model."""
        # Test with minimal data
        request = ResultsRequestBody()
        assert request.page_size is None
        assert request.start_from is None
        
        # Test with pagination
        request = ResultsRequestBody(page_size=25, start_from=15)
        assert request.page_size == 25
        assert request.start_from == 15
    
    def test_pyegeria_model_base(self):
        """Test PyegeriaModel base class."""
        # Test that PyegeriaModel can be instantiated
        model = PyegeriaModel()
        assert model is not None
        
        # Test that it has the expected configuration
        assert hasattr(model, 'model_config')
    
    def test_model_validation(self):
        """Test model validation."""
        # Test valid data
        request = SearchStringRequestBody(search_string="valid search")
        assert request.search_string == "valid search"
        
        # Test with valid pagination
        request = SearchStringRequestBody(
            search_string="test",
            page_size=10,
            start_from=0
        )
        assert request.page_size == 10
        assert request.start_from == 0
        
        # Test with None values
        request = SearchStringRequestBody(search_string="test")
        assert request.page_size is None
        assert request.start_from is None
    
    def test_model_serialization(self):
        """Test model serialization."""
        request = SearchStringRequestBody(
            search_string="test search",
            page_size=10,
            start_from=0
        )
        
        # Test dict conversion
        data = request.model_dump()
        assert isinstance(data, dict)
        assert data["search_string"] == "test search"
        assert data["page_size"] == 10
        assert data["start_from"] == 0
        
        # Test JSON serialization
        json_data = request.model_dump_json()
        assert isinstance(json_data, str)
        assert "test search" in json_data
        assert "10" in json_data
        assert "0" in json_data
    
    def test_model_deserialization(self):
        """Test model deserialization."""
        # Test from dict
        data = {
            "search_string": "test search",
            "page_size": 10,
            "start_from": 0
        }
        request = SearchStringRequestBody.model_validate(data)
        assert request.search_string == "test search"
        assert request.page_size == 10
        assert request.start_from == 0
        
        # Test from JSON
        json_data = '{"search_string": "json test", "page_size": 5}'
        request = SearchStringRequestBody.model_validate_json(json_data)
        assert request.search_string == "json test"
        assert request.page_size == 5
        assert request.start_from is None
    
    def test_enum_usage_in_models(self):
        """Test enum usage in models."""
        # Test ValidStatusValues in UpdateStatusRequestBody
        request = UpdateStatusRequestBody(status=ValidStatusValues.ACTIVE)
        assert request.status == ValidStatusValues.ACTIVE
        
        # Test with string value
        request = UpdateStatusRequestBody(status="ACTIVE")
        assert request.status == "ACTIVE"
        
        # Test with invalid status (should still work as string)
        request = UpdateStatusRequestBody(status="INVALID_STATUS")
        assert request.status == "INVALID_STATUS"
    
    def test_nested_model_usage(self):
        """Test nested model usage."""
        # Test ReferenceableProperties in NewElementRequestBody
        properties = ReferenceableProperties(
            qualified_name="test.qualified.name",
            display_name="Test Name",
            description="Test description"
        )
        
        request = NewElementRequestBody(properties=properties)
        assert request.properties == properties
        assert request.properties.qualified_name == "test.qualified.name"
        assert request.properties.display_name == "Test Name"
        assert request.properties.description == "Test description"
    
    def test_optional_fields(self):
        """Test optional fields in models."""
        # Test that optional fields can be omitted
        request = SearchStringRequestBody(search_string="test")
        assert request.page_size is None
        assert request.start_from is None
        
        # Test that optional fields can be set to None
        request = SearchStringRequestBody(
            search_string="test",
            page_size=None,
            start_from=None
        )
        assert request.page_size is None
        assert request.start_from is None
        
        # Test that optional fields can be set to values
        request = SearchStringRequestBody(
            search_string="test",
            page_size=10,
            start_from=0
        )
        assert request.page_size == 10
        assert request.start_from == 0
