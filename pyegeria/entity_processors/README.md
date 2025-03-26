# Entity Processors Package

This package provides a modular approach to processing Egeria entities from markdown text. It was created to improve the modularity of the original `md_processing_utils.py` file.

## Structure

The package is organized as follows:

- `constants.py`: Contains constants used throughout the package
- `base_processor.py`: Contains the base `EntityProcessor` class with common functionality
- `glossary_processor.py`: Contains the `GlossaryProcessor` class for processing glossary entities
- (Other processor classes would be added for categories, terms, projects, etc.)

## Usage

### Direct Usage

You can use the processor classes directly:

```python
from pyegeria.glossary_manager_omvs import GlossaryManager
from pyegeria.entity_processors import GlossaryProcessor

# Create a client and element dictionary
client = GlossaryManager(...)
element_dictionary = {}

# Create a processor
processor = GlossaryProcessor(client, element_dictionary)

# Process a markdown text
result = processor.process(markdown_text, directive="display")
```

### Backward Compatibility

For backward compatibility, you can use the `md_processing_utils_v2.py` module, which provides the same API as the original `md_processing_utils.py` but uses the new modular structure internally:

```python
from pyegeria.md_processing_utils_v2 import process_glossary_upsert_command

# Use the function as before
result = process_glossary_upsert_command(client, element_dictionary, markdown_text, directive="display")
```

## Benefits

The new modular structure provides several benefits:

1. **Separation of Concerns**: Each processor class is responsible for a specific entity type
2. **Code Reuse**: Common functionality is extracted to the base class
3. **Maintainability**: Smaller, focused classes are easier to understand and maintain
4. **Extensibility**: New entity types can be added by creating new processor classes
5. **Testability**: Classes can be tested in isolation

## Migration

To migrate from the original `md_processing_utils.py` to the new modular structure:

1. Import from `md_processing_utils_v2` instead of `md_processing_utils`
2. Use the same function calls as before

For new code, consider using the processor classes directly for better type checking and more explicit dependencies.