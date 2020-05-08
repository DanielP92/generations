import random
import uuid
import careers
from globals import *


class SimModule:
    def __init__(self, sim):
        self.sim = sim


# # # SIM INFORMATION # # #

class SimInfo(SimModule):
    def __init__(self, sim):
        super().__init__(sim)
        self.basic = dict()
        self.genetics = Genetics(self.sim)
        self.ageing = Ageing(self.sim)

    def set_all(self):
        self.set_basic()

    def add_to_info(self, prop, val):
        self.basic.update({prop: val})

    def set_basic(self):
        basic_info = ['gender', 'name', 'age', 'preference', 'is_pregnant']
        properties = [self.set_gender, self.set_name, self.set_age, self.set_preference, self.is_pregnant]

        for func, item in zip(properties, basic_info):
            self.add_to_info(item, func())

        self.sim.first_name, self.sim.surname = self.basic['name'][0], self.basic['name'][1]

    def set_name(self):
        return [random.choice(NAMES.first_names[self.sim.info.basic['gender']]), self.sim.family.immediate.mother.info.basic['name'][1]]

    def set_age(self):
        return list(random.choice(list(self.sim.info.ageing.ages.items())[3:6]))

    def set_gender(self):
        return random.choice(GENDERS)

    def set_preference(self):
        homo_pc = 0.1
        bi_pc = 0.3

        if random.random() <= homo_pc:
            return self.sim.info.basic['gender']
        elif homo_pc > random.random() <= bi_pc:
            return GENDERS[0] + GENDERS[1]
        else:
            for gender in GENDERS:
                if gender != self.sim.info.basic['gender']:
                    return gender

    def is_pregnant(self):
        if self.sim.info.basic['gender'] == 'girl':
            return False
        elif self.sim.info.basic['gender'] == 'boy':
            return None


# # # JOB # # #

class CurrentJob(SimModule):
    promotion_progress = 35

    def __init__(self, sim):
        super().__init__(sim)
        self.career = None
        self.job = None
        self.level = 0

    def update(self):
        if self.job == None:
            self.find_job()
        elif self.job and self.level < 10:
            self.job_performance()

    def find_job(self):
        get_job = 0.35
        if self.sim.info.basic['age'][0] >= 5 and random.random() < get_job:
            self.set_career()
            self.job = self.set_job()

            key = list(dict(self.job.items()))[0]
            print(f'{self.sim} got a job as a {self.job[key]["Name"]}')

    def set_career(self):
        self.career = random.choice([subclass() for subclass in careers.BaseCareer.__subclasses__()])
        self.career.career_path = self.career.set_career_path()

    def job_performance(self):
        self.promotion_progress += int(random.uniform(-5, 10))
        if self.promotion_progress >= 75:
            self.job = self.set_job()
            self.promotion_progress = 35

            key = list(dict(self.job.items()))[0]
            print(f'{self.sim} has been promoted to {self.job[key]["Name"]}')

    def set_job(self):
        self.level += 1
        return self.career.career_path[self.level]

    def get_wage(self):
        key = list(dict(self.job.items()))[0]
        return self.job[key]['Wage'] * self.job[key]['Hours']

    def pay_wage(self):
        self.sim.relationships.household.funds += self.get_wage()

# # # GENETICS # # #


hair_colours = {'black': 0.9,
                'darkbrown': 0.8,
                'brown': 0.75,
                'lightbrown': 0.5,
                'auburn': 0.35,
                'dirtyblond': 0.25,
                'blonde': 0.2,
                'ginger': 0.1,
                }

eye_colours = {'black': 0.9,
               'brown': 0.8,
               'lightbrown': 0.65,
               'hazel': 0.6,
               'darkblue': 0.45,
               'blue': 0.3,
               'amber': 0.2,
               'lightblue': 0.15,
               'green': 0.1,
               'grey': 0.05,
               }


