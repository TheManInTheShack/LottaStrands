# ==================================================================================================
# INDEX
# This file runs the overall dashboard program
# - Includes the other pieces as imports
# - Puts together the multi-page index and routing
# - Runs the server
# ==================================================================================================

# ==================================================================================================
# Imports from Dash and the other assets in this group
# ==================================================================================================
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app
from initialize import init_dict

from page_splash import *
from page_read import *
from page_view import *

# ==================================================================================================
# Info about the navigable pages
# ==================================================================================================
pages = {}
pages['splash']  = {'href':"/"     , 'name':"Home"  , 'func':layout_splash  }
pages['read']    = {'href':"/read" , 'name':"Read"  , 'func':layout_read    }
pages['view']    = {'href':"/view" , 'name':"View"  , 'func':layout_view    }

# ------------------------------------------------------------------------------
# Store into the dict to be pushed into the layout
# ------------------------------------------------------------------------------
init_dict['pages'] = pages

# ==================================================================================================
# Put together the multi-page index and routing
# ==================================================================================================
# ------------------------------------------------------------------------------
# Single-level layout holds the whole page
# ------------------------------------------------------------------------------
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
], fluid=True)

# ------------------------------------------------------------------------------
# Path routing via a special callback
# - The output is the Div that we made just above
# - The input is the url typed into the browser
# - Each formal path ending will have a corresponding function in layouts
# ------------------------------------------------------------------------------
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    for page in pages:
        if pathname == pages[page]['href']:
            out = pages[page]['func'](init_dict)
            return out
    return '404'

# ==================================================================================================
# Run the server
# ==================================================================================================
# ------------------------------------------------------------------------------
# if in production mode we need to have a reference to the server for wsgi
# ------------------------------------------------------------------------------
server = app.server

# ------------------------------------------------------------------------------
# If we are running it in test mode
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    print("...starting server...")
    app.run_server(debug=True)
