
from __future__ import annotations

from pygame.color import Color

import core.gui as gui
from core.agent import Agent
from core.pairs import XY
from core.world_patch_block import World


def hash_object(agent_1, agent_2, directed=False):
    return (agent_1, agent_2) if directed else frozenset({agent_1, agent_2})


def link_exists(agent_1, agent_2, directed=False):
    """
    Determine whether a directed/undirected link between agent_1 and agent_2 already exists in World.links.

    The strategy is to create a hash_object of the possible link and then see if any existing link has
    the same hash_object.
    """
    hash_obj = hash_object(agent_1, agent_2, directed)
    links = [lnk for lnk in World.links if lnk.hash_object == hash_obj]
    return links[0] if links else None


class Link:

    def __init__(self, agent_1: Agent, agent_2: Agent, directed: bool = False,
                 color: Color = Color('white'), width: int = 1):
        if None in {agent_1, agent_2}:
            raise Exception(f"Can't link to None: agent_1: {agent_1}, agent_2: {agent_2}.")
        self.agent_1: Agent = agent_1
        self.agent_2: Agent = agent_2
        self.both_sides = {agent_1, agent_2}
        if len(self.both_sides) != 2:
            raise Exception(f"Can't have a link from a node to itself: {agent_1} == {agent_2}.")
        self.directed = directed
        # Create a hash_object to be used by both __eq__ and __hash__.
        self.hash_object = hash_object(agent_1, agent_2, directed)
        self.default_color = color
        self.color = color
        self.width = width
        World.links.add(self)

    def __eq__(self, other: Link):
        """
        It's conceivable (although extremely unlikely) that hash(self.hash_object) == hash(other.hash_object) even
        though self.hash_object != other.hash_object.
        Python requires that if two objects compare as __eq__ their hash values must be the same.
        Python doesn't require that if two objects have the same hash values, they must compare as __eq__.
        """
        return self.hash_object == other.hash_object

    def __hash__(self):
        return hash(self.hash_object)

    def __str__(self):
        return f'{self.agent_1} {"-->" if self.directed else "<-->"} {self.agent_2}'

    def draw(self):
        # gui.draw_line(self.agent_1.rect.center, self.agent_2.rect.center, line_color=self.color, width=self.width)
        gui.draw_line(self.agent_1.center_pixel, self.agent_2.center_pixel, line_color=self.color, width=self.width)
        if (my_label := self.label) is not None:
            # Pass the label to avoid computing it twice.
            self.draw_label(my_label)

    def draw_label(self, my_label):
        offset = int(0.5*gui.PATCH_SIZE)
        obj_center = XY(((3*self.agent_1.x + self.agent_2.x)/4, (3*self.agent_1.y + self.agent_2.y)/4))
        text_center = (obj_center.x + offset, obj_center.y + offset)
        line_color = self.color
        gui.draw_label(my_label, text_center, obj_center, line_color)

    def includes(self, agent):
        return agent in (self.agent_1, self.agent_2)

    def is_linked_with(self, other, directed=False):
        return link_exists(self, other, directed)

    @property
    def label(self):
        return None

    def siblings(self):
        """
        Return: A tuple with the lnk_nbrs on each side, smaller side first
        """
        sibs = (self.agent_1.lnk_nbrs(), self.agent_2.lnk_nbrs())
        return sibs if len(sibs[0]) < len(sibs[1]) else (sibs[1], sibs[0])

    def other_side(self, node):
        return (self.both_sides - {node}).pop()

    def set_color(self, color):
        self.color = color

    def set_width(self, width):
        self.width = width
