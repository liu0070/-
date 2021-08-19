import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Output, Input


# 处理数据绘制图表
class Coronavirus_data:
    def __init__(self):
        filename = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
        self.dataframes = pd.read_csv(filename)
        self.all_continents = self.dataframes['continent'].unique()
        self.all_country = self.dataframes['location'].unique()
        self.date = self.dataframes['date'].unique()
        self.date.sort()

    def picture_draw(self):
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        apps = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        apps.layout = html.Div(
            children=[
                dcc.Dropdown(
                    id='country-of-World',
                    options=[{'label': i, 'value': i} for i in self.all_country],
                    value='World',
                ),
                dcc.RadioItems(id='type', options=[{'label': '条形', 'value': '条形'}, {'label': '折线', 'value': '折线'}],
                               value='log')
                , dcc.Graph(id='data-graph'), dcc.Slider(id='graph-slider', )
            ]
        )

        @apps.callback(
            Output('data-graph', 'figure'),
            Input('country-of-World', 'value'),
            Input('type', 'value')
        )
        def update_graph(selected_country, selected_type):
            data = self.dataframes[self.dataframes['location'] == selected_country]
            if selected_type == '条形':
                fig = px.bar(data, x=data['date'], y=data['new_cases'])
                return fig
            else:
                fig = px.line(data, x=data['date'], y=data['new_cases'])
                return fig

        apps.run_server(debug=True)

    def interactive_draw(self):
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        apps = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        x_options = ['cardiovasc_death_rate', 'diabetes_prevalence', 'new_cases_smoothed', 'new_cases',
                     'new_vaccinations',
                     'total_vaccinations_per_hundred', 'new_deaths', 'new_deaths_smoothed',
                     "total_deaths", "people_vaccinated", "people_fully_vaccinated",
                     "people_fully_vaccinated_per_hundred", "new_vaccinations_smoothed_per_million",
                     "stringency_index", "total_deaths_per_million", "reproduction_rate"]
        y_options = ['cardiovasc_death_rate', 'diabetes_prevalence',
                     'new_cases_smoothed', 'new_cases', 'new_vaccinations',
                     'total_vaccinations_per_hundred', 'new_deaths', 'new_deaths_smoothed',
                     "total_deaths", "people_vaccinated", "people_fully_vaccinated",
                     "people_fully_vaccinated_per_hundred", "new_vaccinations_smoothed_per_million",
                     "stringency_index", "total_deaths_per_million", "reproduction_rate"]
        apps.layout = html.Div(children=[html.Div(children=[
            dcc.Dropdown(id='crossfilter-xaxis-column', options=[{'label': i, 'value': i} for i in x_options],
                         value='new_cases'),
            dcc.RadioItems(id='crossfilter-xaxis-type',
                           options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                           value='Linear',
                           labelStyle={'display': 'inline-block', 'marginTop': '5px'})
        ], style={'display': 'inline-block', 'width': '49%', 'float': 'left'}), html.Div(children=[
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in y_options],
                value='new_deaths',
            ),
            dcc.RadioItems(id='crossfilter-yaxis-type',
                           options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                           value='Linear', labelStyle={'display': 'inline-block', 'marginTop': '5px'})
        ], style={'display': 'inline-block', 'width': '49%', 'float': 'right'}),
            html.Div(children=[
                dcc.Graph(id='crossfilter-indicator-scatter', hoverData={'points': [{'customdata': 'China'}]}
                          )
            ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
            html.Div(children=[
                dcc.Graph(id='x-time-series'),
                dcc.Graph(id='y-time-series')
            ], style={'display': 'inline-block', 'width': '49%'}), dcc.Dropdown(
                id='crossfilter-dropdown',
                options=[{'label': i, 'value': i} for i in self.date],
                value=str(self.date[-1])
            )
        ])

        @apps.callback(
            Output('crossfilter-indicator-scatter', 'figure'),
            Input('crossfilter-xaxis-column', 'value'),
            Input('crossfilter-yaxis-column', 'value'),
            Input('crossfilter-xaxis-type', 'value'),
            Input('crossfilter-yaxis-type', 'value'),
            Input('crossfilter-dropdown', 'value')
        )
        def update_graph(xaxis_column, yaxis_column, xaxis_type, yaxis_type, selected_date):
            dff = self.dataframes[self.dataframes['date'] == selected_date]
            fig = px.scatter(x=dff[xaxis_column], y=dff[yaxis_column],
                             hover_name=dff['location'], color=dff['location'])
            fig.update_traces(customdata=dff['location'])
            fig.update_xaxes(title=xaxis_column, type='linear' if xaxis_type == 'Linear' else 'log')
            fig.update_yaxes(title=yaxis_column, type='linear' if yaxis_type == 'Linear' else 'log')
            return fig

        def create_time_series(dff, column, axis_type, title):
            fig = px.scatter(dff, x='date', y=column)
            fig.update_traces(mode='lines+markers')
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log')
            fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom', xref='paper', yref='paper',
                               showarrow=False,
                               align='left', text=title)
            fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})
            return fig

        @apps.callback(
            Output('x-time-series', 'figure'),
            Input('crossfilter-indicator-scatter', 'hoverData'),
            Input('crossfilter-xaxis-column', 'value'),
            Input('crossfilter-xaxis-type', 'value')
        )
        def update_x_time_series(hoverdata, xaxis_column, axistype):
            country_name = hoverdata['points'][0]['hovertext']
            print(hoverdata)
            dff = self.dataframes[self.dataframes['location'] == country_name]
            title = '<b>{}</b><br>{}'.format(country_name, xaxis_column)
            return create_time_series(dff, xaxis_column, axistype, title)

        @apps.callback(
            Output('y-time-series', 'figure'),
            Input('crossfilter-indicator-scatter', 'hoverData'),
            Input('crossfilter-yaxis-column', 'value'),
            Input('crossfilter-yaxis-type', 'value')
        )
        def update_x_time_series(hoverdata, yaxis_column, axistype):
            country_name = hoverdata['points'][0]['hovertext']
            dff = self.dataframes[self.dataframes['location'] == country_name]
            title = '<b>{}</b><br>{}'.format(country_name, yaxis_column)
            return create_time_series(dff, yaxis_column, axistype, title)

        if __name__ == '__main__':
            apps.run_server(debug=True)


app = Coronavirus_data()
app.interactive_draw()
