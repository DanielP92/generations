import random
import time
from sims import Sim, Offspring
from globals import *

max_sims = 25

class Simulation:
	day = 1
	step = 0
	day_name_step = 1
	day_name = DAYS[day_name_step]

	def __init__(self):
		self.sims = []
		self.running = True

	def main_loop(self):
		spawn_pc = 0.05
		print('simulation started')
		print(self.day_name)

		while self.running:
			self.igt()

			if random.random() < spawn_pc and len(self.sims) <= max_sims:
				sim = Sim()
				sim.generate()
				self.add_to_list(sim)
				self.find_relationships()
			elif len(self.sims) >= max_sims:
				no_of_offspring = len([sim for sim in self.sims if isinstance(sim, Offspring)])
				print(f'{no_of_offspring} children out of {len(self.sims)} sims')
				self.running = False

			for sim in self.sims:
				sim.update()

	def add_to_list(self, sim):
		self.sims.append(sim)
		self.sims.sort(key=lambda sim: sim.surname)

	def aging(self, sim):
		sim.info['age'][1]['days_to_age_up'] -= 1

		if sim.info['age'][1]['days_to_age_up'] < 0:
			sim.info['age'][0] += 1

			if sim.info['age'][0] > 6:
				self.sims.remove(sim)
				print(f'{sim.first_name} {sim.surname} died!')
			else:
				sim.add_to_info('age', sim.age_up())
				print(f'{sim.first_name} {sim.surname} aged up to a(n) {sim.info["age"][1]["group"]}!')

	def find_relationships(self):
		single_sims = [sim for sim in self.sims if sim.partner is None and sim.info['age'][0] >= 3]
		for sim in single_sims:
			current_sim = sim
			current_sim_age = current_sim.info['age'][1]['group']
			current_sim_gender = current_sim.info['gender']
			current_sim_pref = current_sim.info['preference']

			for sim in single_sims:
				sim_single = sim.partner is None
				sim_gender = sim.info['gender']
				sim_pref = sim.info['preference']
				sim_age = sim.info['age'][1]['group']

				if sim_single and current_sim_age == sim_age and current_sim_gender in sim_pref and sim_gender in current_sim_pref:
					if sim in current_sim.info['eligable_partners']:
						pass
					else:
						current_sim.info['eligable_partners'].update({sim: int()})

				if current_sim in current_sim.info['eligable_partners']:
					del current_sim.info['eligable_partners'][sim]

	def give_birth(self, sim):
		child = Offspring(sim)
		child.generate()
		self.add_to_list(child)

		sim.offspring.append(child)
		sim.preg_step, sim.preg_day = 0, 1
		sim.info['is_pregnant'] = False
		print(f'{sim.first_name} {sim.surname} gave birth to {child.first_name} {child.surname}!')

		time.sleep(2)

	def pregnancy(self):
		spawn_pc = 0.01

		def pregnancy_timer(sim):
			sim.preg_step += 1

			if sim.preg_step > DAY_LENGTH:
				sim.preg_day += 1
				sim.preg_step = 0

			if sim.preg_day > 3:
				self.give_birth(sim)

		for sim in self.sims:
			chance = random.random() < spawn_pc
			female = sim.info['gender'] == 'girl'
			old_enough = sim.info['age'][0] >= 3
			pregnant = sim.info['is_pregnant']
			partnered = sim.partner
			spawn_day = self.day_name in ["Monday", "Wednesday", "Friday"]

			if spawn_day and female and old_enough and chance and partnered and not pregnant:
				sim.info['is_pregnant'] = True
				print(f'{sim.first_name} {sim.surname} is pregnant!')

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

			for sim in self.sims:
				self.aging(sim)
				print(f'name: {sim.first_name} {sim.surname}, gender: {sim.info["gender"]}, pref: {sim.info["preference"]} age: {sim.info["age"][1]["group"]} relationships: {sim.info["eligable_partners"]}')

		time.sleep(0.2)


s = Simulation()

if __name__ == "__main__":
	s.main_loop()
