
from random import randint, sample
from typing import List

from pygame import Color

from core.agent import Agent
from core.ga import Chromosome, GA_World, Gene, Individual, gui_left_upper
from core.link import Link
from core.sim_engine import SimEngine
from core.world_patch_block import World


class Loop_Agent(Agent):

    @property
    def label(self):
        return str(self.x_y) if SimEngine.gui_get('show_positions') else None


class Loop_Link(Link):

    @property
    def label(self):
        """
        label is defined as a getter. No parentheses needed.
        Returns the length of the link.
        """
        return str(round(self.agent_1.distance_to(self.agent_2), 1))


# noinspection PyTypeChecker
class Loop_Individual(Individual):

    def __str__(self):
        return f'{self.fitness}: {[str(gene) for gene in self.chromosome]}'

    @staticmethod
    def add_gene_to_chromosome(orig_fitness: float, gene: Gene, chromosome: Chromosome) -> Chromosome:
        """ Add gene to the chromosome to minimize the resulting discrepancy. """
        (best_new_chrom, best_new_fitness, best_new_discr) = (None, None, None)
        len_chrom = len(chromosome)
        for i in sample(range(len_chrom), min(3, len_chrom)):
            (new_chrom, new_fitness, new_discr) = \
                Loop_Individual.trial_insertion(orig_fitness, chromosome, i, gene)
            if not best_new_discr or new_discr < best_new_discr:
                (best_new_chrom, best_new_fitness, best_new_discr) = (new_chrom, new_fitness, new_discr)
        return (best_new_chrom, best_new_fitness, best_new_discr)

    def compute_fitness(self) -> float:
        return Loop_Individual.compute_chromosome_fitness(self.chromosome)

    @staticmethod
    def compute_chromosome_fitness(chromosome) -> float:
        len_chrom = len(chromosome)
        # Recall that a chromosome is a tuple of Genes, each of which is a Pixel_xy.
        # We use mod (%) so that we include the distance from chromosome[len_chrom - 1] to chromosome[0]
        distances = [chromosome[i].distance_to(chromosome[(i+1) % len_chrom]) for i in range(len_chrom)]
        fitness = sum(distances)
        return fitness

    def mate_with(self, other):
        return self.cx_all_diff(self, other)

    def mutate(self) -> Individual:
        if randint(0, 100) <= SimEngine.gui_get('replace_gene'):
            (self.chromosome, self.fitness, _) = self.replace_gene_in_chromosome(self.fitness, self.chromosome)

        if randint(0, 100) <= SimEngine.gui_get('reverse_subseq'):
            self.chromosome = self.reverse_subseq(self.chromosome)
            self.fitness = self.compute_fitness()

        return self

    @staticmethod
    def replace_gene_in_chromosome(original_fitness: float, chromosome: Chromosome) -> Chromosome:
        (best_new_chrom, best_new_fitness, best_new_discr) = (None, None, None)
        len_chrom = len(chromosome)
        for i in sample(range(len_chrom), min(3, len_chrom)):
            gene_before = chromosome[i-1]
            removed_gene = chromosome[i]
            # i_p_1 is: (i+1) mod len_chrom
            i_p_1 = (i+1) % len_chrom
            gene_after = chromosome[i_p_1]
            fitness_after_removal = original_fitness - gene_before.distance_to(removed_gene) \
                                                     - removed_gene.distance_to(gene_after)  \
                                                     + gene_before.distance_to(gene_after)
            # Make the removed gene not available because we will add it in explicitly 3 lines down.
            available_genes = GA_World.agents - set(chromosome)
            sample_size = min(5 if len_chrom == 2 else 4, len(available_genes))
            # Include the removed gene as one of the ones to try.
            sampled_available_genes = sample(available_genes, sample_size) + [chromosome[i]]
            # Don't want i_p_1 here since if i is the the last position, i_p_1 is 0,
            # and we would then be adding the entire chromosome back in a second time.
            remaining_genes = chromosome[:i] + chromosome[i+1:]
            for gene in sampled_available_genes:
                (new_chrom, new_fitness, new_discr) = \
                    Loop_Individual.add_gene_to_chromosome(fitness_after_removal, gene, remaining_genes)
                if not best_new_discr or new_discr < best_new_discr:
                    (best_new_chrom, best_new_fitness, best_new_discr) = (new_chrom, new_fitness, new_discr)

        return (best_new_chrom, best_new_fitness, best_new_discr)

    @staticmethod
    def trial_insertion(current_fitness: float, chromosome: Chromosome, pos: int, new_gene: Gene):
        """
        Return what the discrepancy would be if gene were placed
        between positions pos and pos+1
        """
        gene_at_pos = chromosome[pos]
        # This works even if the chromosome has only one element. In that case,
        # both pos and (pos+1) % len(chromosome) will be 0. The gene at
        # these two positions will be chromosome[0]. In that case also,
        # current_fitness will be 0.
        gene_at_pos_plus_1 = chromosome[(pos+1) % len(chromosome)]
        new_fitness = current_fitness - gene_at_pos.distance_to(gene_at_pos_plus_1) \
                                      + gene_at_pos.distance_to(new_gene) \
                                      + new_gene.distance_to(gene_at_pos_plus_1)
        new_chrom = chromosome[:pos] + (new_gene, ) + chromosome[pos:]
        new_discr = abs(GA_World.fitness_target - new_fitness)
        return (new_chrom, new_fitness, new_discr)


