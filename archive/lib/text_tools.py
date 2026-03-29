import sys
import re
import pandas as pd
from unidecode import unidecode
from textblob import TextBlob
from utilities import show_me

# ------------------------------------------------------------------------------
# Given one block of text, lexify it at the word/part of speech level and return
# several useful views
#  - Make a textblob out of the thing 
#  - get the POS stuff
#  - Add the word abstraction
# ------------------------------------------------------------------------------
def lexify(blob):
    if type(blob) is str:
        blob = TextBlob(blob)

    lex_data = pd.DataFrame(blob.tags, columns=["word","tag"])

    def abstract(x):
        return abstract_text(x['word'])
    abs_data = pd.DataFrame(lex_data.apply(abstract, axis=1).values.tolist(), columns=["Blanched","Chopped","Folded","Mashed","Juiced"])
    lex_data = lex_data.join(abs_data)

    return lex_data

# ------------------------------------------------------------------------------
# Pull the files out of the vault and do a basic parse 
# ------------------------------------------------------------------------------
def parse_obsidian_vault(vdir):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...parsing Obsidian vault, looking for new feedback...")

    # --------------------------------------------------------------------------
    # TODO This goes here...
    # --------------------------------------------------------------------------
    vinfo = {}

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return vinfo

# ------------------------------------------------------------------------------
# Put together the text files for the Obsidian vault
# ------------------------------------------------------------------------------
def compile_vault_output(corpus):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...compiling markup text...")

    # --------------------------------------------------------------------------
    # Compile the chapters as raw text
    # --------------------------------------------------------------------------
    chapters = {}
    for chapter in corpus['text']:
        # ----------------------------------------------------------------------
        # Make the chapter name
        # ----------------------------------------------------------------------
        cname = "CHAPTER " + str(chapter[0]) + ": " + chapter[2]

        # ----------------------------------------------------------------------
        # Start the output block of text 
        # ----------------------------------------------------------------------
        block = []

        # ----------------------------------------------------------------------
        # Chapter title
        # ----------------------------------------------------------------------
        block.append("# " + cname)
        block.append("")

        block.append("| | |")
        block.append("|------------|-----|")
        block.append("| Paragraphs |" + str(len(corpus['text'][chapter]['paragraphs'])) + "|")

        # ----------------------------------------------------------------------
        # Each paragraph
        # ----------------------------------------------------------------------
        for i, paragraph in enumerate(corpus['text'][chapter]['paragraphs']):
            # ------------------------------------------------------------------
            # Header
            # ------------------------------------------------------------------
            block.append("")
            block.append("---")
            block.append("## Paragraph " + str(i+1))
            block.append("")

            # ------------------------------------------------------------------
            # Text
            # ------------------------------------------------------------------
            block.append(corpus['text'][chapter]['paragraphs'][paragraph])

        # ----------------------------------------------------------------------
        # add the chapter
        # ----------------------------------------------------------------------
        chapters[cname] = block

    # --------------------------------------------------------------------------
    # Consolidate
    # --------------------------------------------------------------------------
    vault_data = {}
    vault_data['chapters'] = chapters

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return vault_data

# ------------------------------------------------------------------------------
# Write out the data to the text files
# ------------------------------------------------------------------------------
def write_vault_files(vault_data):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...writing text output...")
        
    # --------------------------------------------------------------------------
    # One file per chapter
    # --------------------------------------------------------------------------
    for cname in vault_data['chapters']:
        fpath = "vault\\chapters\\" + cname.split(":")[0] + ".md"
        with open(fpath, "w", encoding="utf-8") as f:
            for line in vault_data['chapters'][cname]:
                print(line, file=f)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return True

# ------------------------------------------------------------------------------
# Squish and squash a piece of text to get abstracted views of the contents
# ------------------------------------------------------------------------------
def abstract_text(text, stopwords=[]):
    # --------------------------------------------------------------------------
    # blanched: normalized characters and lowercase
    # --------------------------------------------------------------------------
    blanche = unidecode(str(text)).lower().strip()

    # --------------------------------------------------------------------------
    # chopped: punctuation and stopwords removed
    # --------------------------------------------------------------------------
    chop = re.sub(r"[^0-9a-zA-z]+", " ", blanche)
    chop = " ".join([x for x in chop.split() if not x in stopwords])

    # --------------------------------------------------------------------------
    # folded: words in sorted order
    # --------------------------------------------------------------------------
    fold = " ".join(sorted(chop.split()))

    # --------------------------------------------------------------------------
    # mashed: whitespace removed
    # --------------------------------------------------------------------------
    mash = fold.replace(" ", "")

    # --------------------------------------------------------------------------
    # juiced: reduced to sorted list of unique characters
    # --------------------------------------------------------------------------
    juice = "".join(sorted(list(set(mash))))

    # --------------------------------------------------------------------------
    # For debugging
    # --------------------------------------------------------------------------
    if False:
        print("-------------")
        print("Original: ", text)
        print("Blanched: ", blanche)
        print("Chopped:  ", chop)
        print("Folded:   ", fold)
        print("Mashed:   ", mash)
        print("Juiced:   ", juice)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return (blanche, chop, fold, mash, juice)