class Genetics(SimModule):
    def __init__(self, sim):
        super().__init__(sim)
        self.genes = {'hair-colour': HairColour(),
                      'eye-colour': EyeColour(),
                      }

    def __str__(self):
        return str([{key: str(value)} for key, value in self.genes.items()])

    def set_genes(self):
        for value in self.genes.values():
            value.set_expression()

    def set_spawned_genetics(self):
        mother = self.sim.family.immediate.mother.info.genetics
        father = self.sim.family.immediate.father.info.genetics
        hair_choices = [random.choice(mother.genes['hair-colour'].pair), random.choice(father.genes['hair-colour'].pair)]
        eye_choices = [random.choice(mother.genes['eye-colour'].pair), random.choice(father.genes['eye-colour'].pair)]
        self.genes['hair-colour'].pair = hair_choices
        self.genes['eye-colour'].pair = eye_choices
        self.set_genes()


class Gene:
    def __init__(self):
        self.pair = []
        self.expression = None
        self.choices = None

    def __str__(self):
        return str(self.expression)

    def set_expression(self):
        traits = [x.trait for x in self.pair]

        if self.choices[traits[0]] > self.choices[traits[1]] or self.choices[traits[0]] == self.choices[traits[1]]:
            self.expression = traits[0]
        elif self.choices[traits[0]] < self.choices[traits[1]]:
            self.expression = traits[1]


class HairColour(Gene):
    def __init__(self):
        super().__init__()
        self.pair = [HairAllele(), HairAllele()]
        self.choices = hair_colours


class EyeColour(Gene):
    def __init__(self):
        super().__init__()
        self.pair = [EyeAllele(), EyeAllele()]
        self.choices = eye_colours


class Allele:
    def __init__(self):
        self.trait = dict()
        self.weighting = int()

    def __str__(self):
        return self.trait


class HairAllele(Allele):
    def __init__(self):
        super().__init__()
        self.trait = random.choice(list(hair_colours.keys()))


class EyeAllele(Allele):
    def __init__(self):
        super().__init__()
        self.trait = random.choice(list(eye_colours.keys()))


# # # FAMILY # # #

class BaseFamily(SimModule):
    def __init__(self, sim):
        super().__init__(sim)
        self.gen = 0

    def update_iterator(self, list_1, list_2):
        for sim_info in list_1:
            for sim in sim_info:
                if sim not in list_2:
                    list_2.append(sim)
                    list_2.sort(key=lambda x: x.surname)


class ImmediateFamily(BaseFamily):
    def __init__(self, sim):
        super().__init__(sim)
        self.grandparents = []
        self.mother = None
        self.father = None
        self.parents = []
        self.siblings = []
        self.offspring = []

    def update_parents(self):
        self.parents = [self.mother, self.father]

    def update_siblings(self):
        mum_offspring = self.mother.family.immediate.offspring
        dad_offspring = self.father.family.immediate.offspring
        self.siblings = (list(dict.fromkeys([x for x in mum_offspring + dad_offspring if x != self.sim])))

    def update_grandparents(self):
        grandparent_list = [[x.family.immediate.mother, x.family.immediate.father] for x in self.parents]
        self.update_iterator(grandparent_list, self.grandparents)


class ExtendedFamily(BaseFamily):
    def __init__(self, sim):
        super().__init__(sim)
        self.great_grandparents = []
        self.aunts = []
        self.uncles = []
        self.cousins = []
        self.second_cousins = []

    def update_aunts_uncles(self):
        mum_siblings = self.sim.family.immediate.mother.family.immediate.siblings
        dad_siblings = self.sim.family.immediate.father.family.immediate.siblings
        all_siblings = [mum_siblings, dad_siblings]
        self.aunts = [x for x in all_siblings for x in x if x.info.basic['gender'] == 'girl']
        self.uncles = [x for x in all_siblings for x in x if x.info.basic['gender'] == 'boy']

    def update_cousins(self):
        offspring_list = [x.family.immediate.offspring for x in [self.aunts, self.uncles] for x in x if len(x.family.immediate.offspring) != 0]
        self.update_iterator(offspring_list, self.cousins)

    def update_second_cousins(self):
        mum_cousins = self.sim.family.immediate.mother.family.extended.cousins
        dad_cousins = self.sim.family.immediate.father.family.extended.cousins
        offspring_list = [x.family.immediate.offspring for x in [mum_cousins, dad_cousins] for x in x if len(x.family.immediate.offspring) != 0]
        self.update_iterator(offspring_list, self.second_cousins)


