import nltk

from mylogger import MyLogger
from enum import Enum

verbose = True

project_root_markers = ['requirements.txt', '.gitignore', 'README.md']

data_root_dir = 'data'
model_root_dir = 'models'
"""
    str (int): Module level variable documented inline.
"""
# TODO:
# - Automatically test for uniqueness of values in the reshape structures below

class BiblioSource(Enum):
    SCOPUS = 'scopus'
    LENS = 'lens'
    DIMS = 'dims'
    BIBLIO = 'biblio'
    UNDEFINED = 'undefined'

    @classmethod
    def is_valid_value(cls, value):
        return value in [member.value for member in cls if member != cls.UNDEFINED]
    
    @classmethod
    def valid_values_str(cls):
        s = '[' + ', '.join([member.value for member in cls if member != cls.UNDEFINED]) + ']'
        return s

class Reshape(Enum):
    SCOPUS_ALL = 1
    SCOPUS_FULL = 2
    SCOPUS_COMPACT = 3
    LENS_ALL = 4
    LENS_FULL = 5
    LENS_COMPACT = 6
    DIMS_ALL = 7
    DIMS_FULL = 8
    DIMS_COMPACT = 9

reshape_struc_scopus_all = {'Authors': 'authors', 
                             'Author(s) ID': 'author_ids', 
                             'Title': 'title', 
                             'Year': 'year', 
                             'Source title': 'source', 
                             'Volume': 'volume',
                             'Issue': 'issue', 
                             'Art. No.': 'art_no', 
                             'Page start': 'page_start', 
                             'Page end': 'page_end', 
                             'Page count': 'page_count', 
                             'Cited by': 'n_cited',
                             'DOI': 'doi', 
                             'Link': 'link', 
                             'Affiliations': 'affils', 
                             'Authors with affiliations': 'auth_affils', 
                             'Abstract': 'abstract', 
                             'Author Keywords': 'kws_author', 
                             'Index Keywords': 'kws_index', 
                             'Correspondence Address': 'address',
                             'Editors': 'editors', 
                             'Publisher': 'publisher', 
                             'ISSN': 'issn', 
                             'ISBN': 'isbn', 
                             'CODEN': 'coden', 
                             'PubMed ID': 'pubmed_id',
                             'Language of Original Document': 'lang',
                             'Abbreviated Source Title': 'source_abbrev',
                             'Document Type': 'doc_type',
                             'Publication Stage': 'pub_stage',
                             'Open Access': 'open',
                             'Source':'scopus_source',
                             'EID':'scopus_id',
                             'bib_src': 'bib_src'}
reshape_struc_scopus_full = {'Authors': 'authors', 
                             'Author(s) ID': 'author_ids', 
                             'Title': 'title', 
                             'Year': 'year', 
                             'Source title': 'source', 
                             'Cited by': 'n_cited',
                             'DOI': 'doi', 
                             'Link': 'link', 
                             'Affiliations': 'affils', 
                             'Authors with affiliations': 'auth_affils', 
                             'Abstract': 'abstract', 
                             'Author Keywords': 'kws_author', 
                             'Index Keywords': 'kws_index', 
                             'ISSN': 'issn', 
                             'ISBN': 'isbn', 
                             'CODEN': 'coden', 
                             'PubMed ID': 'pubmed_id',
                             'Language of Original Document': 'lang',
                             'Abbreviated Source Title': 'source_abbrev',
                             'Document Type': 'doc_type',
                             'Open Access': 'open',
                             'EID':'scopus_id',
                             'bib_src': 'bib_src'}

reshape_struc_scopus_compact = {'Authors': 'authors', 
                                'Author(s) ID': 'author_ids', 
                                'Title': 'title', 
                                'Year': 'year', 
                                'Source title': 'source', 
                                'Cited by': 'n_cited',
                                'DOI': 'doi', 
                                'Abstract': 'abstract', 
                                'Author Keywords': 'kws_author', 
                                'Index Keywords': 'kws_index', 
                                'Language of Original Document': 'lang',
                                'Abbreviated Source Title': 'source_abbrev',
                                'Document Type': 'doc_type',
                                'EID':'scopus_id',
                                'bib_src': 'bib_src'}

