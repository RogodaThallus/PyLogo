# Import the string constants you need (mainly keys) as well as classes and gui elements
from core.graph_framework import (CLUSTER_COEFF, Graph_Node, Graph_World, PATH_LENGTH, TBD, graph_left_upper,
                                  graph_right_upper, RANDOM, LINK_PROB, RING, STAR, WHEEL, SMALL_WORLD, PREF_ATTACHMENT,
                                  GRAPH_TYPE, CREATE_NODE)
from core.link import Link, link_exists
from core.sim_engine import SimEngine
import random
from random import choice

class Graph_Algorithms_World(Graph_World):



    # noinspection PyMethodMayBeStatic
    def average_path_length(self):
        return TBD

    # noinspection PyMethodMayBeStatic
    def clustering_coefficient(self):
        cluster_coefficient_list = []
        for node in self.agents:
            # find all neighbors of the node
            neighbors = []
            # print(node)
            for n_link in node.all_links():
                neighbors.append(n_link.other_side(node))
            # print("number of neighbors" + str(len(neighbors)))
            neighbors_set = set(neighbors)
            number_of_links = 0

            if len(neighbors) > 1:
                for current_node in neighbors:
                    other_nodes = set(neighbors) - {current_node}
                    # print("number of other neighbors" + str(len(other_nodes)))
                    for second_node in other_nodes:
                        if link_exists(current_node, second_node):
                            # print('link exists')
                            number_of_links += 1
                # print('+++++++++++')
                # print(number_of_links/2)
                # print(((len(neighbors) * (len(neighbors)- 1))/2))
                cluster_coefficient_list.append((number_of_links/2) / ((len(neighbors) * (len(neighbors)- 1))/2))

            # for current_node in neighbors:
            #     neighbors_set = neighbors_set - {current_node}
            #     if len(neighbors_set) > 1:
            #         for next_node in neighbors_set:
            #             if link_exists(current_node, next_node):
            #                 number_of_links += 1
            #         # cluster_coefficient_list.append((2 * (number_of_links)) / (len(neighbors) * (len(neighbors) - 1)))
            #
            #         print('links ' + str(number_of_links))
            #         # print('neighbors ' + len(neighbors))
            #         print('possible ' + str((len(neighbors_set) * (len(neighbors_set)- 1))/2))
            #         cluster_coefficient_list.append((number_of_links/2) / ((len(neighbors_set) * (len(neighbors_set)- 1))/2))

        average = sum(cluster_coefficient_list) / len(cluster_coefficient_list)
        # SimEngine.gui_set(CLUSTER_COEFF, value=average)
        # print(average)
        return average

    def compute_metrics(self):
        cluster_coefficient = self.clustering_coefficient()
        SimEngine.gui_set(CLUSTER_COEFF, value=cluster_coefficient)
        avg_path_length = self.average_path_length()
        SimEngine.gui_set(PATH_LENGTH, value=avg_path_length)

    # @staticmethod
    def link_nodes_for_graph(self, graph_type, nbr_nodes, ring_node_list):
        """
        Link the nodes to create the requested graph.

        Args:
            graph_type: The name of the graph type.
            nbr_nodes: The total number of nodes the user requested.
                       (Will be > 0 or this method won't be called.)
            ring_node_list: The nodes that have been arranged in a ring.
                            Will contain either:
                            nbr_nodes - 1 if graph type is STAR or WHEEL
                            or nbr_nodes otherwise

        Returns: None

        Overrides this function from graph_framework.
        """
        if graph_type is RANDOM:
            link_chance = SimEngine.gui_get(LINK_PROB) / 100.0
            not_checked_nodes = set(ring_node_list)
            for first_node in ring_node_list:
                not_checked_nodes = not_checked_nodes - {first_node}
                for second_node in not_checked_nodes:
                    if random.random() < link_chance and not link_exists(first_node, second_node):
                        Link(first_node, second_node)

        type = [RING, STAR, WHEEL]
        if graph_type in type:
            for i in range(len(ring_node_list) - 1):
                Link(ring_node_list[i], ring_node_list[i + 1])
            Link(ring_node_list[-1], ring_node_list[0])

            if graph_type is STAR or graph_type is WHEEL:
                # implement shape if asked, needs to be a non static method to implement
                # center_node = self.agent_class(shape_name=SimEngine.gui_get(SHAPE))
                center_node = self.agent_class()
                for node in ring_node_list:
                    Link(center_node, node)

        if graph_type is SMALL_WORLD:
            # neighborhood_size = SimEngine.gui_get(NEIGHBORHOOD_SIZE)
            # for i, node in ring_node_list:
            #     for j in range(1, neighborhood_size + 1):
            #         if not link_exists(node, ring_node_list[(i + j]):
            #             Link(node, ring_node_list[i + j])

            for i in range(len(ring_node_list)):
                for j in range(1, int(SimEngine.gui_get(NEIGHBORHOOD_SIZE)) + 1):
                    # makes sure to loop back if over list size
                    # only taking into account undirected links
                    # make sure to not connect nodes to themselves
                    if not link_exists(ring_node_list[i], ring_node_list[(i + j) % len(ring_node_list)]) and \
                            ring_node_list[i] is not ring_node_list[(i + j) % len(ring_node_list)]:
                        Link(ring_node_list[i], ring_node_list[(i + j) % len(ring_node_list)])

            # rewire chance for each link
            # get rewire chance
            rewire_chance = SimEngine.gui_get(LINK_PROB) / 100.0

            old_links = []
            # deep copy the links
            for l in self.links:
                old_links.append(l)
            for l in old_links:
                # generate random number to see if it gets rewired
                if random.random() < rewire_chance:

                    # pick the first node in the link
                    # find all the nodes neigbors
                    # cosider yourself as a neighbor
                    neighbors = [l.agent_1]
                    for n_link in l.agent_1.all_links():
                        neighbors.append(n_link.other_side(l.agent_1))

                    # check to see if there exists any agent not considered a neighbor
                    if len(neighbors) < len(self.agents):
                        new_neighbor = choice(list(self.agents - set(neighbors)))
                        # print(new_neighbor)
                        # remove the current link
                        self.links.remove(l)
                        # create the new link add it to the list of links to ignore
                        Link(l.agent_1, new_neighbor)

        ###preferential attachment written by Ricardo
        if graph_type is PREF_ATTACHMENT:
            #make a link first
            Link(ring_node_list[0], ring_node_list[1])
            for node in ring_node_list[2:]:
                self.pref_attachment(node)

        ###preferential attchment written by Samantha
        # if graph_type is PREF_ATTACHMENT:
        #     Link(ring_node_list[0], ring_node_list[1])
        #     for i in ring_node_list[2:]:
        #         other_agents = [a for a in ring_node_list if a is not i]
        #         linked_agent_pairs = [(l.agent_1, l.agent_2) for l in Graph_Algorithms_World.links if
        #                               not l.includes(i)]
        #         linked_agents = [a for pair in linked_agent_pairs for a in pair]
        #         if not Graph_Algorithms_World.links:
        #             Link(i, choice(linked_agents))
        #         else:
        #             Link(i, choice(other_agents))

    def pref_attachment(self, node):
        #get all nodes that are currently in a link
        nodes_linked = set()
        for link in self.links:
            nodes_linked.add(link.agent_1)
            nodes_linked.add(link.agent_2)

        probabilities = []
        for n in nodes_linked:
            probabilities.append((n, len(n.lnk_nbrs())))

        #attached to a selected weighted node
        Link(node, self.weighted_random(probabilities))


    def weighted_random(self, options):
        weighted_list = []
        #generate a list that emulates the probability weight
        #ex [0,0,0,1,1,2,2,2,2,3,3]
        for i, pair in enumerate(options):
            for _ in range(pair[1]):
                weighted_list.append(i)
        #returns the selected node to attach to
        return options[choice(weighted_list)][0]

    def handle_event(self, event):
        """
        This is called when a GUI widget is changed and the change isn't handled by the system.
        The key of the widget that changed is in event.
        """
        # Handle color change requests.
        if event == CREATE_NODE and SimEngine.gui_get(GRAPH_TYPE) in PREF_ATTACHMENT:
            new_node = self.agent_class()
            self.pref_attachment(new_node)
        else:
            super().handle_event(event)


#=====================================================================
#modify the gui to add a neighborhood slider
import PySimpleGUI as sg
NEIGHBORHOOD_SIZE = 'neighborhood size'
graph_left_upper.insert(4, [sg.Text('Neighborhood Size'),
                  sg.Slider(key=NEIGHBORHOOD_SIZE, resolution=1, default_value=1, orientation='horizontal', range=(0,20))])

if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Graph_Algorithms_World, 'Network test', gui_left_upper=graph_left_upper,
           gui_right_upper=graph_right_upper, agent_class=Graph_Node,
           clear=True, bounce=True, auto_setup=False)
