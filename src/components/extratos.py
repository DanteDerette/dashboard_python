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
layout = dbc.Col([
    dbc.Row([
        html.Legend('Tabela de Despesas'),
        html.Div(id='tabela-despesas', className='dbc')
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-graph', style={'margin-left': '20px'})
        ], width=9),

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4('Despesas'),
                    #html.Legend("R$ -", id="valor_despesa_card", style={"font-size": "60px"}),
                    html.Legend("R$ -", id="valor_despesa_card", style={"font-size": "47px"}),
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
    Output('bar-graph', 'figure'),
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
    Output("valor_despesa_card", 'children'),
    Input('store-despesas', 'data')
)
def display_desp(data):
    df = pd.DataFrame(data)
    #pdb.set_trace()
    valor = df['Valor'].sum()

    #return f"R$ {valor}"
    return f"R$ {valor:,.2f}"