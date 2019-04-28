from deapSolver import *
import math


# designVars = {'x1': {'interval': [-1.5,1.5], 'bits': 8, 'type': 'continuous'}, 'x2': {'interval': [-1.5,1.5], 'bits': 8, 'type': 'continuous'}}
#
# gens = 50
# popSize = 100
# mutPB = 0.2
# cxPB = 0.8
#
# f1 = lambda x1, x2: 0.5 * (math.sqrt(1 + (x1 + x2) ** 2) + math.sqrt(1 + (x1 - x2) ** 2) + x1 - x2) + 0.85 * math.exp(-(x1 - x2) ** 2)
# f2 = lambda x1, x2: 0.5 * (math.sqrt(1 + (x1 + x2) ** 2) + math.sqrt(1 + (x1 - x2) ** 2) - x1 + x2) + 0.85 * math.exp(-(x1 - x2) ** 2)
# funcList = [f1, f2]

designVars = {'x1': {'interval': [-7,7], 'bits': 6}}
gens = 10
popSize = 10
mutPB = 0.05
cxPB = 0.8
elites = 2
children = 20

f1 = lambda x: -(math.sin(x) + 0.05*x**2 + 1)
funcList = [f1]

deapSolver(designVars,funcList,popSize,gens,mutPB,cxPB, elites, children)
