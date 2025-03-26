"""
This package contains classes for processing different types of Egeria entities from markdown.
It provides a more modular approach to the functionality in md_processing_utils.py.
"""

from .constants import ERROR, INFO, WARNING, pre_command
from .base_processor import EntityProcessor
from .glossary_processor import GlossaryProcessor
from .category_processor import CategoryProcessor
from .term_processor import TermProcessor
from .project_processor import ProjectProcessor

# Export the constants and classes
__all__ = [
    'EntityProcessor',
    'GlossaryProcessor',
    'CategoryProcessor',
    'TermProcessor',
    'ProjectProcessor',
    'ERROR',
    'INFO',
    'WARNING',
    'pre_command'
]