class Family(BaseFamily):
    def __init__(self, sim):
        super().__init__(sim)
        self.immediate = ImmediateFamily(self.sim)
        self.extended = ExtendedFamily(self.sim)
        self.functions = [self.immediate.update_parents, self.immediate.update_grandparents,
                          self.immediate.update_siblings, self.extended.update_aunts_uncles,
                          self.extended.update_cousins, self.extended.update_second_cousins,
                          ]
        self.u_id = str(uuid.uuid4())

    def set_members(self):
        for func in self.functions:
            func()


# # # AGEING AND PREGNANCY # # #

class Ageing(SimModule):
    def __init__(self, sim):
        super().__init__(sim)
        self.ages = {1: {'group': 'baby', 'days_to_age_up': 7},
                     2: {'group': 'toddler', 'days_to_age_up': 7},
                     3: {'group': 'child', 'days_to_age_up': 14},
                     4: {'group': 'teen', 'days_to_age_up': 21},
                     5: {'group': 'yng_adult', 'days_to_age_up': 28},
                     6: {'group': 'adult', 'days_to_age_up': 60},
                     7: {'group': 'elder', 'days_to_age_up': 28},
                     }
        self.pregnancy = Pregnancy(self.sim)

    def age_up(self):
        return [self.sim.info.basic['age'][0], self.ages[self.sim.info.basic['age'][0]]]

    def update(self):
        self.sim.info.basic['age'][1]['days_to_age_up'] -= 1

        if self.sim.info.basic['age'][1]['days_to_age_up'] < 0:
            self.sim.info.basic['age'][0] += 1

            if self.sim.info.basic['age'][0] > 7:
                self.sim.alive = False
                try:
                    household = self.sim.relationships.household.members
                    household.remove(self.sim)

                    print(f'{self.sim.first_name} {self.sim.surname} died!')

                    if len(household) == 0:
                        split = len(self.sim.family.immediate.offspring)
                        amount = self.sim.relationships.household.funds / split
                        if split == 0:
                            pass
                        else:
                            for child in self.sim.family.immediate.offspring:
                                child.relationships.household.funds += int(amount)
                                print(f'{child} inherited {round(amount, 2)} from {self.sim}')
                except:
                    pass
            else:
                self.sim.info.add_to_info('age', self.age_up())
                print(f'{str(self.sim)} aged up to a(n) {self.sim.info.basic["age"][1]["group"]}!')


class Pregnancy(SimModule):
    step = 0
    day = 1

    def __init__(self, sim):
        super().__init__(sim)

    def timer(self):
        self.step += 1

        if self.step > DAY_LENGTH:
            self.day += 1
            self.step = 0

        if self.day > 3:
            self.sim.give_birth()

    def set_chance(self):
        no_of_children = len(self.sim.family.immediate.offspring)
        if no_of_children < 3:
            return 0.005
        elif 3 <= no_of_children <= 5:
            return 0.001
        else:
            return 0.0005

    def pregnancy(self):
        spawn_pc = self.set_chance()

        spawn_chance = random.random() < spawn_pc and self.sim.relationships.romantic.partner
        pregnant = self.sim.info.basic['is_pregnant']
        hit = spawn_chance and not pregnant
        female = self.sim.info.basic['gender'] == 'girl'
        old_enough = 4 <= self.sim.info.basic['age'][0] <= 6

        if female and old_enough and hit:
            self.sim.info.basic['is_pregnant'] = True
            print(str(self.sim) + ' is pregnant!')

        if self.sim.info.basic['is_pregnant']:
            self.timer()


# # # RELATIONSHIPS # # #

class Household:
    def __init__(self):
        self.members = []
        self.u_id = str(uuid.uuid4())
        self.location = random.uniform(0, 3)
        self.funds = 5000

    def add_member(self, sim):
        self.members.append(sim)

    def pay_bills(self):
        per_person = 350
        total_bills = per_person * len(self.members)
        self.funds -= total_bills


