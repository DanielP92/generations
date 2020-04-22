import random
from globals import *

class Ageing:
    def __init__(self, sim):
        self.sim = sim
        self.ages = {1: {'group': 'baby', 'days_to_age_up': 7},
                     2: {'group': 'child', 'days_to_age_up': 14},
                     3: {'group': 'teen', 'days_to_age_up': 21},
                     4: {'group': 'yng_adult', 'days_to_age_up': 21},
                     5: {'group': 'adult', 'days_to_age_up': 60},
                     6: {'group': 'elder', 'days_to_age_up': 28},
                    }
        self.pregnancy = Pregnancy(self.sim)

    def age_up(self):
        return [self.sim.info['age'][0], self.ages[self.sim.info['age'][0]]]

    def update(self):
        self.sim.info['age'][1]['days_to_age_up'] -= 1

        if self.sim.info['age'][1]['days_to_age_up'] < 0:
            self.sim.info['age'][0] += 1

            if self.sim.info['age'][0] > 6:
                self.sim.alive = False
                self.sim.relationships.household.members.remove(self.sim)
                print(f'{self.sim.first_name} {self.sim.surname} died!')
            else:
                self.sim.add_to_info('age', self.age_up())
                print(f'{str(self.sim)} aged up to a(n) {self.sim.info["age"][1]["group"]}!')

class Pregnancy:
    step = 0
    day = 1

    def __init__(self, sim):
        self.sim = sim

    def is_pregnant(self):
        if self.sim.info['gender'] == 'girl':
            return False
        elif self.sim.info['gender'] == 'boy':
            return None

    def timer(self):
        self.step += 1

        if self.step > DAY_LENGTH:
            self.day += 1
            self.step = 0

        if self.day > 3:
            self.sim.give_birth()

    def pregnancy(self):
        spawn_pc = 0.0075

        spawn_chance = random.random() < spawn_pc and self.sim.relationships.romantic.partner
        pregnant = self.sim.info['is_pregnant']
        hit = spawn_chance and not pregnant
        female = self.sim.info['gender'] == 'girl'
        old_enough = 3 <= self.sim.info['age'][0] <= 5

        if female and old_enough and hit:
            self.sim.info['is_pregnant'] = True
            print(str(self.sim) + ' is pregnant!')

        if self.sim.info['is_pregnant']:
            self.timer()
