import dash_core_components as dcc
import dash_table as dt
import dash_html_components as html
import numpy as np
from .helpers import *
import os
from openml import runs, flows, evaluations, setups, study
import plotly.graph_objs as go

# Font for entire dashboard, we do not have any styling yet
font = [
    "Nunito Sans",
    "-apple-system",
    "BlinkMacSystemFont",
    '"Segoe UI"',
    "Roboto",
    '"Helvetica Neue"',
    "Arial",
    "sans-serif",
    '"Apple Color Emoji"',
    '"Segoe UI Emoji"',
    '"Segoe UI Symbol"'
]


def get_layout_from_data(data_id):
    """

    :param data_id: dataset id
    :return:
     layout: custom layout for data visualization
     df: df cached for use in callbacks

    """
    # Get data and metadata
    df, metadata, numerical_data, nominal_data, name = get_data_metadata(data_id)

    # Define layout
    layout = html.Div(children=[

        # 2. Title
        html.H3(name+' dataset', style={'text-align': 'left', 'text-color': 'black'
                                        }),
        html.P('Choose one or more attributes for distribution plot',
               style={'text-align': 'left', 'color': 'gray',
                      }),
        # 3. Table with meta data
        html.Div([
            # 3a. Table with meta data on left side
            html.Div(
                dcc.Loading(dt.DataTable(
                    data=metadata.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in metadata.columns],
                    row_selectable="multi",
                    sort_action="native",
                    row_deletable=False,
                    selected_rows=[0],
                    #style_as_list_view=True,
                    filter_action="native",
                    id='datatable',
                    style_cell={'textAlign': 'left', 'backgroundColor': 'white',
                                'minWidth': '100px', 'width': '150px', 'maxWidth': '300px',
                                 'textAlign': 'left',
                                "fontFamily": font,
                                'textOverflow': 'ellipsis',"fontSize":14,

                               },
                    style_header={
                        'backgroundColor': 'white',
                        'color': 'grey',
                        'textAlign': 'left'
                    },

                    style_table={
                        'minHeight': '420px',
                        'maxHeight': '420px',
                        'overflowY': 'scroll',
                        'border': 'thin lightgrey solid'
                    },
                    page_action='none',
                    # Select special rows to highlight
                    style_data_conditional=[
                        {
                            "if": {"row_index": 0},
                            "backgroundColor": "rgb(0, 100, 255)",
                            'color': 'white'
                        },
                        {
                            'if': {'column_id': 'Missing values',
                                   'filter_query': '{Missing values} > 0'
                                   },
                            'backgroundColor': 'rgb(255, 200, 200)', 'color': 'white'
                        },
                        {
                            'if': {'column_id': 'Missing values',
                                   'filter_query': '{Missing values} > 10'
                                   },
                            'backgroundColor': 'rgb(255, 100, 100)', 'color': 'white'
                        },
                        {
                             'if': {'column_id':'Missing values',
                                    'filter_query': '{Missing values} > 50'
                                    },
                             'backgroundColor': 'rgb(255, 50, 50)', 'color': 'white'
                        },
                        {
                            'if': {'column_id': 'Missing values',
                                   'filter_query': '{Missing values} > 100'
                                   },
                            'backgroundColor': 'rgb(255, 0, 0)', 'color': 'white'
                        },
                     ]
                ), fullscreen=True),
                style={'width': '45%', 'display': 'inline-block','position': 'relative'}
            ),
            # 3b. Distribution graphs on the right side
            #     Callback for updating this graph = distribution_plot
            html.Div([
                html.Div(
                    dcc.RadioItems(
                        id='radio1',
                        options=[{'label': "Target based distribution", "value": "target"},
                                 {'label': "Individual distribution", "value": "solo"}],
                        value="solo",
                        labelStyle={'display': 'inline-block', 'text-align': 'justify'}

                    )),
                html.Div(
                        dcc.RadioItems(
                            id='stack',
                            value='group',
                            labelStyle={'display': 'inline-block', 'text-align': 'justify'}
                        )),
                html.Div(
                    id='distribution', style={'overflowY': 'scroll', 'width': '100%',
                                              'height': '400px', 'position': 'absolute'}),
            ],  style={'width': '50%', 'display': 'inline-block',
                       'position': 'absolute'}
            ),
        ]),
        # 4. Adding tabs for multiple plots below table and distribution plot
        #    Add another tab for a new plot
        dcc.Tabs(id="tabs", children=[
            dcc.Loading(dcc.Tab(label='Feature Importance', children=[html.Div(id='fi')])),
            dcc.Tab(id="tab2", label='Feature Interactions', children=[
                html.Div([
                    html.Div(
                        dcc.RadioItems(
                            id='radio',
                            options=[{'label': "Top five feature interactions", "value": "top"},
                                     {'label': "Top five numeric feature interactions", "value": "numeric"},
                                     {'label': "Top five nominal feature interactions", "value": "nominal"}],
                            value="top"

                        ), ),
                    html.Div(id='matrix'),
                    html.Div(id='hidden', style={'display': 'none'})


                ])
            ]),
            dcc.Tab(id="tab3", label='Scatter plot', children=[
                html.Div([
                    html.Div(dcc.Dropdown(
                        id='dropdown1',
                        options=[
                            {'label': i, 'value': i} for i in numerical_data
                        ],
                        multi=False,
                        clearable=False,
                        value=numerical_data[0]
                    ), style={'width': '30%'}),
                    html.Div(dcc.Dropdown(
                        id='dropdown2',
                        options=[
                            {'label': i, 'value': i} for i in numerical_data
                        ],
                        multi=False,
                        clearable=False,
                        value=numerical_data[0]

                    ),style={'width': '30%'}),
                    html.Div(dcc.Dropdown(
                        id='dropdown3',
                        options=[
                            {'label': i, 'value': i} for i in nominal_data],
                        multi=False,
                        clearable=False,
                        value=nominal_data[0]), style={'width': '30%'}),
                    html.Div(id='scatter_plot'), ])
            ])if numerical_data and nominal_data else dcc.Tab(label='Scatter Plot',
                                                              children=[html.Div(
                                                                  html.P('No numerical-nominal combination found'))]
                                                              )],
                 )],
        className="container", style={"fontFamily": font})
    return layout, df


