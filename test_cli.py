from commands.cat.dr_egeria import process_markdown_file
from click.testing import CliRunner

runner = CliRunner()
result = runner.invoke(process_markdown_file, ['--input-file', 'sample-data/egeria-inbox/dr-egeria-inbox/Flex.md', '--directive', 'process'])
print(result.output)
if result.exception:
    import traceback
    traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)
