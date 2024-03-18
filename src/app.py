from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime
# from components import sidebar

estilos = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
           "https://use.fontawesome.com/releases/v5.15.3/css/all.css",
           "https://fonts.googleapis.com/icon?family=Material+Icons", dbc.themes.VAPOR]

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

# DataFrames and Dcc.Store
date_format = "%Y-%m-%d"  # Example format: YYYY-MM-DD

df_receitas = pd.read_csv("df_receitas.csv", index_col=0)

df_receitas_aux = df_receitas.to_dict()

df_despesas = pd.read_csv("df_despesas.csv", index_col=0)
df_despesas_aux = df_despesas.to_dict()

# for key, value in df_despesas_aux['Data'].items():
#     df_despesas_aux['Data'][key] = datetime.strptime(value, '%Y-%m-%d').date()


# for key, value in df_despesas_aux['Data'].items():
#     print(key, value)
#     print(type(value))

# for key, value in df_despesas_aux.items():
    # print(key, value)



list_receitas = pd.read_csv('df_cat_receita.csv', index_col=0)
list_receitas_aux = list_receitas.to_dict()

list_despesas = pd.read_csv('df_cat_despesa.csv', index_col=0)
list_despesas_aux = list_despesas.to_dict()

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

# app = Dash(__name__)
app = Dash(__name__, external_stylesheets=estilos)

app.config['suppress_callback_exceptions'] = True
app.scripts.config.serve_locally = True
server = app.server

# 
# INÍCIO dashboards.py
# 
from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import calendar
from globals import *

# from app import app

import pdb

card_icon = {
    'color': 'white',
    'textAlign': 'center',
    'contSize': 30,
    'margin': 'auto',
}

graph_margin = dict(l=25, r=25, t=25, b=0)

# =========  Layout  =========== #
layout_Dash = dbc.Col([
    dbc.Row([
    
        # Saldo Total
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Saldo'),
                    html.H5('R$ -', id='p-saldo-dashboards', style={})
                ], style={'padding-left': '20px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa fa-university', style=card_icon),
                    color='warning',
                    style={'maxWidth': 75, 'height': 100, 'margin-left': '-10px'}
                )
            ])
        ]),

        # Receita
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Receita'),
                    html.H5('R$ 10000', id='p-receita-dashboards', style={})
                ], style={'padding-left': '20px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa fa-smile-o', style=card_icon),
                    color='success',
                    style={'maxWidth': 75, 'height': 100, 'margin-left': '-10px'}
                )
            ])
        ]),

        # Despesa
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Despesa'),
                    html.H5('R$ -', id='p-despesa-dashboards', style={})
                ], style={'padding-left': '20px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa fa-meh-o', style=card_icon),
                    color='danger',
                    style={'maxWidth': 75, 'height': 100, 'margin-left': '-10px'}
                )
            ])
        ])
    ], style={'margin': '10px'}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Legend("Filtrar lançamentos", className='card-title'),
                html.Label("Categoria das receitas"),
                html.Div(
                    dcc.Dropdown(
                        id='dropdown-receita',
                        clearable=False,
                        style={"width": "100%"},
                        persistence=True,
                        persistence_type="session",
                        multi=True
                    )
                ),

                html.Label("Categorias das despesas", style={'margin-top': "10px"}),
                dcc.Dropdown(
                    id="dropdown-despesa",
                    clearable=False,
                    style={"width": "100%"},
                    persistence=True,
                    persistence_type="session",
                    multi=True,
                ),

                html.Legend("Perído de Análise", style={"margin-top": "10px"}),
                dcc.DatePickerRange(
                    month_format='Do MMM, YY',
                    end_date_placeholder_text='Data...',
                    #start_date=datetime(2022, 4, 1).date(),
                    start_date=datetime.today() - timedelta(days=datetime.today().day - 1),
                    end_date=datetime.today() + timedelta(days=31 - datetime.today().day),
                    #end_date=datetime.today() + timedelta(days=31),
                    updatemode='singledate',
                    id='date-picker-config',
                    style={'z-index': '100'}
                ),
            ], style={'height': '100%', 'padding': '20px'})
        ], width=4),

        dbc.Col(
            dbc.Card(dcc.Graph(id='graph1'), style={'height': '100%', 'padding': '10px'}), width=8
        )
    ], style={'margin': '10px'}),

    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id='graph2_1'), style={'padding': '10px'}), width=6),
        dbc.Col(dbc.Card(dcc.Graph(id='graph3'), style={'padding': '10px'}), width=3),
        dbc.Col(dbc.Card(dcc.Graph(id='graph4'), style={'padding': '10px'}), width=3),
    ])
])



# =========  Callbacks  =========== #
#---- Filtros e Totais -----
@app.callback(
    [
        Output("dropdown-receita", "options"),
        Output('dropdown-receita', 'value'),
        Output('p-receita-dashboards', 'children')
    ],
    Input('store-receitas', 'data')
)
def populate_dropdownvalues(data):
    #import pdb

    df = pd.DataFrame(data)
    valor = df['Valor'].sum()
    val = df.Categoria.unique().tolist()
    #pdb.set_trace()

    return ([{'label': i, 'value': i} for i in val], val, f"R$ {valor}")


