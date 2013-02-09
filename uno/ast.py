class Node(object):
    pass

class Op(Node):
    def __init__(self, type, left, right):
        self.type = type
        self.left = left
        self.right = right

    def dump(self):
        return ("op", self.type, self.left.dump(), self.right.dump())

    def run(self, env):
        left = self.left.run(env)
        right = self.right.run(env)
        return left.operator(env, self.type, right)

class Var(Node):
    def __init__(self, name):
        self.name = name

    def dump(self):
        return ("var", self.name)

    def run(self, env):
        return env.getattr(self.name)

class Num(Node):
    def __init__(self, value):
        self.value = value

    def dump(self):
        return ("num", self.value)

    def run(self, env):
        return env.newint(self.value)

class Param(Node):
    def __init__(self, name, guard):
        self.name = name
        self.guard = guard

class BlockVar(Node):
    def __init__(self, params, expr):
        self.params = params
        self.expr = expr

    def dump(self):
        return ("var", self.params, self.expr.dump())

class Block(Node):
    def __init__(self, vars):
        self.vars = vars

    def dump(self):
        return ("block", [x.dump() for x in self.vars])

    def run(self, env):
        return env.newblock(self.vars)

class Record(Node):
    def __init__(self, fields):
        self.fields = fields

    def dump(self):
        return ("record", [x.dump() for x in self.fields])

class Recfield(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def dump(self):
        return (self.type, self.name, self.value.dump())

class RecfieldSet(Recfield):
    type = "set"

class RecfieldUpdate(Recfield):
    type = "update"

class RecfieldMethod(Recfield):
    type = "method"

class RecordSplat(Node):
    def __init__(self, value):
        self.value = value

    def dump(self):
        return ("splat", self.value.dump())

class Access(Node):
    def __init__(self, expr, name):
        self.expr = expr
        self.name = name

    def dump(self):
        return ("access", self.expr.dump(), self.name)

class Method(Node):
    def __init__(self, expr, name):
        self.expr = expr
        self.name = name

    def dump(self):
        return ("method", self.expr.dump(), self.name)

class Call(Node):
    def __init__(self, base, args):
        self.base = base
        self.args = args

    def dump(self):
        return ("call", self.base.dump(), [x.dump() for x in self.args])

    def run(self, env):
        base = self.base.run(env)
        args = [arg.run(env) for arg in self.args]
        return base.call(env, args)

class Exprs(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def dump(self):
        return ("exprs", self.left.dump(), self.right.dump())

    def run(self, env):
        self.left.run(env)
        return self.right.run(env)

class Assign(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def dump(self):
        return ("assign", self.name, self.expr.dump())

    def run(self, env):
        value = self.expr.run(env)
        env.setattr(self.name, value)
        return value


