from rply.token import Token, SourcePosition

class Lexer(object):
    EOF = chr(0)

    def __init__(self, source):
        self.source = source
        self.idx = 0
        self.columno = 0
        self.lineno = 1
        self.current_value = []

    def add(self, ch):
        self.current_value.append(ch)

    def clear(self):
        del self.current_value[:]

    def current_pos(self):
        return SourcePosition(self.idx, self.lineno, self.columno)

    def newline(self):
        self.lineno += 1
        self.columno = 1

    def emit(self, token):
        value = "".join(self.current_value)
        self.clear()
        return Token(token, value, self.current_pos())

    def read(self):
        try:
            ch = self.source[self.idx]
        except IndexError:
            ch = self.EOF
        self.idx += 1
        self.columno += 1
        return ch

    def unread(self):
        idx = self.idx - 1
        assert idx >= 0
        self.idx = idx
        self.columno -= 1

    KEYWORDS = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "MULT",
        "/": "DIV",
        "(": "LPAREN",
        ")": "RPAREN",
        "[": "LBRACKET",
        "]": "RBRACKET",
        "{": "LBRACE",
        "}": "RBRACE",
        ",": "COMMA",
        ".": "DOT",
        ":": "COLON",
        "=": "EQUAL",
        "|": "PIPE",
    }

    def tokenize(self):
        skip_newline = False

        while True:
            ch = self.read()

            if ch == self.EOF:
                break
            elif ch.isdigit():
                skip_newline = False
                for token in self.number(ch):
                    yield token
            elif ch in " \r":
                pass
            elif ch == ":":
                self.add(ch)
                skip_newline = False
                more = self.read()
                if more == "=":
                    self.add(more)
                    yield self.emit("RECUPDATE")
                elif more == "~":
                    self.add(more)
                    yield self.emit("RECMETHOD")
                else:
                    self.unread()
                    yield self.emit("COLON")

            elif ch in "+-*/(),.:=[]|{}":
                skip_newline = not ch in ")]}"
                self.add(ch)
                yield self.emit(self.KEYWORDS[ch])
            elif ch in "\n":
                if not skip_newline:
                    self.add(ch)
                    yield self.emit("NEWLINE")
                self.newline()
                skip_newline = True
            elif ch in ";":
                skip_newline = True
                self.add(ch)
                yield self.emit("SEMICOLON")
            else:
                for token in self.identifier(ch):
                    yield token

        yield None

    def number(self, ch):
        self.add(ch)
        symbol = "INTEGER"
        while True:
            ch = self.read()
            if ch.isdigit():
                self.add(ch)
            else:
                yield self.emit(symbol)
                self.unread()
                break

    def identifier(self, ch):
        self.add(ch)
        symbol = "IDENT"
        while True:
            ch = self.read()
            if ch == self.EOF:
                yield self.emit(symbol)
                self.unread()
                break
            elif ch.isalnum() or ch == "_" or ord(ch) > 127:
                self.add(ch)
            else:
                yield self.emit(symbol)
                self.unread()
                break

