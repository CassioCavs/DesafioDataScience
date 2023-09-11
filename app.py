import dash
import dash_bootstrap_components as dbc

# Cria uma instância da classe Dash e define o nome do módulo atual (__name__).
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Cria uma variável 'server' que referencia o servidor da aplicação Dash.
# Isso é útil quando você precisa implantar a aplicação em um servidor WSGI como Gunicorn ou uWSGI.
server = app.server