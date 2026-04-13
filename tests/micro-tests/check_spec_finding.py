from md_processing.md_processing_utils.md_processing_constants import load_commands, get_command_spec
load_commands()
spec = get_command_spec('Link Agreement Item')
if spec:
    print('Found spec!')
    print(f"Spec Name: {spec.get('display_name')}")
else:
    print('Spec NOT found.')