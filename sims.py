import random
from names import AllNames
from globals import *

basic_info = ['gender', 'name', 'age', 'is_pregnant']
genders = ('boy', 'girl')
n = AllNames()

class Sim:
    sim_day = 1
    sim_step = 0

    def __init__(self):
        self.info = {}
        self.ages = {1: {'group': 'baby', 'days_to_age_up': 7},
                     2: {'group': 'child', 'days_to_age_up': 14},
                     3: {'group': 'teen', 'days_to_age_up': 21},
                     4: {'group': 'yng_adult', 'days_to_age_up': 21},
                     5: {'group': 'adult', 'days_to_age_up': 60},
                     6: {'group': 'elder', 'days_to_age_up': 28},
                    }
        self.offspring = []

    def update(self):
        self.sim_step += 1
    
        if self.sim_step >= DAY_LENGTH:
            self.sim_day += 1
            self.sim_step = 0
            self.sim_aging()

    def generate(self):
        self.properties = self.set_gender, self.set_name, self.set_age, self.is_pregnant
        self.set_basic_info()

        self.first_name, self.surname = self.info['name'][0], self.info['name'][1]
        self.preg_step, self.preg_day = 0, 1
        print(f'{self.first_name} {self.surname} spawned! {self.info["age"]} {self.info["is_pregnant"]}')
    
    def set_basic_info(self):
        for func in self.properties:
            for item in basic_info:
                if str(item) in str(func):
                    self.add_to_info(item, func())

    def sim_aging(self):
        self.info['age'][1]['days_to_age_up'] -= 1

        if self.info['age'][1]['days_to_age_up'] < 0:
            self.info['age'][0] += 1

            if self.info['age'][0] > 6:
                self.sims.remove(self)
                print(f'{self.first_name} {self.surname} died!')
            else:
                self.add_to_info('age', self.age_up())
                print(f'{self.first_name} {self.surname} aged up to a(n) {self.info["age"][1]["group"]}!')

    def set_name(self):
        return [random.choice(n.first_names[self.info['gender']]), random.choice(n.surnames)]

    def set_gender(self):
        return random.choice(genders)
        
    def set_age(self):
        return list(random.choice(list(self.ages.items())[2:]))

    def is_pregnant(self):
        return False

    def age_up(self):
        return [self.info['age'][0], self.ages[self.info['age'][0]]]

    def add_to_info(self, prop, val):
        self.info.update({prop: val})


class Offspring(Sim):
    def __init__(self, mother):
        self.mother = mother
        super().__init__()
        
    def set_age(self):
        first_age = list(self.ages.keys())[0]
        return [first_age, {key: value for key, value in self.ages[first_age].items()}]

    def set_name(self):
        return [random.choice(n.first_names[self.info['gender']]), self.mother.surname]
