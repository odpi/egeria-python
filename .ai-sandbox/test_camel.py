
from pyegeria.view._output_format_models import Column

col = Column(name="GUID", key="guid")
print(f"isinstance(col, dict) = {isinstance(col, dict)}")
print(f"getattr(col, 'key') = {getattr(col, 'key')}")
