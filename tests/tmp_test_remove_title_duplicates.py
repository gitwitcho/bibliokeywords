import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
import numpy as np

from clean import remove_title_duplicates
from pandas import testing as tm

'''
The test function only uses test dfs that have columns that are being changed in 
`remove_title_duplicates` plus one that isn't changed. This needs to be revised if
and when making changes to `remove_title_duplicates`.

The following items are tested:
    - Merging of the columns
        - bib_srcs (joined by '; ')
        - n_cited: sum the citations, except between duplicate sources where the maximum vakue is used
        - fos (joined by '; ')
        - anzsrc_2020 (joined by '; ')
        - kws (joined by '; '): 
            - kws_author, kws_index (Scopus)
            - kws_lens, mesh (Lens)
            - mesh (Dimensions)
        - link:
            - 'https://dx.doi.org/' + 'doi' (Scopus)
            - ext_url (Lens)
            - ext_url (Dimensions)
        - links (joined by '; '):
            - link (Scopus)
            - source_urls (Lens)
            - link (Dimensions)
    - Other operations
        - year replaced by pub_date
        - pub_date replace by year
        - authors format is normalised
        - authors-affiliations format is normalised
    - Values in all other columns are unchanged
'''

dup_1_1_df = [
    {
        'authors': "Kobayashi, T.; Hasui, K.",
        'title': "Efficient immunization strategies to prevent financial contagion",
        'abstract': "Many immunization strategies have been proposed to prevent infectious viruses from spreading through a network. In this work, we study efficient immunization strategies to prevent a default contagion that might occur in a financial network. An essential difference from the previous studies on immunization strategy is that we take into account the possibility of serious side effects. Uniform immunization refers to a situation in which banks are 'vaccinated' with a common low-risk asset. The riskiness of immunized banks will decrease significantly, but the level of systemic risk may increase due to the de-diversification effect. To overcome this side effect, we propose another immunization strategy, called counteractive immunization, which prevents pairs of banks from failing simultaneously. We find that counteractive immunization can efficiently reduce systemic risk without altering the riskiness of individual banks. 2014, Nature Publishing Group. All rights reserved.",
        'year': 2014.0,
        'pub_date': None,
        'n_cited': 18.0,
        'source': "Scientific Reports",
        'kws': "computer simulation; economic model; economic recession; financial management; human; humans; models, economic; risk management; risk sharing, financial",
        'fos': None,
        'anzsrc_2020': None,
        'auth_affils': "Kobayashi, T. (Graduate School of Economics, Kobe University, 2-1 Rokkodai, Nada, Kobe, 657-8501, Japan); Hasui, K. (Graduate School of Economics, Kobe University, 2-1 Rokkodai, Nada, Kobe, 657-8501, Japan)",
        'link': "https://dx.doi.org/10.1038/srep03834",
        'links': "https://dx.doi.org/10.1038/srep03834",
        'bib_src': "scopus",
        'scopus_id': "2-s2.0-84901042803",
        'lens_id': None,
        'dim_id': None
    }
]

dup_1_2_df = [
    {
        'authors': "Kobayashi, T.; Hasui, K.",
        'title': "Efficient immunization strategies to prevent financial contagion",
        'abstract': "Many immunization strategies have been proposed to prevent infectious viruses from spreading through a network. In this work, we study efficient immunization strategies to prevent a default contagion that might occur in a financial network. An essential difference from the previous studies on immunization strategy is that we take into account the possibility of serious side effects. Uniform immunization refers to a situation in which banks are vaccinated with a common low-risk asset. The riskiness of immunized banks will decrease significantly, but the level of systemic risk may increase due to the de-diversification effect. To overcome this side effect, we propose another immunization strategy, called counteractive immunization, which prevents pairs of banks from failing simultaneously. We find that counteractive immunization can efficiently reduce systemic risk without altering the riskiness of individual banks.",
        'year': 2014.0,
        'pub_date': '2014-01-23',
        'n_cited': 20.0,
        'source': "Scientific reports ",
        'kws': "computer simulation; economic recession; financial management; humans; models, economic; risk sharing, financial",
        'fos': "business; systemic risk; asset (economics); financial contagion; immunization (finance); financial management; monetary economics",
        'anzsrc_2020': None,
        'auth_affils': None,
        'link': "http://dx.doi.org/10.1038/srep03834",
        'links': "https://www.ncbi.nlm.nih.gov/pubmed/24452277 https://www.nature.com/srep/2014/140123/srep03834/fig_tab/srep03834_F3.html http://ui.adsabs.harvard.edu/abs/2014NatSR...4E3834K/abstract https://ci.nii.ac.jp/naid/120005600764 https://www.nature.com/articles/srep03834.pdf https://europepmc.org/article/MED/24452277 https://jglobal.jst.go.jp/en/detail?JGLOBAL_ID=201902219536149881 https://www.nature.com/articles/srep03834 https://core.ac.uk/download/41098249.pdf",
        'bib_src': "lens",
        'scopus_id': None,
        'lens_id': "003-657-516-425-014",
        'dim_id': None
    }
]

