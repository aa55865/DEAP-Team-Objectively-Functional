# DEAP-Team-Objectively-Functional
Multi-Objective Genetic Algorithm Optimization

NOTE: Please install DEAP and PrettyTable packages to run this solver.
Link to DEAP: https://pypi.org/project/deap/
Link to PrettyTable: https://pypi.org/project/PrettyTable/

This is an optimization solver based on the Distributed Evolutionary Algorithms in Python (DEAP) package. It uses
binary representations of design variables in each individual. Given an objective function, or list of objective
functions, and constraints, the solver evolves each population of individuals based on a non-dominated sorting 
genetic algorithm technique (NSGA-II).

1. Download project, and make sure test.py and deap_solver.py are both in the same folder.
2. Set up the problem in test.py as shown in the example below
3. Run test.py.
4. See function help below for input parameter and output information.
    
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
