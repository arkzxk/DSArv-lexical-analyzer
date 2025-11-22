####################################
# CHARACTER SET
####################################

capital_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
small_letters   = "abcdefghijklmnopqrstuvwxyz"
letters = capital_letters + small_letters
numbers = "0123456789"
special_characters = "!%^&*()-=+[],./:#@_\"'{}? "

####################################
# ERRORS
####################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

####################################
# POSITION
####################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

####################################
# TOKEN TYPES
####################################

TT_INT    = 'INT'
TT_FLOAT  = 'FLOAT'
TT_STR    = 'STR'
TT_BOOL   = 'BOOL'
TT_LIST   = 'LIST'
TT_TUPLE  = 'TUPLE'
TT_SET    = 'SET'
TT_DICT   = 'DICT'

# Basic arithmetic / punctuation
TT_PLUS       = 'PLUS'     # +
TT_MINUS      = 'MINUS'    # -
TT_MUL        = 'MUL'      # *
TT_DIV        = 'DIV'      # /
TT_MOD        = 'MOD'      # %

# Multi-char operators
TT_FLOOR      = 'FLOOR'    # //
TT_POW        = 'POW'      # **

# Assignment / equality / relational
TT_EQ         = 'EQ'       # =
TT_EE         = 'EE'       # ==
TT_NE         = 'NE'       # !=
TT_LT         = 'LT'       # <
TT_GT         = 'GT'       # >
TT_LTE        = 'LTE'      # <=
TT_GTE        = 'GTE'      # >=

# Assignment variants
TT_PLUSEQ     = 'PLUSEQ'   # +=
TT_MINUSEQ    = 'MINUSEQ'  # -=
TT_MULTEQ     = 'MULTEQ'   # *=
TT_DIVEQ      = 'DIVEQ'    # /=
TT_FLOOREQ    = 'FLOOREQ'  # //=
TT_MODEQ      = 'MODEQ'    # %=
TT_POWEQ      = 'POWEQ'    # **=

# Structure tokens
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD    = 'KEYWORD'
TT_RESERVED   = 'RESERVED'

TT_LPAREN     = 'LPAREN'
TT_RPAREN     = 'RPAREN'
TT_COMMA      = 'COMMA'
TT_COLON      = 'COLON'
TT_STRING     = 'STRING'
TT_NEWLINE    = 'NEWLINE'
TT_DOT        = 'DOT'

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

####################################
# KEYWORDS and RESERVED WORDS
####################################

# Data types
TYPE_KEYWORDS = {
    'int': TT_INT,
    'float': TT_FLOAT,
    'str': TT_STR,
    'bool': TT_BOOL,
    'list': TT_LIST,
    'tuple': TT_TUPLE,
    'set': TT_SET,
    'dict': TT_DICT,
}

# Keywords (control flow, built-in DS ops, method names, etc.)
KEYWORDS = {
    # control flow & misc
    'if','elif','else','for','while','break','continue','pass','return',
    'try','except','finally','raise',

    # functions & flow
    'def','import','from','as','print','in','match','func','asynch','await',

    # declarations
    'let','var','const','auto','type',

    # OOP
    'class','interface','extends','implements','public','private','protected','static','new','this',

    # data structure names and built-ins (page 11)
    'linkedList','tree','graph','stack','queue','heap',
    'insert','append','remove','push','pop','peek',
    'addNode','addEdge','dfs','bfs','enqueue','dequeue',
    'inOrder','preOrder','postOrder'
}

# Reserved words (must be their own token TT_RESERVED)
RESERVED_WORDS = {
    'int','float','str','bool','list','tuple','set','dict',
    'flow','route','transaction','event','ref','move','borrow',
    'try','catch','finally','raise','ensure'
}

# Noise words (per decision: treated as identifiers)
NOISE_WORDS = {'the', 'then', 'of'}

