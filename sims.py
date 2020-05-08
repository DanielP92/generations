import random
import uuid
import sim_modules as modules
from globals import *


class BaseSim:
    day = 1
    step = 0

    def __init__(self):
        self.info = modules.SimInfo(self)
        self.family = modules.Family(self)
        self.relationships = modules.Relationships(self)
        self.job = modules.CurrentJob(self)

    def __str__(self):
        return f'{self.first_name} {self.surname}'

    def update(self):
        self.step += 1
        self.info.ageing.pregnancy.pregnancy()

        if self.step >= DAY_LENGTH:
            self.day += 1
            self.step = 0
            self.info.ageing.update()
            self.relationships.update()
            self.job.update()

    def generate(self):
        self.info.set_basic()
        self.family.set_members()
        self.info.genetics.set_spawned_genetics()
        self.family.gen = max([self.family.immediate.mother.family.gen + 1, self.family.immediate.father.family.gen + 1])
        print(f'{self} spawned! {self.info.basic["age"]}, {self.info.basic["gender"]}, {self.info.basic["preference"]}')

    def give_birth(self):
        child = Offspring(self, self.relationships.romantic.partner)
        child.generate()

        self.family.immediate.offspring.append(child)
        self.relationships.romantic.partner.family.immediate.offspring.append(child)
        self.info.ageing.pregnancy.step, self.info.ageing.pregnancy.day = 0, 1
        self.info.basic['is_pregnant'] = False

        for offspring in self.family.immediate.offspring:
            offspring.family.immediate.update_siblings()

        print(f'{str(self)} gave birth to {str(child)}!')


class SpawnedSim(BaseSim):
    alive = True

    def __init__(self):
        super().__init__()
        self.originals = [self, self]

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
                sim.info.basic.update({'gender': GENDERS[1]})
                sim.info.basic.update({'name': [random.choice(NAMES.first_names[mum.info.basic['gender']]), random.choice(NAMES.surnames)]})
                sim.first_name, sim.surname = sim.info.basic['name'][0], sim.info.basic['name'][1]
            for sim in males:
                sim.family.u_id = self.family.u_id
                sim.info.basic.update({'gender': GENDERS[0]})
                sim.info.basic.update({'name': [random.choice(NAMES.first_names[dad.info.basic['gender']]), mum.info.basic['name'][1]]})
                sim.first_name, sim.surname = sim.info.basic['name'][0], sim.info.basic['name'][1]

        def get_genetics():
            for sim in grandparents:
                sim.info.genetics.set_genes()
            for sim in parents:
                sim.info.genetics.set_spawned_genetics()

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
        self.originals = mother.originals + father.originals
        self.family.u_id = str(self.family.immediate.mother.family.u_id) + str(self.family.immediate.father.family.u_id)

    def generate(self):
        super().generate()
        self.relationships.set_household_offspring(self)

    def set_age(self):
        first_age = list(self.info.ageing.ages.keys())[0]
        return [first_age, {key: value for key, value in self.info.ageing.ages[first_age].items()}]

    def set_name(self):
        return [random.choice(NAMES.first_names[self.info.basic['gender']]), self.family.immediate.mother.surname]
