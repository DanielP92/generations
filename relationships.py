import random
import uuid
from globals import *


class Household:
    def __init__(self):
        self.members = []
        self.u_id = str(uuid.uuid4())
        self.location = random.uniform(0, 3)

    def add_member(self, sim):
        self.members.append(sim)

class Romantic:
    def __init__(self, sim):
        self.sim = sim
        self.partner = None
        self.potential_partners = dict()
        self.chemistry_value = random.choice(range(10))

    def find_partners(self):
        single = self.sim.relationships.romantic.partner is None
        age = self.sim.info['age'][0]
        gender = self.sim.info['gender']
        pref = self.sim.info['preference']
        uid = self.sim.family.immediate.grandparents[0].family.u_id

        for sim in self.sim.relationships.sims_met:
            sim_single = sim.relationships.romantic.partner is None
            sim_gender = sim.info['gender']
            sim_pref = sim.info['preference']
            sim_age = sim.info['age'][0]
            sim_uid = sim.family.immediate.grandparents[0].family.u_id
            chemistry = self.sim.relationships.set_chemistry_value(sim)

            single_check = single == sim_single
            age_check = age == sim_age and sim_age >= 4
            gender_check = gender in sim_pref and sim_gender in pref
            family_check = uid not in sim_uid and sim_uid not in uid


            if single_check and age_check and gender_check and family_check and chemistry >= 1.1:
                if sim in self.sim.relationships.romantic.potential_partners:
                    pass
                else:
                    self.sim.relationships.romantic.potential_partners.update({sim: int()})

            if self.sim in self.sim.relationships.romantic.potential_partners:
                del self.sim.relationships.romantic.potential_partners[self.sim]

    def set_partner(self):
        threshold = 65
        surname = ""

        def set_surnames():
            single_name = 0.95
            follow_pc = 0.66

            if random.random() < single_name or any('-' in x for x in [self.sim.surname, partner.surname]):
                if random.random() < follow_pc:
                    surname = self.sim.surname
                else:
                    surname = partner.surname
            else:
                if random.random() < follow_pc:
                    surname = f'{self.sim.surname}-{partner.surname}'
                else:
                    surname = f'{partner.surname}-{self.sim.surname}'

            self.sim.info['name'][1] = partner.info['name'][1] = surname
            self.sim.surname = partner.surname = surname

        def set_new_household():
            try:
                self.sim.relationships.household.members.remove(self.sim)
                self.partner.relationships.household.members.remove(self.partner)
            except:
                pass
            self.sim.relationships.household = self.partner.relationships.household = Household()
            self.sim.relationships.household.add_member(self.sim)
            self.sim.relationships.household.add_member(partner)

            print(f'{str(self.sim)} and {str(partner)} are now partners!')
        
        def choose_partner():
            if self.sim in partner.relationships.romantic.potential_partners:
                rel1 = self.sim.relationships.romantic.potential_partners[partner]
                rel2 = partner.relationships.romantic.potential_partners[self.sim]

                if rel1 >= threshold and rel2 >= threshold and self.partner == None and partner.relationships.romantic.partner == None:
                    partner.relationships.romantic.partner = self.sim
                    self.partner = partner
                    set_surnames()
                    set_new_household()

        for partner in self.potential_partners:
            choose_partner()


class Friendly:
    def __init__(self, sim):
        self.sim = sim
        self.sims_met = dict()


class Relationships:
    step = 0.01

    def __init__(self, sim):
        self.sim = sim
        self.sims_met = dict()
        self.household = Household()
        self.romantic = Romantic(self.sim)
        self.friendly = Friendly(self.sim)

    def update(self):
        self.step += random.uniform(0.01, 0.025)
        self.relationship_change()
        self.sim.family.set_members()
        if self.romantic.partner == None:
            self.romantic.set_partner()

    def find_new_sims(self, sim_list):
        for sim in sim_list:
            distances = [self.sim.relationships.household.location, sim.relationships.household.location]
            total_distance = max(distances) - min(distances)

            if total_distance <= self.step and total_distance <= sim.relationships.step:
                self.meet_sim(sim)

    def meet_sim(self, sim):
        if sim not in self.sims_met and sim != self.sim:
            self.sims_met.update({sim: int()})
            print(f'{str(self.sim)} and {str(sim)} have met!')

    def set_preference(self):
        homo_pc = 0.1
        bi_pc = 0.3

        if random.random() <= homo_pc:
            return self.sim.info['gender']
        elif homo_pc > random.random() <= bi_pc:
            return GENDERS[0] + GENDERS[1]
        else:
            for gender in GENDERS:
                if gender != self.sim.info['gender']:
                    return gender

    def set_household_spawned(self, sim):
        self.household = Household()
        self.household.add_member(sim)

    def set_household_offspring(self, sim):
        self.sim.family.immediate.mother.relationships.household.add_member(self.sim)
        self.household = sim.family.immediate.mother.relationships.household

    def set_distance_value(self, x):
        distances = [self.sim.relationships.household.location, x.relationships.household.location]
        total_distance = max(distances) - min(distances)
            
        if total_distance < 0.1:
            return 4
        elif 0.1 <= total_distance <= 0.25:
            return 3
        elif 0.25 <= total_distance <= 0.5:
            return 2
        elif 0.5 <= total_distance <= 1:
            return 1
        else:
            return 0

    def set_chemistry_value(self, x):
        chemistries = [self.sim.relationships.romantic.chemistry_value, x.relationships.romantic.chemistry_value]
        difference = max(chemistries) - min(chemistries)

        if difference == 0:
            return 1.75
        elif difference == 1:
            return 1.33
        elif difference == 2:
            return 1.1
        else:
            return 1

    def relationship_change(self):
        for x in self.romantic.potential_partners:
            add_distance = self.set_distance_value(x)
            add_chemistry = self.set_chemistry_value(x)
            new_val = self.romantic.potential_partners[x] + ((random.randint(-2, 4) + add_distance) * add_chemistry)
            if new_val > 100:
                new_val = 100
            self.romantic.potential_partners.update({x: new_val})
