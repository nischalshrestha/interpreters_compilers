## (c) Peter Norvig, 2010; See http://norvig.com/lispy2.html

# I have made some minor changes for Python3, some typo fixes, and better printing
# but works the same as original.

import re, sys, io # StringIO -> io.StringIO

################ Symbol, Procedure, classes

class Symbol(str): pass

def Sym(s, symbol_table={}):
    """Find or create unique Symbol entry for str s in symbol table"""
    if s not in symbol_table: symbol_table[s] = Symbol(s)
    return symbol_table[s]

# destructuring in action again (this time with result of map)
_quote, _if, _set, _define, _lambda, _begin, _definemacro = map(Sym, 
"quote   if   set!   define   lambda   begin   define-macro".split())

_quasiquote, _unquote, _unquotesplicing = map(Sym, 
"quasiquote   unquote   unquote-splicing".split())

class Procedure(object):
    """User-defined Scheme procedure"""
    def __init__(self, params, exp, env):
        self.params, self.exp, self.env = params, exp, env
    
    def __call__(self, *args):
        return eval(self.exp, Env(self.params, args, self.env))
    
################ parse, read, and user interaction

def parse(inport):
    """Parse a program: read and expand/error-check it."""
    if isinstance(inport, str): inport = InPort(io.StringIO(inport))
    return expand(read(inport), toplevel=True)

eof_object = Symbol('#<eof-object>') # Note: uninterned; can't be read

class InPort(object):
    """An input port. Retains a line of chars"""
    # TODO: use a tokenizer without using regex for readability/maintainability
    tokenizer = r'''\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)'''

    def __init__(self, file):
        self.file = file; self.line = ''
        
    def next_token(self):
        """Return the next token, reading new text into line buffer if needed."""
        while True:
            if self.line == '': self.line = self.file.readline()
            if self.line == '': return eof_object
            token, self.line = re.match(InPort.tokenizer, self.line).groups()
            if token != '' and not token.startswith(';'):
                return token

def readchar(inport):
    """Read next char from an inport port"""
    if inport.line != '':
        ch, inport.line = inport.line[0], inport[1:]
        return ch
    else:
        return inport.file.read(1) or eof_object

def read(inport):
    """Read a Scheme expression from an input port."""
    def read_ahead(token):
        if '(' == token:
            L = []
            while True:
                token = inport.next_token()
                if token == ')': return L
                else: L.append(read_ahead(token))
        elif ')' == token: raise SyntaxError('unexpected )')
        elif token in quotes: return [quotes[token], read(inport)]
        elif token is eof_object: raise SyntaxError('unexpected EOF in list')
        else: return atom(token)

quotes = {"'":_quote, "`":_quasiquote, ",":_unquote, ",@":_unquotesplicing}

def atom(token):
    """Numbers become numbers; #t and #f booleans; "..." strings; otherwise, Symbol."""
    if token == '#t': return True
    elif token == '#f': return False
    elif token[0] == '"': return token[1:-1].decode('string_escape')
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            try: return complex(token.replace('i','j',1))
            except ValueError:
                return Symbol(token)

def to_string(x):
    "Convert a Python object back into a Lisp-readable string."
    if x is True: return "#t"
    elif x is False: return "#f"
    elif isa(x, Symbol): return x
    elif isa(x, str): return '"%s"' % x.encode('string_escape').replace('"',r'\"')
    elif isa(x, list): return '('+' '.join(map(to_string, x))+')'
    elif isa(x, complex): return str(x).replace('j', 'i')
    else: return str(x)

def load(filename):
    """Eval every expression from a file."""
    repl(None, InPort(open(filename)), None)

def repl(prompt='lispy> ', inport=InPort(sys.stdin), out=sys.stdout):
    """A read-eval-print-loop"""
    while True:
        try:
            if prompt: sys.stderr.write(prompt)
            x = parse(inport)
            if x is eof_object: return
            val = eval(x)
            if val is not None and out: print(to_string(val), file=out)
        except Exception as e:
            print(f"{type(e).__name__}: {e}")

################ Environment class

class Env(dict):
    """An environment: a dict of {'var': val} pairs, with an outer Env"""
    def __init__(self, params=(), args=(), outer=None):
        self.outer = outer
        if isa(params, Symbol):
            self.update({params: list(args)})    
        else:
            if len(args) != len(params):
                raise TypeError(f"expected {to_string(params)}, given {to_string(args)}")
            self.update(zip(params, args))
    
    def find(self, var):
        """Find the innermost Env where var appears"""
        if var in self: return self
        elif self.outer is None: raise LookupError(var)
        else: return self.outer.find(var)


def is_pair(x): return x != [] and isa(x, list)
def cons(x, y): return [x]+y

# TODO store the continuation away and call it multiple times, each time 
# returning to the same place. (like true Scheme call/cc)
def call_cc(proc):
    """Call proc with current continuation; escape only"""
    ball = RuntimeWarning("Sorry, can't continue this continuation any longer.")
    def throw(retval): ball.retval = retval; raise ball
    try:
        return proc(throw)
    except RuntimeError as w:
        if w is ball: return ball.retval
        else: raise w

def add_globals(env) -> Env:
    """An environment with some Scheme standard procedures"""
    import math, cmath, operator as op
    env.update(vars(math))
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'abs':      abs,
        'append':   op.add,
        'apply':    lambda proc, args: proc(*args),
        'begin':    lambda *x: x[-1], # we unpack bc we're given variadic args, not a list
        'car':      lambda x: x[0],
        'cdr':      lambda x: x[1:],
        'cons':     cons,
        'pair?':    is_pair,
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

