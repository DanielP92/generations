import random
import uuid
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
        self.properties = [self.set_gender, self.set_name, self.set_age,
                           self.is_pregnant, self.set_preference, self.set_eligable_partners]
        self.preg_step, self.preg_day = 0, 1
        self.partner = None
        self.family = Family(self)
        self.household = None

    def __str__(self):
        return f'{self.first_name} {self.surname}'

    def update(self):
        self.step += 1

        if self.step >= DAY_LENGTH:
            self.day += 1
            self.step = 0
            self.relationship_change()
            self.family.set_other_members()
            if self.partner == None:
                self.set_partner()

    def generate(self):
        self.set_basic_info()
        self.family.set_other_members()
        self.family.gen = self.family.mother.family.gen + 1
        self.set_household(self)
        print(f'{self} spawned! {self.info["age"]}, {self.info["gender"]}, {self.info["preference"]}')
    
    def set_household(self, sim):
        sim.household = Household()
        sim.household.add_member(sim)
        if isinstance(sim, Offspring):
            sim.family.mother.household.add_member(self)
            sim.household = sim.family.mother.household
    
    def relationship_change(self):
        for sim in self.info['eligable_partners']:
            new_val = self.info['eligable_partners'][sim] + random.randint(-2, 15)
            if new_val > 100:
                new_val = 100
            self.info['eligable_partners'].update({sim: new_val})

    def set_basic_info(self):
        for func in self.properties:
            for item in basic_info:
                if str(item) in str(func):
                    self.add_to_info(item, func())

        self.first_name, self.surname = self.info['name'][0], self.info['name'][1]

    def set_partner(self):
        threshold = 65
        surname = ""

        def set_surnames():
            single_name = 0.95
            follow_pc = 0.66

            if random.random() < single_name or any('-' in x for x in [self.surname, sim.surname]):
                if random.random() < follow_pc:
                    surname = self.surname
                else:
                    surname = sim.surname
            else:
                if random.random() < follow_pc:
                    surname = f'{self.surname}-{sim.surname}'
                else:
                    surname = f'{sim.surname}-{self.surname}'

            self.info['name'][1] = sim.info['name'][1] = surname
            self.surname = sim.surname = surname

        def choose_partner():
            if self in sim.info['eligable_partners']:
                rel1 = self.info['eligable_partners'][sim]
                rel2 = sim.info['eligable_partners'][self]

                if rel1 >= threshold and rel2 >= threshold and self.partner == None and sim.partner == None:
                    sim.partner = self
                    self.partner = sim
                    self.household.members.remove(self)
                    sim.household.members.remove(sim)
                    self.household = sim.household = Household()
                    self.household.add_member(self)
                    self.household.add_member(sim)

                    set_surnames()
                    print(f'{self.first_name} {self.surname} and {sim.first_name} {sim.surname} are now partners!')

        for sim in self.info['eligable_partners']:
            choose_partner()

    def set_name(self):
        return [random.choice(n.first_names[self.info['gender']]), self.family.mother.info['name'][1]]

    def set_parents(self):
        mum, dad = self.family.mother, self.family.father
        mum, dad = Sim(), Sim()
        mum.family.mother, mum.family.father = Sim(), Sim()
        dad.family.mother, dad.family.father = Sim(), Sim()
        females = [mum, mum.family.mother, dad.family.mother]
        males = [dad, dad.family.father, mum.family.father]

        for sim in females:
            sim.family.u_id = self.family.u_id
            sim.info.update({'gender': genders[1]})
            sim.info.update({'name': [random.choice(n.first_names[mum.info['gender']]), random.choice(n.surnames)]})
            sim.first_name, sim.surname = sim.info['name'][0], sim.info['name'][1]
        for sim in males:
            sim.family.u_id = self.family.u_id
            sim.info.update({'gender': genders[0]})
            sim.info.update({'name': [random.choice(n.first_names[dad.info['gender']]), mum.info['name'][1]]})
            sim.first_name, sim.surname = sim.info['name'][0], sim.info['name'][1]
        
        self.family.mother, self.family.father = mum, dad
        mum.family.mother, mum.family.father = mum.family.mother, mum.family.father
        dad.family.mother, dad.family.father = dad.family.mother, dad.family.father


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
        return list(random.choice(list(self.ages.items())[2:5]))

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
    def __init__(self, mother, father):
        super().__init__()
        self.family.mother, self.family.father = mother, father
        self.family.u_id = str(self.family.mother.family.u_id) + str(self.family.father.family.u_id)

    def set_age(self):
        first_age = list(self.ages.keys())[0]
        return [first_age, {key: value for key, value in self.ages[first_age].items()}]

    def set_name(self):
        return [random.choice(n.first_names[self.info['gender']]), self.family.mother.surname]

class Family:
    def __init__(self, sim):
        self.sim = sim

        self.grandparents = []
        self.mother = None
        self.father = None
        self.siblings = []
        self.aunts = []
        self.uncles = []
        self.cousins = []
        self.second_cousins = []
        self.offspring = []

        self.u_id = str(uuid.uuid4())
        self.gen = 0

    def update_siblings(self):
        self.siblings = (list(dict.fromkeys([x for x in self.mother.family.offspring + self.father.family.offspring if x != self.sim])))

    def update_iterator(self, list_1, list_2):
        for sim_info in list_1:
            for sim in sim_info:
                if sim not in list_2:
                    list_2.append(sim)
                    list_2.sort(key=lambda x: x.surname)

    def update_cousins(self):
        offspring_list = [x.family.offspring for x in [self.aunts, self.uncles] for x in x if len(x.family.offspring) != 0]            
        self.update_iterator(offspring_list, self.cousins)
   
    def update_2nd_cousins(self):
        offspring_list = [x.family.offspring for x in [self.mother.family.cousins, self.father.family.cousins] for x in x if len(x.family.offspring) != 0]            
        self.update_iterator(offspring_list, self.second_cousins)

    def update_grandparents(self):
        grandparent_list = [[x.family.mother, x.family.father] for x in self.parents]
        self.update_iterator(grandparent_list, self.grandparents)

    def set_other_members(self):
        self.parents = [self.mother, self.father]
        self.update_grandparents()
        self.update_siblings()
        self.aunts = [x for x in [self.mother.family.siblings, self.father.family.siblings] for x in x if x.info['gender'] == 'girl']
        self.uncles = [x for x in [self.mother.family.siblings, self.father.family.siblings] for x in x if x.info['gender'] == 'boy']
        self.update_cousins()
        self.update_2nd_cousins()

class Household:
    def __init__(self):
        self.members = []
        self.u_id = str(uuid.uuid4())

    def add_member(self, sim):
        self.members.append(sim)
