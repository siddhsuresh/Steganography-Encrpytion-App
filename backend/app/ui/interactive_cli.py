from __future__ import print_function, unicode_literals

from PyInquirer import prompt

import eclipse.ui.cli_questions as cli_q
from eclipse.common.utils import shred_traces
from eclipse.src.backend import embed, extract
import eclipse.common.settings as error_codes

def interactive_cli():
    """
    Run interactive command-line tool
    """
    # Main operations
    operation_answer = prompt(cli_q.operation_questions)
    if operation_answer["operation"] == "Embed message":

        # Embedding message
        extract_answers = prompt(cli_q.embed_questions)
        cover_image_path = embed(
            original_image_path=extract_answers['original_image_path'],
            stego_image_output_path=extract_answers['stego_image_output_path'],
            message=extract_answers['message_to_hide'],
            password=extract_answers['password'],
            chosen_seed=extract_answers['seed'])
        if cover_image_path == error_codes.ORIGINAL_IMAGE_PATH_DOES_NOT_EXISTS:
            print("[! ERROR !] Original image path is not correct")
            return
        elif cover_image_path == error_codes.OUTPUT_IMAGE_PATH_DOES_NOT_EXISTS:
            print("[! ERROR !] Output path is not a valid path")
            return

        print("[*] Message successfully hidden in the image")

        shred_answers = prompt(cli_q.shred_questions)
        if shred_answers['shred_original_image']:
            shred_traces(path_of_file_to_delete=extract_answers['original_image_path'])
            print('[*] Original image successfully deleted')
        if shred_answers['shred_cover_image']:
            shred_traces(path_of_file_to_delete=cover_image_path)
            print('[*] Cover image successfully deleted')
    else:
        # Extracting
        extract_answers = prompt(cli_q.extract_questions)
        message = extract(stego_img_path=extract_answers['stego_img_path'],
                          password=extract_answers['password'],
                          chosen_seed=extract_answers['seed'])
        if message == error_codes.COULD_NOT_DECRYPT:
            print("[! ERROR !] Could not decrypt the message.")
            return
        elif message == error_codes.ORIGINAL_IMAGE_PATH_DOES_NOT_EXISTS:
            print("[! ERROR !] Image path is not correct")
            return
        print("[*] Extracted hidden message: '%s'" % message)

        if prompt(cli_q.save_message_question)['save_message']:
            msg_path = prompt(cli_q.save_path_question)['message_path']
            with open(msg_path, 'w') as message_file:
                message_file.write(message+'\n')
            print('[*] Message successfully written at %s' % msg_path)
        if prompt(cli_q.delete_stego_image_question)['shred_stego_image']:
            # Deleting
            shred_traces(extract_answers['stego_img_path'])
            print('[*] Stego image successfully deleted')