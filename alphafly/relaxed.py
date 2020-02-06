#using alpha numbers to characterize pattern
#alphas all integral valued
#relax alpha_3 -- no set LENGTH
import sys
import random as r
from statistics import mean
from math import floor

MAX_LENGTH = 10
NUM_SPECIES = 2
NUM_EACH = 20
EPOCHS = 300
PERTURB = 1
MUTATE_PROB = .15 

class Firefly():
    def __init__(self, species):
        self.species = species #which num species
        self.pattern = None
        self.simscore = 0
    
    def __lt__(self, other):
        if self.species == other.species:
            #higher simscore between species is better
            return self.simscore > other.simscore
        else:
            return self.species < other.species

    def __str__(self):
        return str(self.pattern) + self.recreate_pattern() + "  " + str(self.species)

    def init_pattern(self):
        #a_1 is flash duration
        a_1 = r.randint(1, 3) #cannot be on for more than 3 secs at once
        #a_2 is interpulse interval
        a_2 = a_1 + r.randint(1, a_1) #quiet cannot be more than flash duration
        #a_4 is number of flashes
        a_4 = r.randint(1, floor(MAX_LENGTH/a_2))
        #a_3 is flash pattern interval (but rn just "quiet time")
        a_3 = r.randint(0, (MAX_LENGTH - (a_4 * a_2)))
        self.pattern = [0, a_1, a_2, a_3, a_4]


    def recreate_pattern(self):
        p = [0] * MAX_LENGTH
        t = 0
        for i in range(self.pattern[4]):
            for j in range(self.pattern[2]):
                if j <= self.pattern[1]-1:
                    p[t] = 1
                t += 1
        t += self.pattern[3]
        dif = MAX_LENGTH - t
        while dif > 0:
            p.pop()
            dif -= 1
        return str(p)

    def same_species(self, other):
        if self.species == other.species:
            return True
        else: 
            return False

    #og simscore
    def calc_similarity_og(self, other):
        ct = 0
        for i in range(LENGTH):
            if self.pattern[i] != other.pattern[i]:
                ct += 1
        return ct

    #sum the differences between a_i
    def calc_similarity_simp(self, other):
        ct = 0
        p1 = self.recreate_pattern()
        p2 = other.recreate_pattern()
        for i in range(1,5):
            ct += abs(p1[i] - p2[i])
        return ct

    def calc_similarity(self, other):
        # 4 * how many times you flash (a_4)
        ct = 4 * (abs(self.pattern[4] - other.pattern[4]))
        # 3 * how long flash is (a_1)
        ct += 3 * (abs(self.pattern[1] - other.pattern[1]))
        # 2 * how long between flashes (a_2 - a_1)
        ct += 2 * (abs( (self.pattern[2] - self.pattern[1]) - \
                            (other.pattern[2] - other.pattern[1]) ))
        # 1 * length of "pattern" (a_2 * a_4) 
        ct += abs( (self.pattern[2] * self.pattern[4]) - \
                       other.pattern[2] * other.pattern[4])
        # 1/2 * length of quiet time
        ct += .5 * abs(self.pattern[3] - other.pattern[3])
        return ct
        
    def reset_simscore(self):
        self.simscore = 0

    def update_simscore(self, newsim):
        if self.simscore == 0:
            self.simscore = newsim
        else:
            self.simscore = mean([self.simscore, newsim])


    #pick one aspect (a1, a2, a3, a4) to mutate
    #mutate just by +/- 1
    #rechoose other elements to ensure within bounds
    def mutate(self):
        change = r.choice([1, 2, 3, 4])
        if change == 1:
            if self.pattern[1] == 1:
                self.pattern[1] = 2
            elif self.pattern[1] == 2:
                self.pattern[1] += r.choice([-1, 1])
            else:
                self.pattern[1] = 2
            #rechoose silence thats in bounds
            self.pattern[2] = self.pattern[1] + r.randint(1, self.pattern[1])
            #rechoose freq if needed
            if (self.pattern[3] + (self.pattern[2] * self.pattern[4]) > MAX_LENGTH):
                self.pattern[4] = r.randint(1, floor(MAX_LENGTH/self.pattern[2]))
            #rechoose quiet if needed
            if (self.pattern[3] + (self.pattern[2] * self.pattern[4]) > MAX_LENGTH):
                self.pattern[3] = r.randint(0, (MAX_LENGTH - \
                                                    (self.pattern[4] * self.pattern[2])))

        if change == 2: #choose new silence
            self.pattern[2] = self.pattern[1] + r.randint(1, self.pattern[1])
            #rechoose freq if needed
            if (self.pattern[3] + (self.pattern[2] * self.pattern[4]) > MAX_LENGTH):
                self.pattern[4] = r.randint(1, floor(MAX_LENGTH/self.pattern[2]))
            #rechoose quiet if needed
            if (self.pattern[3] + (self.pattern[2] * self.pattern[4]) > MAX_LENGTH):
                self.pattern[3] = r.randint(0, (MAX_LENGTH - \
                                                    (self.pattern[4] * self.pattern[2])))

        if change == 4:
            #rechoose freq
            self.pattern[4] = r.randint(1, floor(MAX_LENGTH/self.pattern[2]))
            #rechoose quiet if needed
            if (self.pattern[3] + (self.pattern[2] * self.pattern[4]) > MAX_LENGTH):
                self.pattern[3] = r.randint(0, (MAX_LENGTH - \
                                                    (self.pattern[4] * self.pattern[2])))

        if change == 3:
            self.pattern[3] = r.randint(0, (MAX_LENGTH - \
                                                (self.pattern[4] * self.pattern[2])))

                
        