dup_1_3_df = [
    {
        'authors': "Kobayashi, T.; Hasui, K.",
        'title': "Efficient immunization strategies to prevent financial contagion",
        'abstract': "Many immunization strategies have been proposed to prevent infectious viruses from spreading through a network. In this work, we study efficient immunization strategies to prevent a default contagion that might occur in a financial network. An essential difference from the previous studies on immunization strategy is that we take into account the possibility of serious side effects. Uniform immunization refers to a situation in which banks are vaccinated with a common low-risk asset. The riskiness of immunized banks will decrease significantly, but the level of systemic risk may increase due to the de-diversification effect. To overcome this side effect, we propose another immunization strategy, called counteractive immunization, which prevents pairs of banks from failing simultaneously. We find that counteractive immunization can efficiently reduce systemic risk without altering the riskiness of individual banks.",
        'year': 2014.0,
        'pub_date': '2014-01-23',
        'n_cited': 22.0,
        'source': "scientific Reports",
        'kws': "computer simulation; economic recession; financial management; humans; models, economic; risk sharing, financial",
        'fos': "35 Commerce, Management, Tourism and Services; 3502 Banking, Finance and Investment; 38 Economics; 3801 Applied Economics",
        'anzsrc_2020': None,
        'auth_affils': "Kobayashi, T. (Graduate School of Economics, Kobe University, 2-1 Rokkodai, 657-8501, Nada, Kobe, Japan); Hasui, K. (Graduate School of Economics, Kobe University, 2-1 Rokkodai, 657-8501, Nada, Kobe, Japan)",
        'link': "https://www.nature.com/articles/srep03834.pdf",
        'links': "https://www.nature.com/articles/srep03834.pdf",
        'bib_src': "dims",
        'scopus_id': None,
        'lens_id': None,
        'dim_id': "pub.1041874688"
    }
]

dup_2_1_df = [
    {
        'authors': "Laskin, D.M.",
        'title': "Should prophylactic antibiotics be used for patients having removal of erupted teeth",
        'abstract': "Generally, antibiotics should not be required before the removal of erupted carious or periodontally involved teeth unless a significant risk of postoperative infection is present. The decision to use prophylactic antibiotics in noninfected cases should also be based on whether patients have any significant medical risk factors that could adversely affect their humoral and cellular defense mechanisms, and whether any systemic risks are associated with the bacteremia that accompanies tooth extraction. This article discusses the various indications for using prophylactic antibiotics in patients having erupted teeth extracted based on a consideration of these factors. 2011 Elsevier Inc.",
        'year': 2011.0,
        'pub_date': None,
        'n_cited': 6.0,
        'source': "Oral and Maxillofacial Surgery Clinics of North America",
        'kws': "antibiotic prophylaxis; bacteremia; dental caries; erupted tooth; focal infection, dental; human; humans; immunocompromised host; immunocompromised patient; infection; periodontal disease; periodontal diseases; postextraction infection; prophylactic antibiotics; prosthesis-related infections; review; risk factor; risk factors; surgical infection; surgical wound infection; tooth extraction; tooth infection; tooth removal",
        'fos': None,
        'anzsrc_2020': None,
        'auth_affils': "Laskin, D.M. (Department of Oral and Maxillofacial Surgery VCU, School of Dentistry, VCU Medical Center, 521 North 11th St., PO Box 980566, Richmond, VA 23298-0566, United States)",
        'link': "https://dx.doi.org/10.1016/j.coms.2011.07.006",
        'links': "https://dx.doi.org/10.1016/j.coms.2011.07.006",
        'bib_src': "scopus",
        'scopus_id': "2-s2.0-80053579003",
        'lens_id': None,
        'dim_id': None
    }
]