reshape_struc_lens_all = {'Lens ID': 'lens_id', 
                          'Title': 'title', 
                          'Date Published': 'pub_date', 
                          'Publication Year': 'year',
                          'Publication Type': 'pub_type', 
                          'Source Title': 'source', 
                          'ISSNs': 'issns', 
                          'Publisher': 'publisher',
                          'Source Country': 'source_country', 
                          'Author/s': 'authors', 
                          'Abstract': 'abstract', 
                          'Volume': 'volume', 
                          'Issue Number': 'issue',
                          'Start Page':'page_start',
                          'End Page':'page_end',
                          'Fields of Study':'fos',
                          'Keywords':'kws_lens',
                          'MeSH Terms':'mesh',
                          'Chemicals':'chemicals',
                          'Funding':'funding',
                          'Source URLs':'source_urls',
                          'External URL':'ext_url',
                          'PMID':'pmid',
                          'DOI':'doi',
                          'Microsoft Academic ID':'ms_acad_id',
                          'PMCID':'pmcid',
                          'Citing Patents Count':'n_patent_cite',
                          'References':'references',
                          'Citing Works Count':'n_cited',
                          'Is Open Access':'open',
                          'Open Access License':'open_license',
                          'Open Access Colour':'open_colour',
                          'bib_src': 'bib_src'}

reshape_struc_lens_full = {'Lens ID': 'lens_id', 
                          'Title': 'title', 
                          'Date Published': 'pub_date', 
                          'Publication Year': 'year',
                          'Publication Type': 'pub_type', 
                          'Source Title': 'source', 
                          'ISSNs': 'issns', 
                          'Author/s': 'authors', 
                          'Abstract': 'abstract', 
                          'Fields of Study':'fos',
                          'Keywords':'kws_lens',
                          'MeSH Terms':'mesh',
                          'Source URLs':'source_urls',
                          'External URL':'ext_url',
                          'DOI':'doi',
                          'References':'references',
                          'Citing Works Count':'n_cited',
                          'Is Open Access':'open',
                          'bib_src': 'bib_src'}

reshape_struc_lens_compact = {'Lens ID': 'lens_id', 
                            'Title': 'title', 
                            'Publication Year': 'year',
                            'Publication Type': 'pub_type', 
                            'Source Title': 'source', 
                            'Author/s': 'authors', 
                            'Abstract': 'abstract', 
                            'Fields of Study':'fos',
                            'Keywords':'kws_lens',
                            'MeSH Terms':'mesh',
                            'External URL':'ext_url',
                            'Citing Works Count':'n_cited',
                            'bib_src': 'bib_src'}

reshape_struc_dims_all = {'Rank': 'rank', 
                          'Publication ID': 'dims_id', 
                          'DOI': 'doi', 
                          'PMID': 'pmid', 
                          'PMCID': 'pmcid', 
                          'ISBN': 'isbn', 
                          'Title': 'title',
                          'Abstract': 'abstract', 
                          'Acknowledgements': 'acknowledgements', 
                          'Funding': 'funding', 
                          'Source title': 'source',
                          'Anthology title': 'anthology_title', 
                          'Publisher': 'publisher', 
                          'ISSN': 'issn', 
                          'MeSH terms': 'mesh',
                          'Publication date': 'pub_date', 
                          'PubYear': 'year', 
                          'Publication date (online)': 'pub_date_online',
                          'Publication date (print)':'pub_date_print',
                          'Volume':'volume',
                          'Issue':'issue',
                          'Pagination':'pagination',
                          'Open Access':'open',
                          'Publication Type':'pub_type',
                          'Authors':'authors',
                          'Authors (Raw Affiliation)':'auth_affils',
                          'Corresponding Authors':'auth_corresp',
                          'Authors Affiliations':'auth_affils_2',
                          'Research Organizations - standardized':'res_orgs_std',
                          'GRID IDs':'grid_ids',
                          'City of Research organization':'city_res_org',
                          'State of Research organization':'state_res_org',
                          'Country of Research organization':'country_res_org',
                          'Funder':'funder',
                          'Funder Group':'funder_group',
                          'Funder Country':'funder_country',
                          'UIDs of supporting grants':'uids_grants',
                          'Supporting Grants':'grants',
                          'Times cited':'n_cited',
                          'Recent citations':'recent_citations',
                          'RCR':'rcr',
                          'FCR':'fcr',
                          'Altmetric':'altmetric',
                          'Source Linkout':'ext_url',
                          'Dimensions URL':'dims_url',
                          'Fields of Research (ANZSRC 2020)':'anzsrc_2020',
                          'RCDC Categories':'rcdc',
                          'HRCS HC Categories':'hrcs_hc',
                          'HRCS RAC Categories':'hrcs_rac',
                          'Cancer Types':'cancer_types',
                          'CSO Categories':'cso',
                          'Units of Assessment':'units_assess',
                          'Sustainable Development Goals':'sdg',
                          'bib_src': 'bib_src'}

