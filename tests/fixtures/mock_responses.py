"""
Mock response factory for EgeriaTech testing.

This module provides realistic mock responses for different Egeria operations
to support comprehensive unit testing without requiring live Egeria instances.
"""

from typing import Dict, List, Any, Optional


class MockResponseFactory:
    """Generate realistic mock responses for different Egeria operations."""
    
    @staticmethod
    def create_digital_products_response(count: int = 5) -> Dict[str, Any]:
        """Create mock Digital Products response."""
        return {
            "kind": "json",
            "data": [
                {
                    "guid": f"product-{i:03d}",
                    "display_name": f"Digital Product {i}",
                    "qualified_name": f"product_{i:03d}",
                    "status": "ACTIVE",
                    "description": f"Mock digital product {i} for testing",
                    "type": "DigitalProduct",
                    "created_by": "test_user",
                    "create_time": "2024-01-01T00:00:00Z"
                }
                for i in range(1, count + 1)
            ]
        }
    
    @staticmethod
    def create_glossary_terms_response(count: int = 5) -> Dict[str, Any]:
        """Create mock Glossary Terms response."""
        return {
            "kind": "json",
            "data": [
                {
                    "guid": f"term-{i:03d}",
                    "display_name": f"Glossary Term {i}",
                    "qualified_name": f"term_{i:03d}",
                    "status": "ACTIVE",
                    "description": f"Mock glossary term {i} for testing",
                    "type": "GlossaryTerm",
                    "usage": f"Used in context {i}",
                    "created_by": "test_user",
                    "create_time": "2024-01-01T00:00:00Z"
                }
                for i in range(1, count + 1)
            ]
        }
    
    @staticmethod
    def create_data_assets_response(count: int = 5) -> Dict[str, Any]:
        """Create mock Data Assets response."""
        return {
            "kind": "json",
            "data": [
                {
                    "guid": f"asset-{i:03d}",
                    "display_name": f"Data Asset {i}",
                    "qualified_name": f"asset_{i:03d}",
                    "status": "ACTIVE",
                    "description": f"Mock data asset {i} for testing",
                    "type": "DataAsset",
                    "owner": f"owner_{i}",
                    "created_by": "test_user",
                    "create_time": "2024-01-01T00:00:00Z"
                }
                for i in range(1, count + 1)
            ]
        }

    @staticmethod
    def create_collections_response(count: int = 5) -> Dict[str, Any]:
        """Create mock Collections response."""
        return {
            "kind": "json",
            "data": [
                {
                    "guid": f"collection-{i:03d}",
                    "display_name": f"Collection {i}",
                    "qualified_name": f"collection_{i:03d}",
                    "status": "ACTIVE",
                    "description": f"Mock collection {i} for testing",
                    "type": "Collection",
                    "member_count": i * 10,
                    "created_by": "test_user",
                    "create_time": "2024-01-01T00:00:00Z"
                }
                for i in range(1, count + 1)
            ]
        }

    @staticmethod
    def create_external_references_response(count: int = 5) -> Dict[str, Any]:
        """Create mock Collections response."""
        return {
            "kind": "json",
            "data": [
                {
                    "guid": f"collection-{i:03d}",
                    "display_name": f"Collection {i}",
                    "qualified_name": f"collection_{i:03d}",
                    "status": "ACTIVE",
                    "description": f"Mock collection {i} for testing",
                    "type": "Collection",
                    "member_count": i * 10,
                    "created_by": "test_user",
                    "create_time": "2024-01-01T00:00:00Z"
                }
                for i in range(1, count + 1)
            ]
        }
    
    @staticmethod
    def create_empty_response() -> Dict[str, Any]:
        """Create empty response."""
        return {"kind": "empty"}
    
    @staticmethod
    def create_error_response(error_message: str = "Test error") -> Dict[str, Any]:
        """Create error response."""
        return {
            "kind": "error",
            "error": error_message,
            "code": "TEST_ERROR"
        }
    
    @staticmethod
    def create_text_response(content: str = "Mock text response") -> Dict[str, Any]:
        """Create text response."""
        return {
            "kind": "text",
            "mime": "text/markdown",
            "content": content
        }
    
    @staticmethod
    def create_html_response(content: str = "<h1>Mock HTML Response</h1>") -> Dict[str, Any]:
        """Create HTML response."""
        return {
            "kind": "text",
            "mime": "text/html",
            "content": content
        }
    
    @staticmethod
    def create_mermaid_response(content: str = "graph TD\n    A[Test] --> B[Response]") -> Dict[str, Any]:
        """Create Mermaid response."""
        return {
            "kind": "text",
            "mime": "text/markdown",
            "content": f"```mermaid\n{content}\n```"
        }
    
    @staticmethod
    def create_bearer_token_response() -> str:
        """Create mock bearer token."""
        return "mock_bearer_token_12345"
    
    @staticmethod
    def create_connection_check_response() -> str:
        """Create mock connection check response."""
        return "Egeria Platform Connection Successful"
    
    @staticmethod
    def create_format_set_metadata() -> Dict[str, Any]:
        """Create mock format set metadata."""
        return {
            "name": "Digital-Products",
            "description": "List digital products",
            "target_type": "DigitalProduct",
            "action": {
                "function": "CollectionManager._async_get_digital_products",
                "required_params": [],
                "optional_params": ["search_string", "page_size", "start_from"],
                "spec_params": {}
            },
            "output_formats": ["DICT", "JSON", "REPORT", "MERMAID", "HTML"]
        }


