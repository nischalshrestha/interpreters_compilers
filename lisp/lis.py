## (c) Peter Norvig, 2010-18; See http://norvig.com/lispy.html

# I have made some minor changes for Python version and better printing
# but works the same as original

# bug: not return a list of map() in expand

import math
import operator as op

"""Type Definitions"""
Symbol = str                # A Scheme Symbol is implemented as a Python str
Number = (int, float)       # A Scheme Number is implemented as a Python int or float
Atom = (Symbol, Number)     # A Scheme Atom is a Symbol or Number
List = list                 # A Scheme List is implemented as a Python list
Exp = (Atom, List)          # A Scheme expression is an Atom or List
Env = dict                  # A Scheme environment (defined below) 
                            # is a mapping of {variable: value}

def tokenize(chars: str) -> list:
    """Convert a string of chars into a list of tokens."""
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(program: str) -> Exp:
    """Read a Scheme expression from a string"""
    return read_from_tokens(tokenize(program))

def read_from_tokens(tokens: list) -> Exp:
    """Read a Scheme expression from a sequence of tokens"""
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0) # pop is used to consume
    if token == '(':
        L = []
        while tokens[0] != ')': # recurse until hitting )
            L.append(read_from_tokens(tokens)) 
        tokens.pop(0) # pop off )
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token: str) -> Atom:
    """Make an atom out of a token"""
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

def standard_env() -> Env:
    """An environment with some Scheme standard procedures"""
    env = Env()
    env.update(vars(math))
    env.update({
        # TODO make operators like + for apply
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'abs':      abs,
        'append':   op.add,
        'apply':    lambda proc, args: proc(*args),
        'begin':    lambda *x: x[-1], # we unpack bc we're given variadic args, not a list
        'car':      lambda x: x[0],
        'cdr':      lambda x: x[1:],
        'cons':     lambda x, y: [x] + y,
        'eq?':      op.is_, 
        'expt':     pow,
        'equal?':   op.eq,
        'length':   len,
        'list':     lambda *x: List(x),
        'list?':    lambda x: isa(x, List),
        'map':      lambda x, y: list(map(x, y)),
        'max':      max,
        'min':      min,
        'not':      op.not_,
        'null?':    lambda x: x == [],
        'number?':  lambda x: isa(x, Number),
        'print':    lambda x: schemestr(x),
        'procedure?': callable,
        'round':    round,
        'symbol?':  lambda x: isa(x, Symbol),
    })
    return env
        
def schemestr(exp) -> str:
    """Convert python object back to a Scheme-readable string"""
    if isa(exp, List):
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    else:
        return str(exp)

class Env(dict):
    """An environment: a dict of {'var': val} pairs, with an outer Env"""
    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer
    
    def find(self, var):
        """Find the innermost Env where var appears"""
        return self if (var in self) else self.outer.find(var)

class Procedure(object):
    """User-defined Scheme procedure"""
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env
    
    def __call__(self, *args):
        return eval(self.body, Env(self.params, args, self.env))

global_env = standard_env()

def eval(x: Exp, env=global_env) -> Exp:
    """Evaluate an expression in an environment"""
    if isa(x, Symbol):              # variable reference 
        return env.find(x)[x]
    elif not isa(x, List):          # constant number
        return x
    op, *args = x
    if op == 'quote':               # quotation
        return args[0]
    elif op == 'if':                # conditional
        # this is called 'destructuring'
        test, conseq, alt = args
        exp = conseq if eval(test, env) else alt
        return eval(exp, env)
    elif op == 'define':            # definition
        symbol, exp = args
        env[symbol] = eval(exp, env)
    elif op == 'set!':              # assignment
        symbol, exp = args
        env.find(symbol)[symbol] = eval(exp, env)
    elif op == 'lambda':            # procedure
        params, body = args
        return Procedure(params, body, env)
    else:                           # procedure call
        proc = eval(op, env) 
        args = [eval(arg, env) for arg in args]
        return proc(*args)

def repl(prompt='lis.py> '):
    """A read-eval-print-loop"""
    while True:
        cmd = input(prompt)
        if cmd == "exit":
            break
        val = eval(parse(cmd))
        if val is not None:
            print(schemestr(val))

def lispstr(x):
    "Convert a Python object back into a Lisp-readable string."
    if x is True: return "#t"
    elif x is False: return "#f"
    elif isa(x, Symbol): return x
    elif isa(x, str): return '"%s"' % x.encode('string_escape').replace('"',r'\"')
    elif isa(x, list): return '('+' '.join(map(lispstr, x))+')'
    elif isa(x, complex): return str(x).replace('j', 'i')
    else: return str(x)

isa = isinstance

if __name__ == '__main__':
    repl()
