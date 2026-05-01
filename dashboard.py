import calendar
from datetime import datetime
import altair as alt
import pandas as pd
import streamlit as st
from db import (
    listar_transacoes,
    listar_evolucao_mensal,
    atualizar_transacao,
    deletar_transacao,
    listar_proximos,
    listar_atrasadas,
    marcar_como_quitado,
    inserir_transacao,
    listar_categorias,
    gerar_recorrencias,
)
from utils import formatar_moeda

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="FinAuto", page_icon="💰", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
}

div[data-testid="metric-container"] {
    background: #1a1b26 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
}

.alert-danger {
    background: rgba(239,68,68,0.12);
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    color: #fca5a5;
}

.alert-warning {
    background: rgba(245,158,11,0.12);
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    color: #fcd34d;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

hoje = datetime.now()
mes_atual = hoje.month
ano_atual = hoje.year

st.sidebar.header("Filtros")
mes = st.sidebar.selectbox(
    "Mês", list(range(1, 13)), index=mes_atual - 1,
    format_func=lambda x: MESES_PT[x],
)
ano = st.sidebar.selectbox(
    "Ano", list(range(ano_atual, ano_atual - 4, -1)), index=0
)
responsavel_sel = st.sidebar.selectbox("Responsável", ["Todos", "Y", "M", "MY"])
resp_filter = None if responsavel_sel in ("Todos", "MY") else responsavel_sel

st.sidebar.divider()
if st.sidebar.button("🔄 Atualizar dados", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def _carregar_mes(ano, mes, resp):
    raw = listar_transacoes(ano=ano, mes=mes, responsavel=resp)
    return pd.DataFrame(raw) if raw else pd.DataFrame()


@st.cache_data(ttl=60)
def _carregar_evolucao(ano, resp):
    raw = listar_evolucao_mensal(ano=ano, responsavel=resp)
    return pd.DataFrame(raw) if raw else pd.DataFrame()


@st.cache_data(ttl=60)
def _carregar_atrasadas(resp):
    raw = listar_atrasadas(responsavel=resp)
    return pd.DataFrame(raw) if raw else pd.DataFrame()


@st.cache_data(ttl=60)
def _carregar_proximos(resp):
    raw = listar_proximos(dias=30, responsavel=resp)
    return pd.DataFrame(raw) if raw else pd.DataFrame()


df = _carregar_mes(ano, mes, resp_filter)
df_evolucao_raw = _carregar_evolucao(ano, resp_filter)
df_atrasadas = _carregar_atrasadas(resp_filter)
df_proximos = _carregar_proximos(resp_filter)

# ── KPIs ───────────────────────────────────────────────────────────────────────
if not df.empty and "valor" in df.columns:
    receita = df[df["movimentacao"] == "Entrada"]["valor"].sum()
    despesa = df[df["movimentacao"] == "Saída"]["valor"].sum()
    saldo = receita - despesa
    taxa_poupanca = (saldo / receita * 100) if receita > 0 else 0.0

    pago = df[(df["movimentacao"] == "Saída") & (df["status"] == "Pago")]["valor"].sum()
    a_pagar = df[(df["movimentacao"] == "Saída") & (df["status"] == "A pagar")]["valor"].sum()
    recebido = df[(df["movimentacao"] == "Entrada") & (df["status"] == "Recebido")]["valor"].sum()
    a_receber = df[(df["movimentacao"] == "Entrada") & (df["status"] == "A receber")]["valor"].sum()
    n_transacoes = len(df)
else:
    receita = despesa = saldo = taxa_poupanca = 0.0
    pago = a_pagar = recebido = a_receber = 0.0
    n_transacoes = 0

total_atrasado = (
    df_atrasadas["valor"].sum()
    if not df_atrasadas.empty and "valor" in df_atrasadas.columns
    else 0.0
)
total_proximos = (
    df_proximos["valor"].sum()
    if not df_proximos.empty and "valor" in df_proximos.columns
    else 0.0
)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("💰 FinAuto — Dashboard Financeiro")
st.caption(
    f"Período: **{MESES_PT[mes]} / {ano}** · Responsável: **{responsavel_sel}** · {n_transacoes} transações"
)

# ── Alert banners ──────────────────────────────────────────────────────────────
if not df_atrasadas.empty:
    st.markdown(
        f'<div class="alert-danger">⚠️ <b>{len(df_atrasadas)} transações atrasadas</b> — '
        f'Total: <b>{formatar_moeda(total_atrasado)}</b> · Acesse a aba 📅 Agenda para quitar.</div>',
        unsafe_allow_html=True,
    )
if not df_proximos.empty:
    st.markdown(
        f'<div class="alert-warning">🔔 <b>{len(df_proximos)} vencimentos nos próximos 30 dias</b> — '
        f'Total: <b>{formatar_moeda(total_proximos)}</b></div>',
        unsafe_allow_html=True,
    )

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "📈 Análises", "📅 Agenda", "⚙️ Gerenciar"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — VISÃO GERAL
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💵 Receita", formatar_moeda(receita))
    c2.metric("💸 Despesas", formatar_moeda(despesa))
    saldo_delta = f"{saldo:+.2f}".replace(".", ",")
    c3.metric("💰 Saldo Líquido", formatar_moeda(saldo), delta=saldo_delta)
    c4.metric("📈 Taxa de Poupança", f"{taxa_poupanca:.1f}%")

    st.divider()

    cs1, cs2, cs3, cs4 = st.columns(4)
    cs1.metric("✅ Despesas Pagas", formatar_moeda(pago))
    cs2.metric("⏳ A Pagar", formatar_moeda(a_pagar))
    cs3.metric("✅ Receitas Recebidas", formatar_moeda(recebido))
    cs4.metric("⏳ A Receber", formatar_moeda(a_receber))

    st.divider()

    if df.empty:
        st.info(f"Nenhuma transação encontrada para {MESES_PT[mes]}/{ano}.")
    else:
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("🍩 Despesas por Categoria")
            df_cat = (
                df[df["movimentacao"] == "Saída"]
                .groupby("categoria")["valor"]
                .sum()
                .reset_index()
                .sort_values("valor", ascending=False)
            )
            if not df_cat.empty:
                chart_cat = (
                    alt.Chart(df_cat)
                    .mark_arc(innerRadius=65, outerRadius=130)
                    .encode(
                        theta=alt.Theta("valor:Q"),
                        color=alt.Color(
                            "categoria:N",
                            legend=alt.Legend(orient="bottom", columns=2),
                        ),
                        tooltip=[
                            alt.Tooltip("categoria:N", title="Categoria"),
                            alt.Tooltip("valor:Q", title="Valor (R$)", format=",.2f"),
                        ],
                    )
                )
                st.altair_chart(chart_cat, use_container_width=True)
            else:
                st.info("Sem despesas no período.")

        with col_g2:
            st.subheader("📊 Evolução Mensal do Ano")
            if not df_evolucao_raw.empty and "data" in df_evolucao_raw.columns:
                df_ev = df_evolucao_raw.copy()
                df_ev["data"] = pd.to_datetime(df_ev["data"])
                df_ev["mes_ano"] = df_ev["data"].dt.to_period("M").dt.to_timestamp()
                df_ev_agg = (
                    df_ev.groupby(["mes_ano", "movimentacao"])["valor"]
                    .sum()
                    .reset_index()
                )
                chart_evol = (
                    alt.Chart(df_ev_agg)
                    .mark_line(point=True, strokeWidth=2.5)
                    .encode(
                        x=alt.X("mes_ano:T", title="Mês", axis=alt.Axis(format="%b")),
                        y=alt.Y("valor:Q", title="Valor (R$)"),
                        color=alt.Color(
                            "movimentacao:N",
                            scale=alt.Scale(
                                domain=["Entrada", "Saída"],
                                range=["#22c55e", "#ef4444"],
                            ),
                            legend=alt.Legend(title=""),
                        ),
                        tooltip=[
                            alt.Tooltip("mes_ano:T", title="Mês", format="%B/%Y"),
                            alt.Tooltip("movimentacao:N", title="Tipo"),
                            alt.Tooltip("valor:Q", title="Valor (R$)", format=",.2f"),
                        ],
                    )
                )
                st.altair_chart(chart_evol, use_container_width=True)
            else:
                st.info("Sem dados de evolução para o ano selecionado.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANÁLISES
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    if df.empty:
        st.info("Sem dados para análise no período selecionado.")
    else:
        col_a1, col_a2 = st.columns(2)

        with col_a1:
            st.subheader("👤 Despesas por Responsável")
            df_resp = (
                df[df["movimentacao"] == "Saída"]
                .groupby("responsavel")["valor"]
                .sum()
                .reset_index()
            )
            if not df_resp.empty:
                chart_resp = (
                    alt.Chart(df_resp)
                    .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
                    .encode(
                        x=alt.X("responsavel:N", title="Responsável"),
                        y=alt.Y("valor:Q", title="Total (R$)"),
                        color=alt.Color("responsavel:N", legend=None),
                        tooltip=[
                            alt.Tooltip("responsavel:N", title="Responsável"),
                            alt.Tooltip("valor:Q", title="Valor (R$)", format=",.2f"),
                        ],
                    )
                )
                st.altair_chart(chart_resp, use_container_width=True)

        with col_a2:
            st.subheader("💳 Despesas por Fonte de Pagamento")
            df_fonte = (
                df[df["movimentacao"] == "Saída"]
                .groupby("fonte")["valor"]
                .sum()
                .reset_index()
            )
            if not df_fonte.empty:
                chart_fonte = (
                    alt.Chart(df_fonte)
                    .mark_arc(innerRadius=55, outerRadius=110)
                    .encode(
                        theta=alt.Theta("valor:Q"),
                        color=alt.Color("fonte:N", legend=alt.Legend(orient="bottom")),
                        tooltip=[
                            alt.Tooltip("fonte:N", title="Fonte"),
                            alt.Tooltip("valor:Q", title="Valor (R$)", format=",.2f"),
                        ],
                    )
                )
                st.altair_chart(chart_fonte, use_container_width=True)

        st.divider()

        col_a3, col_a4 = st.columns(2)

        with col_a3:
            st.subheader("🔄 Despesas por Tipo")
            df_tipo = (
                df[df["movimentacao"] == "Saída"]
                .groupby("tipo")["valor"]
                .sum()
                .reset_index()
                .sort_values("valor", ascending=True)
            )
            if not df_tipo.empty:
                chart_tipo = (
                    alt.Chart(df_tipo)
                    .mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5)
                    .encode(
                        y=alt.Y("tipo:N", title=None, sort="-x"),
                        x=alt.X("valor:Q", title="Total (R$)"),
                        color=alt.Color("tipo:N", legend=None),
                        tooltip=[
                            alt.Tooltip("tipo:N", title="Tipo"),
                            alt.Tooltip("valor:Q", title="Valor (R$)", format=",.2f"),
                        ],
                    )
                )
                st.altair_chart(chart_tipo, use_container_width=True)

        with col_a4:
            st.subheader("🏆 Top 10 Maiores Despesas")
            cols_top = [c for c in ["descricao", "categoria", "valor", "data", "status"] if c in df.columns]
            df_top = (
                df[df["movimentacao"] == "Saída"]
                .nlargest(10, "valor")[cols_top]
                .reset_index(drop=True)
            )
            df_top_display = df_top.copy()
            df_top_display["valor"] = df_top_display["valor"].apply(formatar_moeda)
            st.dataframe(df_top_display, use_container_width=True, hide_index=True)

        st.divider()

        st.subheader("📋 Distribuição por Status")
        col_s1, col_s2 = st.columns(2)

        CORES_SAIDA = alt.Scale(
            domain=["Pago", "A pagar", "Atrasado"],
            range=["#22c55e", "#f59e0b", "#ef4444"],
        )
        CORES_ENTRADA = alt.Scale(
            domain=["Recebido", "A receber", "Atrasado"],
            range=["#22c55e", "#f59e0b", "#ef4444"],
        )

        with col_s1:
            st.caption("Despesas por status")
            df_st_s = (
                df[df["movimentacao"] == "Saída"]
                .groupby("status")["valor"]
                .sum()
                .reset_index()
            )
            if not df_st_s.empty:
                st.altair_chart(
                    alt.Chart(df_st_s)
                    .mark_arc(innerRadius=45)
                    .encode(
                        theta=alt.Theta("valor:Q"),
                        color=alt.Color("status:N", scale=CORES_SAIDA, legend=alt.Legend(orient="bottom")),
                        tooltip=[
                            alt.Tooltip("status:N", title="Status"),
                            alt.Tooltip("valor:Q", title="Valor (R$)", format=",.2f"),
                        ],
                    ),
                    use_container_width=True,
                )

        with col_s2:
            st.caption("Receitas por status")
            df_st_e = (
                df[df["movimentacao"] == "Entrada"]
                .groupby("status")["valor"]
                .sum()
                .reset_index()
            )
            if not df_st_e.empty:
                st.altair_chart(
                    alt.Chart(df_st_e)
                    .mark_arc(innerRadius=45)
                    .encode(
                        theta=alt.Theta("valor:Q"),
                        color=alt.Color("status:N", scale=CORES_ENTRADA, legend=alt.Legend(orient="bottom")),
                        tooltip=[
                            alt.Tooltip("status:N", title="Status"),
                            alt.Tooltip("valor:Q", title="Valor (R$)", format=",.2f"),
                        ],
                    ),
                    use_container_width=True,
                )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — AGENDA
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    col_ag1, col_ag2 = st.columns(2)

    with col_ag1:
        st.subheader("⚠️ Transações Atrasadas")
        if df_atrasadas.empty:
            st.success("Nenhuma transação atrasada. 🎉")
        else:
            for _, row in df_atrasadas.iterrows():
                c_desc, c_val, c_btn = st.columns([3, 2, 1])
                c_desc.markdown(
                    f"**{row.get('descricao', '-')}**  \n"
                    f"_{row.get('categoria', '-')}_ · {row.get('responsavel', '-')}"
                )
                c_val.markdown(
                    f"**{formatar_moeda(row.get('valor', 0))}**  \n{row.get('data', '-')}"
                )
                if c_btn.button("✅", key=f"at_{row['id']}", help="Marcar como quitado"):
                    marcar_como_quitado(row["id"], row["movimentacao"])
                    st.cache_data.clear()
                    st.rerun()
                st.divider()

    with col_ag2:
        st.subheader("🔔 Próximos Vencimentos (30 dias)")
        if df_proximos.empty:
            st.info("Nenhum vencimento nos próximos 30 dias.")
        else:
            for _, row in df_proximos.iterrows():
                c_desc, c_val, c_btn = st.columns([3, 2, 1])
                c_desc.markdown(
                    f"**{row.get('descricao', '-')}**  \n"
                    f"_{row.get('categoria', '-')}_ · {row.get('responsavel', '-')}"
                )
                c_val.markdown(
                    f"**{formatar_moeda(row.get('valor', 0))}**  \n{row.get('data', '-')}"
                )
                if c_btn.button("✅", key=f"px_{row['id']}", help="Marcar como quitado"):
                    marcar_como_quitado(row["id"], row["movimentacao"])
                    st.cache_data.clear()
                    st.rerun()
                st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — GERENCIAR
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    with st.expander("➕ Adicionar Nova Transação", expanded=False):
        with st.form("form_nova_transacao", clear_on_submit=True):
            c_mov, c_resp, c_tipo = st.columns(3)
            with c_mov:
                mov_manual = st.selectbox("Movimentação", ["Saída", "Entrada"])
            with c_resp:
                resp_manual = st.selectbox("Responsável", ["Y", "M", "MY"])
            with c_tipo:
                tipo_manual = st.selectbox(
                    "Tipo",
                    ["P. Unico", "D. Fixa", "Parcelado", "Receita Fixa", "Receita Variável"],
                )

            c_cat, c_desc, c_val = st.columns(3)
            with c_cat:
                cat_manual = st.selectbox("Categoria", listar_categorias())
            with c_desc:
                desc_manual = st.text_input("Descrição")
            with c_val:
                val_manual = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")

            c_data, c_fonte, c_status = st.columns(3)
            with c_data:
                data_manual = st.date_input("Data", hoje)
            with c_fonte:
                fonte_manual = st.selectbox("Fonte", ["Dinheiro", "Cartão Crédito"])
            with c_status:
                status_manual = st.selectbox(
                    "Status",
                    ["Pago", "A pagar", "Atrasado", "Recebido", "A receber"],
                )

            parcelas_manual = st.text_input(
                "Parcelas (ex: 1/12 — apenas para Parcelado)", value="1"
            )

            if st.form_submit_button("💾 Salvar Transação", use_container_width=True):
                if not desc_manual.strip():
                    st.error("Informe a descrição da transação.")
                else:
                    nova_t = {
                        "movimentacao": mov_manual,
                        "responsavel": resp_manual,
                        "tipo": tipo_manual,
                        "categoria": cat_manual,
                        "descricao": desc_manual.strip(),
                        "valor": val_manual,
                        "data": data_manual.strftime("%Y-%m-%d"),
                        "fonte": fonte_manual,
                        "status": status_manual,
                        "parcelas": parcelas_manual or "1",
                    }
                    try:
                        id_gerado = inserir_transacao(nova_t)
                        gerar_recorrencias(id_gerado)
                        st.success(f"✅ Transação #{id_gerado} inserida com sucesso!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao inserir: {e}")

    st.divider()
    st.subheader(f"📝 Transações de {MESES_PT[mes]}/{ano}")

    if df.empty:
        st.info(f"Nenhuma transação em {MESES_PT[mes]}/{ano}.")
    else:
        todas_cats = listar_categorias()
        df_edit = df.copy()
        df_edit.insert(0, "excluir", False)

        cols_show = [
            "excluir", "id", "data", "descricao", "movimentacao", "categoria",
            "valor", "status", "responsavel", "tipo", "fonte", "parcelas",
        ]
        cols_show = [c for c in cols_show if c in df_edit.columns]

        editado = st.data_editor(
            df_edit[cols_show],
            column_config={
                "excluir": st.column_config.CheckboxColumn("🗑️", width="small"),
                "id": st.column_config.NumberColumn("ID", disabled=True, width="small"),
                "data": st.column_config.DateColumn("Data", disabled=True),
                "descricao": st.column_config.TextColumn("Descrição"),
                "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                "categoria": st.column_config.SelectboxColumn("Categoria", options=todas_cats),
                "movimentacao": st.column_config.SelectboxColumn("Mov.", options=["Saída", "Entrada"]),
                "responsavel": st.column_config.SelectboxColumn("Resp.", options=["Y", "M", "MY"]),
                "tipo": st.column_config.SelectboxColumn(
                    "Tipo",
                    options=["P. Unico", "D. Fixa", "Parcelado", "Receita Fixa", "Receita Variável"],
                ),
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Pago", "A pagar", "Atrasado", "Recebido", "A receber"],
                ),
                "fonte": st.column_config.SelectboxColumn("Fonte", options=["Dinheiro", "Cartão Crédito"]),
                "parcelas": st.column_config.TextColumn("Parcelas", width="small"),
            },
            disabled=["id", "data"],
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
        )

        col_save, col_del, _ = st.columns([1, 1, 3])

        with col_save:
            if st.button("💾 Salvar Alterações", use_container_width=True):
                campos_editaveis = [
                    "descricao", "movimentacao", "categoria", "valor",
                    "status", "responsavel", "tipo", "fonte", "parcelas",
                ]
                alteracoes = 0
                for _, row in editado.iterrows():
                    original = df[df["id"] == row["id"]]
                    if original.empty:
                        continue
                    orig = original.iloc[0]
                    novos = {
                        campo: row[campo]
                        for campo in campos_editaveis
                        if campo in row and campo in orig and row[campo] != orig[campo]
                    }
                    if novos:
                        atualizar_transacao(row["id"], novos)
                        alteracoes += 1
                if alteracoes:
                    st.success(f"✅ {alteracoes} transação(ões) atualizada(s).")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.info("Nenhuma alteração detectada.")

        with col_del:
            if st.button("🗑️ Excluir Marcadas", use_container_width=True):
                para_excluir = editado[editado["excluir"]]["id"].tolist()
                if para_excluir:
                    for id_exc in para_excluir:
                        deletar_transacao(id_exc)
                    st.success(f"✅ {len(para_excluir)} transação(ões) excluída(s).")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("Marque ao menos uma transação para excluir.")
