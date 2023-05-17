import sys

import matplotlib.pyplot as plt

from pathlib import Path
from utilities import *
from config import *
from transform import *
from search_terms import *

data_project = 'PINNs'

cols= ['title', 'abstract', 'kws']
full_matches = ['fem', 'ann', 'gan']
search_terms = '''
    ( ( ( TITLE( simulation  OR  "numerical method"  OR  "numerical model"  OR  "navier stokes"  OR  "system dynamics"  OR  "numerical experiment"  OR  fem  OR  turbulence  OR  "numerical analysis"  OR  "multiagent"  OR  "multi-agent"  OR  "surrogate"  OR  pde  OR  "partial differential equation"  OR  "computational fluid"  OR  "computational model*"  OR  "computational method*"  OR  "computational framework"  OR  "computational approach"  OR  "computational experiment"  OR  "computational mechanic*"  OR  "computational technique"  OR  "computational study"  OR  "computational analysis"  OR  "computational science"  OR  "computational electro*"  OR  "computational material"  OR  "computational biomech*"  OR  "computational physics"  OR  "computational research"  OR  "computational engineering"  OR  "finite element"  OR  "finite difference"  OR  "finite volume"  OR  "boundary element method"  OR  "discrete element method"  OR  "meshfree method"  OR  "mesh free method"  OR  "meshless method"  OR  "particle hydrodynamics"  OR  "dissipative particle dynamics"  OR  "particle method" ) OR KEY( simulation  OR  "numerical method"  OR  "numerical model"  OR  "navier stokes"  OR  "system dynamics"  OR  "numerical experiment"  OR  fem  OR  turbulence  OR  "numerical analysis"  OR  "multiagent"  OR  "multi-agent"  OR  "surrogate"  OR  pde  OR  "partial differential equation"  OR  "computational fluid"  OR  "computational model*"  OR  "computational method*"  OR  "computational framework"  OR  "computational approach"  OR  "computational experiment"  OR  "computational mechanic*"  OR  "computational technique"  OR  "computational study"  OR  "computational analysis"  OR  "computational science"  OR  "computational electro*"  OR  "computational material"  OR  "computational biomech*"  OR  "computational physics"  OR  "computational research"  OR  "computational engineering"  OR  "finite element"  OR  "finite difference"  OR  "finite volume"  OR  "boundary element method"  OR  "discrete element method"  OR  "meshfree method"  OR  "mesh free method"  OR  "meshless method"  OR  "particle hydrodynamics"  OR  "dissipative particle dynamics"  OR  "particle method" ) ) AND (TITLE( "neural network" OR "reinforcement learning" OR "machine learning" OR "deep learning" OR "transformer model" OR "BERT" OR "GPT" OR "adversarial network" OR "gan" OR "natural language processing" OR "word embedding" OR "document embedding" OR "sentence embedding" OR "transfer learning" OR "ensemble learning" OR "learning algorithm" OR "genetic algorithm" OR "evolutionary algorithm" OR "support vector machine" OR "decision tree" OR "bayesian network" OR "q-learning" OR "long short-term memory" OR "classification model" OR "classification algorithm" OR "ann" OR "clustering algorithm" OR "feature extraction" OR "anomaly detection" OR "inference engine" OR "k nearest neighbour" OR "cluster analysis" OR "linear regression" OR "hidden markov" OR perceptron OR "random forest" OR "support vector regression" OR cnn OR rnn OR "predictive model" OR "logistic regression" OR "statistical learning" OR lstm ) OR KEY( "neural network" OR "reinforcement learning" OR "machine learning" OR "deep learning" OR "transformer model" OR "BERT" OR "GPT" OR "adversarial network" OR "gan" OR "natural language processing" OR "word embedding" OR "document embedding" OR "sentence embedding" OR "transfer learning" OR "ensemble learning" OR "learning algorithm" OR "genetic algorithm" OR "evolutionary algorithm" OR "support vector machine" OR "decision tree" OR "bayesian network" OR "q-learning" OR "long short-term memory" OR "classification model" OR "classification algorithm" OR "ann" OR "clustering algorithm" OR "feature extraction" OR "anomaly detection" OR "inference engine" OR "k nearest neighbour" OR "cluster analysis" OR "linear regression" OR "hidden markov" OR perceptron OR "random forest" OR "support vector regression" OR cnn OR rnn OR "predictive model" OR "logistic regression" OR "statistical learning" OR lstm ) ) ) OR TITLE-ABS-KEY( "neural differential" OR "neural ordinary" OR "neural ODE" OR "data-driven model" OR "physics-informed" OR "physics-constrained" OR "physics-embedded" OR "physics-inspired" OR "physics-aware" OR "physics-enhanced" OR "hidden physics" OR "differentiable physics" OR "scientific machine learning" OR "physics machine learning" ) )
'''

root_dir = Path(__file__).resolve().parents[1]

biblio_df = read_and_merge_csv_files(project = data_project, 
                                    input_dir = 'raw/scopus',
                                    biblio_type = BiblioSource.SCOPUS,
                                    n_rows = 10)

biblio_df = modify_cols_biblio_df(biblio_df = biblio_df, reshape_base = Reshape.SCOPUS_COMPACT)
biblio_df = normalise_biblio_entities(biblio_df = biblio_df)
biblio_df = clean_biblio_df(biblio_df = biblio_df)

biblio_df = add_search_term_matches_as_col(biblio_df = biblio_df,
                                       cols = cols,
                                       search_terms = search_terms,
                                       full_matches = full_matches,
                                       singularise = True,
                                       expand_synonyms = False,
                                       stem = False)

print(biblio_df[['title', 'abstract', 'kws', 'search_terms']])