# ------------------------------------------------------------------------------
# Given a list of abstracted word clumps, make a list of all individual words
# within those over the whole set, with values that represent the 'importance'
# of the word
# ------------------------------------------------------------------------------
def assign_term_values(source_data):
    # --------------------------------------------------------------------------
    # Put together a full list of cleaned up individual terms
    # --------------------------------------------------------------------------
    source_terms = []
    for stext in source_data:
        blanche = unidecode(str(stext)).lower().strip()
        chop = re.sub(r"[^0-9a-zA-z]+", " ", blanche)
        for term in chop.split():
            source_terms.append(term)

    # --------------------------------------------------------------------------
    # Do the basic counts of the terms
    # --------------------------------------------------------------------------
    source_terms_data = pd.DataFrame(pd.Series(source_terms).value_counts(), columns=["count"])

    # --------------------------------------------------------------------------
    # Get the range of counts and set the ratio for each term
    # --------------------------------------------------------------------------
    maxcount = source_terms_data['count'].max()
    mincount = source_terms_data['count'].min()
    countrange = maxcount - mincount

    if countrange == 0:
        countrange = 1

    source_terms_data['range_ratio'] = source_terms_data['count'] / countrange
    #print(source_terms_data)
    #print(countrange)

    # --------------------------------------------------------------------------
    # Determine the order of magnitude for each
    # --------------------------------------------------------------------------
    def get_order_of_magnitude(ratio):
        pre, post = str(ratio).split(".")
        if int(pre) > 0:
            oom = len(pre) * -1
        else:
            oom = 0
            for digit in post:
                if digit == "0":
                    oom += 1
                else:
                    oom += 1
                    break
        return oom

    source_terms_data['order_of_magnitude'] = source_terms_data['range_ratio'].apply(get_order_of_magnitude)

    # --------------------------------------------------------------------------
    # Get the range of orders of magnitude and use that to determine the
    # increment size
    # --------------------------------------------------------------------------
    maxmag = source_terms_data['order_of_magnitude'].max()
    minmag = source_terms_data['order_of_magnitude'].min()
    magnitude_range = maxmag - minmag
    if magnitude_range == 0:
        magnitude_range = 1
    increment_size = 1/magnitude_range

    # --------------------------------------------------------------------------
    # Each term's value is the order of magnitude by the increment size
    # --------------------------------------------------------------------------
    source_terms_data['value'] = source_terms_data['order_of_magnitude'] * increment_size

    # --------------------------------------------------------------------------
    # ...but those with a count of 1 overwrite that with the full value
    # --------------------------------------------------------------------------
    def override_single_counts(counts, values):
        new_values = []
        for i, count in enumerate(counts):
            if count == 1:
                new_values.append(1.0)
            else:
                new_values.append(values[i])
        return new_values

    source_terms_data['value'] = override_single_counts(source_terms_data['count'].to_list(), source_terms_data['value'].to_list())

    #print(source_terms_data)
    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return source_terms_data

