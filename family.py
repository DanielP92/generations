import uuid

class BaseFamily:
    def __init__(self, sim):
        self.sim = sim
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
        self.aunts = [x for x in all_siblings for x in x if x.info['gender'] == 'girl']
        self.uncles = [x for x in all_siblings for x in x if x.info['gender'] == 'boy']

    def update_cousins(self):
        offspring_list = [x.family.immediate.offspring for x in [self.aunts, self.uncles] for x in x if len(x.family.immediate.offspring) != 0]            
        self.update_iterator(offspring_list, self.cousins)
        
    def update_second_cousins(self):
        offspring_list = [x.family.immediate.offspring for x in [self.aunts, self.uncles] for x in x if len(x.family.immediate.offspring) != 0]
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
