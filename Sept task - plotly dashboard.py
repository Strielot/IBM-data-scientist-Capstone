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
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Br(),
                                 dcc.Dropdown(id='site-dropdown',
    options=[
        {'label': 'All Sites', 'value': 'ALL'}
    ] + [
        {'label': site, 'value': site} for site in sorted(spacex_df['Launch Site'].unique())
    ],
    value='ALL',
    placeholder="Select a Launch Site here",
    searchable=True),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),


                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                id='payload-slider',
    min=min_payload,   # ← como keyword
    max=max_payload,   # ← como keyword
    step=100,
    marks={i: str(i) for i in range(0, int(spacex_df['Payload Mass (kg)'].max())+1, 2000)},
    value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Conteo de lanzamientos exitosos por sitio
        df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(df, values='class', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        # Conteo de éxitos vs fallos para un sitio específico
        df = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = df['class'].value_counts().reset_index()
        counts.columns = ['Outcome', 'Count']
        counts['Outcome'] = counts['Outcome'].replace({1: 'Success', 0: 'Failure'})
        fig = px.pie(counts, values='Count', names='Outcome',
                     title=f'Success vs. Failed Launches for {selected_site}')
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    # Filtrar por rango de payload
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                             (spacex_df['Payload Mass (kg)'] <= high)]
    
    # Filtrar por sitio si no es "ALL"
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Crear gráfico de dispersión
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',  # opcional: colorear por tipo de booster
        title='Payload vs. Success for Launches',
        hover_data=['Launch Site']
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
