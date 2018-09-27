'''
Read in text and convert to internal data structures.
'''
import re
from itertools import chain
from collections import namedtuple

from .types import Symbol, Keyword, Procedure


Tag = namedtuple('Tag', 'name regex')
Token = namedtuple('Token', 'tag val line col')

INT_BASES = {'INT': 10, 'INT_BIN': 2, 'INT_OCT': 8, 'INT_HEX': 16}
QUOTES = {
    'QUOTE': 'quote', 'QUASI_QUOTE': 'quasiquote',
    'UNQUOTE': 'unquote', 'UNQUOTE_SPLICE': 'unquote-splicing'
}

TAGS = [
    Tag('COMMENT_SEXP', r';#\(.*\)'),
    Tag('COMMENT', r';.*\n?'),
    Tag('QUOTE', r"'"),
    Tag('QUASI_QUOTE', r'`'),
    Tag('NULL', r'(\(\)|\s*None)'),
    Tag('PAREN_OPEN', r'\('),
    Tag('PAREN_CLOSE', r'\)'),
    Tag('BRACKET_OPEN', r'\['),
    Tag('BRACKET_CLOSE', r'\]'),
    Tag('BRACE_OPEN', r'{'),
    Tag('BRACE_CLOSE', r'}'),
    Tag('COMPLEX', r'-?\d+\.?\d*[+-]\d+\.?\d*j'),
    Tag('COMPLEX_PURE', r'-?\d+\.?\d*j'),
    Tag('FLOAT', r'-?\d+\.\d+'),
    Tag('INT_BIN', r'-?0b[0-1]+'),
    Tag('INT_OCT', r'-?0o[0-8]+'),
    Tag('INT_HEX', r'-?0x[0-9a-fA-F]+'),
    Tag('INT', r'-?\d+'),
    Tag('BOOL', r'#[tf]'),
    Tag('COMMA', r','),
    Tag('UNQUOTE_SPLICE', r'~@'),
    Tag('UNQUOTE', r'~'),
    Tag('DOT', r'\.'),
    Tag('NEWLINE', r'\n'),
    Tag('WHITESPACE', r'\s+'),
    Tag('DOCSTRING', r'"""([^"]*)"""'),
    Tag('STRING', r'"([^"]*)"'),
    Tag('KEYWORD', r':[^()[\]{}\s\#,\.]+(?=[\)\]}\s])?'),
    Tag('SYMBOL', r'[^()[\]{}\s\#,\.]+(?=[\)\]}\s])?'),
    Tag('SYNTAX_ERROR', r'.'),
]

_TAGS = '|'.join(
    '(?P<{}>{})'.format(t.name, t.regex)
    for t in TAGS
)


