import sqlite3
import pandas as pd

# 1. Conexão à base de dados
conn = sqlite3.connect('dados/consorcio.db')

# 2. Carregar todas as tabelas
df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
df_cotas = pd.read_sql_query("SELECT * FROM cotas", conn)
df_contemplacoes = pd.read_sql_query("SELECT * FROM contemplacoes", conn)

# 3. Cruzamento dos dados
df_completo = df_cotas.merge(df_clientes, on='id_cliente', how='left')
df_completo = df_completo.merge(df_contemplacoes, on='id_cota', how='left')

# 4. Métricas Gerais
total_cotas = len(df_cotas)
total_contempladas = len(df_contemplacoes)
taxa_contemplacao = (total_contempladas / total_cotas) * 100

print(f"Total de Cotas: {total_cotas}")
print(f"Cotas Contempladas: {total_contempladas}")
print(f"Taxa de Contemplação: {taxa_contemplacao:.2f}%")

# 5. Identificar colunas disponíveis na tabela de contemplações
colunas_contemplacao = df_contemplacoes.columns.tolist()
print("\nColunas presentes na tabela contemplacoes:", colunas_contemplacao)

# 6. Distribuição por tipo de contemplação (caso a coluna exista)
for col in ['tipo_contemplacao', 'tipo', 'tp_contemplacao']:
    if col in df_completo.columns:
        print(f"\nDistribuição por {col}:")
        print(df_completo[col].value_counts())
        break

# 7. Salvar base completa unificada
df_completo.to_csv('base_completa_analise.csv', index=False)
print("\nBase unificada salva em 'base_completa_analise.csv' com sucesso!")