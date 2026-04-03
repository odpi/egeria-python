from md_processing.md_processing_utils.md_processing_constants import load_commands, COMMAND_DEFINITIONS, build_command_variants
load_commands()
specs = COMMAND_DEFINITIONS.get('Command Specifications', {})
print(f'Total specs: {len(specs)}')
for cmd in ['Link Agreement to Actor', 'Link Agreement to Item', 'Link Agreement Item']:
    if cmd in specs:
        print(f"Spec '{cmd}' found.")
        variants = build_command_variants(cmd, specs[cmd])
        print(f'  Variants: {sorted(list(variants))}')
    else:
        print(f"Spec '{cmd}' NOT found.")