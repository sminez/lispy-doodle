'''
LISPy types and aliases for existing Python types.

For now, lets keep thigns simple and use builtins for pretty much everything!
    list -> list   (make singly linked later)
    vector -> list

TODO:
    Set a `_ripl_seq` boolean property (lacking interfaces in Python)
    to mark types that are compatable with `conj` and other sequence
    functions.
'''
Vector = list
# Just an alias for now but it may get expanded later
LispList = list


class Symbol(str):
    '''
    Internal representation of symbols
    Symbols can be bound to values using (define Symbol Value)
    '''
    def __eq__(self, other):
        if isinstance(other, Symbol):
            return super().__eq__(other)

        return False

    def __repr__(self):
        # Snip off the quotes for symbols
        return super().__repr__()[1:-1]

    def __hash__(self):
        return hash(str(self))


class Keyword(str):
    '''
    Internal representation of Keywords
    Unlike symbols, keywords can only refer to themselves
        i.e. (define :keyword "foo") is a syntax error
    '''
    def __repr__(self):
        return f':{super().__repr__()[1:-1]}'

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        if isinstance(other, Keyword):
            return super().__eq__(other)

        return False


class Procedure:
    '''
    A user-defined Procedure.
    '''
    def __init__(self, params, docstring, body, env, evaluator):
        '''Stash the procedure body for later evaluation'''
        self._params = params
        self._body = body
        self._outer_env = env
        self._evaluator = evaluator
        self.__doc__ = docstring

    def get_call_env(self, args):
        '''Generate the new nested environment'''
        return self._outer_env.new_child(dict(zip(self._params, args)))

    def __call__(self, *args):
        '''Bind the given arguments and evaluate the procedure'''
        env = self.get_call_env(args)
        return self._evaluator.eval(self._body, env)