@app.callback(
    [
        Output("dropdown-despesa", "options"),
        Output('dropdown-despesa', 'value'),
        Output('p-despesa-dashboards', 'children')
    ],
    Input('store-despesas', 'data')
)
def populate_dropdownvalues(data):
    #import pdb

    df = pd.DataFrame(data)
    valor = df['Valor'].sum()
    val = df.Categoria.unique().tolist()
    #pdb.set_trace()

    return ([{'label': i, 'value': i} for i in val], val, f"R$ {valor}")

@app.callback(
    Output('p-saldo-dashboards', 'children'),
    [
        Input('store-despesas', 'data'),
        Input('store-receitas', 'data'),
    ]
)
def saldo_total(despesas, receitas):
    df_despesas = pd.DataFrame(despesas)
    df_receitas = pd.DataFrame(receitas)

    valor = df_receitas['Valor'].sum() - df_despesas['Valor'].sum()
    return f"R$ {valor}"


# Gráfico 1
@app.callback(
    Output('graph1', 'figure'),
    [
        Input('store-despesas', 'data'),
        Input('store-receitas', 'data'),
        Input('dropdown-despesa', 'value'),
        Input('dropdown-receita', 'value')
    ]
)
def update_output(data_despesa, data_receita, despesa, receita):
    #import pdb
    df_despesas = pd.DataFrame(data_despesa).set_index("Data")[["Valor"]]
    df_ds = df_despesas.groupby("Data").sum().rename(columns={'Valor': 'Despesa'})

    df_receitas = pd.DataFrame(data_receita).set_index("Data")[["Valor"]]
    df_rc = df_receitas.groupby("Data").sum().rename(columns={'Valor': 'Receita'})

    df_acum = df_ds.join(df_rc, how='outer').fillna(0)
    df_acum["Acum"] = df_acum["Receita"] - df_acum["Despesa"]
    df_acum["Acum"] = df_acum["Acum"].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(name="Fluxo de caixa", x=df_acum.index, y=df_acum["Acum"], mode="lines"))

    #pdb.set_trace()

    fig.update_layout(margin=graph_margin, height=400)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    #fig.update_yaxes(range=[0,8000])
    return fig

#Gráfico 2
@app.callback(
    Output('graph2_1', 'figure'),
    [
        Input('store-receitas', 'data'),
        Input('store-despesas', 'data'),
        Input('dropdown-receita', 'value'),
        Input('dropdown-despesa', 'value'),
        Input('date-picker-config', 'start_date'),
        Input('date-picker-config', 'end_date')
    ]
)
def graph2_show_1(data_receita, data_despesa, receita, despesa, start_date, end_date):
    df_ds = pd.DataFrame(data_despesa)
    df_rc = pd.DataFrame(data_receita)

    df_ds["Output"] = "Despesas"
    df_rc["Output"] = "Receitas"
    df_final = pd.concat([df_ds, df_rc])
    df_final["Data"] = pd.to_datetime(df_final["Data"])

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_final = df_final[(df_final["Data"] >= start_date) & (df_final["Data"] <= end_date)]
    df_final = df_final[(df_final["Categoria"].isin(receita)) | (df_final["Categoria"].isin(despesa))]

    fig = px.bar(df_final, x="Data", y="Valor", color='Output', barmode="group")

    fig.update_layout(title={'text': "Lançamentos no Período"})
    fig.update_layout(margin=graph_margin, height=350)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig

#Gráfico 3
@app.callback(
    Output('graph3', 'figure'),
    [
        Input('store-receitas', 'data'),
        Input('dropdown-receita', 'value')
    ]
)
def pie_receita(data_receita, receita):
    df = pd.DataFrame(data_receita)
    df = df[df['Categoria'].isin(receita)]

    fig = px.pie(df, values=df.Valor, names=df.Categoria, hole=.2)
    fig.update_layout(title={'text': "Receitas"})
    fig.update_layout(margin=graph_margin, height=350)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig

#Gráfico 4
@app.callback(
    Output('graph4', 'figure'),
    [
        Input('store-despesas', 'data'),
        Input('dropdown-despesa', 'value')
    ]
)
def pie_receita(data_despesa, despesa):
    df = pd.DataFrame(data_despesa)
    df = df[df['Categoria'].isin(despesa)]

    fig = px.pie(df, values=df.Valor, names=df.Categoria, hole=.2)
    fig.update_layout(title={'text': "Despesas"})
    fig.update_layout(margin=graph_margin, height=350)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig

# 
#  FIM dashboard.py
# 

# 
# INÍCIO extratos.py
# 

import dash
from dash.dependencies import Input, Output
from dash import Dash, dash_table
from dash.dash_table.Format import Group
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# from app import app
import pdb

# =========  Layout  =========== #
layout_extrato = dbc.Col([
    dbc.Row([
        html.Legend('Tabela de Despesas'),
        html.Div(id='tabela-despesas', className='dbc')
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-graph_1', style={'margin-left': '20px'})
        ], width=9),

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4('Despesas'),
                    html.Legend("R$ -", id="valor_despesa_card_1", style={"font-size": "47px"}),
                    html.H6("Total de despesas"),
                ], style={'text-align': 'center', 'padding-top': '20px'})
            )
        ], width=3)
    ], style={'margin-top': '10px'})
], style={'padding': '10px'})