class Reader:
    '''
    Read a string input and convert it to internal data
    '''
    tags = re.compile(_TAGS)
    tokens = None

    def read(self, text):
        '''
        Read in some input and convert it to internal data.
        '''
        return next(self.parse(self.tokenise(text)))

    def tokenise(self, string):
        '''
        Convert an input string into tokens.
        '''
        # Remove surrounding whitespace
        string = string.strip()

        # Check for invalid s-exps
        if string.startswith('('):
            if not string.endswith(')'):
                raise SyntaxError(
                    'Unclosed s-expression in input')

        line_num = 1
        line_start = 0

        for match in re.finditer(self.tags, string):
            lex_tag = match.lastgroup

            # If I'm honest, I forget why I need to do this...!
            group = [g for g in match.groups() if g is not None]
            source_txt = group[1] if len(group) == 2 else match.group(lex_tag)

            if lex_tag == 'SYNTAX_ERROR':
                # There was something that we didn't recognise
                raise SyntaxError('Unable to parse: {}'.format(source_txt))

            elif lex_tag == 'NEWLINE':
                # Increment the line count
                line_start = match.end()
                line_num += 1

            elif lex_tag in 'COMMENT COMMENT_SEXP WHITESPACE'.split():
                # ignore things we don't care about
                pass

            elif lex_tag.startswith('QUOTED'):
                sub = '(quote ' + source_txt[1:] + ')'
                yield from self.tokenise(sub)

            elif lex_tag == 'QUASI_QUOTED':
                sub = '(quasiquote ' + source_txt[1:] + ')'
                yield from self.tokenise(sub)

            else:
                # We have something that we can convert to a value
                if lex_tag == 'NULL':
                    val = []
                elif lex_tag in INT_BASES:
                    val = int(source_txt, INT_BASES[lex_tag])
                elif lex_tag == 'FLOAT':
                    val = float(source_txt)
                elif lex_tag.startswith('COMPLEX'):
                    # regex groups need to be distinct so we differentiate
                    # above as a single regex is huuuuuge!
                    val = complex(source_txt)
                    lex_tag = 'COMPLEX'
                elif lex_tag == 'BOOL':
                    val = True if source_txt == '#t' else False
                else:
                    # string
                    val = source_txt

                column = match.start() - line_start

                # Generate a token
                yield Token(lex_tag, val, line_num, column)

    def parse(self, tokens):
        '''
        Convert a stream of tokens into a nested list of lists for evaluation.
        '''
        if not tokens:
            # Can't run an empty program!
            raise SyntaxError('unexpected EOF while reading input')

        for token in tokens:
            if token.tag == 'PAREN_OPEN':
                # Start of an s-expression, drop the intial paren
                token = next(tokens)
                sexp = []

                if token.tag == 'PAREN_CLOSE':
                    # Special case of the empty list
                    yield []  # EmptyList()

                else:
                    # Read until the end of the current s-exp
                    while token.tag != 'PAREN_CLOSE':
                        tokens = chain([token], tokens)
                        sexp.append(next(self.parse(tokens)))
                        token = next(tokens)

                    yield sexp

            if token.tag in QUOTES:
                yield [Symbol(QUOTES[token.tag]), next(self.parse(tokens))]
                # yield from chain(
                #     [Symbol(QUOTES[token.tag])],
                #     self.parse(tokens))

            elif token.tag == 'BRACKET_OPEN':
                # start of a vector literal, drop the initial bracket
                list_literal, tokens = self._parse_vector(tokens)
                yield list_literal

            elif token.tag == 'BRACE_OPEN':
                # start of a dict literal, drop the initial brace
                dict_literal, tokens = self._parse_dict(tokens)
                yield dict_literal

            elif token.tag in 'PAREN_CLOSE BRACKET_CLOSE BRACE_CLOSE'.split():
                warning = 'unexpected {} in input (line {} col {})'.format(
                    token.val, token.line, token.col)
                raise SyntaxError(warning)

            else:
                yield self.make_atom(token)

    def _parse_vector(self, tokens):
        '''
        Parse a vector literal all at once and return both the list and
        remaining tokens from the input stream.
        '''
        tmp = []
        token = next(tokens)

        try:
            while token.tag != 'BRACKET_CLOSE':
                tmp.append(token)
                token = next(tokens)
            # Drop the final bracket
            parsed = [v for v in self.parse(tmp)]
            return parsed, tokens

        except StopIteration:
            # If we hit here then there was an error in the input.
            raise SyntaxError('missing closing ] in list literal.')

    def _parse_dict(self, tokens):
        '''
        Parse a dict literal and return the dict and remaining tokens
        Dict literals are given as {k1 v1, k2 v2, ...}
        '''
        tmp = []
        token = next(tokens)

        try:
            while token.tag != 'BRACE_CLOSE':
                if token.tag != 'COMMA':
                    tmp.append(token)
                token = next(tokens)

            # Drop the final brace
            parsed = [v for v in self.parse(tmp)]

            if len(parsed) % 2 != 0:
                # We didn't get key/value pairs
                raise SyntaxError("Invalid dict literal")

            pairs = [parsed[i:i+2] for i in range(0, len(parsed), 2)]

            return {k: v for k, v in pairs}, tokens

        except StopIteration:
            # If we hit here then there was an error in the input.
            raise SyntaxError('missing closing } in dict literal.')

    @staticmethod
    def make_atom(token):
        '''
        Strings and numbers are kept, every other token becomes a symbol.
        '''
        if token.tag == 'SYMBOL':
            return Symbol(token.val)
        elif token.tag == 'KEYWORD':
            return Keyword(token.val[1:])
        # elif token.tag == 'UNQUOTE':
        #     # Using `~` and `~@` symbols as markers that the _next_
        #     # token has been unquoted
        #     return Symbol('unquote')
        # elif token.tag == 'UNQUOTE_SPLICE':
        #     # Using `~` and `~@` symbols as markers that the _next_
        #     # token has been unquoted
        #     return Symbol('unquote-splicing')

        return token.val
