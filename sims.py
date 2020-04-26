import random
import uuid
from names import AllNames
from family import Family
from relationships import Relationships
from ageing import Ageing
from genetics import Genetics
from globals import *

basic_info = ['gender', 'name', 'age', 'is_pregnant', 'preference']

n = AllNames()

class BaseSim:
    day = 1
    step = 0

    def __init__(self):
        self.info = {}
        self.genetics = Genetics(self)
        self.family = Family(self)
        self.ageing = Ageing(self)
        self.relationships = Relationships(self)

        self.properties = [self.set_gender, self.set_name, self.set_age,
                           self.ageing.pregnancy.is_pregnant, self.relationships.set_preference]

    def __str__(self):
        return f'{self.first_name} {self.surname}'

    def update(self):
        self.step += 1
        self.ageing.pregnancy.pregnancy()

        if self.step >= DAY_LENGTH:
            self.day += 1
            self.step = 0
            self.ageing.update()
            self.relationships.update()

    def set_basic_info(self):
        for func, item in zip(self.properties, basic_info):
            self.add_to_info(item, func())

        self.first_name, self.surname = self.info['name'][0], self.info['name'][1]

    def generate(self):
        self.set_basic_info()
        self.family.set_members()
        self.genetics.set_spawned_genetics()
        self.family.gen = self.family.immediate.mother.family.gen + 1
        print(f'{self} spawned! {self.info["age"]}, {self.info["gender"]}, {self.info["preference"]}')

    def add_to_info(self, prop, val):
        self.info.update({prop: val})

    def set_gender(self):
        return random.choice(GENDERS)

    def set_name(self):
        return [random.choice(n.first_names[self.info['gender']]), self.family.immediate.mother.info['name'][1]]

    def set_age(self):
        return list(random.choice(list(self.ageing.ages.items())[3:6]))

    def give_birth(self):
        child = Offspring(self, self.relationships.romantic.partner)
        child.generate()

        self.family.immediate.offspring.append(child)
        self.relationships.romantic.partner.family.immediate.offspring.append(child)
        self.ageing.pregnancy.step, self.ageing.pregnancy.day = 0, 1
        self.info['is_pregnant'] = False

        for offspring in self.family.immediate.offspring:
            offspring.family.immediate.update_siblings()
        
        print(f'{str(self)} gave birth to {str(child)}!')

    
class SpawnedSim(BaseSim):
    alive = True

    def __init__(self):
        super().__init__()

    def generate(self):
        self.set_parents()
        super().generate()
        self.relationships.set_household_spawned(self)

    def set_parents(self):
        mum, dad = self.family.immediate.mother, self.family.immediate.father
        mum, dad = SpawnedSim(), SpawnedSim()
        mum.family.immediate.mother, mum.family.immediate.father = SpawnedSim(), SpawnedSim()
        dad.family.immediate.mother, dad.family.immediate.father = SpawnedSim(), SpawnedSim()
        grandparents = [mum.family.immediate.mother, mum.family.immediate.father,
                        dad.family.immediate.mother, dad.family.immediate.father]
        parents = [mum, dad]
        females = [mum, mum.family.immediate.mother, dad.family.immediate.mother]
        males = [dad, dad.family.immediate.father, mum.family.immediate.father]

        def parent_iterator():
            for sim in females:
                sim.family.u_id = self.family.u_id
                sim.info.update({'gender': GENDERS[1]})
                sim.info.update({'name': [random.choice(n.first_names[mum.info['gender']]), random.choice(n.surnames)]})
                sim.first_name, sim.surname = sim.info['name'][0], sim.info['name'][1]
            for sim in males:
                sim.family.u_id = self.family.u_id
                sim.info.update({'gender': GENDERS[0]})
                sim.info.update({'name': [random.choice(n.first_names[dad.info['gender']]), mum.info['name'][1]]})
                sim.first_name, sim.surname = sim.info['name'][0], sim.info['name'][1]

        def get_genetics():
            for sim in grandparents:
                sim.genetics.set_genes()
            for sim in parents:
                sim.genetics.set_spawned_genetics()
            
        parent_iterator()
        get_genetics()

        self.family.immediate.mother, self.family.immediate.father = mum, dad
        mum.family.immediate.mother, mum.family.immediate.father = mum.family.immediate.mother, mum.family.immediate.father
        dad.family.immediate.mother, dad.family.immediate.father = dad.family.immediate.mother, dad.family.immediate.father


class Offspring(BaseSim):
    alive = True

    def __init__(self, mother, father):
        super().__init__()
        self.family.immediate.mother, self.family.immediate.father = mother, father
        self.family.u_id = str(self.family.immediate.mother.family.u_id) + str(self.family.immediate.father.family.u_id)

    def generate(self):
        super().generate()
        self.relationships.set_household_offspring(self)

    def set_age(self):
        first_age = list(self.ageing.ages.keys())[0]
        return [first_age, {key: value for key, value in self.ageing.ages[first_age].items()}]

    def set_name(self):
        return [random.choice(n.first_names[self.info['gender']]), self.family.immediate.mother.surname]