dup_2_2_df = [
    {
        'authors': "Laskin, D.M.",
        'title': "Should prophylactic antibiotics be used for patients having removal of erupted teeth",
        'abstract': "Generally, antibiotics should not be required before the removal of erupted carious or periodontally involved teeth unless a significant risk of postoperative infection is present. The decision to use prophylactic antibiotics in noninfected cases should also be based on whether patients have any significant medical risk factors that could adversely affect their humoral and cellular defense mechanisms, and whether any systemic risks are associated with the bacteremia that accompanies tooth extraction. This article discusses the various indications for using prophylactic antibiotics in patients having erupted teeth extracted based on a consideration of these factors.",
        'year': 2011.0,
        'pub_date': "2011-11",
        'n_cited': 7.0,
        'source': "Oral and maxillofacial surgery clinics of North  America   ",
        'kws': "antibiotic prophylaxis; bacteremia; dental caries; focal infection, dental; humans; immunocompromised host; periodontal diseases; prosthesis-related infections; risk factors; surgical wound infection; tooth extraction",
        'fos': "32 Biomedical and Clinical Sciences; 3203 Dentistry",
        'anzsrc_2020': None,
        'auth_affils': "Laskin, D.M. (Department of Oral and Maxillofacial Surgery VCU School of Dentistry and VCU Medical Center, 521 North 11th Street, PO Box 980566, Richmond, VA 23298-0566, USA)",
        'link': None,
        'links': None,
        'bib_src': "dims",
        'scopus_id': None,
        'lens_id': None,
        'dim_id': "pub.1032068830"
    }
]

dup_3_1_df = [
    {
        'authors': "Celebi, A.R.C.; Kadayifcilar, S.; Eldem, B.",
        'title': "Hyperbaric oxygen therapy in branch retinal artery occlusion in a 15-year-old boy with methylenetetrahydrofolate reductase mutation",
        'abstract': "Purpose. To report the efficacy of hyperbaric oxygen (HBO) therapy in a case of branch retinal artery occlusion (BRAO) in a 15-year-old boy. Methods. We report a 15-year-old boy with sudden loss of vision due to BRAO. Examination included laboratory evaluation for systemic risk factors. Follow-up exams included visual acuity, fundus examination, fundus fluorescein angiography, and visual field testing. HBO therapy was employed for treatment. Medical history was positive for isolated glucocorticoid deficiency. Laboratory evaluation disclosed hyperhomocysteinemia and methylenetetrahydrofolate reductase (MTHFR) mutation. The visual acuity 0.05 at presentation improved to 0.8 after 20 days of HBO therapy. There was no change on visual fields. Conclusion. In this pediatric case, HBO therapy was useful in the treatment of BRAO.",
        'year': 2015.0,
        'pub_date': "2015-02-05",
        'n_cited': 2.0,
        'source': "Case Reports in Ophthalmological Medicine",
        'kws': None,
        'fos': "32 Biomedical and Clinical Sciences; 3212 Ophthalmology and Optometry",
        'anzsrc_2020': None,
        'auth_affils': "Celebi, A.R.C. (Department of Ophthalmology, Acibadem University School of Medicine, 34303 Istanbul, Turkey); Kadayifcilar, S. (Department of Ophthalmology, Hacettepe University School of Medicine, Ankara, Turkey); Eldem, B. (Department of Ophthalmology, Hacettepe University School of Medicine, Ankara, Turkey)",
        'link': "http://downloads.hindawi.com/journals/criopm/2015/640247.pdf",
        'links': "http://downloads.hindawi.com/journals/criopm/2015/640247.pdf",
        'bib_src': "dims",
        'scopus_id': None,
        'lens_id': None,
        'dim_id': "pub.1007905354"
    }
]

new_cols = ['bib_srcs', 'sources']  # the new columns that are created in the function remove_duplicate_titles

# Test case with simple changes
#   1. Capitalises the 'source'
def test_single_standard_df():
    input_df = pd.DataFrame(dup_1_2_df)
    expected_output_df = input_df.copy()
    remove_cols = new_cols  # remove the new columns that are created in the function remove_duplicate_titles

    # Data type changes made in the function
    expected_output_df['year'] = expected_output_df['year'].astype(int)
    expected_output_df['n_cited'] = expected_output_df['n_cited'].astype(int)
    expected_output_df['pub_date'] = pd.to_datetime(expected_output_df['pub_date'])

    # Capitalises the source
    expected_output_df['source'] = 'Scientific Reports'

    output_df = remove_title_duplicates(input_df)

    assert([col in output_df.columns for col in remove_cols])

    output_df.drop(columns = remove_cols, inplace = True)

    for col in output_df.columns:   # use this for pin-pointing problem column
        assert output_df[col].equals(expected_output_df[col])

