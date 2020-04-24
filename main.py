import random
import time
from sims import BaseSim, SpawnedSim, Offspring
from globals import *

max_sims = 1000

class Simulation:
	day = 1
	step = 0
	day_name_step = 1
	day_name = DAYS[day_name_step]

	def __init__(self):
		self.all_sims = []
		self.alive_sims = []
		self.families = []
		self.households = []
		self.running = True

	def spawn_sim(self):
		spawn_pc = 0.025
		if random.random() < spawn_pc:
			sim = SpawnedSim()
			sim.generate()
			self.add_to_lists(sim, sim.family)

	def stop_simulation(self):
		self.get_original_sims()
		for household in self.households:
			print([[str(x), x.info['age'][1]['group']] for x in household.members], household.u_id)
		self.running = False

	def update_sims(self):
		for sim in self.alive_sims:
			sim.update()
			
	def check_lists(self, sim):
		self.find_all_households(sim)
		self.check_offspring(sim)
		self.check_dead_sims(sim)
		self.print_data(sim)

	def igt(self):
		self.step += 1

		if self.step >= DAY_LENGTH:
			self.day += 1
			self.step = 0

			if self.day_name_step < 7:
				self.day_name_step += 1
			else:
				self.day_name_step = 1

			self.day_name = DAYS[self.day_name_step]
			
			for sim in self.alive_sims:
				sim.relationships.find_new_sims(self.alive_sims)
				sim.relationships.romantic.find_partners()
				self.check_lists(sim)

			print(self.day_name)
		time.sleep(0.1)

	def main_loop(self):
		print('simulation started')
		print(self.day_name)

		while self.running:
			self.igt()

			if len(self.alive_sims) <= max_sims:
				self.update_sims()
				self.spawn_sim()

			elif len(self.alive_sims) >= max_sims:
				self.stop_simulation()

	def find_all_households(self, sim):
		if sim.relationships.household not in self.households:
			self.households.append(sim.relationships.household)
			self.households.sort(key=lambda x: x.u_id)

		for household in self.households:
			if len(household.members) == 0:
				self.households.remove(household)

	def add_to_lists(self, sim, family):
		self.add_sim_to_list(sim)
		self.add_family_to_list(family)

	def add_sim_to_list(self, sim):
		self.all_sims.append(sim)
		self.alive_sims.append(sim)
		self.all_sims.sort(key=lambda sim: sim.surname)
		self.alive_sims.sort(key=lambda sim: (sim.surname, sim.family.u_id))

	def add_family_to_list(self, family):
		self.families.append(family)
		self.families = (list(dict.fromkeys([x for x in self.families])))
		self.families.sort(key=lambda family: (str(family.immediate.mother.family.u_id), str(family.immediate.father.family.u_id)))

	def check_dead_sims(self, sim):
		if not sim.alive:
			self.alive_sims.remove(sim)

	def check_offspring(self, sim):
		for child in sim.family.immediate.offspring:
			if child not in self.all_sims or child.family not in self.families:
				self.add_to_lists(child, child.family)

	def print_data(self, sim):
		print(f'name: {str(sim)}, gender: {sim.info["gender"]}, pref: {sim.info["preference"]} age: {sim.info["age"][1]["group"]}')
		print(str(sim.relationships.romantic.partner))
		print('relationships:', [str(x) for x in sim.relationships.romantic.potential_partners])
		print('friends:', [str(x) for x in sim.relationships.sims_met])
		print('grandparents:', [str(x) for x in [x for x in sim.family.immediate.grandparents]])
		print('parents:', [str(x)  for x in sim.family.immediate.parents])
		print('siblings:', [str(x)  for x in sim.family.immediate.siblings])
		print('aunts:', [str(x) for x in sim.family.extended.aunts])
		print('uncles:', [str(x) for x in sim.family.extended.uncles])
		print('cousins:', [str(x) for x in sim.family.extended.cousins])
		print('children:', [str(x) for x in sim.family.immediate.offspring])
		print('2nd cousins:', [str(x) for x in sim.family.extended.second_cousins])
		print([str(x) for x in sim.relationships.household.members])
		print(f'{len(self.alive_sims)} sims alive.')
		print('\n')

	def get_original_sims(self):
		originals = [sim for sim in self.all_sims if isinstance(sim, SpawnedSim)]

		for original in originals:
			family_list = []

			for sim in self.all_sims:
				if original.family.u_id in sim.family.u_id:
					family_list.append([sim, [sim.family.immediate.mother.family.gen, sim.family.immediate.father.family.gen], sim.family.gen])
					family_list.sort(key=lambda x: x[2])

			print([[str(x[0]), x[1], x[2]] for x in family_list])


s = Simulation()

if __name__ == "__main__":
	s.main_loop()
