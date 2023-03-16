from PyInquirer import Validator, ValidationError


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # Move cursor to end


operation_questions = [
    {
        'type': 'list',
        'name': 'operation',
        'message': 'Which operation do you want to perform?',
        'choices': ['Embed message', 'Extract message'],
    },
]

embed_questions = [
    {
        'type': 'input',
        'name': 'original_image_path',
        'message': 'Input the path of the original image:',
    },
    {
        'type': 'input',
        'name': 'stego_image_output_path',
        'message': 'Input the path where to save the output stego image:',
    },
    {
        'type': 'input',
        'name': 'message_to_hide',
        'message': 'Write the message to hide:',
    },
    {
        'type': 'password',
        'message': 'Enter the password that will be used '
                   'to decrypt the message:',
        'name': 'password'
    },
    {
        'type': 'input',
        'name': 'seed',
        'message': 'Input the message repartition code '
                   '(a random number that will be mandatory '
                   'to decrypt the message):',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
]

shred_questions = [
    {
        'type': 'confirm',
        'name': 'shred_original_image',
        'message': 'Do you want delete the original image?'
                   '\n[INFO: This is the image you inputted, '
                   'but it is not the cover image]',
        'default': False
    },
    {
        'type': 'confirm',
        'name': 'shred_cover_image',
        'message': 'Do you want delete the cover image used to hide the message?'
                   '\n[WARNING: For security reasons it is advised to delete it]',
        'default': False
    }
]

extract_questions = [
    {
        'type': 'input',
        'name': 'stego_img_path',
        'message': 'Input the path to the stego image:',
    },
    {
        'type': 'password',
        'message': 'Enter the password chosen to encrypt the message:',
        'name': 'password'
    },
    {
        'type': 'input',
        'name': 'seed',
        'message': 'Input the message repartition code:',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
]

save_message_question = [
    {
        'type': 'confirm',
        'name': 'save_message',
        'message': 'Save the extracted message to file?'
                   '[WARNING: the image and its hidden message'
                   ' will be unrecoverable]',
        'default': False
    }
]

delete_stego_image_question = [
    {
        'type': 'confirm',
        'name': 'shred_stego_image',
        'message': 'Do you want delete the stego image?'
                   '[WARNING: the image and its hidden message'
                   ' will be unrecoverable]',
        'default': False
    }
]

save_path_question = [
    {
        'type': 'input',
        'name': 'message_path',
        'message': 'Enter the absolute path:',
    }
]