# =========  Callbacks  =========== #
# Tabela
@app.callback(
    Output('tabela-despesas', 'children'),
    Input('store-despesas', 'data')
)
def imprimir_tabela(data):
    df = pd.DataFrame(data)
    df['Data'] = pd.to_datetime(df['Data']).dt.date
    df = df.fillna('-')
    df.sort_values(by="Data", ascending=False)

    tabela = dash_table.DataTable(df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns])
    return tabela

#Gráfico Despesas
@app.callback(
    Output('bar-graph_1', 'figure'),
    Input('store-despesas', 'data')
)
def bar_chart(data):
    #Transformar num dataframe do Pandas
    df = pd.DataFrame(data)
    #Agrupar o dataframe por categoria, somando os valores "Valor", reseta o index e
    #  coloca o novo df em df_grouped
    df_grouped = df.groupby("Categoria").sum()[['Valor']].reset_index()
    #Gera o gráfico, passando os dados e os nomes dos eixos X e Y e o nome do gráfico
    graph = px.bar(df_grouped, x='Categoria', y='Valor', title="Despesas Gerais")
    #Tira as cores de fundo do gráfico deixando transparente
    graph.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    #pdb.set_trace()

    return graph

@app.callback(
    Output("valor_despesa_card_1", 'children'),
    Input('store-despesas', 'data')
)
def display_desp(data):
    df = pd.DataFrame(data)
    #pdb.set_trace()
    valor = df['Valor'].sum()

    #return f"R$ {valor}"
    return f"R$ {valor:,.2f}"

# 
# FIM extratos.py
# 

# 
# INÍCIO giro360.py
# 

import calendar
import datetime
import locale


import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_bootstrap_templates import template_from_url, ThemeChangerAIO

# from app import app
# from globals import *

arquivo_txt = "desl.txt"
estado_anterior = None
graph_margin = dict(l=25, r=25, t=25, b=0)
currentDate = datetime.date.today()
card_icon = {
    "color": "white",
    "textAlign": "center",
    "fontSize": 20,
    "margin": "auto",
}

# =========  Layout  =========== #
layout_giro360 = dbc.Col([
    dbc.Row([
        # Clientes Ativos
        # ANTES
        # dbc.Col([
        #     dbc.CardGroup([
        #         dbc.Card([
        #             html.Legend("Clientes Ativos"),
        #             html.H5(id='clientes-ativos'),
        #         ], style={"padding-left": "10px", "padding-top": "10px","background-color": "green"})
        #     ]),
        # ]),

        # DEPOIS
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Clientes Ativos'),
                    html.H5('', id='clientes-ativos', style={})
                ], style={'padding-left': '20px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa fa-university', style=card_icon),
                    color='green',
                    style={'maxWidth': 75, 'height': 100, 'margin-left': '-10px'}
                )
            ])
        ]),

        # Clientes Desligados
        # ANTES
        # dbc.Col([
        #     dbc.CardGroup([
        #         dbc.Card([
        #             html.Legend("Clientes Desligados"),
        #             html.H5(id='clientes-desligados'),
        #         ], style={"padding-left": "10px", "padding-top": "10px","background-color": "red"}),
        #     ])
        # ]),
        # DEPOIS
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Clientes Desligados'),
                    html.H5('', id='clientes-desligados', style={})
                ], style={'padding-left': '20px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa fa-university', style=card_icon),
                    color='red',
                    style={'maxWidth': 75, 'height': 100, 'margin-left': '-10px'}
                )
            ])
        ]),

        # Taxa Inadimplência
        # ANTES
        # dbc.Col([
        #     dbc.CardGroup([
        #         dbc.Card([
        #             html.Legend("Taxa Inadimplência"),
        #             html.H5(id='inadimplencia'),
        #         ], style={"padding-left": "10px", "padding-top": "10px","background-color": "gray"}),])
        # ]),
        # DEPOIS
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Taxa Inadimplência'),
                    html.H5('', id='inadimplencia', style={})
                ], style={'padding-left': '20px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa fa-university', style=card_icon),
                    color='gray',
                    style={'maxWidth': 75, 'height': 100, 'margin-left': '-10px'}
                )
            ])
        ]),

        # Contas a Pagar em Atraso
        # ANTES
        # dbc.Col([
        #     dbc.CardGroup([
        #         dbc.Card([
        #             html.Legend("Contas a Pagar em Atraso"),
        #             html.H5(id='contas-pagar'),
        #         ], style={"padding-left": "10px", "padding-top": "10px","background-color": "gray"}),])
        # ], width=3),
        # DEPOIS
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Contas a Pagar em Atraso'),
                    html.H5('', id='contas-pagar', style={})
                ], style={'padding-left': '20px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa fa-university', style=card_icon),
                    color='gray',
                    style={'maxWidth': 75, 'height': 100, 'margin-left': '-10px'}
                )
            ])
        ]),

        # dbc.Col([
        #     dbc.CardGroup([
        #         dbc.Card([
        #             html.Legend(""),
        #             html.H5("", id="p-despesa-dashboards"),
        #         ], style={"display": "none"}),])
        # ], width=1),

        # dbc.Col([
        #     dbc.CardGroup([
        #         dbc.Card([
        #             html.Legend(""),
        #             html.H5("", id="p-receita-dashboards"),
        #         ], style={"display": "none"}),])
        # ], width=1),

    ], style={"margin": "10px"}),
      
      dbc.Row([
        
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend(""),
                    html.H5("", id="p-despesa-dashboards"),
                ], style={"display": "none"}),])
        ], width=1),

        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend(""),
                    html.H5("", id="p-receita-dashboards"),
                ], style={"display": "none"}),])
        ], width=1),

    ], style={"margin": "10px"}),
    

    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Div(
                    dcc.Dropdown(
                        id="dropdown-receita",
                        clearable=False,
                        style={"display": "none"},
                        persistence=True,
                        persistence_type="session",
                        multi=True)
                ),
                dcc.Dropdown(
                    id="dropdown-despesa",
                    clearable=False,
                    style={"display": "none"},
                    persistence=True,
                    persistence_type="session",
                    multi=True
                ),
                html.Legend("Período de Análise", style={"margin-top": "10px"}),
                dcc.DatePickerRange(
                    month_format='Do MMM, YY',
                    end_date_placeholder_text='Data...',
                    start_date=datetime.date(currentDate.year, currentDate.month, 1),
                    end_date=datetime.date(currentDate.year, currentDate.month,
                                           calendar.monthrange(currentDate.year, currentDate.month)[1]),
                    with_portal=True,
                    updatemode='singledate',
                    id='date-picker-config',
                    style={"display": "none"},)],

                style={"display": "none"}),

        ], width=4),
        dbc.Col(dbc.Card(dcc.Graph(id="graph2"), style={"height": "100%", "padding": "10px","margin-top": "15px","margin-left": "-49%"}),width=8),
        ],style={"margin-bottom": "20px"}),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-graph', style={"margin-right": "20px","margin-left": "5px"}),
        ], width=9),

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4("Despesas"),
                    html.Legend("R$ -", id="valor_despesa_card", style={'font-size': '60px'}),
                    html.H6("Total de despesas"),
                ], style={'text-align': 'center', 'padding-top': '30px'}))
        ], width=3),
    ]),

])



