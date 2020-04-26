import random

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
               'lightblue': 0.15,
               'green': 0.1, 
               'grey': 0.05,
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