# Test case with changes to pub_date and year
#   1. pub_date given, year nan: year is pub_date year
#   2. year given, pub_date nan: pub:date is 1/1/year
#   3. neither year nor pub_date are given: both remain nan
def test_pub_date_year():
    input_df = pd.DataFrame(dup_1_1_df)
    expected_output_df = input_df.copy()
    remove_cols = new_cols  # remove the new columns that are created in the function remove_duplicate_titles

    # Data type changes made by the function
    expected_output_df['n_cited'] = expected_output_df['n_cited'].astype(int)

    # 1. pub_date given, year nan: year is pub_date year
    input_df['year'] = np.nan
    input_df['pub_date'] = '2014-01-23'
    expected_output_df['year'] = 2014
    expected_output_df['pub_date'] = pd.to_datetime('2014-01-23')
    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    assert output_df.equals(expected_output_df)

    # 2. year given, pub_date nan: pub:date is 1/1/year
    input_df['year'] = 1997
    input_df['pub_date'] = np.nan
    expected_output_df['year'] = 1997
    expected_output_df['pub_date'] = pd.to_datetime('1997-01-01')
    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    assert output_df.equals(expected_output_df)

    # 3. neither year nor pub_date are given: both remain nan
    input_df['year'] = np.nan
    input_df['pub_date'] = np.nan
    expected_output_df['year'] = np.nan
    expected_output_df['pub_date'] = pd.NaT
    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    assert output_df.equals(expected_output_df)

# Test case with merging of sources
#   1. Sources are the same, but with difference in white spaces and capitalisation
#   2. Some sources are different
def test_merge_to_single_source():
    input_df_1 = pd.DataFrame([dup_2_1_df[0], dup_2_2_df[0]])
    expected_output_df_1 = input_df_1.copy()
    input_df_2 = pd.DataFrame([dup_1_1_df[0], dup_1_2_df[0], dup_1_3_df[0]])
    expected_output_df_2 = input_df_2.copy()
    remove_cols = list(set(new_cols) - set(['sources']))  # remove all new except 'sources'

    # Data type changes made in the function
    expected_output_df_1['year'] = expected_output_df_1['year'].astype(int)
    expected_output_df_2['year'] = expected_output_df_2['year'].astype(int)
    expected_output_df_1['n_cited'] = 7
    expected_output_df_2['n_cited'] = expected_output_df_2['n_cited'].astype(int)
    expected_output_df_1['pub_date'] = pd.to_datetime(expected_output_df_1['pub_date'])
    expected_output_df_2['pub_date'] = pd.to_datetime(expected_output_df_2['pub_date'])

    # 1. Sources are the same, but with difference in white spaces and capitalisation
    # input_df_1['source'].iloc[1] = 'Journal of finance'
    # expected_output_df_1['sources'] = 'Scientific Reports; Journal of Finance'
    expected_output_df_1['pub_date'] = pd.to_datetime('2011-01-01')
    expected_output_df_1['sources'] = 'Oral and Maxillofacial Surgery Clinics of North America'
    expected_output_df_1['fos'] = input_df_1['fos'].iloc[1]
    expected_output_df_1['anzsrc_2020'] = None
    expected_output_df_1['fos'] = input_df_1['fos'].iloc[1]
    expected_output_df_1['fos'] = input_df_1['fos'].iloc[1]
    expected_output_df_1['fos'] = input_df_1['fos'].iloc[1]

    expected_output_df_1.drop(1, inplace = True)
    output_df = remove_title_duplicates(input_df_1).drop(columns = remove_cols)
    output_df['anzsrc_2020'].equals(expected_output_df_1['anzsrc_2020'])

    for col in output_df.columns:   # use this for pin-pointing problem column
        assert output_df[col].equals(expected_output_df_1[col])

    assert output_df.equals(expected_output_df_1)

    # 2. Some sources are different






# test_single_standard_df()
# test_pub_date_year()
test_merge_to_single_source()