class Romantic(SimModule):
    def __init__(self, sim):
        super().__init__(sim)
        self.partner = None
        self.potential_partners = dict()
        self.chemistry_value = random.choice(range(10))

    def find_partners(self):
        single = self.sim.relationships.romantic.partner is None
        age = self.sim.info.basic['age'][0]
        gender = self.sim.info.basic['gender']
        pref = self.sim.info.basic['preference']
        uid = self.sim.family.immediate.grandparents[0].family.u_id

        for sim in self.sim.relationships.sims_met:
            sim_single = sim.relationships.romantic.partner is None
            sim_gender = sim.info.basic['gender']
            sim_pref = sim.info.basic['preference']
            sim_age = sim.info.basic['age'][0]
            sim_uid = sim.family.immediate.grandparents[0].family.u_id
            chemistry = self.sim.relationships.romantic.set_chemistry_value(sim)

            single_check = single == sim_single
            age_check = age == sim_age and sim_age >= 4
            gender_check = gender in sim_pref and sim_gender in pref
            family_check = uid not in sim_uid and sim_uid not in uid

            if single_check and age_check and gender_check and family_check and chemistry >= 1.1:
                if sim in self.sim.relationships.romantic.potential_partners:
                    pass
                else:
                    self.sim.relationships.romantic.potential_partners.update({sim: int()})

            partners = self.sim.relationships.romantic.potential_partners

            if self.sim in partners:
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

            self.sim.info.basic['name'][1] = partner.info.basic['name'][1] = surname
            self.sim.surname = partner.surname = surname

        def set_new_household():
            sim_hh = self.sim.relationships.household
            partner_hh = partner.relationships.household
            sim_hh_split = len(sim_hh.members)
            partner_hh_split = len(partner_hh.members)

            if sim_hh.funds > 0:
                sim_funds = sim_hh.funds / sim_hh_split
                sim_hh.funds -= sim_funds
            elif sim_hh.funds <= 0:
                sim_funds = 1500

            if partner_hh.funds > 0:
                partner_funds = partner_hh.funds / partner_hh_split
                partner_hh.funds -= partner_funds
            elif partner_hh.funds <= 0:
                partner_funds = 1500

            new_hh_fund = sim_funds + partner_funds

            try:
                self.sim.relationships.household.members.remove(self.sim)
                partner.relationships.household.members.remove(partner)
            except:
                pass

            self.sim.relationships.household = partner.relationships.household = Household()
            self.sim.relationships.household.add_member(self.sim)
            self.sim.relationships.household.add_member(partner)
            self.sim.relationships.household.funds = new_hh_fund

            print(f'{str(self.sim)} and {str(partner)} are now partners! Total household funds: {round(new_hh_fund, 2)}')

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

    def chemistry_between(self, x):
        chemistries = [self.chemistry_value, x.relationships.romantic.chemistry_value]
        return max(chemistries) - min(chemistries)

    def set_chemistry_value(self, x):
        difference = self.chemistry_between(x)

        if difference == 0:
            return 2.75
        elif difference == 1:
            return 2
        elif difference == 2:
            return 1.5
        else:
            return 1


class Friendly(SimModule):
    def __init__(self, sim):
        super().__init__(sim)
        self.sims_met = dict()


class Relationships(SimModule):
    step = 0.01

    def __init__(self, sim):
        super().__init__(sim)
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
            total_distance = self.distance_between(sim)

            if total_distance <= self.step and total_distance <= sim.relationships.step:
                self.meet_sim(sim)

    def meet_sim(self, sim):
        sim_met = False

        def meet_chance():
            return random.random() < 0.05

        if sim not in self.sims_met and sim != self.sim and meet_chance():
            self.sims_met.update({sim: int()})

        elif len(self.sims_met) >= 75:
            pass

    def set_household_spawned(self, sim):
        self.household = Household()
        self.household.add_member(sim)

    def set_household_offspring(self, sim):
        self.sim.family.immediate.mother.relationships.household.add_member(self.sim)
        self.household = sim.family.immediate.mother.relationships.household

    def distance_between(self, x):
        distances = [self.sim.relationships.household.location, x.relationships.household.location]
        return max(distances) - min(distances)

    def set_distance_value(self, x):
        total_distance = self.distance_between(x)

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

    def relationship_change(self):
        for x in self.romantic.potential_partners:
            add_distance = self.set_distance_value(x)
            add_chemistry = self.romantic.set_chemistry_value(x)
            new_val = self.romantic.potential_partners[x] + ((random.randint(-2, 4) + add_distance) * add_chemistry)
            if new_val > 100:
                new_val = 100
            self.romantic.potential_partners.update({x: new_val})
