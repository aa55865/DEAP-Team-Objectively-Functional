Team: Objective(ly) Function(al)

Group Number: 3
Group Members: Oliver Uitz
               Indu Venu
               Andrew Allan
--------------------------------


Multi-Objective Genetic Algorithm Optimization Solver

NOTE: Please install DEAP and PrettyTable packages to run this solver.
Link to DEAP: https://pypi.org/project/deap/
Link to PrettyTable: https://pypi.org/project/PrettyTable/

This is an optimization solver based on the Distributed Evolutionary Algorithms in Python (DEAP) package. It uses
binary representations of design variables in each individual. Given an objective function, or list of objective
functions, and constraints, the solver evolves each population of individuals based on the NSGA-II technique.

1. Download the project
2. Set up the problem in test.py as shown in the example below (see Test Problem 3 in test.py)
3. Run test.py.
4. See function help in deap_solver.py for input parameter and output information.
       
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
  
CITATION FOR DEAP
-----------------
Félix-Antoine Fortin, François-Michel De Rainville, Marc-André Gardner, Marc Parizeau and Christian Gagné, "DEAP: Evolutionary Algorithms Made Easy", Journal of Machine Learning Research, vol. 13, pp. 2171-2175, jul 2012. Paper
