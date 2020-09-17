import sys
import numpy as np

if(len(sys.argv) != 3):
    sys.exit(1)

try:
    x = np.loadtxt(sys.argv[1])
except:
    print('Cannot load ' + sys.argv[1], file = sys.stderr)
    sys.exit(1)

try:
    y = np.loadtxt(sys.argv[2])
except:
    print('Cannot load ' + sys.argv[2], file = sys.stderr)
    sys.exit(1)

print(np.dot(x, y) / np.dot(x,x)**0.5 / np.dot(y,y) ** 0.5)