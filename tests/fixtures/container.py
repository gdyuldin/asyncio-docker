from .image import TEST_IMAGE


TEST_CONFIG = {
    'Image': TEST_IMAGE,
    'Cmd': [
        'sh'
    ],
    # Keep this container running
    'Tty': False,
    'AttachStdin': True,
    'OpenStdin': True,
    'StdinOnce': False
}
