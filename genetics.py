import random

hair_colours = {'black': 'dominant',
                'brown': 'dominant',
                'auburn': 'dominant',
                'blonde': 'recessive',
                'ginger': 'recessive',
                }

eye_colours = {'black': 'dominant', 
               'brown':'dominant', 
               'hazel': 'dominant', 
               'lightbrown': 'dominant', 
               'darkblue': 'recessive',
               'blue': 'recessive',
               'lightblue': 'recessive', 
               'grey': 'recessive',
               }


class Genetics:
    def __init__(self, sim):
        self.sim = sim
        self.genes = {'hair-colour': HairColour(),
                      'eye-colour': EyeColour(),
                      }

    def __str__(self):
        return str([{key: str(value)} for key, value in self.genes.items()])

    def set_genes(self):
        for value in self.genes.values():
            value.set_expression()

    def set_spawned_genetics(self):
        mother = self.sim.family.immediate.mother.genetics
        father = self.sim.family.immediate.father.genetics
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
        trait_1 = self.choices[traits[0]]
        trait_2 = self.choices[traits[1]]

        if trait_1 == 'dominant' and trait_2 == 'dominant':
            self.expression = random.choice(self.pair)
        elif trait_1 == 'dominant' and trait_2 == 'recessive':
            self.expression = self.pair[0]
        elif trait_1 == 'recessive' and trait_2 == 'dominant':
            self.expression = self.pair[1]
        elif trait_1 == 'recessive' and trait_2 == 'recessive':
            self.expression = random.choice(self.pair)


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
