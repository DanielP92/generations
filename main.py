import random
import time
from sims import Sim, Offspring
from globals import *

max_sims = 150

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
		sim = Sim()
		sim.set_parents()
		sim.generate()
		self.add_to_lists(sim, sim.family)
		self.find_partners()

	def stop_simulation(self):
		no_of_offspring = len([sim for sim in self.alive_sims if isinstance(sim, Offspring)])
		print(f'{no_of_offspring} children out of {len(self.alive_sims)} sims')
				
		self.get_original_sims()
		for household in self.households:
			print([[str(x), x.info['age'][1]['group']] for x in household.members], household.u_id)
		self.running = False

	def main_loop(self):
		spawn_pc = 0.05
		print('simulation started')
		print(self.day_name)

		while self.running:
			self.igt()

			if random.random() < spawn_pc and len(self.alive_sims) <= max_sims:
				self.spawn_sim()
			elif len(self.alive_sims) >= max_sims:
				self.stop_simulation()
			
			for sim in self.alive_sims:
				self.set_households(sim)
				sim.update()

	def set_households(self, sim):
		if sim.household not in self.households:
			self.households.append(sim.household)
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

	def aging(self, sim):
		sim.info['age'][1]['days_to_age_up'] -= 1

		if sim.info['age'][1]['days_to_age_up'] < 0:
			sim.info['age'][0] += 1

			if sim.info['age'][0] > 6:
				self.alive_sims.remove(sim)
				sim.household.members.remove(sim)
				print(f'{sim.first_name} {sim.surname} died!')
			else:
				sim.add_to_info('age', sim.age_up())
				print(f'{str(sim)} aged up to a(n) {sim.info["age"][1]["group"]}!')

	def find_partners(self):
		single_sims = [sim for sim in self.alive_sims if sim.partner is None and sim.info['age'][0] >= 3]
		for sim in single_sims:
			current_sim = sim
			current_sim_age = current_sim.info['age'][1]['group']
			current_sim_gender = current_sim.info['gender']
			current_sim_pref = current_sim.info['preference']
			current_sim_uid = current_sim.family.immediate.grandparents[0].family.u_id

			for sim in single_sims:
				sim_single = sim.partner is None
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

	def give_birth(self, sim):
		child = Offspring(sim, sim.partner)
		child.generate()
		self.add_to_lists(child, child.family)

		sim.family.immediate.offspring.append(child)
		sim.partner.family.immediate.offspring.append(child)
		sim.preg_step, sim.preg_day = 0, 1
		sim.info['is_pregnant'] = False

		for offspring in sim.family.immediate.offspring:
			offspring.family.immediate.update_siblings()
		
		print(f'{str(sim)} gave birth to {str(child)}!')

		#time.sleep(2)

	def pregnancy(self):
		spawn_pc = 0.0075

		def pregnancy_timer(sim):
			sim.preg_step += 1

			if sim.preg_step > DAY_LENGTH:
				sim.preg_day += 1
				sim.preg_step = 0

			if sim.preg_day > 3:
				self.give_birth(sim)

		for sim in self.alive_sims:
			spawn_day = self.day_name in ["Monday", "Wednesday", "Friday"]
			spawn_chance = random.random() < spawn_pc and sim.partner and spawn_day
			pregnant = sim.info['is_pregnant']
			hit = spawn_chance and not pregnant
			female = sim.info['gender'] == 'girl'
			old_enough = 3 <= sim.info['age'][0] <= 5

			if female and old_enough and hit:
				sim.info['is_pregnant'] = True
				print(str(sim) + ' is pregnant!')

			if sim.info['is_pregnant']:
				pregnancy_timer(sim)

	def igt(self):
		self.step += 1
		self.pregnancy()

		if self.step >= DAY_LENGTH:
			self.day += 1
			self.step = 0

			if self.day_name_step < 7:
				self.day_name_step += 1
			else:
				self.day_name_step = 1

			self.day_name = DAYS[self.day_name_step]

			print(self.day_name)

			for sim in self.alive_sims:
				self.aging(sim)
				self.print_data(sim)

		#time.sleep(0.1)

	def print_data(self, sim):
		print(f'name: {str(sim)}, gender: {sim.info["gender"]}, pref: {sim.info["preference"]} age: {sim.info["age"][1]["group"]}')
		print(f'relationships: {[str(x) for x in sim.info["eligable_partners"]]}')
		print(str(sim.partner))
		print('grandparents:', [str(x) for x in [x for x in sim.family.immediate.grandparents]])
		print('parents:', [str(x)  for x in sim.family.immediate.parents])
		print('siblings:', [str(x)  for x in sim.family.immediate.siblings])
		print('aunts:', [str(x) for x in sim.family.extended.aunts])
		print('uncles:', [str(x) for x in sim.family.extended.uncles])
		print('cousins:', [str(x) for x in sim.family.extended.cousins])
		print('children:', [str(x) for x in sim.family.immediate.offspring])
		print([str(x) for x in sim.household.members])
		print(f'{len(self.alive_sims)} sims alive.')

	def get_original_sims(self):
		originals = [sim for sim in self.all_sims if not isinstance(sim, Offspring)]

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
