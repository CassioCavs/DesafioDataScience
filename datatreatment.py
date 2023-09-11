import pandas as pd
import re

df = pd.read_csv('vendas.csv')

colunas_para_excluir = ["cogs", "gross margin percentage", "gross income"]
df = df.drop(columns=colunas_para_excluir)


def substituir_id(match):
    if match.group(1) in ('47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57'):
        return match.group(0)[:-2] + '00'
    return match.group(0)


df['Invoice ID'] = df['Invoice ID'].apply(lambda x: re.sub(r'(\d{2})$', substituir_id, x))


df.to_csv('vendasnovo.csv', index=False)

