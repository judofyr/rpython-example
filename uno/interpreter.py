from uno.types import *

class Scope(object):
    def __init__(self, attrs={}, parent=None):
        self.attrs = attrs
        self.parent = parent

    def get(self, name):
        if self.parent is None:
            return self.attrs[name]

        try:
            return self.attrs[name]
        except KeyError:
            return self.parent.get(name)

    def set(self, name, value):
        self.attrs[name] = value

class Interpreter(object):
    def __init__(self, ast):
        self.ast = ast
        self.scope = Scope()

        self.setattr('print', W_NativeFunction(self.p))

    def p(self, args):
        print args[0].inspect()
    
    def run(self):
        self.ast.run(self)
    
    def getattr(self, name):
        return self.scope.get(name)

    def setattr(self, name, value):
        self.scope.set(name, value)

    def newint(self, value):
        return W_Integer(value)

    def newblock(self, vars):
        return W_Block(self.scope, vars)

    def inscope(self, attrs):
        return InScopeManager(self, attrs)

class InScopeManager(object):
    def __init__(self, env, attrs):
        self.env = env
        self.attrs = attrs

    def __enter__(self):
        self.env.scope = Scope(self.attrs, self.env.scope)

    def __exit__(self, exc_type, exc_value, tb):
        self.env.scope = self.env.scope.parent



