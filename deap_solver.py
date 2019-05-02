import random, operator
import numpy as np
from deap import algorithms, base, tools, creator
import matplotlib.pyplot as plt
from prettytable import PrettyTable


def deapSolver(design_var_dict, obj_func_list, obj_func_names=None, norm_facts=None, POPSIZE=1000, GENS=50, MUTPB=None, CXPB=None, SURVIVORS=100, CHILDREN=1000, constraints=None):
    """
    This is an optimization solver based on the Distributed Evolutionary Algorithms in Python (DEAP) package. It uses
    binary representations of design variables in each individual. Given an objective function (or list of objective
    functions) and constraints, the solver evolves each population of individuals based on the NSGA-II genetic algorithm.

    :param design_var_dict: dictionary of design variables
    :param obj_func_list: list of anonymous functions that represents the objective(s)
    :param obj_func_names: optional, specifies function names
    :param norm_facts: specify normalization factors for objective function outputs. If problem has
                       multiple objective functions with outputs expected to be on different orders of magnitude, this
                       is very important to include. Choose normalization factors approximately equal to maximum
                       expected output from its associated function
    :param POPSIZE: size of initial population
    :param GENS: number of generations to be evaluated
    :param MUTPB: probability of mutation
    :param CXPB: probability of crossover
    :param SURVIVORS: number of individuals selected after initial population is evaluated. This governs the size of all
                      future populations
    :param CHILDREN: number of offspring to be produced from the current population at each generation
    :param constraints: list constraints to be applied in evaluating the validity of each individual
    :return: the solver returns a table of solution points that contains the variable and objective function values for
             all optimized solutions. A print(results) statement will display the table. For problems with two objective
             functions, the solver also returns a plot of the Pareto Frontier

    EXAMPLE SETUP FOR SOLVER:

            design_var_dict = {'r': {'interval': [0,10],'bits': 10},'h':{'interval':[0,20],'bits':10}}

            S = lambda r,h: math.pi*r*math.sqrt(r**2+h**2)
            T = lambda r,h: math.pi*r**2+math.pi*r*math.sqrt(r**2+h**2)
            obj_func_list = [S,T]
            obj_func_names = ['Lateral Surface Area','Total Area']
            norm_facts = [155,225]

            constraints = [[V, '>', 200]] --> [[func(r,h),'operator',val],[func(r,h),'operator',val],etc.]

            gens = 50
            popSize = 1000
            mutPB = 0.1
            cxPB = 0.9
            survivors = 100
            children = 1000

            results = deapSolver(design_vars, func_list, obj_func_names=func_names, norm_facts=norm_facts,
                      POPSIZE=popSize, GENS=gens, MUTPB=mutPB, CXPB=cxPB, SURVIVORS=survivors, CHILDREN=children,
                      constraints=constraint_list)
    """
    # Assign values optional keyword arguments whose length depends on the number of objective functions specified
    if norm_facts is None:
        norm_facts = [1 for _ in obj_func_list]

    if MUTPB is None:
        maxbits = 0
        for var in design_var_dict:
            if design_var_dict[var]['bits']>maxbits:
                maxbits=design_var_dict[var]['bits']
        MUTPB = 1/maxbits

    if CXPB is None:
        CXPB  = 1-MUTPB

    if obj_func_names is None:
        obj_func_names = ['f{}'.format(i+1) for i in range(len(obj_func_list))]


    def bi2de_ind(individual): # convert binary individuals to list of decimal variable values
        deciInd = []
        counter = 0
        for var in design_var_dict:
            xL = design_var_dict[var]['interval'][0]
            xU = design_var_dict[var]['interval'][1]
            diff = xU - xL
            bits = design_var_dict[var]['bits']
            step = diff / (2 ** bits - 1)
            binary = ''.join(map(str, individual[counter:(counter + bits)]))
            deciVal = int(binary, 2)
            deciInd.append(xL + deciVal * step)
            counter += bits
        return deciInd

    def func_eval(individual): # evaluate individual fitness by plugging variables into objective function(s)
        deciInd = bi2de_ind(individual)
        outputs = [func(*deciInd)/norm_fact for func,norm_fact in zip(obj_func_list,norm_facts)]
        return tuple(outputs)

    ops = {'>': operator.gt,'<': operator.lt,'>=':operator.ge,'<=':operator.le,'=':operator.eq} #register operator dictionary for constraint evaluation
    def feasibility(individual): # determine if an individual's variables violate any constraints
        deciInd = bi2de_ind(individual)
        for constraint in constraints:
            if ops[constraint[1]](constraint[0](*deciInd),constraint[2]) is False:
                return False
        return True

    def uniform(): # fill each individual in the initial population with total bits in design_var_dict
        bits=0
        for var in design_var_dict:
            bits += design_var_dict[var]['bits']
        individual = [random.randint(0,1) for _ in range(bits)]
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
        if individual[mutPoint] == 1: individual[mutPoint] = 0
        else: individual[mutPoint] = 1
        return individual,

    weights = tuple([-1.0 for _ in obj_func_list]) # weight for all objectives are defaulted to -1
    creator.create("Fitness", base.Fitness, weights=weights) # create fitness class inherited from 'base.Fitness' class
    creator.create("Individual", list, fitness=creator.Fitness) # create Individual class inherited from 'list' class
    toolbox = base.Toolbox() # initialize toolbox class from 'base', contains all evolutionary operators
    toolbox.register("initializer", uniform) # register function 'uniform' to initialize individuals
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.initializer) # register 'individual' creator in toolbox
    toolbox.register("population", tools.initRepeat, list, toolbox.individual) # register 'population' creator in toolbox
    toolbox.register("mate", cx_list) # register crossover strategy as function 'cx_list'
    toolbox.register("mutate",mut_list) # register mutation strategy as function 'mut_list'
    toolbox.register("evaluate", func_eval) # register evaluation strategy as function 'func_eval'
    if constraints:
        toolbox.decorate("evaluate", tools.DeltaPenality(feasibility,10000)) # decorate evaluation strategy with constraints if they exist, penalize invalid individuals
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
    for individual in output[0]: # put optimal solutions into 'results' table
        solutionList = [solution]
        deciInd = bi2de_ind(individual)
        for val in deciInd:
            solutionList.append(val)
        for val,norm_fact in zip(individual.fitness.values,norm_facts):
            solutionList.append(val*norm_fact)
        results.add_row(solutionList)
        solution+=1

    if len(obj_func_list) == 2 : # if two objective functions provided, plot Pareto Frontier
        non_dom = tools.sortNondominated(output[0], k=len(output[0]), first_front_only=True)[0]
        for ind in non_dom:
            fitvals = [ind.fitness.value*norm_fact for ind.fitness.value,norm_fact in zip(ind.fitness.values,norm_facts)]
            plt.plot(*fitvals,'bo')
        plt.title('Pareto Front')
        plt.xlabel('{}'.format(obj_func_names[0]))
        plt.ylabel('{}'.format(obj_func_names[1]))
        plt.show()
        return results
    else:
        return results
