'''
The command line interface from RIPL
'''
import argparse

from .repl import REPL
from . import __version__


def main(argv=None):
    '''
    Main program loop
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        '--filename',
        default='',
        required=False,
    )
    parser.add_argument(
        '-s',
        '--script',
        type=str,
        default='',
        required=False,
    )
    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        required=False,
    )
    parser.add_argument(
        '--no-prelude',
        action='store_true',
        required=False,
    )

    if argv is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)

    if args.version:
        print(__version__)

    repl = REPL(load_prelude=not args.no_prelude)

    if args.filename:
        with open(args.file_name, 'r') as f:
            prog = '\n'.join(line for line in f)

        repl.eval_and_print(prog)

    elif args.script:
        repl.eval_and_print(args.script)

    else:
        repl.input_loop()


if __name__ == '__main__':
    main()
