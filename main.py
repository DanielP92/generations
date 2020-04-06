import random
import time
from sims import Sim, Offspring
from globals import *

max_sims = 25

class Simulation:
	simulation_day = 1
	simulation_step = 0

	def __init__(self):
		self.sims = []
		self.running = True

	def main_loop(self):
		spawn_pc = 0.05
		print('simulation started')

		while self.running:
			self.igt()

			if random.random() < spawn_pc and len(self.sims) <= max_sims:
				sim = Sim()
				sim.generate()
				self.add_to_list(sim)
			elif len(self.sims) >= max_sims:
				no_of_offspring = len([sim for sim in self.sims if isinstance(sim, Offspring)])
				print(f'{no_of_offspring} children out of {len(self.sims)} sims') 
				self.running = False

			for sim in self.sims:
				sim.update()

	def add_to_list(self, sim):
		self.sims.append(sim)
		self.sims.sort(key=lambda sim: sim.surname)
			
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
		spawn_pc = 0.0033

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

			if female and old_enough and chance and not pregnant:
				sim.info['is_pregnant'] = True
				print(f'{sim.first_name} {sim.surname} is pregnant!')

			if sim.info['is_pregnant']:
				pregnancy_timer(sim)

	def igt(self):
		self.simulation_step += 1
		s.pregnancy()

		if self.simulation_step >= DAY_LENGTH:
			self.simulation_day += 1
			self.simulation_step = 0

			for sim in self.sims:
				print(f'name: {sim.first_name} {sim.surname}, gender: {sim.info["gender"]}, age: {sim.info["age"][1]["group"]}')

		time.sleep(0.2)


s = Simulation()

if __name__ == "__main__":
    s.main_loop()