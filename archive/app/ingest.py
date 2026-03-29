# ------------------------------------------------------------------------------
# Ingest
# Reads a 'corpus' hierarchical file and returns a table-structured map document
# ------------------------------------------------------------------------------
import sys
import argparse
import json
import re
import pandas as pd

from text_tools import *
from excel_tools import *
from graph_tools import *
from utilities import *

# ------------------------------------------------------------------------------
# Command line interface
# ------------------------------------------------------------------------------
def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", dest="debug", action="store_true", help="Show extra information")
    parser.set_defaults(debug=False)
    args = parser.parse_args()
    return args

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
def main(args):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("Chew chew chew chew chew...")

    # --------------------------------------------------------------------------
    # Hold the file names as constants, just to keep it clean like that
    # --------------------------------------------------------------------------
    MAP_FILE    = "narrative_map.xlsx"
    CLEAN_FILE  = "clean_input.xlsx"
    CORPUS_FILE = "corpus.json"
    PRIMES_FILE = "primes.txt"

    # --------------------------------------------------------------------------
    # Pick up the hierarchical text file, already divided into the levels
    # CORPUS --> VOLUME --> CHAPTER --> SCENE --> PARAGRAPH --> SENTENCE
    # --------------------------------------------------------------------------
    with open(CORPUS_FILE, encoding="utf-8") as f:
        corpus = json.load(f)

    # --------------------------------------------------------------------------
    # Set that up as a data frame to start with, with the levels flattened and
    # clean numeric and hierarchical index info added
    # --------------------------------------------------------------------------
    records = []
    vnum = 0
    cnum = 0
    snum = 0
    pnum = 0
    tnum = 0
    for volume in corpus:
        vnum += 1
        cnum = 1
        snum = 1
        pnum = 1
        tnum = 1
        for chapter in corpus[volume]:
            cnum += 1
            snum = 1
            pnum = 1
            tnum = 1
            for scene in corpus[volume][chapter]:
                snum += 1
                pnum = 1
                tnum = 1
                for paragraph in corpus[volume][chapter][scene]:
                    pnum += 1
                    tnum = 1
                    for sentence in corpus[volume][chapter][scene][paragraph]:
                        tnum += 1
                        text = corpus[volume][chapter][scene][paragraph][sentence]
                        hidx = ".".join([str(vnum), str(cnum), str(snum), str(pnum), str(tnum)])
                        rec = (vnum, cnum, snum, pnum, tnum, hidx, volume, chapter, scene, paragraph, sentence, text)
                        records.append(rec)

    corpus_data = pd.DataFrame(records, columns = ["vn","cn","sn","pn","tn","hidx","volume","chapter","scene","paragraph","sentence","text"])

    print(f"...read corpus data, retrieved {corpus_data.shape[0]} 'sentence' objects...")

    # --------------------------------------------------------------------------
    # Apply any marked cleaning
    # --------------------------------------------------------------------------
    if os.path.isfile(CLEAN_FILE):
        # ----------------------------------------------------------------------
        # Retrieve the cleaning instructions
        # ----------------------------------------------------------------------
        clean_chapters    = read_map_sheet(CLEAN_FILE, "chapters")
        clean_paragraphs  = read_map_sheet(CLEAN_FILE, "paragraphs")
        clean_sentences   = read_map_sheet(CLEAN_FILE, "sentences")

        # ----------------------------------------------------------------------
        # Apply chapter ignores
        # ----------------------------------------------------------------------
        cclean = clean_chapters['Chapters'].join(clean_chapters['Clean'])
        ignore_chapters = cclean[cclean['Ignore']!=""][['volume','chapter','Ignore']]
        corpus_data = pd.merge(corpus_data, ignore_chapters, how="left", left_on=['volume','chapter'], right_on=['volume','chapter'])
        corpus_data['Ignore'] = corpus_data['Ignore'].fillna("")
        corpus_data = corpus_data[corpus_data['Ignore']==""]

        # ----------------------------------------------------------------------
        # Apply xyz
        # ----------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Sentence data is just the corpus data with the index crumbs taken out
    # --------------------------------------------------------------------------
    sentence_data = corpus_data[["hidx","volume","chapter","scene","paragraph","sentence","text"]]

    # --------------------------------------------------------------------------
    # Compile UP from there to get the paragraph, scene, chapter, volume, while
    # collapsing the text for each.  Then add in text summary measures for each.
    # Drop the text column for everything above paragraph level.
    # --------------------------------------------------------------------------
    print(f"...building aggregated versions of sentence data...")

    def summarize_text(x):
        blob     = TextBlob(x['text'])
        lex_data = lexify(blob)
        numsent  = len(blob.sentences)
        numword  = len(blob.words)
        numglyph = len(blob)
        terms    = lex_data['Chopped'].drop_duplicates().to_list()
        numterms = len(terms)
        first3   = "|".join(blob.words[:3])
        last3    = "|".join(blob.words[-3:])
        return (numsent, numword, numglyph, numterms, first3, last3)


    def aggregate_set(sentence_data, setname, groups):
        print(f"......aggregating {setname}...")
        data = sentence_data.groupby(groups, sort=False)['text'].apply(lambda x : " ".join(x)).reset_index()
        data[['sentences','words','glyphs','terms','first','last']] = data.apply(summarize_text, axis=1, result_type="expand")
        return data
    
    volume_data    = aggregate_set(sentence_data, "volumes",    ["volume"])
    chapter_data   = aggregate_set(sentence_data, "chapters",   ["volume","chapter"])
    scene_data     = aggregate_set(sentence_data, "scenes",     ["volume","chapter","scene"])
    paragraph_data = aggregate_set(sentence_data, "paragraphs", ["volume","chapter","scene","paragraph"])

    volume_data = volume_data.drop('text', axis=1)
    chapter_data = chapter_data.drop('text', axis=1)
    scene_data = scene_data.drop('text', axis=1)

    # --------------------------------------------------------------------------
    # Drill DOWN from there to get everything at the word level, running lexing
    # stuff on it at the same time to get part of speech tagging and word-salad
    # --------------------------------------------------------------------------
    print(f"...building word-level data, this might take a minute...")
    wdata = []
    for i, rec in sentence_data.iterrows():
        xdata = lexify(rec['text'])
        xdata['hidx'] = rec['hidx']
        wdata.append(xdata)
        num = i+1
        if num % 1000 == 0:
            print(f"......{num} sentences processed...")

    word_data = pd.concat(wdata)
    word_data = word_data.reset_index(names="wnum")
    word_data['wnum'] = word_data['wnum'] + 1
    word_data['wnum'] = word_data['wnum'].astype(str)
    word_data['hidx'] = word_data['hidx'] + "." + word_data['wnum']
    word_data['count'] = 1

    print(f"...finished compiling word data, {word_data.shape[0]} objects in total...")

    # --------------------------------------------------------------------------
    # From the words list, we can grab at the second level, where we have both
    # normalized the character set and disregarded punctuation & capitalization, 
    # so we have the set of unique terms to act as the lexicon basis
    # --------------------------------------------------------------------------
    print(f"...building lexicon from word data...")
    lexicon_data = word_data.drop_duplicates(subset=['Chopped'])[['Chopped','Folded','Mashed','Juiced']]
    lexicon_data.columns = ["term","folded","mashed","juiced"]
    lexicon_data = lexicon_data.sort_values(by=['term'])
    lexicon_data = lexicon_data[lexicon_data['term']!=""]
    lexicon_data = lexicon_data.reset_index()

    lex_counts = word_data.groupby("Chopped").sum(numeric_only=True)
    lexicon_data = lexicon_data.join(lex_counts, on="term")

    print(f"...extracted {lexicon_data.shape[0]} unique lexical terms...")

    # --------------------------------------------------------------------------
    # Cleanup of the word set AFTER extracting lex data
    # --------------------------------------------------------------------------
    word_data = word_data[['hidx', 'wnum', 'word', 'tag', "Blanched", 'Chopped']]
    word_data.columns = ["hidx", "wnum", "word", "tag", "normal", "term"]

    # --------------------------------------------------------------------------
    # Ontology 
    # --------------------------------------------------------------------------
    #print(f"...building ontology from lexicon data...")

    # --------------------------------------------------------------------------
    # Taxonomy
    # --------------------------------------------------------------------------
    #print(f"...building taxonomy from ontology data...")

    # --------------------------------------------------------------------------
    # Add prime keys to all of these
    # --------------------------------------------------------------------------
    primebank = [int(x) for x in open(PRIMES_FILE, "r").read().splitlines()]


    # --------------------------------------------------------------------------
    # Transfer or start the auxiliary sections
    # --------------------------------------------------------------------------
    volume_user    = pd.DataFrame()
    chapter_user   = pd.DataFrame()
    scene_user     = pd.DataFrame()
    paragraph_user = pd.DataFrame()
    sentence_user  = pd.DataFrame()
    word_user      = pd.DataFrame()
    lexicon_user   = pd.DataFrame()

    # --------------------------------------------------------------------------
    # Align the cleaning section for that document
    # --------------------------------------------------------------------------
    chapter_clean   = pd.DataFrame(columns=["Ignore", "Rename"])
    paragraph_clean = pd.DataFrame(columns=["Ignore", "Scene"])
    sentence_clean  = pd.DataFrame(columns=["Ignore", "Combine", "Split","Replace", "Edit"])

    # --------------------------------------------------------------------------
    # Most of the formatting will be the same across all sheets
    # --------------------------------------------------------------------------
    std_fmt = {}
    std_fmt['reverse_rows']         = [1,2,3]
    std_fmt['short_rows']           = [2]
    std_fmt['wrap_rows']            = [3]
    std_fmt['fix_row_height_after'] = 3
    std_fmt['freeze_panes']         = "A4"
    std_fmt['zoom']                 = 80

    # --------------------------------------------------------------------------
    # Cleaning document - Chapters
    # --------------------------------------------------------------------------
    cclean_body = prepare_map_body([("Chapters", chapter_data),("Clean",chapter_clean)])
    cclean_fmt = std_fmt.copy()
    cclean_fmt['column_widths'] = [30,30,15,15,15,15,35,35,5,16,30]
    cclean_fmt['gutter_cols'] = ['I']

    # --------------------------------------------------------------------------
    # Cleaning document - Paragraphs
    # --------------------------------------------------------------------------
    pclean_body = prepare_map_body([("Paragraphs", paragraph_data),("Clean",paragraph_clean)])
    pclean_fmt = std_fmt.copy()
    pclean_fmt['column_widths'] = [20,20,10,10,100,15,15,15,15,35,35,5,16,16]
    pclean_fmt['gutter_cols'] = ['L']
    pclean_fmt['wrap_cols'] = ['E']

    # --------------------------------------------------------------------------
    # Cleaning document - Sentences
    # --------------------------------------------------------------------------
    sclean_body = prepare_map_body([("Sentences", sentence_data),("Clean",sentence_clean)])
    sclean_fmt = std_fmt.copy()
    sclean_fmt['column_widths'] = [12,10,10,10,10,10,160,5,16,16,16,16,30]
    sclean_fmt['gutter_cols'] = ['H']
    sclean_fmt['wrap_cols'] = ['G']

    # --------------------------------------------------------------------------
    # Narrative map sheet - Volumes
    # --------------------------------------------------------------------------
    volumes_body = prepare_map_body([("Volumes", volume_data),("User",volume_user)])
    volumes_fmt = std_fmt.copy()
    volumes_fmt['column_widths'] = [30,15,15,15,15,35,35,5,16,16,16,16]
    volumes_fmt['gutter_cols'] = ['H']

    # --------------------------------------------------------------------------
    # Narrative map sheet - Chapters
    # --------------------------------------------------------------------------
    chapters_body = prepare_map_body([("Chapters", chapter_data),("User",chapter_user)])
    chapters_fmt = std_fmt.copy()
    chapters_fmt['column_widths'] = [30,30,15,15,15,15,35,35,5,16,16,16,16]
    chapters_fmt['gutter_cols'] = ['I']

    # --------------------------------------------------------------------------
    # Narrative map sheet - Scenes
    # --------------------------------------------------------------------------
    scenes_body = prepare_map_body([("Scenes", scene_data),("User",scene_user)])
    scenes_fmt = std_fmt.copy()
    scenes_fmt['column_widths'] = [30,30,30,15,15,15,15,35,35,5,16,16,16,16]
    scenes_fmt['gutter_cols'] = ['J']

    # --------------------------------------------------------------------------
    # Narrative map sheet - Paragraphs
    # --------------------------------------------------------------------------
    paragraphs_body = prepare_map_body([("Scenes", paragraph_data),("User",paragraph_user)])
    paragraphs_fmt = std_fmt.copy()
    paragraphs_fmt['column_widths'] = [20,20,10,10,100,15,15,15,15,35,35,5,16,16,16,16]
    paragraphs_fmt['gutter_cols'] = ['L']
    paragraphs_fmt['wrap_cols'] = ['E']

    # --------------------------------------------------------------------------
    # Narrative map sheet - Sentences
    # --------------------------------------------------------------------------
    sentences_body = prepare_map_body([("Sentences", sentence_data),("User", sentence_user)])
    sentences_fmt = std_fmt.copy()
    sentences_fmt['column_widths'] = [12,10,10,10,10,10,150,5,16,16,16,16]
    sentences_fmt['gutter_cols'] = ['H']
    sentences_fmt['wrap_cols'] = ['G']

    # --------------------------------------------------------------------------
    # Narrative map sheet - Words
    # --------------------------------------------------------------------------
    words_body = prepare_map_body([("Words", word_data),("User", word_user)])
    words_fmt = std_fmt.copy()
    words_fmt['column_widths'] = [16,10,30,20,12,30,5,16,16,16,16]
    words_fmt['gutter_cols'] = ['G']

    # --------------------------------------------------------------------------
    # Narrative map sheet - Lexicon
    # --------------------------------------------------------------------------
    lexicon_body = prepare_map_body([("Lexicon", lexicon_data),("User", lexicon_user)])
    lexicon_fmt = std_fmt.copy()
    lexicon_fmt['column_widths'] = [30,20,20,20,15,5,16,16,16,16]
    lexicon_fmt['gutter_cols'] = ["E"]

    # --------------------------------------------------------------------------
    # Write the sheets to the documents
    # --------------------------------------------------------------------------
    print(f"...writing to cleaning document {CLEAN_FILE}...")
    x = replace_excel_sheet(CLEAN_FILE, "chapters",    cclean_body, cclean_fmt)
    x = replace_excel_sheet(CLEAN_FILE, "paragraphs",  pclean_body, pclean_fmt)
    x = replace_excel_sheet(CLEAN_FILE, "sentences",   sclean_body, sclean_fmt)

    print(f"...writing to map document {MAP_FILE}...")
    x = replace_excel_sheet(MAP_FILE, "volumes",    volumes_body,       volumes_fmt)
    x = replace_excel_sheet(MAP_FILE, "chapters",   chapters_body,      chapters_fmt)
    x = replace_excel_sheet(MAP_FILE, "scenes",     scenes_body,        scenes_fmt)
    x = replace_excel_sheet(MAP_FILE, "paragraphs", paragraphs_body,    paragraphs_fmt)
    x = replace_excel_sheet(MAP_FILE, "sentences",  sentences_body,     sentences_fmt)
    x = replace_excel_sheet(MAP_FILE, "words",      words_body,         words_fmt)
    x = replace_excel_sheet(MAP_FILE, "lexicon",    lexicon_body,       lexicon_fmt)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    print("...gulp!")

# ------------------------------------------------------------------------------
# Run
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    start_time = datetime.utcnow()
    main(cli())
    end_time = datetime.utcnow()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time}")
