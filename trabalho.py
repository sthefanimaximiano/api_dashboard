

import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import dash_auth

# Criando o app Dash e configurando autenticação para os usuários
app = Dash(__name__)

url = "https://github.com/mavimelato/visualizacaodados/blob/main/dados.xlsx?raw=true"
df = pd.read_excel(url)

df['Data_Pedido'] = pd.to_datetime(df['Data_Pedido'])
df['Mes'] = df['Data_Pedido'].dt.strftime('%B')


ordem_meses = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

lista_meses = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
lista_meses.append("Todos")

lista_regiao = list(df['Regional'].unique())
lista_regiao.append('Todos')

lista_representante = list(df['Nome_Representante'].unique())
lista_representante.append('Todos')



#Agrupando os meses e quantidade vendida
df_vendas_mes = df.groupby('Mes')['Quantidade_Vendida'].sum().reset_index()
df_vendas_mes['Mes'] = pd.Categorical(df_vendas_mes['Mes'],  categories=ordem_meses, ordered=True)
df_vendas_mes = df_vendas_mes.sort_values('Mes')

df_sale_rep = df.groupby('Nome_Representante')['Quantidade_Vendida'].sum().reset_index()

df_vendas_produto = df.groupby('Nome_Produto')['Quantidade_Vendida'].sum().reset_index()

df_vendas_regiao = df.groupby('Regional')['Quantidade_Vendida'].sum().reset_index()

df_sale_state = df.groupby('Estado_Cliente')['Quantidade_Vendida'].sum().reset_index()


df_agrupados = df.groupby(['Nome_Produto', 'Mes'])['Quantidade_Vendida'].sum().reset_index()
df_agrupados_regional = df.groupby(['Nome_Produto', 'Regional'])['Quantidade_Vendida'].sum().reset_index()
df_agrupados_representante = df.groupby(['Nome_Produto', 'Nome_Representante'])['Quantidade_Vendida'].sum().reset_index()




#App Layout
app.layout = html.Div([

    html.H1(children='Dashboard de Vendas', style={'textAlign': 'center'}),

    html.H2(children='Integrantes: Sthefani Maximiano, Marcos Vinicius', style={'textAlign': 'center'}),

    html.Div([
        html.H3(children="Quantidade Total Vendida Por Mês"),
        dcc.Graph(id="vendas_por_mes", figure=px.line(df_vendas_mes, x='Mes', y='Quantidade_Vendida',  
                title='Quantidade Total Vendida por Mês',
                labels={'Quantidade_Vendida': 'Quantidade_Vendida', 'Mes': 'Mês'},
                template='plotly_dark'))
    ]),

    html.Div([
        html.H3(children="Vendas Por Representante"),
        dcc.Graph(id="vendas_por_representante", figure=px.bar(df_sale_rep, x='Nome_Representante', y='Quantidade_Vendida', color='Nome_Representante', barmode='group', template='plotly_dark'))
    ]),


    html.Div([
        html.H3(children="Quantidade de Vendas por Região"),
        dcc.Graph(id="vendas_por_regiao", figure=px.pie(df_vendas_regiao, values='Quantidade_Vendida', names='Regional', title='Quantidade de Vendas por Região'))
    ]),

    html.Div([
        html.H3(children="Vendas por Estado"),
        dcc.Graph(id="vendas_por_estado", figure=px.bar(df_sale_state, x='Estado_Cliente', y='Quantidade_Vendida', color='Estado_Cliente', barmode='group'))
    ]),

    html.Div([
        html.H3(children="Vendas de Cada Mês", id="subtitulo"),
        dcc.Graph(id="vendas_mes", figure=px.bar(df_vendas_mes, x='Mes', y='Quantidade_Vendida',
             title='Quantidade Total Vendida por Mês', 
             labels={'Quantidade_Vendida': 'Quantidade Vendida', 'Mes': 'Mês'},
             template='plotly_dark', color="Mes", barmode="group")),
        dcc.Dropdown(options=[{'label': mes, 'value': mes} for mes in lista_meses],
                     value="Todos", id='selecao_mes', style={'width': '50%', 'margin': 'auto'})
    ]),

    html.Div([
        html.H3(children="Total de Vendas por Região"),
        dcc.Graph(id='vendas_regiao', figure=px.bar(df_vendas_regiao, x='Regional', y='Quantidade_Vendida',
             title='Quantidade Total Vendida por Região',
             
             template='plotly_dark', color="Regional", barmode="group")),
        dcc.Dropdown(options=[{'label': regiao, 'value': regiao} for regiao in lista_regiao],
                     value="Todos", id='selecao_regiao', style={'width': '50%', 'margin': 'auto'}),
    ]),

    html.Div([
        html.H3(children="Total de Vendas por Representante"),
        dcc.Graph(id='vendas_rep', figure=px.bar(df_sale_rep, x='Nome_Representante', y='Quantidade_Vendida',
             title='Quantidade de Produto Vendido por Representante',
             
             template='plotly_dark', color="Nome_Representante", barmode="group")),
        dcc.Dropdown(options=[{'label': rep, 'value': rep} for rep in lista_representante],
                     value="Todos", id='selecao_rep', style={'width': '50%', 'margin': 'auto'}),
    ]),

    html.Div([
        html.H3(children="Vendas por Estado e Cidade"),
        html.Label('Estado do Cliente'),
        dcc.Dropdown(id='selecao_estado', options=[{'label': estado, 'value': estado} for estado in df['Estado_Cliente'].unique()], value=None),
        html.Label('Cidade do Cliente'),
        dcc.Dropdown(id='selecao_cidade', value=None, multi=True),
        dcc.Graph(id='vendas_estado'),
    ]),

])

