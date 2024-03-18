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
layout = dbc.Col([
    dbc.Row([
        # Clientes Ativos
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend("Clientes Ativos"),
                    html.H5(id='clientes-ativos'),
                ], style={"padding-left": "10px", "padding-top": "10px","background-color": "green"})
            ]),
        ]),

        # Clientes Desligados
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend("Clientes Desligados"),
                    html.H5(id='clientes-desligados'),
                ], style={"padding-left": "10px", "padding-top": "10px","background-color": "red"}),
            ])
        ]),

        # Taxa Inadimplência
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend("Taxa Inadimplência"),
                    html.H5(id='inadimplencia'),
                ], style={"padding-left": "10px", "padding-top": "10px","background-color": "gray"}),])
        ]),

        # Contas a Pagar em Atraso
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend("Contas a Pagar em Atraso"),
                    html.H5(id='contas-pagar'),
                ], style={"padding-left": "10px", "padding-top": "10px","background-color": "gray"}),])
        ], width=3),

        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend(""),
                    html.H5("", id="p-despesa-dashboards"),
                ], style={"display": "none"}),])
        ], width=3),
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend(""),
                    html.H5("", id="p-receita-dashboards"),
                ], style={"display": "none"}),])
        ], width=3),

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
        Input(ThemeChangerAIO.ids.radio("theme"), "value")
    ]
)
def graph2_show(data_receita, data_despesa, receita, despesa, start_date, end_date, theme):
    df_ds = pd.DataFrame(data_despesa)
    df_rc = pd.DataFrame(data_receita)

    dfs = [df_ds, df_rc]

    df_rc['Output'] = 'Receitas'
    df_ds['Output'] = 'Despesas'
    df_final = pd.concat(dfs)

    mask = (df_final['Data'] > start_date) & (df_final['Data'] <= end_date)
    df_final = df_final.loc[mask]

    df_final = df_final[df_final['Categoria'].isin(receita) | df_final['Categoria'].isin(despesa)]

    fig = px.bar(df_final, x="Data", y="Valor", color='Output', barmode="group")
    fig.update_layout(margin=graph_margin, template=template_from_url(theme))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig



# Bar Graph
@app.callback(
    Output('bar-graph', 'figure'),
    [Input('store-despesas', 'data'),
     Input(ThemeChangerAIO.ids.radio("theme"), "value")]
)
def bar_chart(data, theme):
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
                      template=template_from_url(theme),
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