def get_layout_from_task(task_id):
    """

    :param task_id:
    :return:
    layout: the layout for task visualization
    df : the df containing measures

    """

    measures = (evaluations.list_evaluation_measures())
    try:
        os.remove('cache/task'+str(task_id)+'.pkl')
    except OSError:
        pass
    layout = html.Div([
        html.Div(id='intermediate-value', style={'display': 'none'}),
        html.Div(children=[
            # Dropdown to choose metric
            html.Div(
                [dcc.Dropdown(
                    id='metric',
                    options=[
                        {'label': i, 'value': i} for i in measures
                    ],
                    multi=False,
                    clearable=False,
                    placeholder="Select an attribute",
                    value=measures[0]
                )],
                style={'width': '30%', 'display': 'inline-block',
                       'position': 'relative'},
            ),
            # Scatter plot flow vs metric

            dcc.Tabs(id="tabs", children=[
                dcc.Loading(fullscreen=True, children=[
                    dcc.Tab(label='Evaluations', children=[html.Div(id='tab1')])]),
                dcc.Tab(label='People', children=[html.Div(id='tab2')])
            ]),
            html.Div(html.Button('Fetch next 1000 runs', id='button')),


        ]),
    ], style={"fontFamily": font, 'width':'100%'})

    return layout, pd.DataFrame(measures)


def get_layout_from_flow(flow_id):
    """

    :param flow_id:
    :return:
    """
    # Dropdown #1 Metrics
    measures = (evaluations.list_evaluation_measures())
    df = pd.DataFrame(measures)
    # Dropdown #2 task types
    task_types = ["Supervised classification", "Supervised regression", "Learning curve",
                  "Supervised data stream classification", "Clustering", "Machine Learning Challenge",
                  "Survival Analysis", "Subgroup Discovery"]
    # Dropdown #3 flow parameters
    P = setups.list_setups(flow=flow_id, size=1, output_format='dataframe')
    parameter_dict = P['parameters'].values[0]
    parameters = [param['full_name'] for key, param in parameter_dict.items()]
    parameters.append('None')
    layout = html.Div([
        html.Div(id='intermediate-value', style={'display': 'none'}),
        html.Div(children=[
            # 1 Dropdown to choose metric
            html.Div(
                [dcc.Dropdown(
                    id='metric',
                    options=[
                        {'label': i, 'value': i} for i in measures
                    ],
                    multi=False,
                    clearable=False,
                    placeholder="Select an attribute",
                    value=measures[0]
                )],
                style={'width': '30%', 'display': 'inline-block',
                       'position': 'relative'},
            ),
            # 2 Dropdown to choose task type
            html.Div(
                [dcc.Dropdown(
                    id='tasktype',
                    options=[
                        {'label': i, 'value': i} for i in task_types
                    ],
                    multi=False,
                    clearable=False,
                    placeholder="Select an attribute",
                    value=task_types[0]
                )],
                style={'width': '30%', 'display': 'inline-block',
                       'position': 'relative'},
            ),
            # 3 Dropdown to choose parameter
            html.Div(
                [dcc.Dropdown(
                    id='parameter',
                    options=[
                        {'label': i, 'value': i} for i in parameters
                    ],
                    multi=False,
                    clearable=False,
                    placeholder="Select an attribute",
                    value=parameters[-1]
                )],
                style={'width': '30%', 'display': 'inline-block',
                       'position': 'relative'},
            ),

            html.Div(
                [dcc.Loading(dcc.Graph(
                    id='flowplot',
                    style={'height': '100%', 'width': '100%',
                           'position': 'absolute'}))],
            ),

        ]),
    ],style={"fontFamily": font})

    return layout, df


