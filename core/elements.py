import json
from signal import signal

import matplotlib.pyplot as plt
from networkx.classes import nodes
from core import parameters

#from core.utils import example_func

class Signal_information(object):
    def __init__(self, signal_power:float, path):
        self._signal_power= signal_power
        self._noise_power = 0.0
        self._latency = 0.0
        self._path = path[:]

    @property
    def signal_power(self):
        return self._signal_power


    def update_signal_power(self,increment):
        self._signal_power += increment

    @property
    def noise_power(self):
        return self._noise_power

    @noise_power.setter
    def noise_power(self, new_noise):
        self._noise_power = new_noise

    def update_noise_power(self, increment):
        self._noise_power += increment

    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, new_lat):
        self._latency = new_lat

    def update_latency(self, inc):
        self._latency += inc

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path):
        self._path = new_path[:]

    def update_path(self):
        if self._path:
            self._path.pop(0)



class Node(object):
    def __init__(self, input_dict):
        self._label = input_dict['label']
        self._position = tuple(input_dict['position'])
        self._connected_nodes = input_dict['connected_nodes']
        self._successive = dict()

    @property
    def label(self):
        return self._label

    @property
    def position(self):
        return self._position

    @property
    def connected_nodes(self):
        return self._connected_nodes

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, new_successive):
        self._successive = new_successive

    def propagate(self, signal_information):
        signal_information.update_path()
        if signal_information.path:
            next_node = signal_information.path[0]
            for line_label, line in self._successive.items():
                if line_label.find(next_node)!=-1:
                    line.propagate(signal_information)


class Line(object):
    def __init__(self, label, length:float):
        self._label = label
        self._length = length
        self._successive = {}

    @property
    def label(self):
        return self._label

    @property
    def length(self):
        return self._length

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, new_successive):
        self._successive = new_successive

    def latency_generation(self,signal_information):
        latency_generated = self._length / (parameters.c * 2 / 3)
        signal_information.update_latency(latency_generated)

    def noise_generation(self, signal_information):
        noise_generated = 1e-9 * signal_information.signal_power * self._length
        signal_information.update_noise_power(noise_generated)

    def propagate(self, signal_information):
        self.latency_generation(signal_information)
        self.noise_generation(signal_information)
        self._successive[signal_information.path[0]].propagate(signal_information)


class Network(object):
    def __init__(self, json_file_path):
        self._nodes = {}
        self._lines = {}
        with open(json_file_path,"r") as f:
            nodes_data = json.load(f)
        for node_label, node_info in nodes_data.items():
            node_info['label'] = node_label
            node = Node(node_info)
            self._nodes[node.label] = node
        for node_label1, node1 in self._nodes.items():
            for node_label2 in node1.connected_nodes:
                line_label = node_label1+node_label2
                line_length = self._calculate_distance(node1.position, self._nodes[node_label2].position)
                line = Line(line_label, line_length)
                self._lines[line.label] = line
            # nodes_to_pass.append(node_label1) # save the nodes that all the links to them are calculated to surpass them.


    def _calculate_distance(self, pos1, pos2):
        return ((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2) ** 0.5

    @property
    def nodes(self):
        return self._nodes

    @property
    def lines(self):
        return self._lines

    def draw(self):
        nodes_to_pass=[]
        for node_label, node in self._nodes.items():
            for next_node_label in node.connected_nodes:
                if next_node_label in nodes_to_pass:
                    continue    #to avoid drawing repetitive lines
                node2 = self._nodes[next_node_label]
                plt.plot([node.position[0],node2.position[0]],[node.position[1],node2.position[1]],'b')
            nodes_to_pass.append(node_label)
            plt.plot(node.position[0],node.position[1],'go', markersize=15)
            plt.text(node.position[0],node.position[1],node_label)
        plt.title('Network')
        plt.show()


    # find_paths: given two node labels, returns all paths that connect the 2 nodes
    # as a list of node labels. Admissible path only if cross any node at most once
    def find_paths(self, label1, label2):
        possible_paths = []
        stack = [[label1]]
        while stack:
            path = stack.pop()
            if path[-1]==label2:    # Current node
                possible_paths.append(path)
            else:
                for next_node in self._nodes[path[-1]].connected_nodes:
                    if next_node not in path:
                        new_path = path.copy()
                        new_path.append(next_node)
                        stack.append(new_path)
        return possible_paths

    # connect function set the successive attributes of all NEs as dicts
    # each node must have dict of lines and viceversa
    def connect(self):
        for node1_label, node in self._nodes.items():
            for next_node in node.connected_nodes:
                line_label = node1_label + next_node
                node.successive[line_label] = self._lines[line_label]
                self._lines[line_label].successive[next_node] = self._nodes[next_node]

    # propagate signal_information through path specified in it
    # and returns the modified spectral information
    def propagate(self, signal_information):
        first_node = signal_information.path[0]
        self._nodes[first_node].propagate(signal_information)
