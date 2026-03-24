from commands.cat.dr_egeria import process_markdown_file
import traceback
try:
    process_markdown_file.callback(
        input_file='sample-data/egeria-inbox/dr-egeria-inbox/Flex.md',
        output_folder='',
        directive='process',
        server='cocoMDS2',
        url='https://192.168.0.222:39443',
        userid='erinoverview',
        user_pass='secret',
        parse_summary='none',
        attribute_logs='debug'
    )
    print("FINISHED")
except Exception as e:
    print("EXCEPTION CAUGHT")
    traceback.print_exc()
