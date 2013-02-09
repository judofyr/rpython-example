class W_Root(object):
    pass

class W_Integer(W_Root):
    def __init__(self, value):
        self.value = value

    def operator(self, env, type, right):
        if type == "PLUS":
            return env.newint(self.value + right.value)
        elif type == "MINUS":
            return env.newint(self.value - right.value)

    def matches(self, env, other):
        return self.value == other.value

    def inspect(self):
        return self.value

class Nope(Exception):
    pass

class W_Block(W_Root):
    def __init__(self, scope, vars):
        self.scope = scope
        self.vars = vars

    def call(self, env, args):
        for var in self.vars:
            try:
                return self.call_var(env, var, args)
            except Nope:
                pass

    def call_var(self, env, var, args):
        lvars = {}
        guards = {}

        i = 0
        for param in var.params:
            lvars[param.name] = args[i]
            if param.guard:
                guards[i] = param.guard
            i += 1

        with env.inscope(lvars):
            for i in guards:
                exp = guards[i].run(env)
                real = args[i]
                if not real.matches(env, exp):
                    raise Nope

            return var.expr.run(env)

class W_NativeFunction(W_Root):
    def  __init__(self, func):
        self.func = func

    def call(self, env, args):
        self.func(args)