class Loop_World(GA_World):
    
    def __init__(self, *arga, **kwargs):
        super().__init__(*arga, **kwargs)
        self.cycle_length = SimEngine.gui_get('cycle_length')


    def gen_individual(self):
        chromosome_list: List = sample(World.agents, self.cycle_length)
        individual = GA_World.individual_class(GA_World.seq_to_chromosome(chromosome_list))
        return individual

    def handle_event(self, event):
        if event == 'cycle_length':
            new_cycle_length = SimEngine.gui_get('cycle_length')
            if new_cycle_length != self.cycle_length:
                World.links = set()
                self.cycle_length = new_cycle_length
                self.update_cycle_lengths(new_cycle_length)
                self.resume_ga()
            return
        super().handle_event(event)

    def initial_individuals(self) -> List[Loop_Individual]:
        self.cycle_length = SimEngine.gui_get('cycle_length')
        individuals = [self.gen_individual() for _ in range(self.pop_size)]
        Individual.count = self.pop_size
        return individuals

    @staticmethod
    def link_best_chromosome(best_chromosome):
        for i in range(len(best_chromosome)):
            Loop_Link(best_chromosome[i], best_chromosome[(i+1) % len(best_chromosome)])

    def set_results(self):
        super().set_results()
        World.links = set()
        Loop_World.link_best_chromosome(self.best_ind.chromosome)

    def setup(self):
        GA_World.individual_class = Loop_Individual
        nbr_points = SimEngine.gui_get('nbr_points')
        self.create_random_agents(nbr_points, color=Color('white'), shape_name='node')

        self.mating_op = Individual.cx_all_diff
        super().setup()

    def update_cycle_lengths(self, cycle_length):
        for ind in self.individuals:
            chromosome = ind.chromosome
            if cycle_length < len(chromosome):
                ind.chromosome = chromosome[:cycle_length]
                ind.fitness = ind.compute_fitness()
            else:
                available_genes = GA_World.agents - set(ind.chromosome)
                new_genes = sample(available_genes, cycle_length - len(ind.chromosome))
                for gene in new_genes:
                    (ind.chromosome, ind.fitness, _) = \
                        Loop_Individual.add_gene_to_chromosome(ind.fitness, gene, ind.chromosome)


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
loop_gui_left_upper = gui_left_upper + [
                      [sg.Text('Prob replace elt', pad=((0, 5), (20, 0))),
                       sg.Slider(key='replace_gene', range=(0, 100), default_value=95,
                                 orientation='horizontal', size=(10, 20))
                       ],

                      [sg.Text('fitness_target', pad=(None, (20, 0))),
                       sg.Combo(key='fitness_target', default_value=1500, pad=((10, 0), (20, 0)), enable_events=True,
                                values=[0, 100, 500, 700, 900, 1200, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000])
                       ],

                      [sg.Text('Cycle length', pad=(None, (20, 0))),
                       sg.Slider(key='cycle_length', range=(2, 20), default_value=10, pad=((10, 0), (0, 0)),
                                 orientation='horizontal', size=(10, 20), enable_events=True)
                       ],

                      [sg.Checkbox('Show pixel positions', key='show_positions', default=False, pad=((0, 0), (10, 0)))]

    ]


if __name__ == "__main__":
    from core.agent import PyLogo
    # gui_left_upper is from core.ga
    PyLogo(Loop_World, 'Loops', loop_gui_left_upper, agent_class=Loop_Agent)
