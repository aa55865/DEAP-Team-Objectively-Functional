from deapSolver import *
import math
    
DESIGNVARS = {'x1': {'interval': [-1.5,1.5], 'bits': 8, 'type': 'continuous'}, 'x2': {'interval': [-1.5,1.5], 'bits': 8, 'type': 'continuous'}}
GENS = 20
ELITES = 50
CHILDREN = 200
POPSIZE = 50
MUTPB = 0.2
CXPB = 0.8
LBDA = 0.85

class TestProblem:

    def __init__(self,designVars,gens,elites,children,popSize,mutPB,cxPB,lbda):
        self.designVars = designVars
        self.gens = gens
        self.elites = elites
        self.children = children
        self.popSize = popSize
        self.mutPB = mutPB
        self.cxPB = cxPB
        self.lbda = lbda

    def testEqns(self):
        f1 = lambda x1, x2: 0.5 * (math.sqrt(1 + (x1 + x2) ** 2) + math.sqrt(1 + (x1 - x2) ** 2) + x1 - x2) + lbda* math.exp(-(x1 - x2) ** 2)
        f2 = lambda x1, x2: 0.5 * (math.sqrt(1 + (x1 + x2) ** 2) + math.sqrt(1 + (x1 - x2) ** 2) - x1 + x2) + lbda* math.exp(-(x1 - x2) ** 2)
        funcList = [f1, f2]
        return funcList

func_list= TestProblem(designVars=DESIGNVARS,popSize=POPSIZE, gens=GENS,mutPB=MUTPB, cxPB=CXPB,children=CHILDREN, elites=ELITES,lbda=LBDA)

stats = deapSolver(designVars=DESIGNVARS, objFuncList=funcList, popSize=POPSIZE, gens=GENS,mutPB=MUTPB, cxPB=CXPB,children=CHILDREN, elites=ELITES)

# ------------------------------------------------------------------------------------------------
# TEST PROBLEM 1
# ------------------------------------------------------------------------------------------------
# design_vars = {'x1': {'interval': [-1.5,1.5], 'bits': 8}, 'x2': {'interval': [-1.5,1.5], 'bits': 8}}
# gens = 50
# survivors = 20
# children = 40
# popSize = 20
# mutPB = 0.125
# cxPB = 0.875
#
# lbda = 0.85
# f1 = lambda x1, x2: 0.5 * (math.sqrt(1 + (x1 + x2) ** 2) + math.sqrt(1 + (x1 - x2) ** 2) + x1 - x2) + lbda* math.exp(-(x1 - x2) ** 2)
# f2 = lambda x1, x2: 0.5 * (math.sqrt(1 + (x1 + x2) ** 2) + math.sqrt(1 + (x1 - x2) ** 2) - x1 + x2) + 0.85 * math.exp(-(x1 - x2) ** 2)
# func_list = [f1, f2]
#
# results = deapSolver(design_vars, func_list,POPSIZE=popSize,GENS=gens,MUTPB=mutPB,CXPB=cxPB,SURVIVORS=survivors,CHILDREN=children)
# print(results)

# ------------------------------------------------------------------------------------------------
# TEST PROBLEM 2
# ------------------------------------------------------------------------------------------------

# design_vars = {'x': {'interval': [-7,7], 'bits': 4}}
# gens = 50
# popSize = 100
# cxPB = 0.6
# survivors =10
# children = 100
#
# f1 = lambda x: -(math.sin(x) + 0.05*x**2 + 1)
# func_list = [f1]
#
# results = deapSolver(design_vars, func_list, POPSIZE=popSize, GENS=gens, CXPB=cxPB, SURVIVORS=survivors, CHILDREN=children)
# print(results)

# ------------------------------------------------------------------------------------------------
# TEST PROBLEM 3
# ------------------------------------------------------------------------------------------------

# design_vars = {'r': {'interval': [0,10],'bits': 10},'h':{'interval':[0,20],'bits':10}}
#
# s = lambda r,h: math.sqrt(r**2+h**2)
# V = lambda r,h: (math.pi/3)*(r**2)*h
# B = lambda r: math.pi*r**2
# S = lambda r,h: (math.pi*r*s(r,h))
# T = lambda r,h: (B(r)+S(r,h))
#
# func_list = [S,T]
# func_names = ['Lateral Surface Area','Total Area']
# norm_facts = [155,225]
# constraint_list = [[V, '>', 200]]
#
# gens = 50
# popSize = 1000
# mutPB = 0.1
# cxPB = 0.9
# survivors = 100
# children = 1000
#
# results = deapSolver(design_vars, func_list, obj_func_names=func_names, norm_facts=norm_facts, POPSIZE=popSize, GENS=gens, MUTPB=mutPB, CXPB=cxPB, SURVIVORS=survivors, CHILDREN=children, constraints=constraint_list)
# print(results)
