from uno.lexer import Lexer
from uno.parser import parser
from rply.errors import ParsingError

import os
import sys

def entry_point(argv):
    f = os.open("c.test", os.O_RDONLY, 0777)
    data = ""
    while True:
        res = os.read(f, 4096)
        if len(res) == 0:
            break
        data += res

    lexer = Lexer(data)
    res = parser.parse(lexer.tokenize())
    ast = res.getast()
    print ast.run({})
    return 0

def target(*args):
    return entry_point, None

if __name__ == '__main__':
    entry_point(sys.argv)