def get_layout_from_run(run_id):
    """

    :param run_id: id of the run
    :return: layout for run dashboard
    """
    items = vars(runs.get_run(int(run_id)))
    ordered_dict = (items['fold_evaluations'])
    df = pd.DataFrame(ordered_dict.items(), columns=['evaluations', 'results'])
    result_list = []
    error = []
    for dic in df['results']:
        x = (dic[0])
        values = [x[elem] for elem in x]
        mean = str(round(np.mean(np.array(values), axis=0),3))
        std = str(round(np.std(np.array(values), axis=0),3))
        result_list.append(values)
        error.append(mean+" \u00B1 "+std)
    df.drop(['results'], axis=1, inplace=True)
    df['results'] = result_list
    df['values'] = error
    d = df.drop(['results'], axis=1)
    layout = html.Div([
        html.Div(id='intermediate-value', style={'display': 'none'}),
        # Table with metric on left side
        html.Div([
           html.Div(
               dt.DataTable(
                   data=d.to_dict('records'),
                   columns=[{"name": i, "id": i} for i in d.columns],
                   row_selectable="multi",
                   sort_action="native",
                   row_deletable=False,
                   selected_rows=[0],
                   style_cell={'textAlign': 'left', 'backgroundColor': 'white',
                               'minWidth': '50px', 'width': '150px', 'maxWidth': '300px',
                               'textAlign': 'left',
                               'textOverflow': 'ellipsis', "fontSize": 15,
                               "fontFamily": font
                               },
                   id='runtable'), style={'width': '35%', 'display': 'inline-block',
                                          'position': 'relative'}
           ),
           html.Div(
            id='runplot',
            style={'width': '62%', 'display': 'inline-block',
                   'position': 'absolute',
                   'overflowY': 'scroll', 'height': 500}),
        ]),
        dcc.Tabs(id="tabs", children=[
            dcc.Tab(label='PR chart', children=[dcc.Loading(html.Div(id='pr'))]),
            dcc.Tab(label='ROC Chart', children=[html.Div(id='roc')]),
                 ]),

    ],style={"fontFamily": font})
    # Add some more rows indicating prediction id
    df2 = pd.DataFrame(items['output_files'].items(), columns=['evaluations', 'results'])
    df2["values"] = ""
    df3 = pd.DataFrame({'task_type': items['task_type']}.items(), columns=['evaluations', 'results'])
    df2["values"] = ""
    df = df.append(df2)
    df = df.append(df3)
    df.to_pickle('cache/run'+str(run_id)+'.pkl')
    return layout, df


def get_layout_from_study(study_id):
    """
    params:
    study_id: study id provided
    outpus:
    scatter plot for runs and studies combined
    """
    items = study.get_study(int(study_id))
    run_ids = items.runs[1:10]
    item = evaluations.list_evaluations('predictive_accuracy', id=run_ids, output_format='dataframe', per_fold=False)
    layout = html.Div([
        dcc.Dropdown(
            id = 'dropdown-study',
            options = [
                {'label':'mean-value', 'value':'0'},
                {'label':'folded', 'value':'1'}
            ],
            value = '0'
        ),
        html.Div(id='scatterplot-study'),
    ], style={"fontFamily": font})
    return layout, item



