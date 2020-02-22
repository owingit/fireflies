#limit number of "on" bits in pattern

import sys
import random as r
from statistics import mean
from itertools import combinations

LENGTH = 5
MAX_FLASH = 2
NUM_SPECIES = 2
NUM_EACH = 15
EPOCHS = 150
MUTATE_PROB = .1 

class Firefly():
    def __init__(self, species):
        self.species = species #which num species
        self.pattern = None
        self.simscore = 0
    
    def __lt__(self, other):
        if self.species == other.species:
            return self.simscore < other.simscore
        else:
            return self.species < other.species

    def init_pattern(self):
        p = [0] * LENGTH
        num_flash = r.randint(1, MAX_FLASH)
        indicies = r.sample(range(LENGTH), num_flash)
        for i in indicies:
            p[i] = 1
        self.pattern = p

    def same_species(self, other):
        if self.species == other.species:
            return True
        else: 
            return False

    #find longest shared substring
    #repeat each pattern so we get the "wrap"
    #smol similarity is better
    def calc_similarity(self, other):
        X = self.pattern + self.pattern[:LENGTH-1]
        Y = other.pattern + other.pattern[:LENGTH-1]
        table = [[0 for k in range(2*LENGTH)] for l in range(2*LENGTH)]
        score = 0
        for i in range(2*LENGTH):
            for j in range(2*LENGTH):
                if (i == 0 or j == 0):
                    table[i][j] = 0
                elif (X[i-1] == Y[j-1]):
                    table[i][j] = table[i-1][j-1] + 1
                    score = max(score, table[i][j])
                else:
                    table[i][j] = 0

        return score

    def reset_simscore(self):
        self.simscore = 0

    def update_simscore(self, newsim):
        if self.simscore == 0:
            self.simscore = newsim
        else:
            self.simscore = mean([self.simscore, newsim])

    #first choose whether to (0) add a flash, (1) remove a flash, or (2) move a flash
    #if already at max_flash, cannot add
    def mutate(self):
        if sum(self.pattern) == MAX_FLASH:
            m = r.randint(1,2)
        elif sum(self.pattern) == 1:
            m = r.choice([0,2])
        else:
            m = r.randint(0,2)
        current_flashes = []
        current_silence = []
        for i in range(LENGTH):
            if self.pattern[i] == 1:
                current_flashes.append(i)
            else:
                current_silence.append(i)

        if m == 0:
            add = r.choice(current_silence)
            self.pattern[add] = 1
        elif m == 1:
            delete = r.choice(current_flashes)
            self.pattern[delete] = 0
        elif m == 2: #no limit on how far flash can move rn
            add = r.choice(current_silence)
            delete = r.choice(current_flashes)
            self.pattern[add] = 1
            self.pattern[delete] = 0


def printall(flies):
    flies.sort()
    for f in flies:
        print(f.pattern, f.species)
    print(flies[0].calc_similarity(flies[NUM_SPECIES*NUM_EACH - 1]))
    
def main(args):
    #create fireflies
    fireflies = [0] * (NUM_SPECIES * NUM_EACH)
    for i in range(NUM_SPECIES):
        for j in range(NUM_EACH):
            fireflies[j+(NUM_EACH*i)] = Firefly(i)

    for epoch in range(EPOCHS):
        r.shuffle(fireflies)

        for (i, j) in combinations(fireflies, 2):
            same = i.same_species(j)
            #same species
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
                else:
                    #compare aggregate sim scores, replicate smaller one 
                    #when replicating, do so with chance of mutation
                    if i.simscore <= j.simscore:
                        j.pattern = i.pattern
                        if r.random() < MUTATE_PROB and epoch < 175:
                            j.mutate()
                        j.reset_simscore()
                    else:
                        i.pattern = j.pattern
                        if r.random() < MUTATE_PROB and epoch < 975:
                            i.mutate()
                        i.reset_simscore()
            #diff species
            else:
                if i.pattern == None:
                    i.init_pattern()
                if j.pattern == None:
                    j.init_pattern()
                distance = i.calc_similarity(j)
                i.update_simscore(distance)
                j.update_simscore(distance)


    printall(fireflies)
                    



if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
