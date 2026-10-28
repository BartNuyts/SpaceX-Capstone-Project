
# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# TASK 1: Create dropdown options for launch site selection
launch_sites = sorted(spacex_df['Launch Site'].dropna().unique())

site_options = [{'label': 'All Sites', 'value': 'ALL'}]
site_options += [
    {'label': site, 'value': site}
    for site in launch_sites
]

# Create the application layout
app.layout = html.Div(children=[

    html.H1(
        'SpaceX Launch Records Dashboard',
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'font-size': 40
        }
    ),

    # TASK 1: Add dropdown list
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True,
        clearable=False
    ),

    html.Br(),

    # TASK 2: Add pie chart
    html.Div(
        dcc.Graph(id='success-pie-chart')
    ),

    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add payload range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={
            i: str(i)
            for i in range(0, 10001, 2500)
        },
        value=[0, 10000]
    ),

    # TASK 4: Add scatter chart
    html.Div(
        dcc.Graph(id='success-payload-scatter-chart')
    )

])


# TASK 2: Callback for the pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):

    if entered_site == 'ALL':

        filtered_df = spacex_df[spacex_df['class'] == 1]

        fig = px.pie(
            filtered_df,
            names='Launch Site',
            title='Total Success Launches By Site'
        )

    else:

        filtered_df = spacex_df[
            spacex_df['Launch Site'] == entered_site
        ]

        counts = (
            filtered_df['class']
            .value_counts()
            .reindex([0, 1], fill_value=0)
            .reset_index()
        )

        counts.columns = ['class', 'count']

        counts['Outcome'] = counts['class'].map({
            0: 'Failure',
            1: 'Success'
        })

        fig = px.pie(
            counts,
            values='count',
            names='Outcome',
            title=f'Success vs. Failure for {entered_site}'
        )

    return fig


# TASK 4: Callback for the scatter chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def get_scatter_chart(entered_site, payload):

    low, high = payload

    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if entered_site == 'ALL':

        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites',
            hover_data=['Launch Site']
        )

    else:

        filtered_df = filtered_df[
            filtered_df['Launch Site'] == entered_site
        ]

        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for {entered_site}',
            hover_data=['Launch Site']
        )

    fig.update_yaxes(
        tickvals=[0, 1],
        ticktext=['Failure', 'Success']
    )

    return fig


# Run the application
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)
