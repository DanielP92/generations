import random
from names import AllNames
from globals import *

basic_info = ['gender', 'name', 'age', 'is_pregnant', 'preference', 'eligable_partners']
genders = ('boy', 'girl')
n = AllNames()

class Sim:
    day = 1
    step = 0

    def __init__(self):
        self.info = {}
        self.ages = {1: {'group': 'baby', 'days_to_age_up': 7},
                     2: {'group': 'child', 'days_to_age_up': 14},
                     3: {'group': 'teen', 'days_to_age_up': 21},
                     4: {'group': 'yng_adult', 'days_to_age_up': 21},
                     5: {'group': 'adult', 'days_to_age_up': 60},
                     6: {'group': 'elder', 'days_to_age_up': 28},
                    }
        self.partner = None
        self.offspring = []

    def __str__(self):
        return f'{self.first_name} {self.surname}'

    def update(self):
        self.step += 1

        if self.step >= DAY_LENGTH:
            self.day += 1
            self.step = 0
            self.relationship_change()
            if self.partner == None:
                self.set_partner()

    def generate(self):
        self.properties = [self.set_gender, self.set_name, self.set_age,
                           self.is_pregnant, self.set_preference, self.set_eligable_partners]
        self.set_basic_info()

        self.first_name, self.surname = self.info['name'][0], self.info['name'][1]
        self.preg_step, self.preg_day = 0, 1
        print(f'{self.first_name} {self.surname} spawned! {self.info["age"]}, {self.info["gender"]}, {self.info["preference"]}, {self.info["eligable_partners"]}')

    def relationship_change(self):
        for sim in self.info['eligable_partners']:
            new_val = self.info['eligable_partners'][sim] + random.randint(-2, 15)
            self.info['eligable_partners'].update({sim: new_val})

    def set_basic_info(self):
        for func in self.properties:
            for item in basic_info:
                if str(item) in str(func):
                    self.add_to_info(item, func())

    def set_partner(self):
        threshold = 65
        for sim in self.info['eligable_partners']:
            if self in sim.info['eligable_partners']:
                rel1 = self.info['eligable_partners'][sim]
                rel2 = sim.info['eligable_partners'][self]
                if rel1 >= threshold and rel2 >= threshold and self.partner == None and sim.partner == None:
                    sim.partner = self
                    self.partner = sim
                    print(f'{self.first_name} {self.surname} and {sim.first_name} {sim.surname} are now partners!')

    def set_name(self):
        return [random.choice(n.first_names[self.info['gender']]), random.choice(n.surnames)]

    def set_gender(self):
        return random.choice(genders)

    def set_preference(self):
        homo_pc = 0.1
        bi_pc = 0.3

        if random.random() <= homo_pc:
            return self.info['gender']
        elif homo_pc > random.random() <= bi_pc:
            return genders[0] + genders[1]
        else:
            for gender in genders:
                if gender != self.info['gender']:
                    return gender

    def set_eligable_partners(self):
        return dict()

    def set_age(self):
        return list(random.choice(list(self.ages.items())[2:]))

    def is_pregnant(self):
        if self.info['gender'] == 'girl':
            return False
        elif self.info['gender'] == 'boy':
            return None

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
