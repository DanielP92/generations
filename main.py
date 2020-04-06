import random
import time
from names import AllNames

max_sims = 25
day_length = 16
basic_info = ['gender', 'name', 'age']
genders = ('boy', 'girl')


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
			elif len(self.sims) >= max_sims:
				no_of_offspring = len([sim for sim in self.sims if isinstance(sim, Offspring)])
				print(f'{no_of_offspring} children out of {len(self.sims)} sims') 
				self.running = False

			for sim in self.sims:
				sim.update()

	def sim_aging(self, sim):
		sim.info['age'][1]['days_to_age_up'] -= 1
		if sim.info['age'][1]['days_to_age_up'] < 0:
			sim.info['age'][0] += 1
			if sim.info['age'][0] > 6:
				self.sims.remove(sim)
				print(f'{sim.first_name} {sim.surname} died!')
			else:
				sim.add_to_info('age', sim.age_up())
				print(f'{sim.first_name} {sim.surname} aged up to a(n) {sim.info["age"][1]["group"]}!')

	def sim_births(self):
		spawn_pc = 0.005

		for sim in self.sims:
			if random.random() < spawn_pc and sim.info['gender'] == 'girl' and sim.info['age'][0] >= 3:
				child = Offspring(sim)
				child.generate()
				sim.offspring.append(child)

				print(f'{sim.first_name} {sim.surname} gave birth to {child.first_name} {child.surname}!')

				time.sleep(2)

	def igt(self):
		self.simulation_step += 1
		s.sim_births()

		if self.simulation_step >= day_length:
			self.simulation_day += 1
			self.simulation_step = 0
			for sim in self.sims:
				print(f'name: {sim.first_name} {sim.surname}, gender: {sim.info["gender"]}, age: {sim.info["age"][1]["days_to_age_up"]}')

		time.sleep(0.2)


s = Simulation()
n = AllNames()


class Sim:
	sim_day = 1
	sim_step = 0

	def __init__(self):
		self.info = {}
		self.ages = {1: {'group': 'baby', 'days_to_age_up': 7},
					 2: {'group': 'child', 'days_to_age_up': 14},
					 3: {'group': 'teen', 'days_to_age_up': 21},
					 4: {'group': 'yng_adult', 'days_to_age_up': 21},
					 5: {'group': 'adult', 'days_to_age_up': 60},
					 6: {'group': 'elder', 'days_to_age_up': 28},
				    }
		self.offspring = []

	def update(self):
		self.sim_step += 1
	
		if self.sim_step >= day_length:
			self.sim_day += 1
			self.sim_step = 0
			s.sim_aging(self)

	def generate(self):
		self.properties = self.set_gender, self.set_name, self.set_age
		self.set_basic_info()
		self.first_name, self.surname = self.info['name'][0], self.info['name'][1]
		print(f'{self.first_name} {self.surname} spawned! {self.info["age"]}')
		s.sims.append(self)
	
	def set_basic_info(self):
		for func in self.properties:
			for item in basic_info:
				if str(item) in str(func):
					self.add_to_info(item, func())

	def set_name(self):
		return [random.choice(n.first_names[self.info['gender']]), random.choice(n.surnames)]

	def set_gender(self):
		return random.choice(genders)
		
	def set_age(self):
		return list(random.choice(list(self.ages.items())[2:]))

	def age_up(self):
		return [self.info['age'][0], self.ages[self.info['age'][0]]]

	def add_to_info(self, prop, val):
		self.info.update({prop: val})


class Offspring(Sim):
	def __init__(self, mother):
		self.mother = mother
		super().__init__()
		
	def set_age(self):
		first_age = list(self.ages.keys())[0]
		return [first_age, {key: value for key, value in self.ages[first_age].items()}]

	def set_name(self):
		return [random.choice(n.first_names[self.info['gender']]), self.mother.surname]

if __name__ == "__main__":
	s.main_loop()
