# naming game with TWO rounds
#first round: original game (teaching patterns and renaming based on scores)
#           : if meet opposite, do nothing
#second round: send partial pattern, make decision --> get score

import sys
import random as r
from statistics import mean

LENGTH = 10
NUM_SPECIES = 2
NUM_EACH = 20
EPOCHS = 500
FIRST_ROUNDS = 2
SECOND_ROUNDS = 5
PERTURB_PROB = .2
MUTATE_PROB = .3
DECISION_THRESHOLD = .7 
PENALTY = -10
REWARD = 10

class Firefly():
    def __init__(self, species):
        self.species = species #which num species
        self.pattern = None
        self.score = None
    
    def __lt__(self, other):
        return self.species < other.species

    def init_pattern(self):
        p = [0] * LENGTH
        for i in range(LENGTH):
            if r.random() < .5:
                p[i] = 1
        self.pattern = p

    def same_species(self, other):
        if self.species == other.species:
            return True
        else: 
            return False

    #find longest shared substring with segment of sequence given
    # no wrapping of partial sequence
    def calc_similarity(self, seq):
        X = self.pattern + self.pattern[:LENGTH-1]
        Y = seq
        table = [[0 for k in range(len(seq)+1)] for l in range(2*LENGTH)]
        score = 0
        for i in range(2*LENGTH):
            for j in range(len(seq)+1):
                if (i == 0 or j == 0):
                    table[i][j] = 0
                elif (X[i-1] == Y[j-1]):
                    table[i][j] = table[i-1][j-1] + 1
                    score = max(score, table[i][j])
                else:
                    table[i][j] = 0

        #want to normalize with respect to how long seq is and how confident
        return score/len(seq)

    def reset_score(self):
        self.score = None

    def update_score(self, new):
        if self.score == None:
            self.score = new
        else:
            self.score += new

    def mutate(self):
        for i in range(LENGTH):
            if r.random() < PERTURB_PROB:
                self.pattern[i] = (self.pattern[i] + 1) %2

def printall(flies):
    flies.sort()
    for f in flies:
        print(f.pattern, f.species)
    print(flies[0].calc_similarity(flies[39].pattern))

def round_one(flies):
    for f in range(NUM_EACH):
        i = 2*f
        j = i+1
        same = flies[i].same_species(flies[j]) #only do exchange within same species
        if same:
            #both no pattern
            if flies[i].pattern == None and flies[j].pattern == None:
                flies[i].init_pattern()
                flies[j].pattern = flies[i].pattern
            #j has pattern
            elif flies[i].pattern == None:
                flies[i].pattern = flies[j].pattern
            #i has pattern
            elif flies[j].pattern == None:
                flies[j].pattern = flies[i].pattern
            #both have pattern
            #have gone through round 2 -- NEED TO CHECK THIS LOGIC. 
            elif flies[i].score != None and flies[j].score != None:
                if flies[i].score >= flies[j].score:
                    flies[j].pattern = flies[i].pattern
                    if r.random() < MUTATE_PROB:
                        flies[j].mutate()
                    flies[j].reset_score()
                else:
                    flies[i].pattern = flies[j].pattern
                    if r.random() < MUTATE_PROB:
                        flies[i].mutate()
                    flies[i].reset_score()

def round_two(flies):
    for f in range(NUM_EACH):
        i = 2*f
        j = i+1
        #i sends partial sequence
        start = r.randint(0, LENGTH-5) #note we're picking indices
        end = r.randint(start+4, LENGTH-1) #ensure that seq is at least 4 long
        seq_length = end-start
        seq = flies[i].pattern[start:end]
        #j makes decision based on substring match with j's full pattern
        decision = flies[j].calc_similarity(seq)
        if decision < DECISION_THRESHOLD:
            #decided different species
            if flies[i].same_species(flies[j]):
                #negative reward to both??, scaled by length of seq??
                flies[i].update_score(PENALTY*(LENGTH/seq_length))
                flies[j].update_score(PENALTY*(LENGTH/seq_length))
            else:
                #pos reward
                flies[i].update_score(REWARD*(LENGTH/seq_length))
                flies[j].update_score(REWARD*(LENGTH/seq_length))
        else:
            #decided same species
            if flies[i].same_species(flies[j]):
                #pos reward
                flies[i].update_score(REWARD*(LENGTH/seq_length))
                flies[j].update_score(REWARD*(LENGTH/seq_length))
            else:
                #neg reward
                flies[i].update_score(PENALTY*(LENGTH/seq_length))
                flies[j].update_score(PENALTY*(LENGTH/seq_length))
                

def main(args):
    #create fireflies
    fireflies = [0] * (NUM_SPECIES * NUM_EACH)
    for i in range(NUM_SPECIES):
        for j in range(NUM_EACH):
            fireflies[j+(NUM_EACH*i)] = Firefly(i)

    for epoch in range(EPOCHS):

        for round in range(FIRST_ROUNDS):
            #if very first round, don't shuffle
            if epoch != 0 or round != 0:
                r.shuffle(fireflies)
            round_one(fireflies)
            if epoch == 0:
                break
        
        for round in range(SECOND_ROUNDS):
            r.shuffle(fireflies)
            round_two(fireflies)


    printall(fireflies)
                    



if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))