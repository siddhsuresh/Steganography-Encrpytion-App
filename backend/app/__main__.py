"""Eclipse

Usage:
  __main__.py --interactive
  __main__.py hide [--stealthy] --image <image-path> --message <message-txt> --code <seed> --output <path>
  __main__.py extract [--stealthy | --output <path>] --image <image-path> --code <seed>
  __main__.py (-h | --help)
  __main__.py --version

Options:
  --interactive                             Enables interactive CLI.
  -i <image-path>, --image <image-path>     Path of the original | stegoimage.
  -m <image-path>, --message <message-txt>  Message to hide.
  -c <seed>, --code <seed>      Repartition code used to retrieve the message.
  -o <path>, --output <path>    Path of the output stegoimage/extracted text.
  -s, --stealthy                Stealthy mode: bury traces -original img, cover img-
  -h, --help    Show this screen.
  --version     Show version.
"""
from docopt import docopt
from pyfiglet import Figlet

from eclipse.ui.main_cli import main

if __name__ == "__main__":
    f = Figlet(font='isometric3')
    print(f.renderText('HIDE'))
    arguments = docopt(__doc__, version='Eclipse 0.1')
    main(arguments)
