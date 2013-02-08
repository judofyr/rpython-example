import sys
import os

def slurp(fp):
    body = ""
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        body += read
    return body

def run(body):
    stack = []

    for char in body:
        if char == '1':
            stack.append(1)
        elif char == '2':
            stack.append(2)
        elif char == '+':
            a = stack.pop()
            b = stack.pop()
            stack.append(a + b)
        elif char == '.':
            print stack.pop()

def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print "You must supply a filename"
        return 1

    fp = os.open(filename, os.O_RDONLY, 0777)
    body = slurp(fp)
    run(body + " ")
    os.close(fp)
    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)

