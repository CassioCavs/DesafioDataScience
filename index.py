from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Carregar os dados do arquivo CSV
df = pd.read_csv('vendasnovo.csv', sep=',')

# Iniciar o aplicativo Dash
app = Dash(__name__)

# Layout da aplicação
app.layout = html.Div([
    html.H3("Supermarket sales"),
    dcc.Dropdown(
        id='rating-dropdown',
        options=[{'label': col, 'value': col} for col in df.columns if col == 'Rating'],
        value='Rating'
    ),
    dcc.Graph(id='pizza_graph'),
    html.H4(id='media-mensal-text'),
    html.H4("Produtos Mais Caros por Categoria de Produto:"),
    dcc.Dropdown(
        id='product-line-dropdown',
        options=[{'label': linha, 'value': linha} for linha in df['Product line'].unique()],
        value=df['Product line'].unique()[0]
    ),
    html.Div(id='produtos-mais-caros-por-categoria'),
    html.H4(id='correlacao-preco-vendas'),
    html.Div(id='produtos-mais-populares'),
    html.Div(id='produtos-menos-populares'),

    dcc.Graph(id='scatter-plot'),
    dcc.Graph(id='customer-profile'),
    dcc.Graph(id='sales-months'),
    dcc.Graph(id='revenue-by-branch'),
    dcc.Graph(id='sales-pattern-weekend-vs-weekday')
])

# Callback para atualizar o gráfico de pizza
@app.callback(
    Output('pizza_graph', 'figure'),
    Input('rating-dropdown', 'value')
)
def update_pizza_graph(selected_column):
    if selected_column is None:
        return go.Figure()

    # Calcular a média de avaliações por categoria de produto
    media_avaliacoes_por_categoria = df.groupby('Product line')[selected_column].mean().reset_index()

    # Criar um gráfico de pizza Plotly
    fig = go.Figure(data=[go.Pie(
        labels=media_avaliacoes_por_categoria['Product line'],
        values=media_avaliacoes_por_categoria[selected_column],
        hole=0.3,
        textinfo='percent+label',
        insidetextorientation='radial'
    )])

    # Atualizar o layout do gráfico
    fig.update_layout(
        title=f'Avaliações por Categoria de Produto ({selected_column})'
    )

    return fig

# Callback para atualizar a lista dos 5 produtos mais caros por categoria de produto
@app.callback(
    Output('produtos-mais-caros-por-categoria', 'children'),
    Input('product-line-dropdown', 'value')
)
def update_produtos_mais_caros(selected_product_line):
    # Filtrar o DataFrame pela linha de produto selecionada
    df_filtered = df[df['Product line'] == selected_product_line]

    # Encontrar os 5 produtos mais caros por linha de produto e indicar o Invoice ID correspondente
    produtos_mais_caros_por_categoria = df_filtered.nlargest(5, 'Unit price')[['Invoice ID', 'Unit price']]

    return html.Div([html.H5(f"Produtos Mais Caros por {selected_product_line}:"), html.Ul([html.Li(f"Invoice ID: {invoice_id} - Preço: ${preco:.2f}") for invoice_id, preco in zip(produtos_mais_caros_por_categoria['Invoice ID'], produtos_mais_caros_por_categoria['Unit price'])])])

# Callback para atualizar a lista dos 10 produtos mais populares
@app.callback(
    Output('produtos-mais-populares', 'children'),
    Input('rating-dropdown', 'value')
)
def update_produtos_mais_populares(selected_column):
    if selected_column is None:
        return ""

    # Encontrar os 10 produtos mais populares e indicar o Invoice ID e a linha de produtos correspondentes
    produtos_mais_populares = df.nlargest(10, 'Rating')[['Invoice ID', 'Rating', 'Product line']]

    return html.Div([html.H5("Produtos Mais Populares:")] + [html.Li(f"Invoice ID: {invoice_id} - Nota: {quantidade} - Linha de Produto: {linha}") for invoice_id, quantidade, linha in zip(produtos_mais_populares['Invoice ID'], produtos_mais_populares['Rating'], produtos_mais_populares['Product line'])])

@app.callback(
    Output('produtos-menos-populares', 'children'),
    Input('rating-dropdown', 'value')
)
def update_produtos_menos_populares(selected_column):
    if selected_column is None:
        return ""

    # Encontrar os 10 produtos menos populares e indicar o Invoice ID correspondente
    produtos_menos_populares = df.nsmallest(10, 'Rating')[['Invoice ID', 'Rating', 'Product line']]
    
    return html.Div([html.H5("Produtos Menos Populares:")] + [html.Li(f"Invoice ID: {invoice_id} - Nota: {nota} - Linha de Produto: {linha}") for invoice_id, nota, linha in zip(produtos_menos_populares['Invoice ID'], produtos_menos_populares['Rating'], produtos_menos_populares['Product line'])])

# Callback para calcular a correlação entre o preço de um produto e a quantidade vendida
@app.callback(
    Output('correlacao-preco-vendas', 'children'),
    Input('product-line-dropdown', 'value')
)
def calcular_correlacao_preco_vendas(selected_product_line):
    # Filtrar o DataFrame pela linha de produto selecionada
    df_filtered = df[df['Product line'] == selected_product_line]

    # Calcular a correlação entre o preço de um produto e a quantidade vendida
    correlacao_preco_vendas = df_filtered['Unit price'].corr(df_filtered['Quantity'])

    return html.H5(f"Correlação entre Preço e Quantidade Vendida para {selected_product_line}: {correlacao_preco_vendas:.2f}")

