from pyegeria.view.base_report_formats import select_report_spec
spec = select_report_spec("Cited Document-DrE", "MD")
print(spec is not None)
