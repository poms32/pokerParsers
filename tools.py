import sys
import cStringIO
import traceback
import time
import os


# ---------------------------------------------------------------------------------------
def Print(*args, **kwargs):
    """
        This functions behaves like the new python 3.0 print function
        http://docs.python.org/dev/3.0/whatsnew/3.0.html#print-is-a-function
    """
    validkwargs = 'sep', 'end', 'file'
    for var in kwargs.iterkeys():
        if var not in validkwargs:
            raise TypeError('Invalid keyword in function arguments: %s' % var)
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    file = kwargs.get('file', sys.stdout)
    lenargs = len(args)-1
    for n, out in enumerate(args):
        file.write(str(out))
        if n!=lenargs:
            file.write(sep)
    if end:
        file.write(end)

# ---------------------------------------------------------------------------------------
def exc_plus(trunc=3000):
    """
    Return the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """

    if not any(sys.exc_info()):
        raise RuntimeError('No exception on stack')

    ret = cStringIO.StringIO()
    traceback.print_exc(file=ret)

    tb = sys.exc_info()[2]
    while 1:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()

    Print(' '*4, "Locals by frame, innermost last:", file=ret)
    for frame in stack:
        Print(' '*6, "Frame %s in %s at line %s:" % (frame.f_code.co_name, frame.f_code.co_filename, frame.f_lineno), file=ret)
        for k, v in sorted(frame.f_locals.iteritems()):
            try:
                v = repr(v)
                if len(v) > trunc:
                    v = v[:trunc-len('---truncated---')]+'---truncated---'
                Print(' '*8, '%-16s'%str(k), ' = ',  str(v)[:trunc], sep='', file=ret)
            except:
                Print(' '*8, 'FAILED TO PRINT VALUE', sep='', file=ret)
    return ret.getvalue()

# ---------------------------------------------------------------------------------------
def errorhandling(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            Print(exc_plus())
            raise
    return wrapper


# ---------------------------------------------------------------------------------------
def timeit(func):
    def wrapper(*args, **kwargs):
        t = time.time()
        func(*args, **kwargs)
        td = time.time() - t

        d=int(td/86400)      #days
        h=int(td%86400/3600) #hours
        m=int(td%3600/60)    #minutes
        s=td%60              #seconds

        out = ''
        if d>0:
            out += '%id'%d
        if h>0:
            out += '%02ih'%h
        out += '%02im%02is'%(m,s)

        print "time elapsed:", out
    return wrapper
    
# ---------------------------------------------------------------------------------------
def iterfiles(folder):
    for r,d,f in os.walk(folder):
        for fn in f:
            yield os.path.join(r, fn)