# Callback para atualizar o texto de média mensal de vendas
@app.callback(
    Output('media-mensal-text', 'children'),
    Input('rating-dropdown', 'value')
)
def calcular_media_mensal_vendas(selected_column):
    if selected_column is None:
        return ""

    # Calcular a média mensal de vendas
    media_mensal_vendas = df['Total'].mean()

    return f"Média Mensal de Vendas: ${media_mensal_vendas:.2f}"

# Mapear os métodos de pagamento para valores numéricos
method_payment_mapping = {
    'Ewallet': 0,
    'Cash': 1,
    'Credit card': 2
}

df['Payment_numeric'] = df['Payment'].map(method_payment_mapping)

def create_scatter_plot():
    # Criar um gráfico de dispersão Plotly
    scatter_fig = go.Figure(data=go.Scatter(
        x=df['Unit price'],
        y=df['Payment_numeric'],  # Usar a coluna com valores numéricos
        mode='markers',
        text=df['Invoice ID'],
        marker=dict(
            size=8,
            color=df['Payment_numeric'],  # Usar a coluna com valores numéricos para as cores
            colorscale='Viridis',  # Escolha uma escala de cores adequada
            colorbar=dict(title='Método de Pagamento')
        )
    ))

    # Atualizar o layout do gráfico de dispersão
    scatter_fig.update_layout(
        title='Correlação entre Preço de Produto e Método de Pagamento',
        xaxis=dict(title='Preço do Produto'),
        yaxis=dict(title='Método de Pagamento')
    )

    return scatter_fig

# Callback para atualizar o gráfico de dispersão
@app.callback(
    Output('scatter-plot', 'figure'),
    Input('rating-dropdown', 'value')
)
def update_scatter_plot(selected_column):
    if selected_column is None:
        return create_scatter_plot()  # Pode definir uma configuração padrão se nenhum valor estiver selecionado

    # Chamando a função create_scatter_plot para gerar o gráfico de dispersão
    return create_scatter_plot()

# Callback para atualizar o gráfico de perfil de cliente que mais compra
@app.callback(
    Output('customer-profile', 'figure'),
    Input('rating-dropdown', 'value')
)
def update_customer_profile(selected_column):
    if selected_column is None:
        return go.Figure()

    # Calcular o perfil de cliente que mais compra com base em cidade, tipo de cliente e gênero
    customer_profile = df.groupby(['City', 'Customer type', 'Gender'])[selected_column].count().reset_index()
    customer_profile = customer_profile.rename(columns={selected_column: 'Count'})

    # Criar um gráfico (por exemplo, um gráfico de barras empilhadas) para representar o perfil do cliente
    fig = px.bar(customer_profile, x='City', y='Count', color='Customer type', facet_col='Gender', labels={'City': 'Cidade', 'Count': 'Contagem'}, title='Perfil de Cliente que Mais Compra')

    return fig

# Callback para atualizar o gráfico de meses de pico e mais fracos de vendas
@app.callback(
    Output('sales-months', 'figure'),
    Input('rating-dropdown', 'value')
)
def update_sales_months(selected_column):
    if selected_column is None:
        return go.Figure()

    # Calcular as vendas mensais totais
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.month
    monthly_sales = df.groupby('Month')['Total'].sum().reset_index()

    # Criar um gráfico (por exemplo, um gráfico de barras) para mostrar as diferenças entre os meses
    fig = px.bar(monthly_sales, x='Month', y='Total', labels={'Month': 'Mês', 'Total': 'Vendas Totais'}, title='Meses de Pico e Mais Fracos de Vendas')

    return fig

# Callback para atualizar o gráfico de filial que gera mais receita
@app.callback(
    Output('revenue-by-branch', 'figure'),
    Input('rating-dropdown', 'value')
)
def update_revenue_by_branch(selected_column):
    if selected_column is None:
        return go.Figure()

    # Calcular a receita total por filial
    revenue_by_branch = df.groupby('Branch')['Total'].sum().reset_index()

    # Criar um gráfico de barras para mostrar a receita por filial
    fig = px.bar(revenue_by_branch, x='Branch', y='Total', labels={'Branch': 'Filial', 'Total': 'Receita Total'}, title='Receita por Filial')

    return fig

# Callback para atualizar o gráfico de padrão de vendas nos fins de semana versus dias de semana
@app.callback(
    Output('sales-pattern-weekend-vs-weekday', 'figure'),
    Input('rating-dropdown', 'value')
)
def update_sales_pattern(selected_column):
    if selected_column is None:
        return go.Figure()

    # Adicionar uma coluna para indicar se a venda ocorreu em um dia da semana ou fim de semana
    df['Weekday_or_weekend'] = df['Date'].dt.dayofweek < 5  # True para dia da semana, False para fim de semana

    # Calcular as vendas totais para dias da semana e fins de semana
    sales_pattern = df.groupby('Weekday_or_weekend')['Total'].sum().reset_index()

    # Criar um gráfico de pizza para mostrar a diferença no padrão de vendas
    fig = go.Figure(data=[go.Pie(
        labels=['Dia da Semana', 'Fim de Semana'],
        values=sales_pattern['Total'],
        hole=0.3,
        textinfo='percent+label',
        insidetextorientation='radial'
    )])

    fig.update_layout(
        title='Padrão de Vendas: Dia da Semana vs. Fim de Semana'
    )

    return fig

# Iniciar o servidor da aplicação
if __name__ == '__main__':
    app.run_server(debug=True, port=8052)
