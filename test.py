from deapSolver import *
import math


# TEST PROBLEM 1
# designVars = {'x1': {'interval': [-1.5,1.5], 'bits': 8, 'type': 'continuous'}, 'x2': {'interval': [-1.5,1.5], 'bits': 8, 'type': 'continuous'}}
# gens = 50
# elites = 50
# children = 200
# popSize = 100
# mutPB = 0.2
# cxPB = 0.8
#
# lbda = 0.85
# f1 = lambda x1, x2: 0.5 * (math.sqrt(1 + (x1 + x2) ** 2) + math.sqrt(1 + (x1 - x2) ** 2) + x1 - x2) + lbda* math.exp(-(x1 - x2) ** 2)
# f2 = lambda x1, x2: 0.5 * (math.sqrt(1 + (x1 + x2) ** 2) + math.sqrt(1 + (x1 - x2) ** 2) - x1 + x2) + 0.85 * math.exp(-(x1 - x2) ** 2)
# funcList = [f1, f2]

# TEST PROBLEM 2
# designVars = {'x1': {'interval': [-7,7], 'bits': 6}}
# gens = 50
# popSize = 10
# mutPB = 0.05
# cxPB = 0.6
# elites = 2
# children = 20
#
# f1 = lambda x: -(math.sin(x) + 0.05*x**2 + 1)
# funcList = [f1]

# TEST PROBLEM 3

designVars = {'r': {'interval': [0,10],'bits': 6},'h':{'interval':[0,20],'bits':6}}
s = lambda r,h: math.sqrt(r**2+h**2)
V = lambda r,h: (math.pi/3)*(r**2)*h
B = lambda r: math.pi*r**2
S = lambda r,h: math.pi*r*s(r,h)
T = lambda r,h: B(r)+S(r,h)




stats = deapSolver(designVars,funcList,popSize,gens,mutPB,cxPB, elites, children)
