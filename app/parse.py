# ------------------------------------------------------------------------------
# Hyperion Context - Parse
# ------------------------------------------------------------------------------
import sys
import argparse
import json
import re
from bs4 import BeautifulSoup
from textblob import TextBlob

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
    print("Begining parse...")

    # --------------------------------------------------------------------------
    # Parse and organize each volume as a clean hierarchy of levels
    # - Corpus
    # - Volume
    # - Chapter
    # - Scene
    # - Paragraph
    # - Sentence
    # --------------------------------------------------------------------------
    sources = []

    corpus = {}

    # --------------------------------------------------------------------------
    # Show 
    # --------------------------------------------------------------------------
    if args.debug and False:
        for volume in corpus:
            for chapter in corpus[volume]:
                for scene in corpus[volume][chapter]:
                    for para in corpus[volume][chapter][scene]:
                        for sentence in corpus[volume][chapter][scene][para]:
                            print(volume, chapter, scene, para, sentence)

    # --------------------------------------------------------------------------
    # Let's save that hierarchical data as json
    # --------------------------------------------------------------------------
    with open("corpus.json", "w", encoding="utf-8") as f:
        json.dump(corpus, f)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    print("...finished!")

# ------------------------------------------------------------------------------
# Run
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main(cli())
