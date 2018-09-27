'''
The ripl-repl
'''
import sys
import readline
import traceback

from .interpretor import Interpretor
from .types import LispList, Procedure, Vector


COMPLETIONS = ['start', 'stop', 'list', 'print']


def has_matching_parens(text):
    '''Check that a piece of text is balanced for matching ()[]{}'''
    # TODO :: discard ()[]{} inside of string literals
    paren = text.count('(') == text.count(')')
    bracket = text.count('[') == text.count(']')
    brace = text.count('{') == text.count('}')
    return paren and bracket and brace


class SimpleCompleter:
    '''A very simple completion engine for the repl'''
    def __init__(self, options):
        self.options = sorted(options)
        self.matches = []

    def complete(self, text, state):
        '''Find completions for the given text'''
        response = None
        if state == 0:
            # This is the first time for this text,
            # so build a match list.
            if text:
                self.matches = [
                    s for s in self.options
                    if s and s.startswith(text)
                ]

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None

        return response


class REPL(Interpretor):
    '''A Read Eval Print Loop using the RIPL interpretor'''
    in_prompt = "λ > "
    out_prompt = "   "

    def __init__(self, load_prelude=True):
        '''Configure readline for parsing input'''
        super().__init__()
        self._load_prelude = load_prelude

        # Register the completer function
        readline.set_completer(SimpleCompleter(COMPLETIONS).complete)
        # Use the tab key for completion
        readline.parse_and_bind('tab: complete')

    def input_loop(self):
        '''Read input from the user as part of a session'''
        prompt = self.in_prompt

        print('((Welcome to RIPL!)')

        if self._load_prelude:
            print('  (Loading prelude...)\n')
            try:
                self.load_prelude()
                print('  (...done!))')
            except Exception as e:
                print(f'  (ERROR IN PRELUDE)\n  ({e})')
                sys.exit(42)
        else:
            print(')')

        previous_input = ''
        while True:
            try:
                # Read input from the console
                _input = input(prompt)

                # Concatenate to any unparsed previous input we have
                if previous_input:
                    _input = previous_input + '\n' + _input

                if _input:
                    if has_matching_parens(_input):
                        # TODO: Add history save
                        result = self.evaluator.eval(self.reader.read(_input))

                        if result is not None:
                            print('> ' + self.py_to_lisp_str(result) + '\n')

                        prompt = self.in_prompt
                        previous_input = ''
                    else:
                        # Unclosed expression
                        prompt = self.out_prompt
                        previous_input = _input

            except StopIteration:
                previous_input = ''

            except (EOFError, KeyboardInterrupt):
                # User hit Ctl+d
                return

            except:
                excinf = sys.exc_info()
                sys.last_type, sys.last_value, last_tb = excinf
                sys.last_traceback = last_tb
                try:
                    lines = traceback.format_exception(
                        excinf[0],
                        excinf[1],
                        last_tb.tb_next)
                    print(''.join(lines), file=sys.stderr)
                finally:
                    last_tb, excinf = None, None

                previous_input = ''

    def eval_and_print(self, prog):
        '''Evaluate and print the result of a program'''
        for exp in map(self.py_to_lisp_str, self.evaluator.eval(prog)):
            print(exp)

    def py_to_lisp_str(self, exp):
        '''
        Convert a Python object back into a Lisp-readable string for display.
        '''
        if isinstance(exp, LispList):
            # (1 2 ... n)
            string = f'({" ".join(map(self.py_to_lisp_str, exp))})'
        elif isinstance(exp, Vector):
            # [1 2 ... n]
            string = f'[{" ".join(map(self.py_to_lisp_str, exp))}]'
        elif isinstance(exp, dict):
            # {a 1, b 2, ... k v}
            tmp = ['{} {}'.format(k, v) for k, v in exp.items()]
            string = '{' + ', '.join(tmp) + '}'
        elif isinstance(exp, tuple):
            # (, 1 2 ... n)
            string = f'(, {" ".join(map(self.py_to_lisp_str, exp))})'
        elif isinstance(exp, bool):
            string = '#t' if exp else '#f'
        elif isinstance(exp, Procedure):
            if exp.__doc__ != '':
                string = f'Procedure: {exp.__doc__}'
            else:
                string = 'Anonymous Procedure (λ)'
        else:
            string = str(exp)

        return string
