import random
import time
from sims import BaseSim, SpawnedSim, Offspring
from globals import *

max_sims = 1000


class SimulationData:
    def __init__(self):
        self.all_sims = []
        self.alive_sims = []
        self.families = []
        self.households = []

    def add_sim_to_list(self, sim):
        self.all_sims.append(sim)
        self.alive_sims.append(sim)
        self.all_sims.sort(key=lambda sim: sim.surname)
        self.alive_sims.sort(key=lambda sim: (sim.surname, sim.family.u_id))

    def add_family_to_list(self, family):
        self.families.append(family)
        self.families = (list(dict.fromkeys([x for x in self.families])))
        self.families.sort(key=lambda family: (str(family.immediate.mother.family.u_id), str(family.immediate.father.family.u_id)))

    def add_to_lists(self, sim, family):
        self.add_sim_to_list(sim)
        self.add_family_to_list(family)

    def check_lists(self, sim):
        self.check_offspring(sim)
        self.check_dead_sims(sim)
        # self.print_data(sim)

    def check_dead_sims(self, sim):
        if not sim.alive:
            self.alive_sims.remove(sim)

    def check_offspring(self, sim):
        for child in sim.family.immediate.offspring:
            if child not in self.all_sims or child.family not in self.families:
                self.add_to_lists(child, child.family)

    def get_original_sims(self):
        all_originals = [sim for sim in self.all_sims if isinstance(sim, SpawnedSim)]

        for original in all_originals:
            family_list = []
            for offspring in self.all_sims:
                if original in offspring.originals:
                    family_list.append([offspring, offspring.family.gen])
                    family_list.sort(key=lambda x: x[1])

            print([[str(x[0]), x[1]] for x in family_list])

    def print_data(self, sim):
        print(f'name: {str(sim)}, gender: {sim.info.basic["gender"]}, pref: {sim.info.basic["preference"]} age: {sim.info.basic["age"][1]["group"]}, job: {str(sim.job)}')
        print(f'job: {str(sim.job.job)} {sim.job.promotion_progress}')
        print(f'funds: {round(sim.relationships.household.funds, 2)}')
        print(f'genetics: {str(sim.info.genetics)}')
        print(str(sim.relationships.romantic.partner))
        print('relationships:', [str(x) for x in sim.relationships.romantic.potential_partners])
        print('friends:', [str(x) for x in sim.relationships.sims_met])
        print('grandparents:', [str(x) for x in [x for x in sim.family.immediate.grandparents]])
        print('parents:', [str(x) for x in sim.family.immediate.parents])
        print('siblings:', [str(x) for x in sim.family.immediate.siblings])
        print('aunts:', [str(x) for x in sim.family.extended.aunts])
        print('uncles:', [str(x) for x in sim.family.extended.uncles])
        print('cousins:', [str(x) for x in sim.family.extended.cousins])
        print('children:', [str(x) for x in sim.family.immediate.offspring])
        print('2nd cousins:', [str(x) for x in sim.family.extended.second_cousins])
        print([str(x) for x in sim.relationships.household.members])
        print(f'{len(self.alive_sims)} sims alive.')
        print('\n')


class Simulation:
    day = 1
    step = 0
    day_name_step = 1
    day_name = DAYS[day_name_step]

    def __init__(self):
        self.lists = SimulationData()
        self.running = True

    def main_loop(self):
        print('simulation started')
        print(self.day_name)

        while self.running:
            self.igt()

            if len(self.lists.alive_sims) <= max_sims:
                self.update_sims()
                self.spawn_sim()
                print(len(self.lists.alive_sims))

            elif len(self.lists.alive_sims) >= max_sims:
                self.stop_simulation()

    def spawn_sim(self):
        spawn_pc = 0.0375
        if random.random() < spawn_pc:
            sim = SpawnedSim()
            sim.generate()
            self.lists.add_to_lists(sim, sim.family)

    def stop_simulation(self):
        self.lists.get_original_sims()
        self.lists.households.sort(key=lambda x: x.funds)
        for household in self.lists.households:
            print([[str(x), x.info.basic['age'][1]['group']] for x in household.members], household.u_id, round(household.funds, 2))
        self.running = False

    def update_sims(self):
        for sim in self.lists.alive_sims:
            sim.update()

    def pay_wages(self, sim):
        if sim.job.job is not None:
            key = str(list(dict(sim.job.job.items()))[0])

            if self.day_name in sim.job.job[key]["Days"]:
                sim.job.pay_wage()

    def pay_bills(self):
        for household in self.lists.households:
            household.pay_bills()

    def igt(self):
        self.step += 1

        if self.step >= DAY_LENGTH:
            self.day += 1
            self.step = 0

            if self.day_name_step < 7:
                self.day_name_step += 1
            else:
                self.pay_bills()
                self.day_name_step = 1

            self.day_name = DAYS[self.day_name_step]

            for sim in self.lists.alive_sims:
                if sim.relationships.romantic.partner == None:
                    sim.relationships.find_new_sims(self.lists.alive_sims)
                    sim.relationships.romantic.find_partners()

                if self.day_name == "Monday":
                    self.lists.check_lists(sim)

                self.pay_wages(sim)

            print(self.day_name)

        # time.sleep(0.1)


s = Simulation()

if __name__ == "__main__":
    s.main_loop()
