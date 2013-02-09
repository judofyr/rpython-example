from rply import ParserGenerator
from rply.token import BaseBox, Token
from rply.errors import ParsingError
from uno.lexer import Lexer
import uno.ast as ast

tokens = ["PLUS", "MINUS", "MULT", "DIV", "INTEGER", "SEMICOLON", "NEWLINE", "IDENT", "LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "COMMA", "DOT", "COLON", "EQUAL", "PIPE", "LBRACE", "RBRACE", "RECUPDATE", "RECMETHOD"]
precedence = [
    ("left", ["EQUAL"]),
    ("left", ["PLUS", "MINUS"]),
    ("left", ["MULT", "DIV"]),
    ("left", ["LPAREN"]),
]

class BoxAST(BaseBox):
    def __init__(self, node):
        self.node = node

    def lineno_from(self, token):
        self.node.lineno = token.getsourcepos().lineno
        return self

    def getast(self):
        return self.node

class BoxASTList(BaseBox):
    def __init__(self, nodes):
        self.nodes = nodes

    def append(self, node):
        self.nodes.append(node)

    def getastlist(self):
        return self.nodes

def newast(node):
    return BoxAST(node)

def newastlist(nodes):
    return BoxASTList(nodes)

pg = ParserGenerator(tokens, precedence)

@pg.production("top_exprs : exprs opt_terms")
def main(p):
    return p[0]

@pg.production("exprs : expr")
def exprs_one(p):
    return p[0]

@pg.production("exprs : exprs terms expr")
def exprs_more(p):
    return newast(ast.Exprs(p[0].getast(), p[2].getast()))

@pg.production("term : SEMICOLON")
@pg.production("term : NEWLINE")
@pg.production("terms : term")
@pg.production("terms : terms term")
@pg.production("opt_terms : ")
@pg.production("opt_terms : term")
def term(p):
    return None

@pg.production("expr : INTEGER")
def expr_num(p):
    num = int(p[0].getstr())
    return newast(ast.Num(num)).lineno_from(p[0])

@pg.production("expr : IDENT")
def ident(p):
    return newast(ast.Var(p[0].getstr())).lineno_from(p[0])

@pg.production("expr : block")
def block_expr(p):
    return p[0]

@pg.production("param : IDENT")
@pg.production("param : IDENT expr")
def param(p):
    expr = None
    try:
        expr = p[1].getast()
    except IndexError:
        pass
    return newast(ast.Param(p[0].getstr(), expr)).lineno_from(p[0])

@pg.production("paramlist :")
def paramlist_none(p):
    return newastlist([])

@pg.production("paramlist : param")
def paramlist_one(p):
    return newastlist([p[0].getast()])

@pg.production("paramlist : paramlist COMMA param")
def paramlist_many(p):
    p[0].append(p[2].getast())
    return p[0]

@pg.production("blockvar : PIPE paramlist PIPE top_exprs")
def blockvar(p):
    return newast(ast.BlockVar(p[1].getastlist(), p[3].getast())).lineno_from(p[0])

@pg.production("blockvars : blockvar")
def blockvars_one(p):
    return newastlist([p[0].getast()])

@pg.production("blockvars : blockvars blockvar")
def blockvars_many(p):
    p[0].append(p[1].getast())
    return p[0]

@pg.production("block : LBRACKET blockvars RBRACKET")
def block_with_vars(p):
    return newast(ast.Block(p[1].getastlist())).lineno_from(p[0])

@pg.production("block : LBRACKET top_exprs RBRACKET")
def block_without_vars(p):
    return newast(ast.Block([ast.BlockVar([], p[1].getast())])).lineno_from(p[0])

@pg.production("listterm : COMMA")
@pg.production("listterm : NEWLINE")
@pg.production("opt_listterm :")
@pg.production("opt_listterm : listterm")
def recterm(p):
    return None

## Records
@pg.production("expr : LBRACE recfields opt_listterm RBRACE")
def record(p):
    return newast(ast.Record(p[1].getastlist())).lineno_from(p[0])

@pg.production("recfields :")
def recfields_none(p):
    return newastlist([])

@pg.production("recfields : recfield")
def recfields_one(p):
    return newastlist([p[0].getast()])

@pg.production("recfields : recfields listterm recfield")
def recfields_many(p):
    p[0].append(p[2].getast())
    return p[0]

@pg.production("recfield : IDENT COLON expr")
def recfield_set(p):
    return newast(ast.RecfieldSet(p[0].getstr(), p[2].getast())).lineno_from(p[0])

@pg.production("recfield : IDENT RECUPDATE expr")
def recfield_update(p):
    return newast(ast.RecfieldUpdate(p[0].getstr(), p[2].getast())).lineno_from(p[0])

@pg.production("recfield : IDENT RECMETHOD block")
def recfield_update(p):
    return newast(ast.RecfieldMethod(p[0].getstr(), p[2].getast())).lineno_from(p[0])

@pg.production("recfield : expr")
def record_splat(p):
    return newast(ast.RecordSplat(p[0].getast()))

@pg.production("expr : expr PLUS expr")
@pg.production("expr : expr MINUS expr")
@pg.production("expr : expr MULT expr")
@pg.production("expr : expr DIV expr")
def expr_op(p):
    return newast(ast.Op(p[1].gettokentype(), p[0].getast(), p[2].getast())).lineno_from(p[1])

@pg.production("expr : LPAREN expr RPAREN")
def expr_sub(p):
    return p[1]

@pg.production("expr : IDENT EQUAL expr")
def expr_assign(p):
    return newast(ast.Assign(p[0].getstr(), p[2].getast())).lineno_from(p[0])

@pg.production("expr : expr DOT IDENT")
def expr_access(p):
    return newast(ast.Access(p[0].getast(), p[2].getstr())).lineno_from(p[2])

@pg.production("expr : expr COLON IDENT")
def expr_method(p):
    return newast(ast.Method(p[0].getast(), p[2].getstr())).lineno_from(p[2])

@pg.production("expr : expr LPAREN arglist opt_listterm RPAREN")
def expr_call(p):
    return newast(ast.Call(p[0].getast(), p[2].getastlist())).lineno_from(p[1])

@pg.production("arglist :")
def arglist_none(p):
    return newastlist([])

@pg.production("arglist : expr")
def arglist_one(p):
    return newastlist([p[0].getast()])

@pg.production("arglist : arglist listterm expr")
def arglist_many(p):
    p[0].append(p[2].getast())
    return p[0]


parser = pg.build()

