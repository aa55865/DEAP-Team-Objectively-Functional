import random, operator, time
import numpy as np
from deap import algorithms, base, tools, creator
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import os
from results_extractor import *


def deap_solver(design_var_dict, obj_func_names=None, norm_facts=None, POPSIZE=1000, GENS=50, MUTPB=None, CXPB=None, SURVIVORS=100, CHILDREN=1000, constraints=None):
    combination_dict = {'initial_val': None}

    def func_eval(individual): # evaluate individual fitness by plugging variables into objective function(s)
        combination = '{}, {:.1f}'.format(individual[0],individual[1])
        if combination not in combination_dict.keys(): #update dictionary with current solution string if not in dictionary yet
            combination_dict.update({combination: (1,1)}) #assign default value to solution in solution dictionary (gets overwritten at the end of func_eval
            infill_type = individual[0]
            with open('inputs.txt','w+') as writefile:
                for value in individual:
                    writefile.write('{}\n'.format(value))

            os.system('abaqus cae noGUI={}_thermo.py'.format(infill_type))
            os.system('abaqus cae noGUI={}_stress.py'.format(infill_type))

            while 'stress_results' not in 'Abaqus results directory':
                time.sleep(5)
            results = extractor()
            combination_dict[combination] = results #update solution dictionary to check against future individuals
            return results
        else:
            return combination_dict[combination] #return same fitness value as previously calculated if individual already evaluated

    def uniform(): # fill each individual in the initial population with total bits in design_var_dict
        individual = []
        for var in design_var_dict:
            if design_var_dict[var]['type'] == 'discrete':
                individual.append(random.choice(design_var_dict[var]['options']))
            else:
                individual.append(random.uniform(design_var_dict[var]['interval'][0],design_var_dict[var]['interval'][1]))
        return individual

    def cx_list(ind1, ind2): # define crossover strategy for lists
        cxPt = random.randint(0,len(ind1)-1)
        child1 = toolbox.individual()
        child2 = toolbox.individual()
        child1[::] = ind1[0:cxPt]+ind2[cxPt::]
        child2[::] = ind2[0:cxPt]+ind1[cxPt::]
        return child1,child2

    def mut_list(individual): # define mutation strategy for lists
        mutPoint = random.randint(0,len(individual)-1)
        if type(individual[mutPoint]) is str:
            if individual[mutPoint] == 'zig-zag': individual[mutPoint] = 'sine-wave'
            else: individual[mutPoint] == 'zig-zag'
        else: individual[mutPoint] = random.choice(design_var_dict['thickness']['interval'][0],design_var_dict['thickness']['interval'][1])
        return individual,

    creator.create("Fitness", base.Fitness, weights=(-1.0,-1.0)) # create fitness class inherited from 'base.Fitness' class
    creator.create("Individual", list, fitness=creator.Fitness) # create Individual class inherited from 'list' class
    toolbox = base.Toolbox() # initialize toolbox class from 'base', contains all evolutionary operators
    toolbox.register("initializer", uniform) # register function 'uniform' to initialize individuals
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.initializer) # register 'individual' creator in toolbox
    toolbox.register("population", tools.initRepeat, list, toolbox.individual) # register 'population' creator in toolbox
    toolbox.register("mate", cx_list) # register crossover strategy as function 'cx_list'
    toolbox.register("mutate",mut_list) # register mutation strategy as function 'mut_list'
    toolbox.register("evaluate", func_eval) # register evaluation strategy as function 'func_eval'
    # if constraints:
    #     toolbox.decorate("evaluate", tools.DeltaPenality(feasibility,10000)) # decorate evaluation strategy with constraints if they exist
    toolbox.register("select", tools.selNSGA2) # register selection strategy for sorting evaluated individuals as NSGA-II
    stats = tools.Statistics(lambda ind: ind.fitness.values) # log statistics during evolution
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)

    pop = toolbox.population(n=POPSIZE) # generate initial population
    hof = tools.ParetoFront() # register criteria for selecting hall of fame individuals (Pareto dominant solutions)
    output = algorithms.eaMuPlusLambda(pop, toolbox, SURVIVORS, CHILDREN, CXPB, MUTPB, GENS, stats, halloffame=hof) # conduct evolutionary optimization process


    headerList = ['Solution Point']
    for var in design_var_dict: headerList.append(var)
    for name in obj_func_names: headerList.append(name)
    results = PrettyTable(headerList) # generate table to store and display results

    solution = 1
    solutionList = []
    for individual in output[0]: # put optimal solutions into 'results' table
        solutionList.append(individual[0])
        solutionList.append(individual[1])
        for val,norm_fact in zip(individual.fitness.values,norm_facts):
            solutionList.append(val*norm_fact)
        results.add_row(solutionList)
        solution+=1

    non_dom = tools.sortNondominated(output[0], k=len(output[0]), first_front_only=True)[0]
    for ind in non_dom:
        fitvals = [ind.fitness.value*norm_fact for ind.fitness.value,norm_fact in zip(ind.fitness.values,norm_facts)]
        plt.plot(*fitvals,'bo')
    plt.title('Pareto Front')
    plt.xlabel('{}'.format(obj_func_names[0]))
    plt.ylabel('{}'.format(obj_func_names[1]))
    plt.show()
    return results


design_vars = {'infill': {'type': 'discrete', 'options': ['zig-zag', 'sine-wave','cross-hatch','grid']},
               'thickness': {'type': 'continuous', 'interval': [3, 9], 'bits': 8}}
gens = 50
popSize = 10
cxPB = 0.5
mutPB = 0.5
survivors = 5
children = 10

obj_func_names = ['T_avg [Celsius]', 'max_stress [MPA]']
norm_facts = [30, 60000]

deap_solver(design_vars, obj_func_names, norm_facts, popSize, gens, mutPB, cxPB, survivors, children)
