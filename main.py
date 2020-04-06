import random
import time
from names import AllNames

max_sims = 25
basic_info = ['gender', 'name', 'age']
genders = ('boy', 'girl')


class Simulation:
	day = 1
	step = 0

	def __init__(self):
		self.sims = []
		self.running = True

	def main_loop(self):
		spawn_pc = 0.05

		while self.running:
			self.igt()

			if random.random() < spawn_pc and len(self.sims) <= max_sims:
				sim = Sim()
				sim.generate()
			elif len(self.sims) >= max_sims:
				self.running = False

	def sim_aging(self):
		for sim in self.sims:
			sim.info['age'][1]['days_to_age_up'] -= 1

			if sim.info['age'][1]['days_to_age_up'] < 0:
				sim.info['age'][0] += 1
				if sim.info['age'][0] > 6:
					self.sims.remove(sim)
					print(f'{sim.first_name} {sim.surname} died!')
				else:
					sim.add_to_info('age', sim.age_up())

			print(sim.info['name'], sim.info['age'][1]['group'], sim.info['gender'])

	def sim_births(self):
		spawn_pc = 0.05

		for sim in self.sims:
			if random.random() < spawn_pc and sim.info['gender'] == 'girl' and sim.info['age'][0] >= 3:
				child = Offspring(sim)
				child.generate()
				sim.offspring.append(child)

				print(f'{sim.first_name} {sim.surname} gave birth to {child.first_name} {child.surname}!')

				time.sleep(2)

	def igt(self):
		self.step += 1

		if self.step >= 8:
			self.day += 1
			self.step = 0
			self.sim_aging()
			self.sim_births()
			#print(self.day)
			#print([sim.info for sim in self.sims])

		time.sleep(0.2)


s = Simulation()
n = AllNames()


class Sim:
	def __init__(self):
		self.info = {}
		self.ages = {1: {'group': 'baby', 'days_to_age_up': 7},
				  	 2: {'group': 'child', 'days_to_age_up': 14},
				  	 3: {'group': 'teen', 'days_to_age_up': 21},
				  	 4: {'group': 'yng_adult', 'days_to_age_up': 21},
				  	 5: {'group': 'adult', 'days_to_age_up': 60},
				  	 6: {'group': 'elder', 'days_to_age_up': 2},
				    }
		self.offspring = []

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
		return list(random.choice(list(self.ages.items())))

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
