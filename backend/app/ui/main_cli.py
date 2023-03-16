import getpass

from eclipse.common.utils import shred_traces
from eclipse.src import backend
from eclipse.ui.interactive_cli import interactive_cli
import eclipse.common.settings as error_codes

def main(arguments : dict):
    """
    Run the main application as command line tool
    :param arguments: Dictionary of arguments
    """
    if arguments['--interactive']:
        interactive_cli()
    else:
        image_path = arguments['--image']
        repartition_code = int(arguments['--code'])
        password = getpass.getpass(prompt='Password to encrypt/decrypt the message: ',
                                   stream=None)
        if arguments['hide']:
            # HIDE MODE ===============================================================
            message_to_hide = arguments['--message']
            output_image_path = arguments['--output']
            cover_image_path = backend.embed(original_image_path=image_path,
                                             stego_image_output_path=output_image_path,
                                             message=message_to_hide,
                                             password=password,
                                             chosen_seed=repartition_code)
            if cover_image_path == error_codes.ORIGINAL_IMAGE_PATH_DOES_NOT_EXISTS:
                print("[! ERROR !] Original image path is not correct")
                return
            elif cover_image_path == error_codes.OUTPUT_IMAGE_PATH_DOES_NOT_EXISTS:
                print("[! ERROR !] Output path is not a valid path")
                return
            print("[*] Message successfully hidden in the image")
            if arguments['--stealthy']:
                shred_traces(path_of_file_to_delete=image_path)
                shred_traces(path_of_file_to_delete=cover_image_path)
                print("[!] Original image and cover image deleted permanently")
        elif arguments['extract']:
            # EXTRACT MODE ============================================================
            retrieved_message = backend.extract(stego_img_path=image_path,
                                                password=password,
                                                chosen_seed=repartition_code)
            if retrieved_message == error_codes.COULD_NOT_DECRYPT:
                # ERROR: Could not decrypt message
                print("[! ERROR !] Could not decrypt the message.")
                return
            elif retrieved_message == error_codes.ORIGINAL_IMAGE_PATH_DOES_NOT_EXISTS:
                print("[! ERROR !] Image path is not correct")
                return
            print("[*] Extracted hidden message: '%s'" % retrieved_message)
            if arguments['--stealthy']:
                shred_traces(path_of_file_to_delete=image_path)
                print("[!] Original image and cover image deleted permanently")
            if arguments['--output']:
                with open(arguments['--output'], 'w') as message_file:
                    message_file.write(retrieved_message + '\n')

