## (c) Peter Norvig, 2010-18; See http://norvig.com/lispy.html

# I have made some minor changes for Python version and better printing
# but works the same as original

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
    env.update(vars(cmath))
    self.update({
     '+':op.add, '-':op.sub, '*':op.mul, '/':op.div, 'not':op.not_, 
     '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
     'equal?':op.eq, 
     'eq?':op.is_, 
     'length':len, 
     'cons':lambda x,y:[x]+list(y), 
     'car':lambda x:x[0], 
     'cdr':lambda x:x[1:], 'append':op.add,  
     'list':lambda *x:list(x), 
     'list?': lambda x:isa(x,list),
     'null?':lambda x:x==[], 
     'symbol?':lambda x: isa(x, Symbol),
     'boolean?':lambda x: isa(x, bool), 
     'pair?':is_pair, 
     'port?': lambda x:isa(x,file), 
     'apply':lambda proc,l: proc(*l), 
     'eval':lambda x: eval(expand(x)), 
     'load':lambda fn: load(fn), 
     'call/cc':callcc,
     'open-input-file':open,
     'close-input-port':lambda p: p.file.close(), 
     'open-output-file':lambda f:open(f,'w'), 
     'close-output-port':lambda p: p.close(),
     'eof-object?':lambda x:x is eof_object, 
     'read-char':readchar,
     'read':read, 
     'write':lambda x,port=sys.stdout:port.write(to_string(x)),
     'display':lambda x,port=sys.stdout:port.write(x if isa(x,str) else to_string(x))})
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

def to_string(x):
    "Convert a Python object back into a Lisp-readable string."
    if x is True: return "#t"
    elif x is False: return "#f"
    elif isa(x, Symbol): return x
    elif isa(x, str): return '"%s"' % x.encode('string_escape').replace('"',r'\"')
    elif isa(x, list): return '('+' '.join(map(to_string, x))+')'
    elif isa(x, complex): return str(x).replace('j', 'i')
    else: return str(x)

isa = isinstance

if __name__ == '__main__':
    repl()
