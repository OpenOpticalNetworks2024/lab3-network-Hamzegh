import json
import math

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from core.elements import Network, Signal_information

# Exercise Lab3: Network

ROOT = Path(__file__).parent.parent
INPUT_FOLDER = ROOT / 'resources'
file_input = INPUT_FOLDER / 'nodes.json'


# Load the Network from the JSON file, connect nodes and lines in Network.
# Then propagate a Signal Information object of 1mW in the network and save the results in a dataframe.
# Convert this dataframe in a csv file called 'weighted_path' and finally plot the network.
# Follow all the instructions in README.md file

def main():
    net = Network(file_input)
    #print(net.nodes)
    #print(net.lines)
    #net.draw()
    net.connect()
    all_possible_paths = []
    all_possible_paths_string = []
    acc_latency =[]
    acc_noise = []
    SNR = []
    signal_power = 1e-3
    # Find all possible paths
    for node1_label, node1 in net.nodes.items():
        for node2_label, node2 in net.nodes.items():
            if node1_label == node2_label:
                continue
            paths = (net.find_paths(node1_label,node2_label))
            path_string = ['->'.join(i) for i in paths]
            all_possible_paths.extend(paths)
            all_possible_paths_string.extend(path_string)
            for path in paths:
                signal = Signal_information(signal_power,path.copy())
                net.propagate(signal)
                acc_latency.append(signal.latency)
                acc_noise.append(signal.noise_power)
                SNR.append(10*math.log10(signal.signal_power/signal.noise_power))
    data = pd.DataFrame({'Path':all_possible_paths_string,'Accumulated Latency':acc_latency,
                         'Accumulated Noise':acc_noise, 'SNR':SNR})
    data.to_csv(INPUT_FOLDER/'weighted_path.csv',index=False)
    net.draw()
    #print(paths)
    print(all_possible_paths)
            #for path in possible_paths:


if __name__ == '__main__':
    main()
