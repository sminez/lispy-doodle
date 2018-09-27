'''
An environment to evaluate expressions in using collections.ChainMap
'''
import operator as op
import functools as ft

from importlib import import_module
from collections import ChainMap as Env

from .types import Symbol


def cons(val, lst):
    '''Naive implementation of cons using python lists'''
    if not isinstance(lst, list):
        raise ValueError('The second argument to cons must be a list')

    return [val] + lst


def append(lst_1, lst_2):
    '''Append two lists'''
    if not (isinstance(lst_1, list) and isinstance(lst_2, list)):
        raise ValueError('Append must be applied to two lists')

    return lst_1 + lst_2


def pyimport(module, env, _as=None, _from=None):
    '''
    Import a module and insert it into the given environment.
    --> This will perform inports with local scope.

    _from is a string list of submodules to import
    '''
    if _as and _from:
        # Can't do `from foo as bar import baz`
        raise SyntaxError("Invalid import: Can't do 'from X import Y as Z")

    # Grab the module from sys.modules
    raw = import_module(module)
    mod = vars(raw).items()

    if _as:
        defs = {Symbol('{}.{}'.format(_as, k)): v for k, v in mod}
    elif _from:
        defs = {Symbol(k): v for k, v in mod if k in _from}
    else:
        defs = {Symbol('{}.{}'.format(module, k)): v for k, v in mod}

    env.update(defs)
    return env


def curry(func, *args):
    '''
    Wrapper around functools.partial
        functools will use the _functools c version where possible

    add3 = curry(op.add, 3)
    add3(1) == 4

    RIPL SYNTAX
        Going to try having a curry macro that is invoked as:
        (define add3 $(add 3))
    '''
    if (len(args) == 1) and isinstance(args[0], dict):
        # allow splatting of a single dict
        return ft.partial(func, **args[0])

    return ft.partial(func, *args)


def make_global_env():
    '''
    Build a global environment with some standard procedures to get started.
    '''
    def lisp_variadic(func):
        '''Change Python single arg functions to LISPy variadic function'''
        return lambda *args: ft.reduce(func, args)

    py_builtins = {Symbol(k): v for k, v in __builtins__.items()}

    std_ops = {
        Symbol('+'): lisp_variadic(op.add),
        Symbol('-'): lisp_variadic(op.sub),
        Symbol('*'): lisp_variadic(op.mul),
        Symbol('/'): lisp_variadic(op.truediv),
        Symbol('%'): lisp_variadic(op.mod),
        Symbol('>'): lisp_variadic(op.gt),
        Symbol('<'): lisp_variadic(op.lt),
        Symbol('>='): lisp_variadic(op.ge),
        Symbol('<='): lisp_variadic(op.le),
        Symbol('='): lisp_variadic(op.eq),
        Symbol('!='): lisp_variadic(op.ne),
        }

    key_words = {
        Symbol('append'): append,
        Symbol('apply'): lambda x, xs: env[x](xs),
        Symbol('begin'): lambda *x: x[-1],
        Symbol('car'): lambda x: x[0],
        Symbol('cdr'): lambda x: x[1:],
        Symbol('cons'): cons,
        Symbol('and'): op.and_,
        Symbol('or'): op.or_,
        Symbol('not'): op.not_,
        Symbol('len'): len,
        }

    type_cons = {
        Symbol('str'): str,
        Symbol('int'): int,
        Symbol('float'): float,
        Symbol('complex'): complex,
        Symbol('dict'): dict,
        Symbol('list'): list,
        Symbol('vector'): list,
        Symbol('tuple'): tuple,
        Symbol(','): tuple
        }

    bool_tests = {
        Symbol('eq?'): op.is_,
        Symbol('equal?'): op.eq,
        Symbol('callable?'): callable,
        Symbol('null?'): lambda x: x == [],
        Symbol('string?'): lambda x: isinstance(x, str),
        Symbol('symbol?'): lambda x: isinstance(x, Symbol),
        Symbol('dict?'): lambda x: isinstance(x, dict),
        Symbol('tuple?'): lambda x: isinstance(x, tuple),
        Symbol('list?'): lambda x: isinstance(x, list),
        Symbol('int?'): lambda x: isinstance(x, int),
        Symbol('float?'): lambda x: isinstance(x, float),
        Symbol('number?'): lambda x: isinstance(x, (int, float, complex)),
    }

    # Create a new top level environment
    env = Env(py_builtins)

    # Place all of the builtins at the same level (future envs will be nested)
    for defs in [std_ops, key_words, type_cons, bool_tests]:
        env.update(defs)

    return env
