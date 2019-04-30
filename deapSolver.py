import random
import numpy as np
from datetime import datetime
from deap import algorithms, base, tools, creator
import matplotlib.pyplot as plt
from prettytable import PrettyTable


def deapSolver(designVarDict, objFuncList, popSize, gens, mutPB, cxPB, elites, children, *constraintList):

    def funcEval(individual):
        deciInd = []
        counter = 0
        for var in designVarDict:
            xL = designVarDict[var]['interval'][0]
            xU = designVarDict[var]['interval'][1]
            diff = xU-xL
            bits = designVarDict[var]['bits']
            step = diff/(2**bits-1)
            binary = ''.join(map(str,individual[counter:(counter+bits)]))
            deciVal = int(binary,2)
            deciInd.append(xL+deciVal*step)
            counter+=bits
        outputs = [func(*deciInd) for func in objFuncList]
        return tuple(outputs)

    def feasible(individual):
        deciInd = []
        counter = 0
        deciInd = []
        counter = 0
        for var in designVarDict:
            xL = designVarDict[var]['interval'][0]
            xU = designVarDict[var]['interval'][1]
            diff = xU-xL
            bits = designVarDict[var]['bits']
            step = diff/(2**bits-1)
            binary = ''.join(map(str,individual[counter:(counter+bits)]))
            deciVal = int(binary,2)
            deciInd.append(xL+deciVal*step)
            counter+=bits


    def uniform(designVars): #this function determines the values that fill each individual in the initial population
        random.seed(datetime.now())
        bits=0
        for var in designVars:
            bits += designVars[var]['bits']
        individual = [random.randint(0,1) for _ in range(bits)]
        return individual

    def cxList(ind1, ind2): #define crossover strategy for lists
        random.seed(datetime.now())
        cxPt = random.randint(0,len(ind1)-1)
        child1 = toolbox.individual()
        child2 = toolbox.individual()
        child1[::] = ind1[0:cxPt]+ind2[cxPt::]
        child2[::] = ind2[0:cxPt]+ind1[cxPt::]
        return child1,child2

    def mutList(individual): #define mutation strategy for lists
        random.seed(datetime.now())
        mutPoint = random.randint(0,len(individual)-1)
        if individual[mutPoint] == 1: individual[mutPoint] = 0
        else: individual[mutPoint] = 1
        return individual,

    weights = tuple([-1.0 for _ in objFuncList])
    creator.create("Fitness", base.Fitness, weights=weights)
    creator.create("Individual", list, fitness=creator.Fitness)
    toolbox = base.Toolbox()
    toolbox.register("designVar", uniform, designVarDict)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.designVar)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", cxList)
    toolbox.register("mutate",mutList)
    toolbox.register("evaluate", funcEval)
    if constraintList:
        toolbox.decorate('evaluate', tools.DeltaPenalty(feasible, 10,000))
    toolbox.register("select", tools.selNSGA2)
    pop = toolbox.population(n=popSize)
    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)

    stats = algorithms.eaMuPlusLambda(pop, toolbox, elites, children, cxPB, mutPB, gens, stats, halloffame=hof)
    
    fits = [ind.fitness.values[:] for ind in stats[0]]
    
    headerList = ['Solution'] # generate headers for table
    for var in designVarDict:
        headerList.append(var)
    for i in range(len(objFuncList)):
        headerList.append("f{0}".format(i+1))
    results = PrettyTable(headerList)
    solution = 1
    for individual in stats[0]: # generate rows of values for table
        solutionList = []
        counter = 0
        for var in designVarDict:
            xL = designVarDict[var]['interval'][0]
            xU = designVarDict[var]['interval'][1]
            diff = xU-xL
            bits = designVarDict[var]['bits']
            step = diff/(2**bits-1)
            binary = ''.join(map(str,individual[counter:(counter+bits)]))
            deciVal = xL + int(binary,2)*step
            print(deciVal)
            solutionList.append(solution)
            solutionList.append(deciVal)
        for fitVal in individual.fitness.values:
            solutionList.append(fitVal)
        results.add_row(solutionList)
    solution+=1
    
    print(results)

    if len(objFuncList) == 2 :
        non_dom = tools.sortNondominated(stats[0], k=len(stats[0]), first_front_only=True)[0]
        for ind in non_dom:
            plt.plot(*ind.fitness.values, 'bo')
        plt.title('Pareto Front')
        plt.xlabel('f1')
        plt.ylabel('f2')
        plt.show()
        return stats
    else:
        return stats