reshape_struc_dims_full = {'Rank': 'rank', 
                          'Publication ID': 'dims_id', 
                          'DOI': 'doi', 
                          'ISBN': 'isbn', 
                          'Title': 'title',
                          'Abstract': 'abstract', 
                          'Source title': 'source',
                          'ISSN': 'issn', 
                          'MeSH terms': 'mesh',
                          'Publication date': 'pub_date', 
                          'PubYear': 'year', 
                          'Open Access':'open',
                          'Publication Type':'pub_type',
                          'Authors':'authors',
                          'Authors (Raw Affiliation)':'auth_affils',
                          'Times cited':'n_cited',
                          'RCR':'rcr',
                          'FCR':'fcr',
                          'Altmetric':'altmetric',
                          'Source Linkout':'ext_url',
                          'Dimensions URL':'dims_url',
                          'Fields of Research (ANZSRC 2020)':'anzsrc_2020',
                          'RCDC Categories':'rcdc',
                          'HRCS HC Categories':'hrcs_hc',
                          'HRCS RAC Categories':'hrcs_rac',
                          'bib_src': 'bib_src'}

reshape_struc_dims_compact = {'Publication ID': 'dims_id', 
                          'Title': 'title',
                          'Abstract': 'abstract', 
                          'Source title': 'source',
                          'MeSH terms': 'mesh',
                          'PubYear': 'year', 
                          'Publication Type':'pub_type',
                          'Authors':'authors',
                          'Times cited':'n_cited',
                          'Source Linkout':'ext_url',
                          'Dimensions URL':'dims_url',
                          'Fields of Research (ANZSRC 2020)':'anzsrc_2020',
                          'bib_src': 'bib_src'}

reshape_strucs = {Reshape.SCOPUS_ALL.value: reshape_struc_scopus_all,
                  Reshape.SCOPUS_FULL.value: reshape_struc_scopus_full,
                  Reshape.SCOPUS_COMPACT.value: reshape_struc_scopus_compact,
                  Reshape.LENS_ALL.value: reshape_struc_lens_all,
                  Reshape.LENS_FULL.value: reshape_struc_lens_full,
                  Reshape.LENS_COMPACT.value: reshape_struc_lens_compact,
                  Reshape.DIMS_ALL.value: reshape_struc_dims_all,
                  Reshape.DIMS_FULL.value: reshape_struc_dims_full,
                  Reshape.DIMS_COMPACT.value: reshape_struc_dims_compact}


# If search_terms is directly copied from Scopus, Lens, or Dimensions, then remove
# the following strings before extracting the search terms. If the search_term
# contains additional strings not in this list, they will be added 
scopus_strings_remove = ['(',')','TITLE-ABS-KEY', 'TITLE', 'TITLE-ABS', 'KEY', 'NOT']
lens_strings_remove = ['(',')','title:', 'abstract:', 'keyword:', 'not']
dims_strings_remove = ['(', ')', 'not']


# Download stopwords if they haven't been downloaded previously
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

nltk_stopwords = nltk.corpus.stopwords.words('english')


# If verbose == True, set the logging level so that info messages are printed
logger = MyLogger("WARNING")
if verbose: logger.set_level("DEBUG")