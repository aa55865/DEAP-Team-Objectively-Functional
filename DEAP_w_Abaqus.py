import time, random, copy, math
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
from deap import algorithms, base, tools, creator

def Abaqus_evaluation(individual): ### this algorithm calculates fitness values for a given individual
        with open("inputs.txt","w+") as writefile:
            for value in individual:
                writefile.write(value+'\n')
    
        if individual[0] == 'zig-zag':
            os.system("abaqus cae noGUI=zigzag_script_thermo.py") # opens Abaqus, runs script to generate/run model, write results
            os.system("abaqus cae noGUI=zigzag_script_stress.py")
        elif individual[0] == 'sine-wave':
            os.system("abaqus cae noGUI=sine-wave_script_thermo.py")
            os.system("abaqus cae noGUI=sine-wave_script_stress.py")
        elif individual[0] == 'strut':
            os.system("abaqus cae noGUI=strut_script_thermo.py")
            os.system("abaqus cae noGUI=strut_script_stress.py")
#       etc...

#   while 'results file' not in 'Abaqus results directory':
#       wait

    tempr_numeric = 0.0;
    tempr_counter = 0;
    with open ('temperature_results.txt', 'rt') as tempr_file: # Open file
        for tempr in tempr_file:              
            tempr_numeric = tempr_numeric + float(tempr);
            tempr_counter = tempr_counter + 1;
    tempr_avg = tempr_numeric/tempr_counter;

    stress_numeric = -math.inf; 
    with open ('stress_results.txt', 'rt') as stress_file: # Open file
        for stress in stress_file:              
            if stress_numeric < float(stress):
                stress_numeric=float(stress)

    return temp_avg, stress_numeric


def uniform(designVars): #this function determines the values that fill each individual in the intial population
    individual = [None]*designVars
    decider = random.randint(0,2) ###DETERMINE INFILL TYPE
    if decider == 0: individual[0] = 'patt1'
    elif decider ==1: individual[0] = 'patt2'
    elif decider ==2: individual[0] = 'patt3'
    individual[1] = random.uniform(0,1) ###DETERMINE INFILL THICKNESS
    individual[2] = random.uniform(0,1) ###DETERMINE WALL THICKNESS
    individual[3] = random.uniform(0,1) ###DETERMINE INFILL SPACING
    return individual

def cxList(ind1, ind2): #define crossover strategy for lists
    cxPt = random.randint(0,len(ind1)-1)
    child1 = toolbox.individual()
    child2 = toolbox.individual()
    child1[::] = ind1[0:cxPt]+ind2[cxPt::]
    child2[::] = ind2[0:cxPt]+ind1[cxPt::]

    return child1,child2

def mutList(individual): #define mutation strategy for lists
    mutPoint = random.randint(0,len(individual))
    if mutPoint==0:
        decider = random.randint(0,2) ###MUTATE INFILL TYPE
        if decider == 0: individual[0] = 'patt1'
        elif decider ==1: individual[0] = 'patt2'
        elif decider ==2: individual[0] = 'patt3'
    if mutPoint==1: individual[1] = random.uniform(0,1) ###MUTATE INFILL THICKNESS
    if mutPoint==2: individual[2] = random.uniform(0,1) ###MUTATE WALL THICKNESS
    if mutPoint==3: individual[3] = random.uniform(0,1) ###MUTATE INFILL SPACING
    return individual,

designVars = 4 #number of values contained within an individual
creator.create("Fitness", base.Fitness, weights=(-1.0,-1.0)) #creates Fitness class with two objectives to be minimized (Thermal Conductivity, Strength/Weight)
creator.create("Individual", list, fitness=creator.Fitness) #creates Individual class (type = list) with a fitness attribute

toolbox = base.Toolbox() # "the toolbox is a container for all the tools selected by the user" - DEAP documentation
#sets the type and range of values contained in each individual
toolbox.register("designVar", uniform, designVars) #attr_designVar refers to function 'uniform', with args designVars
#registers the tool to create individuals (i.e. ind1 = toolbox.individual())
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.designVar) #individual refers to function initIterate, with args c.Ind & tool.attr_designVar
#registers the tool to create a population of individuals (i.e. pop1 = toolbox.population(n=popsize))#
toolbox.register("population", tools.initRepeat, list, toolbox.individual) #population referst to func initRepeat, with args list and tool.individual
#registers the crossover strategy for lists
toolbox.register("mate", cxList)
#registers the mutation strategy for lists
toolbox.register("mutate",mutList)
#registers the function to determine fitness when toolbox.evaluate is called
toolbox.register("evaluate", Abaqus_evaluation) 
#registers the genetic algorithm to be implemented
toolbox.register("select", tools.selNSGA2)


def main(): ###THIS FUNCTION RUNS THE ALGORITHM BUILT INTO DEAP
    random.seed(datetime.now())
    NGEN = 100 #number of generations
    MU = 50 #number of individuals to select for next generation
    LAMBDA = 100 #number of children produced at each generation
    CXPB = 0.80 #crossover probability
    MUTPB = 0.05 #mutation probability
    
    pop = toolbox.population(n=MU)
    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)
    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats, halloffame=hof)
    return pop, stats, hof




if __name__ == '__main__':
    stats = main()
    non_dom = tools.sortNondominated(stats[0], k=len(stats[0]), first_front_only=True)[0]
    for ind in non_dom:
        plt.plot(ind.fitness.values[0], ind.fitness.values[1], 'bo')
    plt.title('Sample Pareto front')
    plt.xlabel('T_conductivity')
    plt.ylabel('Strength-to-Weight')
    plt.show()
