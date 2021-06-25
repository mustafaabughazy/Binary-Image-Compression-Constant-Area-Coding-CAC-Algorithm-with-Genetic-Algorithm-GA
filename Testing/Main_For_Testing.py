from PIL import Image
import numpy as np
import pandas as pd
import math
import time
from random import randint, sample, uniform, seed
from itertools import permutations, combinations
from datetime import datetime
from multiprocessing import Pool

seed(datetime.now())


def divisor_generator(n):
    divisors = []
    large_divisors = []
    for i in range(1, int(math.sqrt(n) + 1)):
        if n % i == 0:
            divisors.append(i)
            if i * i != n:
                large_divisors.append(int(n / i))
    return sorted(divisors + large_divisors)


def image_reading(file):
    image = Image.open(file).convert("1")
    image_array = np.asarray(image)
    return image_array


def get_block_type(image_array, block_width, block_height, w_start, h_start):
    has_white = False
    has_black = False
    for w in range(w_start, w_start + block_width):
        for h in range(h_start, h_start + block_height):
            if image_array[h][w]:
                has_white = True
            else:
                has_black = True
            if has_white and has_black:
                return 'M'
    if has_white:
        return 'W'
    elif has_black:
        return 'B'


def blocks_counter_encoder(blocks_array):
    unique, counts = np.unique(blocks_array, return_counts=True)
    counter = dict(zip(unique, counts))
    codes = counter.copy()
    max_count = max(counter, key=counter.get)
    codes[max_count] = '0'
    i = 0
    for key, value in counter.items():
        if key is not max_count:
            if len(counter) == 2:
                codes[key] = '1'
            elif len(counter) == 3:
                if i == 0:
                    codes[key] = '01'
                    i = i + 1
                elif i == 1:
                    codes[key] = '11'
    return counter, codes


def CAC(image_array, block_width, block_height, debug=False, get_result=False):
    image_width = len(image_array[0])
    image_height = len(image_array)
    blocks_array = np.asarray(
        [[get_block_type(image_array, block_width, block_height, x * block_width, y * block_height)
          for x in range(int(image_width / block_width))] for y in range(int(image_height / block_height))])
    counter, codes = blocks_counter_encoder(blocks_array)
    N1 = image_width * image_height
    N2 = 0
    for key, value in counter.items():
        if key == 'M':
            N2 = N2 + value * (len(codes[key]) + block_width * block_height)
        else:
            N2 = N2 + (value * len(codes[key]))
    CR = N1 / N2
    if get_result:
        with open("Result.txt", "w") as result:
            for h in range(len(blocks_array)):
                for w in range(len(blocks_array[0])):
                    if blocks_array[h][w] == 'M':
                        result.write(codes['M'])
                        for hx in range(h * block_height, (h + 1) * block_height):
                            for wx in range(w * block_width, (w + 1) * block_width):
                                result.write(str(int(image_array[hx][wx])))
                    else:
                        result.write(codes[blocks_array[h][w]])
            result.close()
    else:
        open("Result.txt", "w").close()
    return CR


def brute_force(image_array, block_sizes, debug=False):
    max_CR = {'CR': -1, 'block_width': 0, 'block_height': 0}
    for block_width, block_height in block_sizes:
        CR = CAC(image_array, block_width, block_height, debug=debug)
        if CR > max_CR['CR']:
            max_CR['CR'] = CR
            max_CR['block_width'] = block_width
            max_CR['block_height'] = block_height
    return max_CR


def genetic_algorithm(image_array, block_sizes, delta_error=10 ** -5, least_number_of_generations=2, debug=False):
    max_CR = {'CR': -1, 'block_width': 0, 'block_height': 0}
    multiplicat = uniform((4 / len(block_sizes)), 0.1)
    if len(block_sizes) < 40:
        multiplicat = (4 / len(block_sizes))
    if multiplicat > 1:
        multiplicat = 1
    population_size = randint(4, int(len(block_sizes) * multiplicat))
    least_number_of_mating_pools = population_size
    for X in range(population_size):
        if population_size <= (X + len(list(permutations([None] * X, 2)))):
            least_number_of_mating_pools = X
            break
    number_of_mating_pools = randint(least_number_of_mating_pools, population_size)
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
    return max_CR, {
        "Least_Number_of_Generations": least_number_of_generations,
        "Delta_Error": delta_error,
        "Population_Size_Range": "[4->" + str(int(len(block_sizes) * multiplicat)) + "]",
        "Population_Size": population_size,
        "Number_of_Mating_Pools_Range": "[" + str(least_number_of_mating_pools) + "->" + str(population_size) + "]",
        "Number_of_Mating_Pools": number_of_mating_pools,
        "Mutation_Percentage": 50,
        "Generations_Counter": generations_counter
    }


def image_compression(image_array, file, use_genetic_algorithm=False, debug=False):
    start_time = time.time()
    block_widths = divisor_generator(len(image_array[0]))
    block_heights = divisor_generator(len(image_array))
    block_sizes = [(width, height) for width in block_widths for height in block_heights]
    algorithm_details = {
        "Least_Number_of_Generations": "",
        "Delta_Error": "",
        "Population_Size_Range": "",
        "Population_Size": "",
        "Number_of_Mating_Pools_Range": "",
        "Number_of_Mating_Pools": "",
        "Mutation_Percentage": "",
        "Generations_Counter": ""
    }
    if use_genetic_algorithm:
        max_CR, algorithm_details = genetic_algorithm(image_array, block_sizes, debug=debug)
    else:
        max_CR = brute_force(image_array, block_sizes, debug=debug)
    CAC(image_array, max_CR['block_width'], max_CR['block_height'], get_result=True, debug=True)
    execution_time = time.time() - start_time
    return {
        "File_Name": file,
        "Image_Width": len(image_array[0]),
        "Image_Height": len(image_array),
        "Max_CR": max_CR['CR'],
        "Block_Width": max_CR['block_width'],
        "Block_Height": max_CR['block_height'],
        "Number_of_Possible_Block_Sizes": len(block_sizes),
        "Genetic_Algorithm": use_genetic_algorithm,
        "Brute_Force": not use_genetic_algorithm,
        "Execution_Time": execution_time,
        # "Algorithm_Details": algorithm_details[""]
        "Least_Number_of_Generations": algorithm_details["Least_Number_of_Generations"],
        "Delta_Error": algorithm_details["Delta_Error"],
        "Population_Size_Range": algorithm_details["Population_Size_Range"],
        "Population_Size": algorithm_details["Population_Size"],
        "Number_of_Mating_Pools_Range": algorithm_details["Number_of_Mating_Pools_Range"],
        "Number_of_Mating_Pools": algorithm_details["Number_of_Mating_Pools"],
        "Mutation_Percentage": algorithm_details["Mutation_Percentage"],
        "Generations_Counter": algorithm_details["Generations_Counter"]
    }


if __name__ == "__main__":
    filex = '../Dataset/Comma-10.gif'
    print(image_compression(image_reading(filex), filex, use_genetic_algorithm=False, debug=False))
