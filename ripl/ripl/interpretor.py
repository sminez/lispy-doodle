'''
The core interpretor class for running RIPL
'''
import os

from .read import Reader
from .eval import Evaluator


RIPL_DIR = os.path.dirname(os.path.abspath(__file__))
PRELUDE_DIR = os.path.join(RIPL_DIR, 'prelude')


class Interpretor:
    '''
    A LISP interpretor for RIPL
    '''
    prelude_dir = PRELUDE_DIR

    def __init__(self):
        '''Allow for disabling the prelude'''
        self.reader = Reader()
        self.evaluator = Evaluator(read_proc=self.reader.read)

    def load_prelude(self):
        '''Load in the prelude if requested'''
        for fname in os.listdir(self.prelude_dir):
            self.slurp(os.path.join(self.prelude_dir, fname))

    def slurp(self, fname):
        '''
        Read the contents of a ripl file into the environment
        '''
        if not fname.endswith('.rpl'):
            raise NameError(f'Attempt to slurp non *.rpl file: {fname}')

        with open(fname, 'r') as f:
            while True:
                try:
                    # Read as many expressions as we can find
                    self.eval_expr(f)
                except StopIteration:
                    return

    def eval_expr(self, expr):
        pass