isa = isinstance
global_env = add_globals(Env())

################ eval (tail recursive)

# TODO make tail recursive
def eval(x, env=global_env):
    """Evaluate an expression in an environment"""
    if isa(x, Symbol):              # variable reference 
        return env.find(x)[x]
    elif not isa(x, List):          # constant number
        return x
    op = x[0]
    if op == _quote:               # (quote exp)
        _, exp = x
        return exp
    elif op == _if:                # (if test conseq alt)
        # this is called 'destructuring'
        _, test, conseq, alt = x
        x = conseq if eval(test, env) else alt
    elif op == _define:            # (define var exp)
        _, var, exp = x
        env[var] = eval(exp, env)
        return None
    elif op == _set:               # (set! var exp)
        _, var, exp = x
        env.find(var)[var] = eval(exp, env)
        return None
    elif op == _lambda:            # (lambda (var*) exp)
        _, params, exp = x
        return Procedure(params, exp, env)
    elif op == _begin:             # (begin exp+)
        _, params, body = x
        for exp in x[1:-1]:
            eval(exp, env)
        x = x[-1]
    else:                           # (proc exp*)
        exps = [eval(exp, env) for exp in x]
        proc = exps.pop(0) 
        if isa(proc, Procedure):
            x = proc.exp
            env = Env(proc.params, exps, proc.env)
        else:
            return proc(*exps)

################ expand (handle macros)

def expand(x, toplevel=False):
    """Walk tree of x and make optimizations/fixes, and signal SyntaxError"""
    require(x, x != [])                 # () => Error
    op = x[0]
    if not isa(x, list):                # constant
        return x
    elif op is _quote:                  # (quote exp)
        require(x, len(x) == 2)
        return x
    elif op is _if:
        if len(x) == 3: x = x + [None]  # (if t c) => (if t c None) 
        require(x, len(x) == 4)
        return map(expand, x)
    elif op is _set:                    # (set! non-var exp) => Error
        require(x, len(x) == 3)
        var = x[1]
        require(x, isa(var, Symbol), "can set! only a symbol")
        return [_set, var, expand(x[2])]
    elif op is _define or op is _definemacro:
        require(x, len(x) >= 3)
        _def, v, body = op, x[1], x[2:]
        if isa(v, list) and v:          # (define (f args) body)
            f, args = v[0], v[1:]       # => (define f (lambda (args) body))
            return expand([_def, f, [_lambda, args] + body])
        else:
            require(x, len(x) == 3)     # (define non-var/list exp) => Error
            require(x, isa(v, Symbol), "can define only a symbol")
            exp = expand(x[2])
            if _def is _definemacro:
                require(x, toplevel, "define-macro only allowed at top level")
                proc = eval(exp)
                require(x, callable(proc))
                macro_table[v] = proc   # (define-macro v proc)
                return None             # => None; add v:proc to macro_table
            return [_define, v, exp]
    elif op is _begin:
        if len(x) == 1: return None     # (begin) => None
        else: return [expand(xi, toplevel) for xi in x]
    elif op is _lambda:                 # (lambda (x) e1 e2) 
        require(x, len(x) >= 3)         #  => (lambda (x) (begin e1 e2))
        vars, body = x[1], x[2:]
        require(x, (isa(vars, list) and all(isa(v, Symbol) for v in vars))
                or isa(vars, Symbol), "illegal lambda argument list")
        exp = body[0] if len(body) == 1 else [_begin] + body
        return [_lambda, vars, expand(exp)]
    elif op is _quasiquote:
        require(x, len(x) == 2)
        return expand_quasiquote(x[1])
    elif isa(x[0], Symbol) and x[0] in macro_table:
        return expand(macro_table[x[0]](*x[1:]), toplevel) # (m arg...) 
    else:                                #        => macroexpand if m isa macro
        return map(expand, x)            # (f arg...) => expand each

def require(x, predicate, msg="wrong length"):
    """Signal a syntax error if predicate is false."""
    if not predicate: raise SyntaxError(to_string(x)+': '+msg)

_append, _cons, _let = map(Sym, "append cons let".split())

def expand_quasiquote(x):
    """Expand `x => 'x; `,x => x; `(,@x y) => (append x y)"""
    if not is_pair(x):
        return [_quote, x]
    require(x, x[0] is not _unquotesplicing, "can't splice here")
    if x[0] is _unquote:
        require(x, len(x) == 2)
        return x[1]
    elif is_pair(x[0]) and x[0][0] is _unquotesplicing:
        require(x[0], len(x[0])==2)
        return [_append, x[0][1], expand_quasiquote(x[1:])]
    else:
        return [_cons, expand_quasiquote(x[0]), expand_quasiquote(x[1:])]

def let(*args):
    args = list(args)
    x = cons(_let, args)
    require(x, len(args) > 1)
    bindings, body = args[0], args[1:]
    blist = [isa(b, list) and len(b) == 2 and isa(b[0], Symbol) for b in bindings]
    require(x, all(blist), "illegal binding list")
    vars, vals = zip(*bindings)
    return [[_lambda, list(vars)] + map(expand, body)] + map(expand, vals)

macro_table = {_let:let} # More macros can go here

# TODO add a way to read / compile scm files as well
# if __name__ == '__main__':
    # repl()