@app.callback(
    Output('clientes-ativos', 'children'),
    Input('stored-cat-receitas', 'data')
)
def update_clientes_ativos(data):
    result = len(data['Categoria'])
    return result


@app.callback(
    Output('clientes-desligados', 'children'),
    Input('stored-cat-receitas', 'data')
)
def update_clientes_desligados(data):
    global estado_anterior

    caminho_arquivo = ''
    for root, dirs, files in os.walk(os.getcwd()):
        if 'desl.txt' in files:
            caminho_arquivo = os.path.join(root,'desl.txt')
            print(caminho_arquivo)

    if estado_anterior is None:
        estado_anterior = data.copy()
        with open(caminho_arquivo, 'r') as file:
            valor_atual = int(file.read().strip())
        return valor_atual

    categorias_atuais = set(data['Categoria'])
    categorias_anteriores = set(estado_anterior['Categoria'])

    clientes_desligados = len(categorias_anteriores - categorias_atuais)
    estado_anterior = data.copy()



    with open(caminho_arquivo, 'r') as file:
        valor_atual = int(file.read().strip())

    valor_atual += clientes_desligados

    with open(caminho_arquivo, 'w') as file:
        file.write(str(valor_atual))

    return valor_atual


@app.callback(
    Output('inadimplencia', 'children'),
    Input('store-receitas', 'data')
)
def update_inadimplencia(data):

    df_receita = pd.DataFrame(data)
    
    df_efetuado_0 = df_receita[df_receita['Efetuado'] == 0]
    df_efetuado_1 = df_receita[df_receita['Efetuado'] == 1]
    
    num_categorias_efetuado_0 = len(df_efetuado_0['Categoria'].unique())
    num_categorias_efetuado_1 = len(df_efetuado_1['Categoria'].unique())
    
    if num_categorias_efetuado_1 == 0:
        result = float('inf')
    else:
        result = (num_categorias_efetuado_0 / (num_categorias_efetuado_0 + num_categorias_efetuado_1)) * 100

    result = round(result, 2)

    return f'{result}%'


@app.callback(
    Output('contas-pagar', 'children'),
    Input('store-despesas', 'data')
)
def update_contas_pagar(data):

    df_despesa = pd.DataFrame(data)
    
    total_entradas = len(df_despesa)
    total_efetuado_0 = len(df_despesa[df_despesa['Efetuado'] == 0])
    
    if total_entradas == 0:
        result = float('inf')
    else:
        result = (total_efetuado_0 / total_entradas) * 100
    
    result = round(result, 2)
    
    return f'{result}%'


