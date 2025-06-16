# Import required libraries
import pandas as pd             # For data manipulation and analysis
import dash                     # The main Dash application framework
from dash import html           # For creating HTML components in the Dash layout
from dash import dcc            # For creating interactive Dash Core Components (e.g., dropdowns, sliders, graphs)
from dash.dependencies import Input, Output # For defining callback inputs and outputs
import plotly.express as px     # For creating interactive plots easily

# --- Data Loading and Preparation ---
# Read the SpaceX launch data into a pandas DataFrame
# The data is loaded from a CSV file named "spacex_launch_dash.csv"
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Determine the maximum and minimum payload mass from the DataFrame
# These values will be used to set the range for the payload slider
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# --- Dash Application Initialization ---
# Create a Dash application instance
# __name__ is a special Python variable that gets the name of the current module
app = dash.Dash(__name__)

# --- Dropdown Options Generation ---
# Get a list of unique launch sites from the 'Launch Site' column of the DataFrame
launch_sites = spacex_df['Launch Site'].unique().tolist()

# Prepare the options list for the 'site-dropdown' Dcc.Dropdown component.
# It includes an "All Sites" option and then dynamically adds each unique launch site.
# Each option is a dictionary with 'label' (what the user sees) and 'value' (what the callback receives).
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# --- Dash Application Layout ---
# Define the layout of the Dash application using HTML and Dash Core Components
app.layout = html.Div(children=[
    # Main title of the dashboard
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Add a dropdown list for Launch Site selection
    # Users can select 'All Sites' or a specific launch site.
    dcc.Dropdown(id='site-dropdown',               # Unique ID for this component
                 options=dropdown_options,         # Options generated above
                 value='ALL',                      # Default selected value
                 placeholder="Select a Launch Site here", # Placeholder text
                 searchable=True                   # Allows searching within the dropdown
                 ),
    html.Br(), # Adds a line break for spacing

    # TASK 2: Placeholder for the pie chart
    # This html.Div will contain the dcc.Graph component for the pie chart, which will be updated by a callback.
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(), # Adds a line break for spacing

    # Text label for the payload range slider
    html.P("Payload range (Kg):"),

    # TASK 3: Add a Range Slider to select payload
    # Allows users to select a range of payload mass.
    dcc.RangeSlider(id='payload-slider',          # Unique ID for this component
                    min=0, max=10000,              # Minimum and maximum values for the slider
                    step=1000,                     # Increment step for the slider
                    marks={0: '0', 100: '100'},
                    value=[min_payload, max_payload] # Initial selected range (full range of data)
                    ),
    html.Br(), # Adds a line break for spacing

    # TASK 4: Placeholder for the scatter chart
    # This html.Div will contain the dcc.Graph component for the scatter chart, updated by a callback.
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# --- Dash Callbacks ---

# TASK 2: Callback function to update the 'success-pie-chart'
# This callback triggers when the value of 'site-dropdown' changes.
@app.callback(Output(component_id='success-pie-chart', component_property='figure'), # Output graph
              Input(component_id='site-dropdown', component_property='value'))      # Input from dropdown
def get_pie_chart(entered_site):
    """
    Generates a pie chart based on the selected launch site.
    - If 'ALL' is selected, shows total successful launches by site.
    - If a specific site is selected, shows success vs. failure for that site.
    """
    if entered_site == 'ALL':
        # Filter for all successful launches (class = 1)
        # The 'values' parameter sums up the 'class' column (where 1 means success) for each 'Launch Site'
        fig = px.pie(spacex_df, values='class',
                     names='Launch Site',
                     title='Total Successful Launches By Site')
        return fig
    else:
        # Filter the DataFrame for the selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count the occurrences of success (1) and failure (0) for the selected site
        # .value_counts() returns a Series, reset_index() converts it to a DataFrame
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count'] # Rename columns for clarity

        # Create a pie chart showing success and failure counts
        fig = px.pie(success_counts,
                     values='count',        # The counts for each class (success/failure)
                     names='class',         # The names for the slices (0 or 1)
                     title=f'Total Launch Success and Failure for {entered_site}')
        return fig

# TASK 4: Callback function to update the 'success-payload-scatter-chart'
# This callback triggers when either the 'site-dropdown' or 'payload-slider' values change.
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'), # Output graph
              [Input(component_id='site-dropdown', component_property='value'),           # Input from dropdown
               Input(component_id="payload-slider", component_property="value")])         # Input from slider
def get_scatter_chart(entered_site, payload_range):
    """
    Generates a scatter plot showing correlation between payload and launch outcome.
    - Filters data by the selected payload range.
    - If 'ALL' sites are selected, shows data for all sites within the payload range.
    - If a specific site is selected, shows data for that site within the payload range.
    - Points are colored by 'Booster Version Category'.
    """
    # Extract the lower and upper bounds of the selected payload range
    low, high = payload_range[0], payload_range[1]

    # Filter the entire DataFrame by the selected payload range first
    filtered_payload_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                                     (spacex_df['Payload Mass (kg)'] <= high)]

    if entered_site == 'ALL':
        # If 'ALL' sites are selected, create a scatter plot using the payload-filtered data
        fig = px.scatter(filtered_payload_df,
                         x='Payload Mass (kg)',        # X-axis: Payload Mass
                         y='class',                    # Y-axis: Launch Outcome (0=failure, 1=success)
                         color='Booster Version Category', # Color points by Booster Version
                         title='Correlation between Payload and Success for All Sites (Filtered by Payload)')
        return fig
    else:
        # If a specific launch site is selected, further filter the payload-filtered data by that site
        filtered_site_payload_df = filtered_payload_df[filtered_payload_df['Launch Site'] == entered_site]
        # Create a scatter plot for the specific site and payload range
        fig = px.scatter(filtered_site_payload_df,
                         x='Payload Mass (kg)',        # X-axis: Payload Mass
                         y='class',                    # Y-axis: Launch Outcome
                         color='Booster Version Category', # Color points by Booster Version
                         title=f'Correlation between Payload and Success for {entered_site} Site (Filtered by Payload)')
        return fig

# --- Run the Application ---
# This block ensures the Dash app runs only when the script is executed directly (not imported as a module).
if __name__ == '__main__':
    # Run the server in debug mode, which provides hot-reloading and an interactive debugger.
    app.run(debug = True, port = 8051)
