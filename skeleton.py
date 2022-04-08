import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import shapefile as shp
import plotly.express as px
import plotly.io
import json
import numpy as np
import dash
from dash import Dash, dcc, html, Input, Output
from dash import html
from dash.dependencies import Input, Output, State
import time

from urllib.request import urlopen
import json
import plotly.graph_objects as go

# -----------------------------------------Loading the dataframes and JSONS--------------------------------------------
# *********************************************************************************************************************
# ---------------------------------------------------------------------------------------------------------------------

df = pd.read_csv(r'C:\Users\felip\Documents\JBG050-Data Challenge 2\Project_VIS_DC2\data\final_dataset.csv')
crimetype = pd.read_csv(r'C:\Users\felip\Documents\JBG050-Data Challenge 2\Project\data\all_variables.csv')
predictions = pd.read_csv(r'C:\Users\felip\Documents\JBG050-Data Challenge 2\Project\data\predictions.csv')

with urlopen('https://raw.githubusercontent.com/gausie/LSOA-2011-GeoJSON/master/lsoa.geojson') as response:
    lsoas = json.load(response)

with urlopen(
        'https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/administrative/eng/lad.json') as response:
    constituencies = json.load(response)

# ---------------------------------Initializing the app, auxiliary functions and styles---------------------------------
# *********************************************************************************************************************
# ---------------------------------------------------------------------------------------------------------------------
# defining needed categories in the dataframe
df = df[df['Year'] <= 2018]
df['county'] = [' '.join(item.split()[:-1]) for item in np.array(df['LSOA_name'])]
df['CrimeTypeI'] = crimetype['Type_I_crime_amount']
df['CrimeTypeII'] = crimetype['Type_II_crime_amount']

predictions['Year'] = predictions['Unnamed: 0'].map(lambda x: x.split('-')[0])
predictions['Month'] = predictions['Unnamed: 0'].map(lambda x: x.split('-')[1])

codes_dic = {'london': 'E01000005', 'surrey-heath': 'E01030759', 'durham': 'E01020795'}
city_of_london = 'E01000005'  # London
surrey_heath = 'E01030759'
durham = 'E01020795'

colors = {
    'background': '#2e2e2e',
    'text': '#d6d6d6',
    'orange': '#e87d3e',
    'purple': '#9e86c8',
    'Blue': '#6c99bb'
}

dic_col = {'london': ['Urban Type 1 Crime', 'Urban Type 2 Crime'],
           'surrey-heath': ['Town Type 1 Crime', 'Town Type 1 Crime'],
           'durham': ['Village Type 1 Crime', 'Village Type 2 Crime']}


# Creates the banner on top of the page
def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.H1("Visualization of Crimes and Crime Prediction in England", style={'display': 'inline'}),
            html.Img(src=(
                'https://sciencebusiness.net/sites/default/files/styles/medium/public/2021-02/TUe-logo-descriptor-stack-scarlet-S%5B1%5D.png?itok=1Ade0EKq'),
                style={'display': 'inline'}),

        ],
    )


# ----------------------------------------------------HTML-------------------------------------------------------------
# *********************************************************************************************************************
# ---------------------------------------------------------------------------------------------------------------------

app = Dash(__name__,
           meta_tags=[
               {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
           ]
           )
app.title = "Visualization Data Challenge 2"
server = app.server

app.layout = html.Div(
    id='root',
    className='root',
    style={'display': 'grid', 'grid-template-columns': ' 20% 50% 30%', 'grid-template-rows': 'auto auto auto',
           'column-gap': '3px'},
    children=[
        html.Div(
            id="header",
            style={'grid-column-start': '1', 'grid-row-start': '1', 'grid-column-end': '4', 'border': 'solid 2px',
                   'border-color': 'dark-blue'
                   },
            children=[
                html.H1("Visualization of Crimes and Crime Prediction in England"),
                html.P(
                    'Maja Burnell, Cheuk Lam Mo, Felipe Franco Bucci Cintra, Stefan Robu,  Mees Thije ook genoemd Boonkkamp ')

            ]),
        html.Div(
            className='options-panel',
            style={'column-span': '1', 'row-span': '1', 'grid-column-start': '1', 'grid-row-start': '2',
                   'border': 'solid 2px',
                   'border-color': 'dark-blue'},
            children=[
                html.H5('options for the Visualization',
                        id='panel-header'),
                html.Div(
                    children=[
                        html.Br(),
                        html.P(id="slider-text",
                               children="Drag the slider to change the year:",
                               ),
                        dcc.Slider(
                            df['Year'].min(),
                            df['Year'].max(),
                            step=None,
                            value=df['Year'].min(),
                            marks={str(year): str(year) for year in df['Year'].unique()},
                            id='year-slider',
                        ),
                    ]),
                html.Br(),
                html.Div(
                    children=[
                        html.P(
                            id="radio-items text",
                            children="Select between a single LSOAS or overview of the counties"),
                        dcc.RadioItems(['county', 'london', 'surrey-heath', 'durham'], 'county', id='radio-LSOA')
                    ]
                ),

            ]
        ),
        html.Div(
            style={'column-span': '1', 'row-span': '1', 'grid-column-start': '2', 'grid-row-start': '2',
                   'border': 'solid 2px',
                   'border-color': 'dark-blue'},
            children=[
                html.Div(
                    id='graph-container1',
                    children=[
                        dcc.Graph(id='graph-with-slider'),
                    dcc.Loading(
                        id="loading-1",
                        type="default",
                        children=html.Div(id="loading-output-1"),
                    ),
                    ],
                ),

            ],
        ),
        html.Div(
            style={'column-span': '1', 'row-span': '1', 'grid-column-start': '3', 'grid-row-start': '2',
                   'border': 'solid 2px',
                   'border-color': 'dark-blue'},
            id='minplots',
            children=[
                html.P(
                    id="rminiplots-text",
                    children="Select: Crime type or Crime trend"),
                dcc.RadioItems(['Crime Type', 'Crime Trend'], 'Crime Type', id='radio-Miniplots'),
                dcc.Graph(id='distplot-1'),

            ],
        ),

    ],
)


# ----------------------------------------------------Callbacks--------------------------------------------------------
# *********************************************************************************************************************
# ---------------------------------------------------------------------------------------------------------------------
@app.callback(Output("loading-output-1", "children"),
              Input('radio-LSOA', 'value'),)
def input_triggers_spinner(value):
    if value != 'county':
        time.sleep(30)



@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('year-slider', 'value'),
    Input('radio-LSOA', 'value'), )