def printall(flies):
    flies.sort()
    for f in flies:
        print(f)
    
    
def main(args):
    #create fireflies
    fireflies = [0] * (NUM_SPECIES * NUM_EACH)
    for i in range(NUM_SPECIES):
        for j in range(NUM_EACH):
            fireflies[j+(NUM_EACH*i)] = Firefly(i)

    for epoch in range(EPOCHS):
        r.shuffle(fireflies)

        for f in range(NUM_EACH):
            i = 2*f
            j = i+1
            same = fireflies[i].same_species(fireflies[j])
            #same species
            if same:
                #both no pattern
                if fireflies[i].pattern == None and fireflies[j].pattern == None:
                    fireflies[i].init_pattern()
                    fireflies[j].pattern = fireflies[i].pattern[:]
                #j has pattern
                elif fireflies[i].pattern == None:
                    fireflies[i].pattern = fireflies[j].pattern[:]
                #i has pattern
                elif fireflies[j].pattern == None:
                    fireflies[j].pattern = fireflies[i].pattern[:]
                #both have
                else:
                    #compare aggregate sim scores, replicate higher one 
                    #with probability simscore/length
                    #when replicating, do so with chance of mutation
                    if fireflies[i].simscore >= fireflies[j].simscore:
                        fireflies[j].pattern = fireflies[i].pattern[:]
                        if r.random() < MUTATE_PROB: #and epoch < 75:
                            fireflies[j].mutate()
                        fireflies[j].reset_simscore()
                    else:
                        fireflies[i].pattern = fireflies[j].pattern[:]
                        if r.random() < MUTATE_PROB: #and epoch < 75:
                            fireflies[i].mutate()
                        fireflies[i].reset_simscore()
            #diff species
            else:
                if fireflies[i].pattern == None:
                    fireflies[i].init_pattern()
                if fireflies[j].pattern == None:
                    fireflies[j].init_pattern()
                distance = fireflies[i].calc_similarity(fireflies[j])
                fireflies[i].update_simscore(distance)
                fireflies[j].update_simscore(distance)


    printall(fireflies)
                    



if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))