class MockSubClientFactory:
    """Factory for creating mock sub-clients with realistic behavior."""
    
    @staticmethod
    def create_mock_collection_manager():
        """Create mock CollectionManager with common methods."""
        class MockCollectionManager:
            def __init__(self, *args, **kwargs):
                self.token = None
                self.view_server = kwargs.get('view_server', 'test-server')
                self.platform_url = kwargs.get('platform_url', 'https://test.com')
                self.user_id = kwargs.get('user_id', 'test_user')
                self.user_pwd = kwargs.get('user_pwd', 'test_pass')
            
            def create_egeria_bearer_token(self, user_id=None, user_pwd=None):
                self.token = MockResponseFactory.create_bearer_token_response()
                return self.token
            
            def set_bearer_token(self, token):
                self.token = token
            
            def get_token(self):
                return self.token
            
            def close_session(self):
                self.token = None
            
            def _clearasync_get_digital_products(self, **kwargs):
                return MockResponseFactory.create_digital_products_response()
            
            async def _async_get_collections(self, **kwargs):
                return MockResponseFactory.create_collections_response()

            async def _async_find_collections(self, **kwargs):
                return MockResponseFactory.create_digital_products_response()['data']

            async def _async_find_glossary_terms(self, **kwargs):
                """Mock _async_find_glossary_terms method."""
                response = MockResponseFactory.create_glossary_terms_response()
                return response.get('data', [])
        
        return MockCollectionManager

    @staticmethod
    def create_mock_external_references():
        """Create mock CollectionManager with common methods."""

        class MockCExternalReferences:
            def __init__(self, *args, **kwargs):
                self.token = None
                self.view_server = kwargs.get('view_server', 'test-server')
                self.platform_url = kwargs.get('platform_url', 'https://test.com')
                self.user_id = kwargs.get('user_id', 'test_user')
                self.user_pwd = kwargs.get('user_pwd', 'test_pass')

            def create_egeria_bearer_token(self, user_id=None, user_pwd=None):
                self.token = MockResponseFactory.create_bearer_token_response()
                return self.token

            def set_bearer_token(self, token):
                self.token = token

            def get_token(self):
                return self.token

            def close_session(self):
                self.token = None


            async def _async_find_external_references(self, **kwargs):
                return MockResponseFactory.create_external_references_response()['data']



        return MockCExternalReferences
    
    @staticmethod
    def create_mock_governance_officer():
        """Create mock GovernanceOfficer with common methods."""
        class MockGovernanceOfficer:
            def __init__(self, *args, **kwargs):
                self.token = None
                self.view_server = kwargs.get('view_server', 'test-server')
                self.platform_url = kwargs.get('platform_url', 'https://test.com')
                self.user_id = kwargs.get('user_id', 'test_user')
                self.user_pwd = kwargs.get('user_pwd', 'test_pass')
            
            def create_egeria_bearer_token(self, user_id=None, user_pwd=None):
                self.token = MockResponseFactory.create_bearer_token_response()
                return self.token
            
            def set_bearer_token(self, token):
                self.token = token
            
            def get_token(self):
                return self.token
            
            def close_session(self):
                self.token = None
            
            async def _async_get_governance_definitions(self, **kwargs):
                return MockResponseFactory.create_glossary_terms_response()
        
        return MockGovernanceOfficer
    
    @staticmethod
    def create_mock_metadata_explorer():
        """Create mock MetadataExplorer with common methods."""
        class MockMetadataExplorer:
            def __init__(self, *args, **kwargs):
                self.token = None
                self.view_server = kwargs.get('view_server', 'test-server')
                self.platform_url = kwargs.get('platform_url', 'https://test.com')
                self.user_id = kwargs.get('user_id', 'test_user')
                self.user_pwd = kwargs.get('user_pwd', 'test_pass')

            def create_egeria_bearer_token(self, user_id=None, user_pwd=None):
                self.token = MockResponseFactory.create_bearer_token_response()
                return self.token

            def set_bearer_token(self, token):
                self.token = token

            def get_token(self):
                return self.token

            def close_session(self):
                self.token = None

            async def _async_get_data_assets(self, **kwargs):
                return MockResponseFactory.create_data_assets_response()

        return MockMetadataExplorer

    @staticmethod
    def create_mock_glossary_manager():
        """Create mock GlossaryManager that inherits from MockCollectionManager."""

        class MockGlossaryManager():
            """Mock GlossaryManager with glossary-specific methods."""
            def __init__(self, *args, **kwargs):
                self.token = None
                self.view_server = kwargs.get('view_server', 'test-server')
                self.platform_url = kwargs.get('platform_url', 'https://test.com')
                self.user_id = kwargs.get('user_id', 'test_user')
                self.user_pwd = kwargs.get('user_pwd', 'test_pass')

            def create_egeria_bearer_token(self, user_id=None, user_pwd=None):
                self.token = MockResponseFactory.create_bearer_token_response()
                return self.token

            def set_bearer_token(self, token):
                self.token = token

            def get_token(self):
                return self.token

            def close_session(self):
                self.token = None

            async def _async_find_glossary_terms(self, **kwargs):
                """Mock _async_find_glossary_terms method."""
                response = MockResponseFactory.create_glossary_terms_response()
                return response.get('data', [])

            async def _async_get_terms_by_name(self, **kwargs):
                """Mock _async_get_terms_by_name method."""
                response = MockResponseFactory.create_glossary_terms_response()
                return response.get('data', [])

            async def _async_get_term_by_guid(self, **kwargs):
                """Mock _async_get_term_by_guid method."""
                response = MockResponseFactory.create_glossary_terms_response()
                if response.get('data'):
                    return response['data'][0]
                return {}

        return MockGlossaryManager


