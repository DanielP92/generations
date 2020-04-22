import random
import uuid
from globals import *


class Household:
    def __init__(self):
        self.members = []
        self.u_id = str(uuid.uuid4())

    def add_member(self, sim):
        self.members.append(sim)

class Romantic:
    def __init__(self, sim):
        self.sim = sim
        self.partner = None

    def find_partners(self, sim_list):
        for sim in sim_list:
            current_sim = sim
            current_sim_age = current_sim.info['age'][1]['group']
            current_sim_gender = current_sim.info['gender']
            current_sim_pref = current_sim.info['preference']
            current_sim_uid = current_sim.family.immediate.grandparents[0].family.u_id

            for sim in sim_list:
                sim_single = sim.relationships.romantic.partner is None
                sim_gender = sim.info['gender']
                sim_pref = sim.info['preference']
                sim_age = sim.info['age'][1]['group']
                sim_uid = sim.family.immediate.grandparents[0].family.u_id

                age_check = current_sim_age == sim_age
                gender_check = current_sim_gender in sim_pref and sim_gender in current_sim_pref
                family_check = current_sim_uid not in sim_uid and sim_uid not in current_sim_uid

                if sim_single and age_check and gender_check and family_check:
                    if sim in current_sim.info['eligable_partners']:
                        pass
                    else:
                        current_sim.info['eligable_partners'].update({sim: int()})

                if current_sim in current_sim.info['eligable_partners']:
                    del current_sim.info['eligable_partners'][sim]

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
            self.sim.relationships.household.members.remove(self.sim)
            self.partner.relationships.household.members.remove(self.partner)
            self.sim.relationships.household = self.partner.relationships.household = Household()
            self.sim.relationships.household.add_member(self.sim)
            self.sim.relationships.household.add_member(partner)

            print(f'{self.sim.first_name} {self.sim.surname} and {partner.first_name} {partner.surname} are now partners!')
        
        def choose_partner():
            if self.sim in partner.info['eligable_partners']:
                rel1 = self.sim.info['eligable_partners'][partner]
                rel2 = partner.info['eligable_partners'][self.sim]

                if rel1 >= threshold and rel2 >= threshold and self.partner == None and partner.relationships.romantic.partner == None:
                    partner.relationships.romantic.partner = self.sim
                    self.partner = partner
                    set_surnames()
                    set_new_household()

        for partner in self.sim.info['eligable_partners']:
            choose_partner()


class Relationships:
    def __init__(self, sim):
        self.sim = sim
        self.household = None
        self.romantic = Romantic(self.sim)
        self.friendly = None # new class

    def update(self):
        self.relationship_change()
        self.sim.family.set_members()
        if self.romantic.partner == None:
            self.romantic.set_partner()

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

    def relationship_change(self):
        for x in self.sim.info['eligable_partners']:
            new_val = self.sim.info['eligable_partners'][x] + random.randint(-2, 15)
            if new_val > 100:
                new_val = 100
            self.sim.info['eligable_partners'].update({x: new_val})
