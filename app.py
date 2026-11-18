import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# 1. Defino a configuração inicial da minha página e o layout em tela cheia
st.set_page_config(
    page_title="Auditoria Inteligente de Faturamento | Keven Soares",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Aplico minha estilização CSS customizada (Dark Executive Theme de alto contraste)
st.markdown("""
<style>
    /* Ajusto o fundo principal e o espaçamento superior/inferior */
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Deixo a barra lateral mais escura e com borda sutil */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    /* Estilizo o meu banner de apresentação de portfólio / PoC */
    .portfolio-badge {
        background: linear-gradient(90deg, #111827 0%, #1e293b 100%);
        border-left: 4px solid #38bdf8;
        border-top: 1px solid #1f2937;
        border-right: 1px solid #1f2937;
        border-bottom: 1px solid #1f2937;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        color: #e2e8f0;
        font-size: 0.92rem;
        line-height: 1.5;
    }
    .portfolio-badge strong {
        color: #38bdf8;
    }
    /* Estilizo os cards de métricas (KPIs) para destacar os números */
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 18px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricLabel"] > div {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #f8fafc !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)


# 3. Crio minha função geradora de dados sintéticos com sazonalidade e anomalias propositais
def gerar_dados_exemplo(dias, faturamento_base):
    np.random.seed(42)  # Fixo a semente para garantir reprodutibilidade nos testes
    datas = pd.date_range(
        end=pd.Timestamp.today().normalize(),
        periods=int(dias),
        freq="D"
    )
    tendencia = np.linspace(faturamento_base * 0.85, faturamento_base * 1.15, int(dias))
    sazonalidade = np.where(datas.dayofweek >= 5, faturamento_base * 0.20, 0)
    ruido = np.random.normal(0, faturamento_base * 0.08, int(dias))
    faturamento = np.maximum(100, tendencia + sazonalidade + ruido)

    df = pd.DataFrame({
        "data": datas,
        "faturamento": np.round(faturamento, 2)
    })

    # Injeto 3 anomalias proporcionais ao histórico para validar o radar do algoritmo
    if len(df) >= 30:
        indices = [int(len(df) * 0.2), int(len(df) * 0.55), int(len(df) * 0.88)]
        df.loc[indices[0], "faturamento"] = round(faturamento_base * 2.4, 2)
        df.loc[indices[1], "faturamento"] = round(faturamento_base * 0.15, 2)
        df.loc[indices[2], "faturamento"] = round(faturamento_base * 2.7, 2)
    return df


# 4. Exibo meu banner de apresentação de portfólio no topo da aplicação
st.markdown("""
<div class="portfolio-badge">
    <strong>📌 Projeto de Portfólio & Prova de Conceito (PoC)</strong> — Desenvolvi esta aplicação
    (<strong>Keven Soares</strong>) para demonstrar na prática como automatizar a detecção de anomalias
    financeiras e operacionais utilizando <strong>Python, Pandas, Estatística Aplicada (Z-Score Móvel) e Plotly</strong>.
    <em>Os dados padrão exibidos são sintéticos para fins de demonstração.</em>
</div>
""", unsafe_allow_html=True)

st.title("🛡️ Auditoria Inteligente de Faturamento")
st.caption("Monitoramento contínuo de séries temporais para detecção de erros de lançamento, duplicidades e rupturas operacionais.")

# 5. Estruturo minha barra lateral com os controles de entrada e autoria
with st.sidebar:
    st.markdown("### ⚙️ Configuração da Análise")
    modo = st.radio(
        "Fonte de Dados:",
        ["Simulação Sintética (Demo)", "Upload de Planilha Própria"]
    )

    arquivo = None
    if modo == "Upload de Planilha Própria":
        arquivo = st.file_uploader(
            "Arquivo (.csv ou .xlsx)",
            type=["csv", "xlsx"],
            help="A planilha deve conter as colunas 'data' e 'faturamento'."
        )
        # Disponibilizo uma planilha modelo para facilitar o teste de quem visita meu projeto
        df_modelo = gerar_dados_exemplo(60, 15000)
        csv_modelo = df_modelo.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Baixar Planilha Modelo (.csv)",
            data=csv_modelo,
            file_name="modelo_faturamento_auditoria.csv",
            mime="text/csv"
        )
    else:
        dias_sim = st.slider("Horizonte Histórico (Dias)", 30, 365, 180, step=15)
        fat_base_sim = st.number_input("Faturamento Médio Diário (R$)", value=18000.0, step=1000.0)

    st.divider()
    st.markdown("### 🎛️ Parâmetros do Modelo")
    janela = st.slider(
        "Janela Móvel (Dias)",
        min_value=7,
        max_value=30,
        value=14,
        help="Quantidade de dias anteriores que uso como base de comparação."
    )
    limiar_z = st.slider(
        "Sensibilidade (Z-Score)",
        min_value=1.5,
        max_value=4.0,
        value=2.8,
        step=0.1,
        help="Quanto menor o valor, mais rigorosa será minha detecção de desvios."
    )

    st.divider()
    st.markdown("""
    **Desenvolvido por**
    **Keven Soares**
    [GitHub (@KevenGSS)](https://github.com/KevenGSS)
    """)

# 6. Faço a ingestão, limpeza e validação dos dados
df = None
if modo == "Upload de Planilha Própria":
    if arquivo is not None:
        try:
            df = pd.read_csv(arquivo) if arquivo.name.endswith(".csv") else pd.read_excel(arquivo)
            df.columns = [c.strip().lower() for c in df.columns]
            if "data" not in df.columns or "faturamento" not in df.columns:
                st.error("❌ Estrutura inválida: a planilha precisa conter as colunas `data` e `faturamento`.")
                st.stop()
            # Uso errors="coerce" para descartar automaticamente linhas de rodapé (ex: TOTAL)
            df["data"] = pd.to_datetime(df["data"], errors="coerce")
            df["faturamento"] = pd.to_numeric(df["faturamento"], errors="coerce")
            df = df.dropna(subset=["data", "faturamento"]).sort_values("data").reset_index(drop=True)
        except Exception as e:
            st.error(f"❌ Falha ao ler o arquivo: {e}")
            st.stop()
    else:
        st.info("👈 Envie uma planilha `.csv` ou `.xlsx` na barra lateral (ou baixe meu modelo de teste) para auditar.")
        st.stop()
else:
    df = gerar_dados_exemplo(dias_sim, fat_base_sim)

# 7. Aplico o motor estatístico (Z-Score Móvel deslocado em 1 dia)
df["media_movel"] = df["faturamento"].rolling(window=janela).mean().shift(1).bfill()
df["desvio_movel"] = df["faturamento"].rolling(window=janela).std().shift(1).bfill().replace(0, 1)
df["z_score"] = (df["faturamento"] - df["media_movel"]) / df["desvio_movel"]
df["anomalia"] = df["z_score"].abs() > limiar_z
df["limite_superior"] = df["media_movel"] + (limiar_z * df["desvio_movel"])
df["limite_inferior"] = np.maximum(0, df["media_movel"] - (limiar_z * df["desvio_movel"]))
df["desvio_rs"] = df["faturamento"] - df["media_movel"]
df["diagnostico"] = np.where(
    ~df["anomalia"],
    "Normal",
    np.where(
        df["z_score"] > 0,
        "🔴 Pico Atípico (Risco de Duplicidade/Erro)",
        "🟠 Queda Brusca (Risco de Falha/Ruptura)"
    )
)

anomalias_df = df[df["anomalia"]].copy()
volume_divergente = anomalias_df["desvio_rs"].abs().sum()

# 8. Organizo a visualização em duas abas: Painel Executivo vs. Minha Metodologia
aba_painel, aba_metodo = st.tabs(["📊 Painel de Auditoria", "🧠 Metodologia & Caso de Uso"])

with aba_painel:
    # Exibo os 4 KPIs principais no topo
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Período Auditado", f"{len(df)} dias")
    c2.metric("Anomalias Isoladas", f"{len(anomalias_df)} ocorrências")
    c3.metric("Divergência Acumulada", f"R$ {volume_divergente:,.2f}")
    c4.metric("Régua Estatística", f"{janela}d | ±{limiar_z}σ")

    st.markdown("<br>", unsafe_allow_html=True)

    # Monto o gráfico interativo Plotly em tema escuro de alto contraste
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=pd.concat([df["data"], df["data"][::-1]]),
        y=pd.concat([df["limite_superior"], df["limite_inferior"][::-1]]),
        fill="toself",
        fillcolor="rgba(56, 189, 248, 0.12)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        name="Banda de Normalidade Esperada"
    ))

    fig.add_trace(go.Scatter(
        x=df["data"],
        y=df["faturamento"],
        mode="lines",
        line=dict(color="#38bdf8", width=2.2),
        name="Faturamento Registrado"
    ))

    fig.add_trace(go.Scatter(
        x=anomalias_df["data"],
        y=anomalias_df["faturamento"],
        mode="markers+text",
        marker=dict(
            color="#f43f5e",
            size=12,
            line=dict(color="#0b0f19", width=2)
        ),
        text=[f"R$ {v/1000:.1f}k" for v in anomalias_df["faturamento"]],
        textposition="top center",
        textfont=dict(color="#fda4af", size=12),
        name="Anomalia Detectada",
        customdata=anomalias_df["diagnostico"],
        hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Registrado:</b> R$ %{y:,.2f}<br><b>Status:</b> %{customdata}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text="<b>Comportamento Diário vs. Limites Dinâmicos de Controle</b>",
            font=dict(size=16, color="#f8fafc")
        ),
        yaxis_title="Faturamento (R$)",
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#cbd5e1"),
        xaxis=dict(gridcolor="#1f2937", zerolinecolor="#1f2937"),
        yaxis=dict(gridcolor="#1f2937", zerolinecolor="#1f2937"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450,
        margin=dict(l=24, r=24, t=64, b=24)
    )

    st.plotly_chart(fig, width="stretch")

    # Exibo o log detalhado e gero a exportação nativa em Excel (.xlsx)
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.subheader("📋 Log de Ocorrências Auditadas")
    with col_t2:
        if not anomalias_df.empty:
            df_export = anomalias_df[["data", "faturamento", "media_movel", "desvio_rs", "z_score", "diagnostico"]].copy()
            df_export["data"] = df_export["data"].dt.strftime("%d/%m/%Y")
            df_export["diagnostico"] = df_export["diagnostico"].str.replace("🔴 ", "").str.replace("🟠 ", "")
            df_export["media_movel"] = df_export["media_movel"].round(2)
            df_export["desvio_rs"] = df_export["desvio_rs"].round(2)
            df_export["z_score"] = df_export["z_score"].round(2)
            df_export.columns = ["Data", "Valor Registrado (R$)", "Média Esperada (R$)", "Impacto (R$)", "Z-Score", "Diagnóstico"]

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_export.to_excel(writer, index=False, sheet_name="Anomalias_Auditadas")
                ws = writer.sheets["Anomalias_Auditadas"]
                for col in ws.columns:
                    max_len = max(len(str(cell.value or "")) for cell in col) + 4
                    ws.column_dimensions[col[0].column_letter].width = max_len

            st.download_button(
                label="⬇️ Exportar Relatório (.xlsx)",
                data=buffer.getvalue(),
                file_name="relatorio_anomalias_auditadas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )

    if anomalias_df.empty:
        st.success("✅ Nenhuma anomalia encontrada para os parâmetros atuais de sensibilidade.")
    else:
        tabela_saida = anomalias_df[["data", "faturamento", "media_movel", "desvio_rs", "z_score", "diagnostico"]].copy()
        tabela_saida["data"] = tabela_saida["data"].dt.strftime("%d/%m/%Y")
        tabela_saida["faturamento"] = tabela_saida["faturamento"].map("R$ {:,.2f}".format)
        tabela_saida["media_movel"] = tabela_saida["media_movel"].map("R$ {:,.2f}".format)
        tabela_saida["desvio_rs"] = tabela_saida["desvio_rs"].map("R$ {:+,.2f}".format)
        tabela_saida["z_score"] = tabela_saida["z_score"].map("{:.2f} σ".format)
        tabela_saida.columns = ["Data", "Valor Registrado", "Média Esperada", "Impacto (R$)", "Desvio (Z-Score)", "Diagnóstico"]
        st.dataframe(tabela_saida, width="stretch", hide_index=True)

with aba_metodo:
    st.markdown("""
    ### Como estruturei este algoritmo para ambientes reais (ERP / Banco de Dados)

    Muitas empresas tentam auditar vendas usando **médias fixas mensais** ou regras estáticas. Na minha experiência com sistemas de gestão, médias fixas falham assim que a empresa cresce ou enfrenta sazonalidade.

    #### 1. Por que utilizei Z-Score Móvel com Deslocamento (`shift`)?
    * **Adaptação à Tendência:** O algoritmo recalcula a média e o desvio-padrão olhando apenas para os últimos $N$ dias (janela móvel configurável).
    * **Prevenção de Contaminação (`shift(1)`):** O dia atual é sempre avaliado contra o histórico fechado até ontem. Isso impede que um erro grave de lançamento distorça a própria régua no dia em que ocorre.

    #### 2. Onde aplico essa arquitetura em projetos reais
    * **Varejo & Distribuição:** Detecção automática de notas fiscais digitadas com zeros a mais ou falhas de sincronização entre PDV e ERP.
    * **Indústria & Serviços:** Alerta preventivo de queda brusca de faturamento por filial ou linha de produto antes do fechamento mensal.
    * **Integração Automatizada:** Em produção, conecto este motor direto ao banco de dados (SQL Server / PostgreSQL) rodando via rotina agendada e disparando alertas automáticos para a diretoria.
    """)
