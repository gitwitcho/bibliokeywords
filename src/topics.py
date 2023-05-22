import pandas as pd
import time

from config import *
from typing import Tuple, Optional, List

from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer

# TODO:
# Add the stitching. Currently the merged_df doesn't actually include the merged dataframe

def generate_bert_topics(biblio_df_: pd.DataFrame,
                         input_col: Optional[str] = None,
                         n_gram_range: Tuple = (1,1),
                         sample_size: Optional[int] = None,
                         verbose: bool = False,
                         calc_probs: bool = False,
                         remove_stopwords: bool = False
                         ) -> Tuple[BERTopic, pd.DataFrame]:
    """
    Generate BERTopic topics from the titles or abstracts of a biblio_df.

    Parameters:

    biblio_df (pd.DataFrame): 
        The pandas DataFrame containing the text.
    input_col (Optional[str]): 
        The name of the column containing the text (default: None, uses first/only column).
    n_gram_range (Tuple): 
        The range of n-grams to use for topic modeling (default: (1,1)).
    sample_size (Optional[int]): 
        The number of texts that are randomly sampled for topic modeling (default: None, uses all texts).
    verbose (bool): 
        Whether to print verbose output (default: False).
    calc_probs (bool): 
        Whether to calculate topic probabilities (default: False).
    remove_stopwords (bool)
        Whether to remove the English stopwords from the topics (default: False).

    Returns:

    BERTopic: 
        The fitted BERTopic model.

    docs:
        The list of texts used to fit the BERTopic model.
    """

    biblio_df = biblio_df_.copy()
    
    # If input_col is not provided, use the first/only column of biblio_df
    if input_col is None:
        input_col = str(biblio_df.columns[0])
        logger.info(f"Using column {input_col} as the texts for BERTopic")
    else:
        # Check that input_col is a column in biblio_df
        if input_col not in biblio_df.columns:
            raise ValueError(f"{input_col} is not a column in biblio_df")
        
    # Check that the column input_col contains text data
    if not biblio_df[input_col].dropna().apply(lambda x: isinstance(x, str)).all():
        raise ValueError(f"The '{input_col}' column must contain text data")

    # Remove rows where input_col is NaN, empty, or an empty string
    biblio_df = biblio_df.dropna(subset = [input_col])
    biblio_df = biblio_df[biblio_df[input_col].apply(lambda x: (x != '') and not x.isspace())]

    # Sample from the document if sample_size is provided
    if sample_size:
        biblio_df = biblio_df.sample(n = sample_size)

    biblio_df.reset_index(drop = True, inplace = True)

    # Create a list of the titles
    docs = biblio_df[input_col].to_list()

    # Set the timer
    start_time = time.time()

    # Create topics
    model = BERTopic(language = "english", 
                     n_gram_range = n_gram_range, 
                     verbose = verbose, 
                     calculate_probabilities = calc_probs)
    topics, probs = model.fit_transform(docs)

    # Remove stopwords
    if remove_stopwords:
        vectorizer_model = CountVectorizer(stop_words = "english")
        model.update_topics(docs, vectorizer_model = vectorizer_model)

    doc_info_df = model.get_document_info(docs)

    # Reset the indices of both dataframes and then merge horizontally
    # biblio_stripped_se.reset_index(drop = True, inplace = True)
    # doc_info_df.reset_index(drop = True, inplace = True)
    merged_df = pd.concat([biblio_df, doc_info_df], axis = 1)

    # Calculate the time needed to dit the BERTopic model
    logger.info("--- %s seconds ---" % (time.time() - start_time))

    return model, merged_df


def create_topic_summary_df(topic_info_df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a topic summary dataframe.
    
    The dataframe groups the input dataframe `doc_info_df` by the `tp_num` and 
    `tp_names` columns and counts the number of articles per topic. The resulting 
    dataframe has columns for the number of articles (`n_articles`), the topic 
    number (`tp_num`), and the topic name (`tp_names`).

    Parameters:
    doc_info_df : pd.DataFrame
        The pandas DataFrame containing the document information.

    Returns:
    pd.DataFrame
        The pandas DataFrame containing the summary information grouped by topic.
    """

    # Group by tp_num and tp_names to count the number of titles per topic
    counts = topic_info_df.groupby(['tp_num', 'tp_name', 'top_n_words'])['title'].count().reset_index()
    counts.rename(columns={'title': 'n_articles'}, inplace = True)

    # Select only the relevant columns and drop any duplicates
    topic_summary_info_df = counts[['n_articles', 'tp_num', 'tp_name', 'top_n_words']] \
                                .drop_duplicates().sort_values('n_articles', ascending=False)
    
    return topic_summary_info_df