# Gráfico 2
@app.callback(
    Output('graph2', 'figure'),
    [
        Input('store-receitas', 'data'),
        Input('store-despesas', 'data'),
        Input('dropdown-receita', 'value'),
        Input('dropdown-despesa', 'value'),
        Input('date-picker-config', 'start_date'),
        Input('date-picker-config', 'end_date'),
        # Input(ThemeChangerAIO.ids.radio('theme'), 'value')
    ]
)
# def graph2_show(data_receita, data_despesa, receita, despesa, start_date, end_date, theme):
def graph2_show(data_receita, data_despesa, receita, despesa, start_date, end_date):


    df_ds = pd.DataFrame(data_despesa)
    df_rc = pd.DataFrame(data_receita)

    dfs = [df_ds, df_rc]

    df_rc['Output'] = 'Receitas'
    df_ds['Output'] = 'Despesas'
    df_final = pd.concat(dfs)

    mask = (df_final['Data'] > start_date) & (df_final['Data'] <= end_date)
    df_final = df_final.loc[mask]

    df_final = df_final[df_final['Categoria'].isin(receita) | df_final['Categoria'].isin(despesa)]

    fig = px.bar(
        df_final,
        x="Data",
        y="Valor",
        color='Output',
        barmode="group",
        # paper_bgcolor="#2F303A",
        # font_color="#C0C0C0"
        #template=template_from_url(theme)
    )
    
    #fig.update_layout(margin=graph_margin, template=template_from_url(theme))

    #fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig



# Bar Graph
@app.callback(
    Output('bar-graph', 'figure'),
    [
        Input('store-despesas', 'data')
        # Input(ThemeChangerAIO.ids.radio("theme"), "value")
    ]
)
def bar_chart(data):
# def bar_chart(data, theme):
    df = pd.DataFrame(data)
    df_grouped = df.groupby("Categoria").sum()[["Valor"]].reset_index()
    df_sorted = df_grouped.sort_values(by='Valor', ascending=False)
    df_sorted['Cumulative Percentage'] = (df_sorted['Valor'].cumsum() / df_sorted['Valor'].sum()) * 100

    # Bar chart
    fig = px.bar(df_sorted, x='Categoria', y='Valor', title="Despesas Gerais", labels={'Categoria': 'Categoria', 'Valor': 'Valor'})

    # Line chart for cumulative percentage
    fig.add_trace(go.Scatter(x=df_sorted['Categoria'], y=df_sorted['Cumulative Percentage'], yaxis='y2',
                             mode='lines+markers', name='Cumulative Percentage', line=dict(color='red')))

    fig.update_layout(yaxis=dict(title='Valor'),
                      yaxis2=dict(title='Cumulative Percentage', overlaying='y', side='right'),
                      title="Despesas Gerais",
                    #   template=template_from_url(theme),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig


# Simple card
@app.callback(
    Output('valor_despesa_card', 'children'),
    Input('store-despesas', 'data')
)
def display_desp(data):
    df = pd.DataFrame(data)
    valor = df['Valor'].sum()

    return f"R$ {valor}"

# 
# FIM giro360.py
# 

# 
# INÍCIO sidebar.py
# 

import os
import dash
import json
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# from app import app
from datetime import datetime, date

import pdb
# from dash_bootstrap_templates import ThemeChangerAIO

# ========= DataFrames ========= #
import plotly.express as px
import numpy as np
import pandas as pd
# from globals import *


# ========= Layout ========= #
layout_sidebar = dbc.Card([
    html.H1("MyBudget", className="text-primary"),
    html.P("By DanteDerette", className="text-info"),
    html.Hr(),

    # Seção PERFIL -------------------
    dbc.Button(id='botao_avatar',
               children=[html.Img(src='assets/img_hom.png', id='avatar_change', alt='Avatar', className='perfil_avatar')
                         ], style={'background-color': 'transparent', 'border-color': 'transparent'}),

    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Selecionar Perfil")),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardImg(src="/assets/img_hom.png", className='perfil_avatar', top=True),
                        dbc.CardBody([
                            html.H4("Perfil Homem", className="card-title"),
                            html.P(
                                "Um Card com exemplo do perfil Homem. Texto para preencher o espaço",
                                className="card-text",
                            ),
                            dbc.Button("Acessar", color="warning"),
                        ]),
                    ]),
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardImg(src="/assets/img_fem2.png", top=True, className='perfil_avatar'),
                        dbc.CardBody([
                            html.H4("Perfil Mulher", className="card-title"),
                            html.P(
                                "Um Card com exemplo do perfil Mulher. Texto para preencher o espaço",
                                className="card-text",
                            ),
                            dbc.Button("Acessar", color="warning"),
                        ]),
                    ]),
                ], width=6),
            ], style={"padding": "5px"}),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardImg(src="/assets/img_home.png", top=True, className='perfil_avatar'),
                        dbc.CardBody([
                            html.H4("Perfil Casa", className="card-title"),
                            html.P(
                                "Um Card com exemplo do perfil Casa. Texto para preencher o espaço",
                                className="card-text",
                            ),
                            dbc.Button("Acessar",  color="warning"),
                        ]),
                    ]),
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardImg(src="/assets/img_plus.png", top=True, className='perfil_avatar'),
                        dbc.CardBody([
                            html.H4("Adicionar Novo Perfil", className="card-title"),
                            html.P(
                                "Esse projeto é um protótipo, o botão de adicionar um novo perfil esta desativado momentaneamente!",
                                className="card-text",
                            ),
                            dbc.Button("Adicionar", color="success"),
                        ]),
                    ]),
                ], width=6),
            ], style={"padding": "5px"}),
        ]),
    ],
    style={"background-color": "rgba(0, 0, 0, 0.5)"},
    id="modal-perfil",
    size="lg",
    is_open=False,
    centered=True,
    backdrop=True,
    ),  

    # Seção NOVO ---------------------
    dbc.Row([
        dbc.Col([
            dbc.Button(color='success', id='open-novo-receita',
                       children=['+ Receita'])
        ], width=6),

        dbc.Col([
            dbc.Button(color='danger', id='open-novo-despesa',
                       children=['- Despesa'])
        ], width=6)
    ]),

    # Modal Receita
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('Adicionar Receita')),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label('Descrição: '),
                    dbc.Input(placeholder="Ex.: dividendos na bolsa, herança...", id="txt-receita"),
                ], width=6),
                dbc.Col([
                    dbc.Label('Valor: '),
                    dbc.Input(placeholder="R$100,00", id="valor_receita", value=""),
                ], width=6),
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Data: "),
                    dcc.DatePickerSingle(id='date-receitas',
                        min_date_allowed=date(2020,1,1),
                        max_date_allowed=date(2030,12,31),
                        date=datetime.today(),
                        style={"width": "100%"}
                        ),
                ], width=4),

                dbc.Col([
                    dbc.Label("Extras"),
                    dbc.Checklist(
                        options=[{'label': 'Foi recebida', 'value': 1},
                                 {'label': 'Receita recorrente', 'value': 2}],
                        value=[1],
                        id='switches-input-receita',
                        switch=True
                    )
                ], width=4),

                dbc.Col([
                    html.Label('Categoria da receita'),
                    dbc.Select(id='select_receita',
                               options=[{'label': i, 'value': i} for i in cat_receita],
                               value= cat_receita[0])
                ], width=4),
            ], style={'margin-top': '25px'}),

            dbc.Row([
                dbc.Accordion([
                    dbc.AccordionItem(children=[
                        dbc.Row([
                            dbc.Col([
                                html.Legend("Adicionar categoria", style={'color': 'green'}),
                                dbc.Input(type="text", placeholder="Nova categoria...", id="input-add-receita", value=""),
                                html.Br(),
                                dbc.Button("Adicionar", className="btn btn-success", id="add-category-receita", style={"margin-top": "20px"}),
                                html.Br(),
                                html.Div(id="category-div-add-receita", style={}),
                            ]),

                            dbc.Col([
                                html.Legend('Excluir categorias', style={'color': 'red'}),
                                dbc.Checklist(
                                    id='checklist-selected-style-receita',
                                    options=[{'label': i, 'value': i} for i in cat_receita],
                                    value=[],
                                    label_checked_style={'color': 'red'},
                                    input_checked_style={'backgroundColor': "#fa7268", 'borderColor': "#ea6258"},
                                ),
                                dbc.Button('Remover', color='warning', id='remove-category-receita', style={'margin-top': '20px'}),
                            ], width=6)
                        ])
                    ], title='Adicionar/Remover Categorias')
                ], flush=True, start_collapsed=True, id='accordion-receita'),

                html.Div(id='id_teste_receita', style={'padding-top': '20px'}),
                dbc.ModalFooter([
                    dbc.Button("Adicionar Receita", id="salvar_receita", color="success"),
                    dbc.Popover(dbc.PopoverBody("Receita Salva"), target="salvar_receita", placement="left", trigger="click"),
                ])
            ], style={'margin-top': '25px'}),
        ]),
    ], id='modal-novo-receita',
    style={"background-color": "rgba(17, 140, 79, 0.05)"},
    size="lg",
    is_open=False,
    centered=True,
    backdrop=True,
    ),
    
    # Modal Despesa
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('Adicionar Despesa')),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label('Descrição: '),
                    dbc.Input(placeholder="Ex.: gasolina, petshop...", id="txt-despesa"),
                ], width=6),
                dbc.Col([
                    dbc.Label('Valor: '),
                    dbc.Input(placeholder="R$100,00", id="valor_despesa", value=""),
                ], width=6),
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Data: "),
                    dcc.DatePickerSingle(id='date-despesas',
                        min_date_allowed=date(2020,1,1),
                        max_date_allowed=date(2030,12,31),
                        date=datetime.today(),
                        style={"width": "100%"}
                        ),
                ], width=4),

                dbc.Col([
                    dbc.Label("Extras"),
                    dbc.Checklist(
                        options=[{'label': 'Foi recebida', 'value': 1},
                                 {'label': 'Despesa recorrente', 'value': 2}],
                        value=[1],
                        id='switches-input-despesa',
                        switch=True
                    )
                ], width=4),

                dbc.Col([
                    html.Label('Categoria da despesa'),
                    dbc.Select(id='select_despesa',
                               options=[{'label': i, 'value': i} for i in cat_despesa],
                               value=[cat_despesa[0]])
                ], width=4),
            ], style={'margin-top': '25px'}),

            dbc.Row([
                dbc.Accordion([
                    dbc.AccordionItem(children=[
                        dbc.Row([
                            dbc.Col([
                                html.Legend("Adicionar categoria", style={'color': 'green'}),
                                dbc.Input(type="text", placeholder="Nova categoria...", id="input-add-despesa", value=""),
                                html.Br(),
                                dbc.Button("Adicionar", className="btn btn-success", id="add-category-despesa", style={"margin-top": "20px"}),
                                html.Br(),
                                html.Div(id="category-div-add-despesa", style={}),
                            ]),

                            dbc.Col([
                                html.Legend('Excluir categorias', style={'color': 'red'}),
                                dbc.Checklist(
                                    id='checklist-selected-style-despesa',
                                    options=[{"label": i, "value": i} for i in cat_despesa],
                                    value=[],
                                    label_checked_style={'color': 'red'},
                                    input_checked_style={'backgroundColor': 'blue', 'borderColor': 'orange'},
                                ),
                                dbc.Button('Remover', color='warning', id='remove-category-despesa', style={'margin-top': '20px'}),
                            ], width=6)
                        ])
                    ], title='Adicionar/Remover Categorias')
                ], flush=True, start_collapsed=True, id='accordion-despesa'),

                html.Div(id='id_teste_despesa', style={'padding-top': '20px'}),
                dbc.ModalFooter([
                    dbc.Button("Adicionar Despesa", id="salvar_despesa", color="danger", value="despesa"),
                    dbc.Popover(dbc.PopoverBody("Despesa Salva"), target="salvar_despesa", placement="left", trigger="click"),
                ])
            ], style={'margin-top': '25px'}),
        ]),
    ], id='modal-novo-despesa',
    style={"background-color": "rgba(17, 140, 79, 0.05)"},
    size="lg",
    is_open=False,
    centered=True,
    backdrop=True,
    ),

    # Seção NAV ----------------------
    html.Hr(),
    dbc.Nav(
    [
        dbc.NavLink("Dashboard", href="/painel", active="exact"),
        dbc.NavLink("Extratos", href="/extratos", active="exact"),
        dbc.NavLink("Giro 360", href="/giro360", active="exact"),
    ], vertical=True, pills=True, id='nav_buttons', style={"margin-bottom": "50px"}),
    #pills é o denho em torno do menu quando ele é selecionado. O href vai fazer mudar a url.

], id='sidebar-completa', style={'padding': '10px', 'margin-top': '10px'})





