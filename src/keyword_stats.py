import pandas as pd

from typing import List, Dict
from transform import *

def generate_keyword_stats(biblio_df_: pd.DataFrame,
                           cols: List,
                           assoc_filter: Optional[str],
                           singularise: bool = False,
                           stem: bool = False
                           ) -> Dict:
    
    if any(string not in biblio_df_.columns for string in cols):
        raise ValueError(f"Some columns in {cols} are not in biblio_df")
    
    kws_df = biblio_df_[cols].copy()
    kws_count_df_dict = {}
    kws_assoc_count_df_dict = {}
    
    for col in cols:

        # Create a single keyword list by exploding the table
        # kws_col_df = kws_df.apply(lambda x: x.str.split(',')).explode(col).reset_index(drop = True)
        kws_col_df = kws_df.fillna('').apply(lambda x: x.str.split(';')).explode(col).reset_index(drop=True)
        kws_col_df = kws_col_df[kws_col_df[col] != '']
        kws_col_df[col] = kws_col_df[col].str.replace('-', ' ')


        # Create a count table for the keywords
        # kw_count_df = pd.DataFrame(kws_col_df[col].value_counts()).reset_index(drop = True)
        kw_count_df = kws_col_df[col].value_counts().reset_index()
        kw_count_df.columns = ['kw', 'count']
        kw_count_df = kw_count_df.sort_values(by = ['count', 'kw'], ascending = [False, True]).reset_index(drop = True)
        # kw_count_df.drop(['index'], axis = 1, inplace = True)

        kws_count_df_dict[col] = kw_count_df

        if assoc_filter:
            if not '{}' in assoc_filter:
                raise ValueError(f"The assoc_filter needs to include place holders '{{}}' for the keyword column")
            
            kw_assoc_count_df = kw_count_df.copy()
            kw_assoc_count_df = filter_biblio_df(kw_count_df,
                                                 assoc_filter.format('kw'))
            kws_count_df_dict[col + '_assoc'] = kw_count_df

    return kws_count_df_dict