####################################
# LEXER
####################################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    # lookahead helper
    def peek(self, offset=1):
        idx = self.pos.idx + offset
        return self.text[idx] if 0 <= idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char is not None:
            # whitespace (spaces and tabs)
            if self.current_char in ' \t':
                self.advance()

            # comments (# ... newline)
            elif self.current_char == '#':
                self.skip_comment()

            # newline token
            elif self.current_char == '\n':
                tokens.append(Token(TT_NEWLINE))
                self.advance()

            # identifiers must start with a letter (capital or small)
            elif self.current_char in letters:
                tokens.append(self.make_identifier())

            # numbers
            elif self.current_char in numbers:
                tokens.append(self.make_number())

            # strings (single or double quote)
            elif self.current_char == '"':
                tokens.append(self.make_string('"'))
            elif self.current_char == "'":
                tokens.append(self.make_string("'"))

            # plus, plus= 
            elif self.current_char == '+':
                tokens.append(self._make_plus())

            # minus, minus=
            elif self.current_char == '-':
                tokens.append(self._make_minus())

            # star: *, **, *=, **=
            elif self.current_char == '*':
                tokens.append(self._make_star())

            # slash: /, //, /=, //=
            elif self.current_char == '/':
                tokens.append(self._make_slash())

            # percent: %, %=
            elif self.current_char == '%':
                tokens.append(self._make_mod())

            # assignment / equality
            elif self.current_char == '=':
                tokens.append(self._make_equals())

            # not equals (starts with '!')
            elif self.current_char == '!':
                tokens.append(self._make_not_equals())

            # relational < <=
            elif self.current_char == '<':
                tokens.append(self._make_less())

            # relational > >=
            elif self.current_char == '>':
                tokens.append(self._make_greater())

            # parentheses, comma, colon
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN)); self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN)); self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA)); self.advance()
            elif self.current_char == ':':
                tokens.append(Token(TT_COLON)); self.advance()

            # dot: member access or start of a float like ".5"
            elif self.current_char == '.':
                nxt = self.peek()
                if nxt is not None and nxt in numbers:
                    # treat as a float starting with a dot
                    tokens.append(self.make_number())
                else:
                    tokens.append(Token(TT_DOT)); self.advance()

            else:
                pos_start = self.pos.copy()
                ch = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f"'{ch}'")

        return tokens, None

    ####################
    # helpers
    ####################

    def skip_comment(self):
        # consume until newline or EOF
        self.advance()
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        # newline token will be handled by main loop

    def make_string(self, quote_type):
        # assume current_char == opening quote
        self.advance()  # skip opening quote
        s = ''
        escape = False

        while self.current_char is not None and (self.current_char != quote_type or escape):
            if escape:
                if self.current_char == 'n':
                    s += '\n'
                elif self.current_char == 't':
                    s += '\t'
                else:
                    s += self.current_char
                escape = False
            else:
                if self.current_char == '\\':
                    escape = True
                else:
                    s += self.current_char
            self.advance()

        # consume closing quote if present
        if self.current_char == quote_type:
            self.advance()
            return Token(TT_STRING, s)
        # unterminated string: still return what we captured
        return Token(TT_STRING, s)

    def make_identifier(self):
        # First char is guaranteed to be a letter
        id_str = self.current_char
        self.advance()

        # subsequent chars: letters, numbers, underscore
        while (self.current_char is not None and
                (self.current_char in letters or
                self.current_char in numbers or
                self.current_char == '_')):
            id_str += self.current_char
            self.advance()

        # Prefer returning explicit TYPE tokens for data-type keywords
        if id_str in TYPE_KEYWORDS:
            return Token(TYPE_KEYWORDS[id_str], id_str)

        # existing behavior: reserved/keyword/identifier
        if id_str in RESERVED_WORDS:
            return Token(TT_RESERVED, id_str)
        if id_str in KEYWORDS:
            return Token(TT_KEYWORD, id_str)
        return Token(TT_IDENTIFIER, id_str)

    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char is not None and (self.current_char in numbers + '.'):
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        return Token(TT_FLOAT, float(num_str))

    ####################
    # operator helpers
    ####################

    def _make_plus(self):
        # handles + and +=
        self.advance()
        if self.current_char == '=':
            self.advance(); return Token(TT_PLUSEQ)
        return Token(TT_PLUS)

    def _make_minus(self):
        # handles - and -=
        self.advance()
        if self.current_char == '=':
            self.advance(); return Token(TT_MINUSEQ)
        return Token(TT_MINUS)

    def _make_star(self):
        # handles *, **, *=, **=
        self.advance()
        if self.current_char == '*':
            self.advance()
            if self.current_char == '=':
                self.advance(); return Token(TT_POWEQ)
            return Token(TT_POW)
        if self.current_char == '=':
            self.advance(); return Token(TT_MULTEQ)
        return Token(TT_MUL)

    def _make_slash(self):
        # handles /, //, /=, //=
        self.advance()
        if self.current_char == '/':
            self.advance()
            if self.current_char == '=':
                self.advance(); return Token(TT_FLOOREQ)
            return Token(TT_FLOOR)
        if self.current_char == '=':
            self.advance(); return Token(TT_DIVEQ)
        return Token(TT_DIV)

    def _make_mod(self):
        # handles % and %=
        self.advance()
        if self.current_char == '=':
            self.advance(); return Token(TT_MODEQ)
        return Token(TT_MOD)

    def _make_equals(self):
        # handles = and ==
        self.advance()
        if self.current_char == '=':
            self.advance(); return Token(TT_EE)
        return Token(TT_EQ)

    def _make_not_equals(self):
        # handles ! and != (treat lone '!' as error token 'BANG' for completeness)
        self.advance()
        if self.current_char == '=':
            self.advance(); return Token(TT_NE)
        return Token('BANG')

    def _make_less(self):
        # handles < and <=
        self.advance()
        if self.current_char == '=':
            self.advance(); return Token(TT_LTE)
        return Token(TT_LT)

    def _make_greater(self):
        # handles > and >=
        self.advance()
        if self.current_char == '=':
            self.advance(); return Token(TT_GTE)
        return Token(TT_GT)

####################################
# RUN
####################################

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    return tokens, error

####################################
# QUICK TEST (optional)
####################################

# if __name__ == '__main__':
#     sample = '''
#     # sample DSArv snippet
#     stack clothes
#     clothes.push("Bench")
#     clothes.push('Penshoppe')
#     print(clothes.peek())
#     jabee = queue
#     jabee.enqueue("Frances")
#     jabee.enqueue("Cherry")
#     jabee.dequeue()
#     x = 3.14
#     a += 2
#     if a == 5:
#         print("ok")
#     '''
#     toks, err = run('<stdin>', sample)
#     print(toks)
#     if err:
#         print(err.as_string())