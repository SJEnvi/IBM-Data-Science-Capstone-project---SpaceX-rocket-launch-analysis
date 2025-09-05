# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                    ],
                                    value='ALL',
                                    placeholder="place holder here",
                                    searchable=True),
                                    html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                html.P("Payload range (Kg):"),

                                # TASK 3: Add a slider to select payload range
                                
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={
                                        0: '0',
                                        2500: '2500',
                                        5000: '5000',
                                        7500: '7500',
                                        10000: '10000'
                                    },
                                    value=[min_payload, max_payload]
                                ),


                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        # Total successful launches by site (sum of class since class ∈ {0,1})
        fig = px.pie(
            filtered_df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # Filter to selected site; show Success (1) vs Failed (0) counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(
            filtered_df,
            names='class',  # counts occurrences of 0 and 1
            title=f'Total Success vs. Failure for site {entered_site}'
        )
        return fig



# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs,
# and `success-payload-scatter-chart` as output.
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')
)
def update_scatter(selected_site, payload_range):
    # payload_range is [min, max] from the RangeSlider
    low, high = payload_range

    # Filter by payload range first
    df = spacex_df[spacex_df['Payload Mass (kg)'].between(low, high)]

    # If a specific site is selected, filter by site
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]
        title = f'Correlation between Payload and Success for {selected_site}'
    else:
        title = 'Correlation between Payload and Success for All Sites'

    # Scatter: x = Payload Mass (kg), y = class (0/1), color by Booster Version Category
    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site', 'class'],
        title=title
    )

    # Improve axis labels and y ticks
    fig.update_xaxes(title='Payload Mass (kg)')
    fig.update_yaxes(title='Launch Outcome (1 = Success, 0 = Failure)', tickvals=[0, 1])

    return fig


# Run the app
if __name__ == '__main__':
    app.run()
