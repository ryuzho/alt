import torch
from torch.utils.data import Dataset
from pathlib import Path
import os
import pickle
import networkx as nx
from tqdm import tqdm

from data.data_utils import adj_to_graph, adj_to_adj_list
from data.tokens import tokenize

import sys

DATA_DIR = "resource"
    
class EgoDataset(Dataset):
    data_name = "GDSS_ego"
    raw_dir = f"{DATA_DIR}/GDSS_ego"
    is_mol = False
    def __init__(self, split, order='C-M', data_name = data_name):
        self.order = order
        with open(f'{self.raw_dir}.pkl', 'rb') as f:
            graphs = pickle.load(f)
        adjs = [nx.adjacency_matrix(graph) for graph in graphs]
        self.adj_list = [adj_to_adj_list(adj) for adj in adjs]

    def __len__(self):
        return len(self.adj_list)
    
    def __getitem__(self, idx: int):
        return torch.LongTensor(tokenize(self.adj_list[idx], self.data_name))
    
class ComDataset(EgoDataset):
    data_name = 'GDSS_com'
    raw_dir = f'{DATA_DIR}/GDSS_com'
    is_mol = False
    
class EnzDataset(EgoDataset):
    data_name = 'GDSS_enz'
    raw_dir = f'{DATA_DIR}/GDSS_enz'
    is_mol = False

class GridDataset(EgoDataset):
    data_name = 'GDSS_grid'
    raw_dir = f'{DATA_DIR}/GDSS_grid'
    is_mol = False
    
class GridSmallDataset(EgoDataset):
    data_name = 'grid_small'
    raw_dir = f'{DATA_DIR}/grid_small'
    is_mol = False

class QM9Dataset(EgoDataset):
    data_name = "qm9"
    raw_dir = f"{DATA_DIR}/qm9"
    is_mol = True
        
class ZINCDataset(EgoDataset):
    data_name = 'zinc'
    raw_dir = f'{DATA_DIR}/zinc'
    is_mol = True
    
class PlanarDataset(EgoDataset):
    data_name = 'planar'
    raw_dir = f'{DATA_DIR}/planar'
    is_mol = False
            
class SBMDataset(EgoDataset):
    data_name = 'sbm'
    raw_dir = f'{DATA_DIR}/sbm'
    is_mol = False

class ProteinsDataset(EgoDataset):
    data_name = 'proteins'
    raw_dir = f'{DATA_DIR}/proteins'
    is_mol = False