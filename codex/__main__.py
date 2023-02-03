import sys
from codex.parser import parse

if len(sys.argv) < 2:
    print("Usage: python -m codex <file>")
    sys.exit(1)

with open(sys.argv[1]) as fl:
    source = fl.read()

print(parse(source))