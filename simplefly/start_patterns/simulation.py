#naming game

import sys
import random as r
import csv 
from itertools import combinations
import pickle

from fly import Firefly

SEED_FILE = 'consangineus'

NUM_SPECIES = 3
NUM_EACH = 15
EPOCHS = 1
MUTATE_PROB = .1
TRIALS = 1

#given list of fireflies, the epoch number
#implement original naming game 
def round_one(fireflies, epoch, A, B):
    for (i, j) in combinations(fireflies, 2):
        same = i.same_species(j)
        if same:
            #both no pattern
            if i.pattern == None and j.pattern == None:
                i.init_pattern()
                j.pattern = i.pattern
            #j has pattern
            elif i.pattern == None:
                i.pattern = j.pattern
            #i has pattern
            elif j.pattern == None:
                j.pattern = i.pattern
            #both have
            elif i.score() != None and j.score() != None:
            #compare lincombo, replicate smaller one
                iscore = (A*i.score()) + (B*i.num_flash())
                jscore = (A*j.score()) + (B*j.num_flash())
                if iscore <= jscore:
                    j.pattern = i.pattern[:]
                    if r.random() < MUTATE_PROB and epoch < 495:
                        j.mutate()
                    j.reset_simscore()
                    j.last_score = iscore
                else:
                    i.pattern = j.pattern[:]
                    if r.random() < MUTATE_PROB and epoch < 495:
                        i.mutate()
                    i.reset_simscore()
                    i.last_score = jscore

        else:
            #calculate and update similarity score
            if i.pattern == None:
                i.init_pattern()
            if j.pattern == None:
                j.init_pattern()
            distance = i.calc_similarity(j)
            i.update_simscore(distance)
            j.update_simscore(distance)

#printing results
def list_flies(flies):
    flies.sort()
    seen = {}
    for f in flies:
        if (str(f.set_start()), f.species) not in seen:
            seen[(str(f.set_start()), f.species)] = f.last_score
        elif f.last_score < seen[(str(f.set_start()), f.species)]:
            seen[(str(f.set_start()), f.species)] = f.last_score
            
    return seen

#write to csv
def print_csv(results):
    with open('results.csv', mode = 'w') as file:
        writer = csv.writer(file, delimiter = ',')
        
        for run in results.keys():
            row = [run]
            flies = results[run]
            row += flies
            row += flies.values()
            writer.writerow(row)


def main(args):
    #keep track of all the results
    runs = {}

    a = [.2, .25, .3, .35, .4, .45, .5]

    #load the start patterns
    #choose which one to seed -- run x trials
    
    
    for A in a:
        B = 1-A
        with open(SEED_FILE+'.pickle', 'rb') as f:
            start_patterns = pickle.load(f)
        for start_p in start_patterns:
            for rep in range(TRIALS):
                fireflies = [0] * (NUM_SPECIES * NUM_EACH)
                for i in range(NUM_SPECIES):
                    for j in range(NUM_EACH):
                        fireflies[j+(NUM_EACH*i)] = Firefly(i)
                        if i == 0:
                            fireflies[j+(NUM_EACH*i)].pattern = start_p

            for epoch in range(EPOCHS):
                r.shuffle(fireflies)
                round_one(fireflies, epoch, A, B)
            
            runs[(A, B, rep)] = list_flies(fireflies)

    print_csv(runs)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
