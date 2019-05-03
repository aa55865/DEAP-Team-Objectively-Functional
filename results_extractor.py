import math
def extractor():
    tempr_numeric = 0.0
    tempr_counter = 0
    with open ('temperature_results.txt', 'rt') as tempr_file: # Open file
        for tempr in tempr_file:
            tempr_numeric += float(tempr)
            tempr_counter = tempr_counter + 1
    tempr_avg = tempr_numeric/tempr_counter

    stress_numeric = -math.inf
    with open ('stress_results.txt', 'rt') as stress_file: # Open file
        for stress in stress_file:
            if stress_numeric < float(stress):
              stress_numeric=float(stress)

    return (tempr_avg,stress_numeric)