#    Input('Crime-Checkbox', 'value'))
def update_graph(selected_year, selected_LSOA):
    if selected_LSOA == 'county':
        df_selected = df[df['Year'] == selected_year]
        df_selected = df_selected.groupby(['Year', 'county'])['Amount'].sum()
        df_selected = df_selected.reset_index()
        fig = go.Figure(
            data=go.Choropleth(geojson=constituencies, locations=df_selected['county'], z=df_selected['Amount'],
                               colorscale='redor',
                               featureidkey='properties.LAD13NM', marker_line_width=0.015, ))

        fig.update_layout(transition_duration=50)
        fig.update_geos(fitbounds="locations", visible=False)

    else:

        filtered_df = predictions
        a = filtered_df['Amount'] = filtered_df[dic_col[selected_LSOA]].sum().sum()
        p_plot = [codes_dic[selected_LSOA], a]

        fig = go.Figure(data=go.Choropleth(geojson=lsoas, locations=[p_plot[0]], z=[p_plot[1]],
                                           colorscale='Teal',
                                           featureidkey='properties.LSOA11CD', marker_line_width=0.015,
                                           ))

        fig.update_layout(transition_duration=500)
        fig.update_geos(fitbounds="locations", visible=False)

    return fig


@app.callback(
    Output('distplot-1', 'figure'),
    Input('radio-LSOA', 'value'),
    Input('radio-Miniplots', 'value'),
    Input('graph-with-slider', 'clickData')
)
def update_graph(selected_LSOA, miniplot, selected_county):
    if miniplot == 'Crime Trend':
        if selected_LSOA == 'county' and selected_county is not None:
            county = df[df['county'] == selected_county['points'][0]['location']]
            county = county.groupby(['Year'])['Amount'].sum()
            county = county.reset_index()
            y_plot = county['Amount']

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=y_plot.index, y=y_plot, mode='lines', line={'color': colors['Blue']}, name='crimes'))

            fig.update_layout(
                title_text='Trend of Crimes' + selected_county['points'][0]['location'] + ' County',
                font_size=12
            )
            return fig

        elif selected_LSOA == "county" and selected_county is None:
            county = df
            county = county.groupby(['Year'])['Amount'].sum()
            county = county.reset_index()
            y_plot = county['Amount']
            #
            # p_plot = predictions.groupby(['Year', 'Month']).sum()
            # p_plot = p_plot.sum(axis=1)
            # p_plot = p_plot.reset_index()
            # p_plot['i'] = p_plot.index + 10

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=y_plot.index, y=y_plot, mode='lines', line={'color': colors['Blue'], }, name='crimes'))
            fig.update_layout(
                title_text='Crimes in England',
            )
            return fig

        else:
            county = df[df['LSOA_code'] == codes_dic[selected_LSOA]]
            county = county.groupby(['Year', 'Month'])['Amount'].sum()
            county = county.reset_index()
            y_plot = county['Amount']

            p_plot = predictions[dic_col[selected_LSOA]].sum(axis=1)

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=y_plot.index, y=y_plot, mode='lines', line={'color': colors['Blue']}, name='crimes'))
            fig.add_trace(
                go.Scatter(x=p_plot.index + 97, y=p_plot, mode='lines', line={'color': 'orange'}, name='prediction'))

            return fig

    else:
        if selected_LSOA == 'county' and selected_county is not None:
            county = df[df['county'] == selected_county['points'][0]['location']]
            county = county.groupby(['Crime_type']).sum()
            county = county.reset_index()
            y_plot = county['Amount']

            fig = {}
            fig = px.bar(county, x='Crime_type', y='Amount')
            fig.update_layout(
                title_text='Type I,II Crimes in ' + selected_county['points'][0]['location'] + 'county',
            )
            return fig

        elif selected_LSOA == "county" and selected_county is None:
            county = df
            county = county.groupby(['Crime_type']).sum()
            county = county.reset_index()
            fig = px.bar(county, x='Crime_type', y='Amount')
            fig.update_layout(
                title_text='Type I,II Crimes in England',
            )
            return fig

        else:
            county = df[df['LSOA_code'] == codes_dic[selected_LSOA]]
            county = county.groupby(['Crime_type']).sum()
            county = county.reset_index()
            y_plot = county['Amount']

            p_plot = predictions[dic_col[selected_LSOA]].sum()
            p_plot =p_plot.reset_index()
            p_plot['Amount'] = p_plot[0]
            p_plot['i'] = p_plot['index']

            fig = px.bar(county, x='Crime_type', y='Amount')
            fig.add_bar( x='i', y='Amount')
            fig.update_layout(
                title_text='Type I,II Crimes' + selected_LSOA,
            )
            return fig

if __name__ == '__main__':
    app.run_server(debug=False, threaded=True)
