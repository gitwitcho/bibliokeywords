import pandas as pd
import re

from config import *
from utilities import *

def generate_pandas_query_string(query_str: str) -> str:
    """
    Generates a query string that can be used by the pandas `query` function  based on 
    the input `query_str`.

    Pandas query strings can be cumbersome, for instance when string functions need to 
    be used on columns for partial/substring matches. You then need to use strings like
    `~(title.str.contains(r'(?=.*systemic risk)^(?=.*\\bequity\\b)', case = False, regex = True))`,
    which are unwieldy to create.

    This function allows queries to be written in a simplified form that covers most needs
    for column filtering in bibliographic `DataFrames`. Here are some query examples:
    
    - filter_query = "systemic in* title"
    - filter_query = "public in* title | extreme in* abstract"
    - filter_query = "013 in* lens_id"
    - filter_query = "'exists' in* abstract"
    - filter_query = "['modules', extreme] in* title"
    - filter_query = "extreme in* [title, abstract]"
    - filter_query = "[[systemic, 'equity']] in* title"
    - filter_query = "[[procyc, 'module']] in* [title, abstract]"
    - filter_query = "['modules', extreme] in* [title, abstract]"
    - filter_query = "~systemic in* title"
    - filter_query = "~(~public in* title | extreme in* abstract)"
    - filter_query = "~'exists' in* abstract"
    - filter_query = "~['modules', extreme] in* title"
    - filter_query = "~[[systemic risk, 'equity']] in* title"
    - filter_query = "(risk in* title) & (year == 2014)"

    The syntax rules are:

    - In addition to the pandas query() syntax, there is an additional binary operator `in*`.
    - The general syntax is `STRINGS in* COLUMNS`. This searches for (sub)strings in the
      text of the specified columns.
    - STRINGS:
        - If you put single or double quotes around a string, it will search for a full 
        word match. Otherwise it will search for partial matches.
        - If you surround multiple strings with single square brackets, it will search 
          for *any* matches ('or' operation). If you use double square brackets, it will
          search for *all* matches ('and' operation).
        - You can use the  ('not') operator inside the square brackets.
    - COLUMNS:
        - You can use single brackets to search in multiple columns for *any* matches ('or' 
          operation). So, `risk in* [title, abstract]` searches for the substring "risk" 
          in columns 'title' and 'abstract' and produces a match when it finds "risk" in 
          the value title or in the abstract.
        - Double brackets are not allowed for columns. You can achieve this by using `&``
          outside the `in*` operation.
        - The ~ ('not') operator is not allowed for columns.

    - Outside the `in*` binary operations, you can use the query() operators such as &, |, ~~
      in the normal way. See the last example above.

    Args:
        query_str: Input query string to be modified.

    Returns:
        Modified query string that the Pandas `query` function understands.

    Raises:
        ValueError: If the not operator '~' is used inside square brackets '[...]' or applied to the columns using 'in*'.

    """

    # Define the characters to split query string
    split_at = r"()|&~"
    pad = r"|&~"
    split_at_escaped = re.escape(split_at)

    if re.search(r'\[[^\]]*~[^\]]*\]', query_str):
        raise ValueError(f"The not operator '~' is not allowed inside square brackets '[...]'")
    
    if re.search(r'in\*\s*~', query_str):
        raise ValueError(f"Applying the not operator '~' on the columns is not allowed")
    
    # Split the query string into parts at the split_at characters
    pattern = fr"(?=[{split_at_escaped}])|(?<=[{split_at_escaped}])"
    query_parts = re.split(pattern, query_str)
    query_parts = [item.strip() for item in query_parts if item.strip()]

    modified_query_parts = []

    for query_part in query_parts:

        if 'in*' in query_part:

            # Split the 'in*' part into search string and column string
            in_parts = query_part.split('in*')
            search_str = in_parts[0].strip()
            col_str = in_parts[1].strip()                

            # Check if multiple columns are specified for searching
            match_col = re.match(r"^\[.*\]$", col_str)

            if match_col:
                matched_col_lst = [string.strip() for string in match_col.group().replace('[', '').replace(']', '').split(',')]
            else:
                matched_col_lst = [col_str]

            # Check for multiple search strings and the operation type ('and' or 'or')
            match_and = re.match(r"^\[\[.*\]\]$", search_str)
            match_or = re.match(r"^\[.*\]$", search_str)
            match = match_and if match_and else (match_or if match_or else False)

            if match:
                # Mutiple search terms
                matched_string = match.group().strip().replace('[', '').replace(']', '')
                search_str_lst = [string.strip() for string in matched_string.split(',')]
                first_col_str = True
                subst_query = ""

                for col_str in matched_col_lst: # one or several columns

                    # Build the query string for multiple search terms and one or multiple columns
                    subst_query += f"{' | ' if not first_col_str else ''}({col_str}.str.contains(r'"
                    first_search_str = True

                    for search_str in search_str_lst:
                        if re.match(r"^['\"].*['\"]$", search_str):
                            # Single search string with full word match enforced
                            search_str = search_str.strip().replace("'", "").replace('"', "")
                            if match_and:
                                subst_query += f"{'^' if not first_search_str else ''}(?=.*\\b{search_str}\\b)"
                            else:
                                subst_query += f"{'|' if not first_search_str else ''}\\b{search_str}\\b"
                            first_search_str = False
                        else:
                            # Single search string with partial word match allowed
                            search_str = search_str.strip()
                            if match_and:
                                subst_query += f"{'^' if not first_search_str else ''}(?=.*{search_str})"
                            else:
                                subst_query += f"{'|' if not first_search_str else ''}{search_str}"
                            first_search_str = False

                    subst_query += f"', case = False, regex = True))"
                    first_col_str = False

                modified_query_parts.append(subst_query)
            else:
                # Single search term
                first_col_str = True
                subst_query = ""

                for col_str in matched_col_lst: # one or several columns
 
                    # Build the query string for multiple search terms and one or multiple columns
                    subst_query += f"{' | ' if not first_col_str else '('}"

                    if re.match(r"^['\"].*['\"]$", search_str):
                        # Single search string with full word match enforced
                        search_str = search_str.strip().replace("'", "").replace('"', "")
                        subst_query += f"{col_str}.str.contains(r'\\b{search_str}\\b', case = False, regex = True)"
                    else:
                        # Single search string with partial word match allowed
                        subst_query += f"{col_str}.str.contains('{search_str}', case = False, regex = True)"
                    
                    first_col_str = False

                subst_query += f")"
                modified_query_parts.append(subst_query)
        else:
            modified_query_parts.append(query_part)

    # Add padding spaces around operators
    modified_query_parts = [s if s not in pad else f" {s} " for s in modified_query_parts]

    # Generate the query string from the individual parts
    modified_query = ''.join(modified_query_parts)

    return modified_query


def filter_biblio_df(biblio_df: pd.DataFrame, 
                     query_str: str
                     ) -> pd.DataFrame:
    """
    Filter biblio_df using a query string.

    Parameters:

    biblio_df (pd.DataFrame): 
        The DataFrame to filter.
    query_str (str): 
        The query string to use for filtering.

    Raises:
        ValueError: If the query string is not valid, or if any of the column names
        referred to in the query string do not exist in the DataFrame.

    Returns:

    pd.DataFrame: 
        The filtered DataFrame.
    """

    # Build pandas query string
    filter_pandas_query = generate_pandas_query_string(query_str = query_str)

    # Check that the query string is valid
    try:
        filtered_df = biblio_df.query(filter_pandas_query)
    except (SyntaxError, ValueError) as e:
        raise ValueError("Invalid query string") from e

    # Return the filtered DataFrame
    return filtered_df
