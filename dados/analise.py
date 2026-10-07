import sqlite3
import unicodedata
import pandas as pd

# 1. Conexão ao banco (rode o script a partir da pasta que contém "dados/")
conn = sqlite3.connect('dados/consorcio.db')

# 2. Carregar tabelas
df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
df_cotas = pd.read_sql_query("SELECT * FROM cotas", conn)
df_contemplacoes = pd.read_sql_query("SELECT * FROM contemplacoes", conn)
df_parceiros = pd.read_sql_query("SELECT * FROM parceiros", conn)
df_grupos = pd.read_sql_query("SELECT id_grupo, qtd_cotas_grupo, data_abertura FROM grupos", conn)

# 3. Limpeza
# 3.1 Cotas duplicadas: 70 id_cota aparecem 2x (69 linhas idênticas e 1 com parceiro divergente).
#     Mantém a linha cujo id_parceiro existe na tabela parceiros.
df_cotas['parceiro_valido'] = df_cotas['id_parceiro'].isin(df_parceiros['id_parceiro'])
df_cotas = (df_cotas.sort_values('parceiro_valido', ascending=False)
                    .drop_duplicates(subset='id_cota', keep='first')
                    .drop(columns='parceiro_valido')
                    .sort_values('id_cota')
                    .reset_index(drop=True))

# 3.2 Padronizar categoria (19 grafias -> 4 categorias)
def padroniza(txt):
    t = unicodedata.normalize('NFKD', str(txt)).encode('ascii', 'ignore').decode().lower().strip()
    mapa = {'celular': 'celular', 'smartphone': 'celular',
            'auto': 'automovel', 'automovel': 'automovel',
            'imoveis': 'imovel', 'imovel': 'imovel',
            'servicos': 'servicos', 'servico': 'servicos'}
    return mapa.get(t, t)

df_cotas['categoria'] = df_cotas['categoria'].map(padroniza)

# 4. Cruzamento (cota -> cliente, contemplação, parceiro, grupo)
df_completo = (df_cotas
               .merge(df_clientes, on='id_cliente', how='left')
               .merge(df_contemplacoes.drop(columns='id_grupo'), on='id_cota', how='left')
               .merge(df_parceiros, on='id_parceiro', how='left')
               .merge(df_grupos, on='id_grupo', how='left'))

assert df_completo['id_cota'].is_unique, "Há id_cota duplicado na base final"

# 5. Métricas gerais
total_cotas = df_cotas['id_cota'].nunique()
total_contempladas = df_contemplacoes['id_cota'].nunique()
taxa_contemplacao = total_contempladas / total_cotas * 100

print(f"Total de Cotas: {total_cotas}")
print(f"Cotas Contempladas: {total_contempladas}")
print(f"Taxa de Contemplação: {taxa_contemplacao:.2f}%")

print("\nDistribuição por tipo de contemplação:")
print(df_completo['tipo_contemplacao'].value_counts())

print("\nCotas por status:")
print(df_completo['status_cota'].value_counts())

# 6. Salvar base unificada
df_completo.to_csv('base_completa_analise.csv', index=False)
print("\nBase unificada salva em 'base_completa_analise.csv' com sucesso!")

# 7. Resultado enxuto (sem dados pessoais de clientes), mesmas colunas da entrega
resultado = (df_cotas
             .merge(df_contemplacoes.rename(columns={'id_grupo': 'id_grupo_y'}), on='id_cota', how='left')
             .rename(columns={'id_grupo': 'id_grupo_x'}))
colunas = ['id_cota', 'id_grupo_x', 'id_cliente', 'id_parceiro', 'canal_venda', 'categoria',
           'valor_credito', 'prazo_meses', 'taxa_adm_pct', 'valor_parcela', 'data_adesao',
           'status_cota', 'data_cancelamento', 'id_contemplacao', 'id_grupo_y',
           'data_assembleia', 'tipo_contemplacao', 'valor_lance']
resultado[colunas].to_csv('resultado_analise.csv', index=False)
print(f"resultado_analise.csv salvo com {len(resultado)} linhas.")
