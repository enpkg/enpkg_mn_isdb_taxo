import os
import numpy as np
import pandas as pd
from matchms import calculate_scores
from matchms.similarity import ModifiedCosine
from matchms.networking import SimilarityNetwork
import networkx as nx

def connected_component_subgraphs(G):
            for c in nx.connected_components(G):
                yield G.subgraph(c)
                
def generate_mn(spectra_query, mn_graphml_ouput_path, mn_ci_ouput_path, msms_mz_tol, score_cutoff, top_n, max_links):
    """Generate a Molecular Network from MS/MS spectra using the modified cosine score

    Args:
        spectra_query (list): A list of matchms spectra objects
        mn_graphml_ouput_path (str): Path to export the .graphml MN file
        mn_ci_ouput_path (str): Path to export the .tsv MN metadata file
        msms_mz_tol (float): Tolerance in Da for MS/MS fragments matching
        score_cutoff (float): Minimal modified cosine score for edge creation
        top_n (int): Consider edge between spectrumA and spectrumB if score falls into top_n for spectrumA or spectrumB \
            (link_method="single"), or into top_n for spectrumA and spectrumB (link_method="mutual"). From those potential links, \
            only max_links will be kept, so top_n must be >= max_links.
        max_links (int): Maximum number of links to add per node.
    """    
    score = ModifiedCosine(tolerance=float(msms_mz_tol))
    scores = calculate_scores(spectra_query, spectra_query, score, is_symmetric=True)
    ms_network = SimilarityNetwork(identifier_key="scans", score_cutoff = score_cutoff, top_n = top_n, max_links = max_links, link_method = 'mutual')
    ms_network.create_network(scores)
    os.makedirs(os.path.dirname(mn_graphml_ouput_path), exist_ok=True)
    ms_network.export_to_graphml(mn_graphml_ouput_path)
    
    components = connected_component_subgraphs(ms_network.graph)
    comp_dict = {idx: comp.nodes() for idx, comp in enumerate(components)}
    attr = {n: {'component_id' : comp_id} for comp_id, nodes in comp_dict.items() for n in nodes}
    comp = pd.DataFrame.from_dict(attr, orient = 'index')
    comp.reset_index(inplace = True)
    comp.rename(columns={'index': 'feature_id'}, inplace=True)
    count = comp.groupby('component_id').count()
    count['new_ci'] = np.where(count['feature_id'] > 1, count.index, -1)
    new_ci = pd.Series(count.new_ci.values,index=count.index).to_dict()
    comp['component_id'] = comp['component_id'].map(new_ci)
    spectra_query_metadata_df = pd.DataFrame(s.metadata for s in spectra_query)
    comp = comp.merge(spectra_query_metadata_df[['feature_id', 'precursor_mz']], how='left')
    os.makedirs(os.path.dirname(mn_ci_ouput_path), exist_ok=True)
    comp.to_csv(mn_ci_ouput_path, sep = '\t', index = False)