# ------------------------------------------------------------------------------
# Get a single best match
# text        - a string
# source_data - pre-prepared list of 'abstracted' terms, using abstract_text()
# term_values - matching list of term values, prepared by assign_term_values()
# stopwords   - list of individual words to ignore for matching purposes
# ------------------------------------------------------------------------------
def get_closest_match(text, source_data, term_values, stopwords=[]):
    # --------------------------------------------------------------------------
    # Get the alternate forms of the string
    # also hold aside the list of words as a list
    # also the 'mashed' version of the text which is words stripped-alphabetized
    # very much like this:
    # likemuchseethisveryyou
    # --------------------------------------------------------------------------
    text_parts = abstract_text(text, stopwords)
    wordsa = text_parts[1].split()
    mashed = text_parts[-2]
    juiced = text_parts[-1]

    # --------------------------------------------------------------------------
    # The change threshold depends on the size of the mashed text, making
    # concessions for short ones
    # --------------------------------------------------------------------------
    if len(mashed) > 8:
        thresh = math.floor(len(juiced) * 0.2)
    elif len(mashed) > 3:
        thresh = math.floor(len(mashed) * 0.4)
    elif len(mashed) > 1:
        thresh = 0
    elif len(mashed) == 1:
        thresh = 0

    #if text=="Wunderman Applogix":
    #    print(text, text_parts, wordsa)

    # --------------------------------------------------------------------------
    # Check the string vs every item in the source data
    # --------------------------------------------------------------------------
    candidates = {}
    for stext in source_data:
        # ----------------------------------------------------------------------
        # Check the word set for clean matches - this is a cumulative score
        # using lookups from the previously defined values
        # ----------------------------------------------------------------------
        wordsb = source_data[stext][1].split()
        
        wscore = 0.0
        for worda in wordsa:
            # ------------------------------------------------------------------
            # Work through each word
            # ------------------------------------------------------------------
            for wordb in wordsb:
                # --------------------------------------------------------------
                # Maybe it's an exact match, which we like a lot, so flag it
                # with a score related to its frequency and move on
                # --------------------------------------------------------------
                if worda == wordb:
                    tscore = 0.0
                    wscore += term_values[worda]
                    continue

                # --------------------------------------------------------------
                # Get the text similarity if it's still here
                # --------------------------------------------------------------
                tscore = text_similarity_score(worda, wordb)

                # --------------------------------------------------------------
                # Null text sim score gets discarded
                # --------------------------------------------------------------
                if not isinstance(tscore, int):
                    continue

                # --------------------------------------------------------------
                # Low sim scores, which indicate closeness, get a piece
                # --------------------------------------------------------------
                elif tscore < 1:
                    wscore += 0.9
                elif tscore < 2:
                    wscore += 0.3
                elif tscore < 3:
                    wscore += 0.1

        # ----------------------------------------------------------------------
        # The text itself is a perfect match, regardless of the term values,
        # so just make the word score whatever the number of words are
        # ----------------------------------------------------------------------
        if text == stext:
            wscore = 1.0 * len(wordsa)

        # ----------------------------------------------------------------------
        # Get the similarity score of the most abstracted version
        # Chop off anything that doesn't even fit half the size of the sample
        # ----------------------------------------------------------------------
        jtscore = text_similarity_score(text_parts[-1], source_data[stext][-1])
        jscore = jtscore
        if jtscore is None:
            jscore = None
        elif jtscore > thresh:
            jscore = None
        elif jtscore == 0:
            jscore = 0.0

        # ----------------------------------------------------------------------
        # If it passes, do the next abstraction level up, same way
        # ----------------------------------------------------------------------
        mtscore = text_similarity_score(text_parts[-2], source_data[stext][-2])
        mscore = mtscore
        if not is_number(mtscore):
            mscore = None
        elif mtscore > thresh:
            mscore = None
        elif mtscore == 0:
            mscore = 0.0

        # ----------------------------------------------------------------------
        # If it passes the mashed test, check the folded
        # ----------------------------------------------------------------------
        ftscore = text_similarity_score(text_parts[-3], source_data[stext][-3])
        fscore = ftscore
        if not is_number(ftscore):
            fscore = None
        elif ftscore > thresh:
            fscore = None
        elif ftscore == 0:
            fscore = 0.0

        #if text=="Wunderman Applogix":
        #    print(stext.ljust(84), str(thresh).ljust(8), str(jtscore).ljust(20), str(jscore).ljust(20), str(mscore).ljust(20), str(fscore).ljust(20), str(wscore).ljust(20))
        #    if wscore >= 1.0:
        #        print("WHAMMY!")
        #        print(type(jtscore))

        # ----------------------------------------------------------------------
        # If it's still passed or words were common, it's a candidate
        # - First skip past any that have no characters in common at all
        # - High word scores are very good
        # - Decent word score and mashed score are pretty good
        # - If there's a folded score, it's pretty good
        # ----------------------------------------------------------------------
        if not isinstance(jtscore, float):
            continue

        if wscore >= 1.0:
            candidates[stext] = {"thresh":thresh, "jscore":jscore, "mscore":mscore, "fscore":fscore, "wscore":wscore}
        elif wscore >= 0.3 and isinstance(mscore, float):
            candidates[stext] = {"thresh":thresh, "jscore":jscore, "mscore":mscore, "fscore":fscore, "wscore":wscore}
        elif isinstance(fscore, float):
            candidates[stext] = {"thresh":thresh, "jscore":jscore, "mscore":mscore, "fscore":fscore, "wscore":wscore}

    # --------------------------------------------------------------------------
    # Find the best match
    # --------------------------------------------------------------------------
    best_score = 1000.0
    best_match = ""

    for stext in candidates:
        jscore = candidates[stext]['jscore']
        mscore = candidates[stext]['mscore']
        fscore = candidates[stext]['fscore']
        wscore = candidates[stext]['wscore']

        composite_score = (-1 * wscore)
        if valid_value(jscore):
            composite_score += jscore
        if valid_value(mscore):
            composite_score += mscore
        if valid_value(fscore):
            composite_score += fscore

        if len(candidates) == 1:
            best_match = stext
            best_score = composite_score
        elif composite_score < best_score:
            best_match = stext
            best_score = composite_score

        #print(text.ljust(45), stext.ljust(45), candidates[stext])

    # --------------------------------------------------------------------------
    # Consolidate
    # --------------------------------------------------------------------------
    match_data = {}
    match_data['candidates'] = candidates
    match_data['best_match'] = best_match
    match_data['best_score'] = best_score

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return match_data
