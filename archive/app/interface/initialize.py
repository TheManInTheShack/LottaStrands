
# ==================================================================================================
# Imports
# ==================================================================================================
import sys
import os
import json
from utilities import read_map_sheet

# ==================================================================================================
# Initialize
# ==================================================================================================
# ------------------------------------------------------------------------------
# Start
# ------------------------------------------------------------------------------
print("-"*80)
print("Starting...")
print("-"*80)

# ------------------------------------------------------------------------------
# Put together the blocks of text and image assets used in all sheets
# ------------------------------------------------------------------------------
title = "Hyperion Context"

footnote = {}
footnote['credits'] = "Text copyright Dan Simmons. Dashboard implementation by Grant Dickerson, copyright 2023."
footnote['revnum']  = "Rev.0"

# ==================================================================================================
# Store default style components
# ==================================================================================================
# ------------------------------------------------------------------------------
# Default
# ------------------------------------------------------------------------------
style_default = {}
style_default['backgroundColor']  = '#111111'
style_default['color']            = '#FFFFFF'
style_default['textAlign']        = 'center'

# ==================================================================================================
# Pull in the main data source shared by all pages
# ==================================================================================================
# ------------------------------------------------------------------------------
# Read the data file
# ------------------------------------------------------------------------------
print("...reading data...")
data_fname = "narrative_map.xlsx"
data = {}
#data['volume']      = read_map_sheet(data_fname, "volumes")
#data['chapter']     = read_map_sheet(data_fname, "chapters")
#data['scene']       = read_map_sheet(data_fname, "scenes")
data['paragraph']   = read_map_sheet(data_fname, "paragraphs")
#data['sentences']   = read_map_sheet(data_fname, "sentences")
#data['words']       = read_map_sheet(data_fname, "words")
#data['lexicon']     = read_map_sheet(data_fname, "lexicon")

# ------------------------------------------------------------------------------
# Get universal metrics
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Hold the initialized data so we can pass it to the pages
# ------------------------------------------------------------------------------
init_dict = {}
init_dict['title']             = title
init_dict['footnote']          = footnote
init_dict['style_default']     = style_default
init_dict['data']              = data

# ------------------------------------------------------------------------------
# User info
# ------------------------------------------------------------------------------