@app.callback(
    Output('selecao_cidade', 'options'),
    Input('selecao_estado', 'value')
)
def update_cidades_options(selected_estado):
    cidades_estado = df[df['Estado_Cliente'] == selected_estado]['Cidade_Cliente'].unique()
    options = [{'label': cidade, 'value': cidade} for cidade in cidades_estado]
    return options

@app.callback(
    Output('vendas_estado', 'figure'),
    Input('selecao_estado', 'value'),
    Input('selecao_cidade', 'value')
)
def update_graph(selected_estado, selected_cidades):
    if selected_cidades is None or len(selected_cidades) == 0:
        # Total de vendas por estado
        vendas_por_estado = df.groupby('Estado_Cliente')['Quantidade_Vendida'].sum().reset_index()
        fig = px.bar(vendas_por_estado, x='Estado_Cliente', y='Quantidade_Vendida', title='Total de Vendas por Estado')
    else:
        # Total de vendas por produto na cidade selecionada
        df_filtrado = df[df['Cidade_Cliente'].isin(selected_cidades)]
        vendas_produto = df_filtrado.groupby('Nome_Produto')['Quantidade_Vendida'].sum().reset_index()
        fig = px.bar(vendas_produto, x='Nome_Produto', y='Quantidade_Vendida', title='Quantidade Vendida por Produto na(s) Cidade(s) Selecionada(s)')
    return fig

@app.callback(
        Output('subtitulo', 'children'),
        Output('vendas_mes', 'figure'),
        Output('vendas_regiao', 'figure'),
        Output('vendas_rep', 'figure'),
        Input('selecao_mes', 'value'),
        Input('selecao_regiao', 'value'),
        Input('selecao_rep', 'value')
    )

    
def selecionar(mes, regiao, representante):
    if mes == "Todos" and regiao== "Todos" and representante== "Todos":
        texto = "Vendas de Cada Mês"
        fig1 = px.bar(df_vendas_mes, x='Mes', y='Quantidade_Vendida',
             title='Quantidade Total Vendida por Mês', 
             labels={'Quantidade_Vendida': 'Quantidade Vendida', 'Mes': 'Mês'},
             template='plotly_dark', color="Mes", barmode="group")
        
        fig2 = px.bar(df_vendas_regiao, x='Regional', y='Quantidade_Vendida',
             title='Quantidade Total Vendida por Região',
             labels={'Quantidade_Vendida': 'Quantidade Vendida', 'Regional': 'Região' },
             template='plotly_dark', color="Regional", barmode="group")
        
        fig3 = px.bar(df_sale_rep, x='Nome_Representante', y='Quantidade_Vendida',
             title='Quantidade de Produto Vendido por Representante',
             labels={'Quantidade_Vendida': 'Quantidade Vendida', 'Nome_Representante': 'Representante' },
             template='plotly_dark', color="Nome_Representante", barmode="group")
        
    else:
        df_filtrada = df_agrupados
        df_filtrada2 = df_agrupados_regional
        df_filtrada3 = df_agrupados_representante
        if mes != "Todos":
            df_filtrada = df_filtrada.loc[df_filtrada['Mes']==mes, :]
        if regiao != "Todos":
            df_filtrada2 = df_filtrada2.loc[df_filtrada2['Regional']==regiao, :]
        if representante != "Todos":
            df_filtrada3 = df_filtrada3.loc[df_filtrada3['Nome_Representante']==representante, :]
        
        texto = f"Vendas no Mês de {mes}"
        fig1 = px.bar(df_filtrada, x='Nome_Produto', y='Quantidade_Vendida',
             title='Quantidade Total Vendida por Mês', 
             labels={'Quantidade_Vendida': 'Quantidade Vendida', 'Mes': 'Mês'},
             template='plotly_dark', color="Nome_Produto", barmode="group")
        
        
        fig2 = px.bar(df_filtrada2, x='Nome_Produto', y='Quantidade_Vendida',
             title='Quantidade Total Vendida por Região',
             labels={'Quantidade_Vendida': 'Quantidade Vendida', 'Regional': 'Região' },
             template='plotly_dark', color="Nome_Produto", barmode="group")
        
        fig3 = px.bar(df_filtrada3, x='Nome_Produto', y='Quantidade_Vendida',
             title='Quantidade de Produto Vendido por Representante',
             labels={'Quantidade_Vendida': 'Quantidade Vendida', 'Nome_Representante': 'Representante' },
             template='plotly_dark', color="Nome_Produto", barmode="group")
            
    return texto, fig1, fig2, fig3


if __name__ == '__main__':
    app.run_server(debug=True)
# %%
