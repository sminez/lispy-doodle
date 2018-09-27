'''
Evaluate internal expressions
'''
from collections import Counter

from .env import make_global_env
from .types import Symbol, Keyword, LispList, Procedure


class RiplError(Exception):
    pass


def is_balanced(text):
    '''Check that () {} [] are all matched'''
    c = Counter(text)
    return all([c['('] == c[')'], c['{'] == c['}'], c['['] == c[']']])


class Evaluator:
    '''An Evaluator can reduce a list of internal data types to a result'''
    value_types = (
        int, float, complex, dict, set, bool, Keyword
    )

    def __init__(self, read_proc):
        self.global_env = make_global_env()
        self.macro_table = {}

        self._set_read_proc(read_proc)

    def _set_read_proc(self, read_proc):
        '''
        Bind in the read procedure from the Reader.
        '''
        self.global_env['read'] = read_proc

    def eval(self, expr, env=None):
        '''
        Evaluate an expression in an environment.

        Branches ending in an assignment to `expr` are to enable
        tail call optimisation.
        '''
        if env is None:
            env = self.global_env

        while True:
            if isinstance(expr, self.value_types):
                return expr

            elif isinstance(expr, Symbol):
                val = env.get(expr)
                if val is None:
                    raise RiplError(f'Unknown symbol: `{expr}`')
                return val

            elif isinstance(expr, LispList):
                head, *rest = expr

                if not isinstance(head, Symbol):
                    # We can't apply this yet so evaluate it and then
                    # apply the result.
                    # i.e. ((if (> x 2) + -) 2 3 4 5)
                    head = self.eval(head, env)
                    args = self.get_args(rest, env)
                    return self.apply(head, args)

                # Check for known macros
                macro = self.macro_table.get(head)
                if macro:
                    # Run the macro
                    expr = self.apply(macro, rest)
                    # Evaluate in the global env
                    # XXX: Is this right? (From Norvig I think...)
                    return self.eval(expr, self.global_env)

                # Now we switch based on the head and deal with special forms
                if head == Symbol('quote'):
                    return rest[0]

                elif head == Symbol('quasiquote'):
                    # expr = self.expand_quasiquote(rest[0])
                    return self.expand_quasiquote(rest[0])

                elif head in [Symbol('unquote'), Symbol('unquote-splicing')]:
                    raise RiplError("Can't unquote outside of quasi-quote")

                elif head == Symbol('if'):
                    cond, *rest = rest
                    cond = self.eval(cond, env)
                    true, *rest = rest

                    if cond:
                        expr = true
                    else:
                        try:
                            false, *rest = rest
                        except ValueError:
                            # No false branch
                            return None

                        if rest:
                            # > 2 clauses
                            raise RiplError(f'Malformed `if` form: {rest}')

                        expr = false

                elif head == Symbol('cond'):
                    # The rest of the list should be ((cond body) ...)
                    for branch in rest:
                        if not (isinstance(branch, list) and len(branch) == 2):
                            raise RiplError(
                                f'Invalid `cond` branche: {branch}')

                        cond, body = branch
                        cond = self.eval(cond, env)

                        if isinstance(cond, bool):
                            if cond:
                                expr = body
                        elif cond == Keyword('else'):
                            expr = body
                        else:
                            raise RiplError(
                                f'Invalid `cond` condition: {cond}')

                elif head == Symbol('set!'):
                    try:
                        sym, value = rest
                    except ValueError:
                        raise RiplError('Invalid `set!`: {value}')

                    if not isinstance(sym, Symbol):
                        raise RiplError(
                            f'Attempt to `set!` non-Symbol: {sym}')

                    current = env.get(sym)
                    if current is None:
                        raise RiplError(
                            f'Attempt to `set!` non existant symbol: {sym}')

                    env[sym] = self.eval(value, env)
                    return

                elif head == Symbol('define'):
                    try:
                        sym, value = rest
                    except ValueError:
                        raise RiplError('Invalid `define`: {value}')

                    if not isinstance(sym, Symbol):
                        raise RiplError(
                            f'Attempt to define non-Symbol: {sym}')

                    current = env.get(sym)
                    if current is not None:
                        raise RiplError(
                            f'Attempt to re-define symbol: {sym}')

                    env[sym] = self.eval(value, env)
                    return

                elif head in [Symbol('lambda'), Symbol('λ'), Symbol('fn')]:
                    try:
                        params, body = rest
                        return Procedure(params, "", body, env, self)
                    except ValueError:
                        raise RiplError(
                            f'Invalid procedure definition: {rest}')

                elif head == Symbol('defn'):
                    try:
                        if len(rest) == 4:
                            doc_str = rest.pop(1)
                        else:
                            doc_str = ""

                        name, params, body = rest
                        if not isinstance(name, Symbol):
                            raise RiplError(
                                f'Attempt to define non-Symbol: {name}')

                        current = env.get(name)
                        if current is not None:
                            raise RiplError(
                                f'Attempt to re-define symbol: {name}')

                        env[name] = Procedure(
                            params, doc_str, body, env, self
                        )
                        return

                    except ValueError:
                        raise RiplError(
                            f'Invalid procedure definition: {rest}')

                elif head == Symbol('defmacro'):
                    if env != self.global_env:
                        raise RiplError(
                            'Macro definition only allowed at the top level')

                    try:
                        if len(rest) == 4:
                            doc_str = rest.pop(1)
                        else:
                            doc_str = ""

                        name, params, body = rest
                        if not isinstance(name, Symbol):
                            raise RiplError(
                                f'Attempt to define non-Symbol: {name}')

                        current = self.macro_table.get(name)
                        if current is not None:
                            raise RiplError(
                                f'Attempt to re-define existing macro: {name}')

                        self.macro_table[name] = Procedure(
                            params, doc_str, body, env, self
                        )
                        return

                    except ValueError:
                        raise RiplError(
                            f'Invalid macro definition: {rest}')

                # (let ((parm val) ...) body)
                # => ((lambda (parm ...) body) val ...)
                elif head == Symbol('let'):
                    bindings, body = rest
                    parms, vals = zip(*bindings)
                    # Convert to interal repr
                    parms = LispList(parms)
                    vals = LispList(vals)
                    expr = LispList([
                        LispList([Symbol('lambda'), parms, body]),
                        *vals])

                elif head == Symbol('begin'):
                    for exp in rest[:-1]:
                        self.eval(exp, env)

                    expr = rest[-1]

                elif head == Symbol('eval'):
                    # evaluate a quoted expression
                    if isinstance(rest[0], list):
                        # tokens are [quote, [ ... ]]
                        expr = rest[1]
                    else:
                        # single token is a symbol, try to look it up
                        try:
                            _val = env[rest[0]]
                            expr = _val
                        except AttributeError:
                            raise NameError(
                                'Undefined symbol {}'.format(rest[0]))

                elif head == Symbol('apply'):
                    # (apply f (...))
                    proc = self.eval(rest[0], env)
                    args = self.get_args(rest[1:], env)

                    if isinstance(proc, Procedure):
                        expr = proc._body
                        env = proc.get_call_env(args)

                    return proc(*args)

                else:
                    # Assume that `head` is a proc and `rest` are args
                    proc = self.eval(head, env)
                    args = self.get_args(rest, env)

                    if isinstance(proc, Procedure):
                        expr = proc._body
                        env = proc.get_call_env(args)
                    else:
                        # If this is a Python function then just call it
                        return proc(*args)

            else:
                raise RiplError(
                    f'Unknown expression in input: {expr}')

    def apply(self, proc, args):
        '''Apply a procedue to an argument list'''
        return proc(*args)

    # XXX PRESENTLY BORKED
    def expand_quasiquote(self, expr):
        '''Expand a quasi-quoted expression in an environment'''
        def is_pair(e):
            return isinstance(e, LispList) and len(e) != 0

        if not is_pair(expr):
            # return LispList([Symbol("quote"), expr])
            return expr

        # Make sure we aren't splicing a list into the head
        # position of the new list
        if expr[0] == Symbol("unquote-splicing"):
            raise RiplError(
                f"Can't splice at the head of a list: {expr}")

        if expr[0] == Symbol('unquote'):
            if len(expr) != 2:
                raise RiplError(f'Unquoting error: {expr}')
            return expr[1]

        elif is_pair(expr[0]) and expr[0][0] == Symbol('unquote-splicing'):
            if len(expr[0]) != 2:
                raise RiplError(f'Unquoting error: {expr}')

            return LispList(expr[0][1] + self.expand_quasiquote(expr[1:]))

        else:
            return LispList([
                [self.expand_quasiquote(expr[0])] +
                self.expand_quasiquote(expr[1:])
            ])

    def get_args(self, lst, env):
        '''
        Find the arguments for a procedure via recursive evaluation.
        NOTE: This will need to change if we move to internal
              s-exps for data representation.
        '''
        return LispList([self.eval(elem, env) for elem in lst])
