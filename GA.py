from random import randint, sample
from itertools import permutations


# image_array --> 2D Boolean  [height][width]
# block_sizes --> List of Tuples of all possible solutions [(width, height),.........]
# CAC --> function perform CAC Algorithm and return CR Value
# --------------------------------------------- Genetic Algorithm Function --------------------------------------------
def genetic_algorithm(image_array, block_sizes, delta_error=10 ** -5, least_number_of_generations=5):
    population_size = 10  # Set value here
    number_of_mating_pools = 5  # Set value here
    max_CR = {'CR': -1, 'block_width': 0, 'block_height': 0}
    generations_counter = 0
    new_populations = []
    random_indexes = sample(range(len(block_sizes)), population_size)
    for i in range(population_size):
        new_populations += [block_sizes[random_indexes[i]]]
    condition = True
    while condition:
        last_max_CR = max_CR.copy()
        generations_counter += 1
        populations = new_populations.copy()
        populations_with_fitnesses = [(CAC(image_array, width, height), width, height) for width, height in populations]
        populations_with_fitnesses.sort(reverse=True)
        max_CR['CR'] = populations_with_fitnesses[0][0]
        max_CR['block_width'] = populations_with_fitnesses[0][1]
        max_CR['block_height'] = populations_with_fitnesses[0][2]
        mating_pools = []
        for i in range(number_of_mating_pools):
            mating_pools += [(populations_with_fitnesses[i][1], populations_with_fitnesses[i][2])]
        possible_offsprings = [(X1, Y2) for (X1, Y1), (X2, Y2) in list(permutations(mating_pools, 2))]
        offsprings = []
        random_indexes = sample(range(len(possible_offsprings)), population_size - number_of_mating_pools)
        for i in range(population_size - number_of_mating_pools):
            offsprings += [possible_offsprings[random_indexes[i]]]
        mutants = offsprings.copy()
        for i in range(len(mutants)):
            index = randint(0, 1)
            temp_mutant = list(mutants[i])
            temp_mutant[index] = block_sizes[randint(0, len(block_sizes) - 1)][index]
            mutants[i] = tuple(temp_mutant)
        new_populations = mating_pools + mutants
        condition = (generations_counter < least_number_of_generations) or (
                (max_CR['CR'] - last_max_CR['CR']) > delta_error)
    return max_CR
