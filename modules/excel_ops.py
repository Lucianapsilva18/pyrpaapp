"""Módulo de operações Excel/CSV para o PyRPA."""

import io

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class ExcelOperations:

    def read_file(self, uploaded_file) -> dict:
        if not HAS_PANDAS:
            return {"status": "Erro", "message": "Instale: pip install pandas openpyxl"}
        try:
            name = uploaded_file.name.lower()
            if name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            return {"status": "Sucesso", "data": df}
        except Exception as e:
            return {"status": "Erro", "message": str(e)}

    def consolidate(self, files: list) -> dict:
        if not HAS_PANDAS:
            return {"status": "Erro", "message": "Instale: pip install pandas openpyxl"}
        try:
            frames = []
            for f in files:
                name = f.name.lower()
                if name.endswith(".csv"):
                    df = pd.read_csv(f)
                else:
                    df = pd.read_excel(f)
                df["_origem"] = f.name
                frames.append(df)
            result = pd.concat(frames, ignore_index=True)
            return {"status": "Sucesso", "data": result}
        except Exception as e:
            return {"status": "Erro", "message": str(e)}

    def apply_transforms(self, df, transforms: list):
        if not HAS_PANDAS:
            return df
        import pandas as pd

        df = df.copy()
        if "Remover duplicatas" in transforms:
            df = df.drop_duplicates()
        if "Preencher vazios" in transforms:
            for col in df.select_dtypes(include=["number"]).columns:
                df[col] = df[col].fillna(0)
            for col in df.select_dtypes(include=["object"]).columns:
                df[col] = df[col].fillna("")
        if "Converter tipos" in transforms:
            for col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    pass
        if "Filtrar linhas" in transforms:
            df = df.dropna(how="all")
        if "Remover colunas vazias" in transforms:
            df = df.dropna(axis=1, how="all")
        return df

    def generate_script(self, operations: list) -> str:
        sections = []
        sections.append('"""Script de processamento Excel/CSV gerado pelo PyRPA."""\nimport pandas as pd\n')

        if "Leitura" in operations:
            sections.append("""
# ── Leitura ──
def ler_arquivo(caminho: str) -> pd.DataFrame:
    if caminho.endswith('.csv'):
        return pd.read_csv(caminho, encoding='utf-8')
    return pd.read_excel(caminho, engine='openpyxl')

df = ler_arquivo('dados.xlsx')
print(f"Lido: {df.shape[0]} linhas x {df.shape[1]} colunas")
""")

        if "Limpeza" in operations:
            sections.append("""
# ── Limpeza ──
df = df.drop_duplicates()
df = df.dropna(how='all')                  # remove linhas totalmente vazias
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
print(f"Após limpeza: {df.shape}")
""")

        if "Filtro" in operations:
            sections.append("""
# ── Filtro ──
# Ajuste as condições conforme necessário
# df_filtrado = df[df['coluna'] > valor]
# df_filtrado = df[df['status'].isin(['Ativo', 'Aprovado'])]
# df_filtrado = df.query("data >= '2024-01-01'")
df_filtrado = df.copy()
print(f"Após filtro: {df_filtrado.shape}")
""")

        if "Agregação" in operations:
            sections.append("""
# ── Agregação ──
# Ajuste colunas e funções conforme necessário
# resumo = df.groupby('categoria').agg(
#     total=('valor', 'sum'),
#     media=('valor', 'mean'),
#     contagem=('valor', 'count'),
# ).reset_index()
# print(resumo)
""")

        if "Pivot" in operations:
            sections.append("""
# ── Tabela Dinâmica (Pivot) ──
# pivot = pd.pivot_table(
#     df,
#     values='valor',
#     index='departamento',
#     columns='mes',
#     aggfunc='sum',
#     fill_value=0,
# )
# print(pivot)
""")

        if "Exportação" in operations:
            sections.append("""
# ── Exportação ──
df.to_excel('saida.xlsx', index=False, engine='openpyxl')
df.to_csv('saida.csv', index=False, encoding='utf-8-sig')
print("Arquivos exportados com sucesso!")
""")

        return "\n".join(sections)