# =========  Callbacks  =========== #
# Pop-up receita
@app.callback(
    Output('modal-novo-receita', 'is_open'),
    Input('open-novo-receita', 'n_clicks'),
    State('modal-novo-receita', 'is_open'),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    
# Pop-up despesa
@app.callback(
    Output('modal-novo-despesa', 'is_open'),
    Input('open-novo-despesa', 'n_clicks'),
    State('modal-novo-despesa', 'is_open'),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open

@app.callback(
    Output('store-receitas', 'data'),
    Input('salvar_receita', 'n_clicks'),
    [
        State('txt-receita', 'value'),
        State('valor_receita', 'value'),
        State('date-receitas', "date"),
        State('switches-input-receita', 'value'),
        State('select_receita', 'value'),
        State('store-receitas', 'data')
    ]
)
def salve_from_receita(n, descricao, valor, date, switches, categoria, dict_receitas):
    #import pdb
    #pdb.set_trace()

    df_receitas = pd.DataFrame(dict_receitas)

    #'if n not None' é o mesmo que 'if n'
    if n and not (valor == "" or valor == None):
        valor = round(float(valor), 2)
        date = pd.to_datetime(date).date()
        categoria = categoria[0] if type(categoria) == list() else categoria
        recebido = 1 if 1 in switches else 0
        fixo = 1 if 2 in switches else 0

        df_receitas.loc[df_receitas.shape[0]] = [valor, recebido, fixo, date, categoria, descricao]
        df_receitas.to_csv("df_receitas.csv")
        
    data_return = df_receitas.to_dict()
    return data_return


@app.callback(
    Output('store-despesas', 'data'),
    Input('salvar_despesa', 'n_clicks'),
    [
        State('txt-despesa', 'value'),
        State('valor_despesa', 'value'),
        State('date-despesas', "date"),
        State('switches-input-despesa', 'value'),
        State('select_despesa', 'value'),
        State('store-despesas', 'data')
    ]
)
def salve_from_despesa(n, descricao, valor, date, switches, categoria, dict_despesas):
    #import pdb
    #pdb.set_trace()

    df_despesas = pd.DataFrame(dict_despesas)

    #'if n not None' é o mesmo que 'if n'
    if n and not (valor == "" or valor == None):
        valor = round(float(valor), 2)
        date = pd.to_datetime(date).date()
        categoria = categoria[0] if type(categoria) == list else categoria
        recebido = 1 if 1 in switches else 0
        fixo = 1 if 2 in switches else 0

        df_despesas.loc[df_despesas.shape[0]] = [valor, recebido, fixo, date, categoria, descricao]
        df_despesas.to_csv("df_despesas.csv")
        
    data_return = df_despesas.to_dict()
    return data_return

#----Callback botões de categorias----
#Despesa
@app.callback(
    #Preciso alterar o select de despesas, as opções de excluir categorias, o nosso dado na memória e os
    #  valores marcados do checklist (Os 3 primeiros são triviais, mas este último não, Rodrigo 
    # só descobriu fazendo)
    [
        Output("select_despesa", "options"),
        Output('checklist-selected-style-despesa', 'options'),
        Output('checklist-selected-style-despesa', 'value'),
        Output('stored-cat-despesas', 'data'),
    ],
    [
        Input('add-category-despesa', 'n_clicks'),
        Input('remove-category-despesa', 'n_clicks'),
    ],
    [
        State('input-add-despesa', 'value'),
        State('checklist-selected-style-despesa', 'value'),
        State('stored-cat-despesas', 'data'),
    ]
)
def add_category(n, n2, txt, check_delete, data):
    #import pdb
    
    #transformar o dicionário de dicionários 'data' em uma lista
    cat_despesa = list(data["Categoria"].values())
    #pdb.set_trace()

    if n and not (txt == "" or txt == None):
        cat_despesa = cat_despesa + [txt] if txt not in cat_despesa else cat_despesa
    
    if n2:
        if len(check_delete) > 0:
            cat_despesa = [i for i in cat_despesa if i not in check_delete]

    opt_despesa = [{'label': i, 'value': i} for i in cat_despesa]
    df_cat_despesa = pd.DataFrame(cat_despesa, columns=['Categoria'])
    df_cat_despesa.to_csv("df_cat_despesa.csv")
    data_return = df_cat_despesa.to_dict()

    #return em ordem dos Outputs do callback
    return [opt_despesa, opt_despesa, [], data_return]

#Receita
@app.callback(
    #Preciso alterar o select de receitas, as opções de excluir categorias, o nosso dado na memória e os
    #  valores marcados do checklist (Os 3 primeiros são triviais, mas este último não, Rodrigo 
    # só descobriu fazendo)
    [
        Output("select_receita", "options"),
        Output('checklist-selected-style-receita', 'options'),
        Output('checklist-selected-style-receita', 'value'),
        Output('stored-cat-receitas', 'data'),
    ],
    [
        Input('add-category-receita', 'n_clicks'),
        Input('remove-category-receita', 'n_clicks'),
    ],
    [
        State('input-add-receita', 'value'),
        State('checklist-selected-style-receita', 'value'),
        State('stored-cat-receitas', 'data'),
    ]
)
def add_category(n, n2, txt, check_delete, data):
    #import pdb
    
    #transformar o dicionário de dicionários 'data' em uma lista
    cat_receita = list(data["Categoria"].values())
    #pdb.set_trace()

    if n and not (txt == "" or txt == None):
        cat_receita = cat_receita + [txt] if txt not in cat_receita else cat_receita
    
    if n2:
        if len(check_delete) > 0:
            cat_receita = [i for i in cat_receita if i not in check_delete]

    opt_receita = [{'label': i, 'value': i} for i in cat_receita]
    df_cat_receita = pd.DataFrame(cat_receita, columns=['Categoria'])
    df_cat_receita.to_csv("df_cat_receita.csv")
    data_return = df_cat_receita.to_dict()

    #return em ordem dos Outputs do callback
    return [opt_receita, opt_receita, [], data_return]

# Pop-up perfis
@app.callback(
    Output("modal-perfil", "is_open"),
    Input("botao_avatar", "n_clicks"),
    State("modal-perfil", "is_open")
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open

# 
# FIM sidebar.py
# 





# =========  Layout  =========== #
# content = html.Div(id="page-content")

# app.layout = html.Div([
#     html.H1(children='Title of Dash App', style={'textAlign':'center'}),
#     dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
#     dcc.Graph(id='graph-content')
# ])

# =========  Layout  =========== #
content = html.Div(id="page-content")

app.layout = dbc.Container(children=[
    dcc.Store(id='store-receitas', data=df_receitas_aux),
    dcc.Store(id="store-despesas", data=df_despesas_aux),
    dcc.Store(id='stored-cat-receitas', data=list_receitas_aux),
    dcc.Store(id='stored-cat-despesas', data=list_despesas_aux),

    dbc.Row([
        dbc.Col([
            dcc.Location(id="url"),
            layout_sidebar
        ], md=2),

        dbc.Col([
            html.Div(id="page-content")
        ], md=10),
    ])

], fluid=True, style={"padding": "0px"}, className="dbc")


# @callback(
#     Output('graph-content', 'figure'),
#     Input('dropdown-selection', 'value')
# )
# def update_graph(value):
#     dff = df[df.country==value]
#     return px.line(dff, x='year', y='pop')

# if __name__ == '__main__':
#     app.run(debug=True)

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/painel" or pathname == "/":
        return layout_Dash

    if pathname == "/extratos":
        return layout_extrato
    
    if pathname == "/giro360":
        return layout_giro360


if __name__ == '__main__':
    app.run_server(debug=True, port='10000')

