# Manual de Customização Visual — FinAuto Dashboard

## Visão Geral

O visual do dashboard é controlado em dois lugares:

| Arquivo | O que controla |
|---|---|
| `.streamlit/config.toml` | Cores base, fundo, cor primária |
| `dashboard.py` (linhas 24–184) | Todo o CSS customizado (cards, botões, tabelas, calendário, etc.) |

---

## 1. Cores Principais — `.streamlit/config.toml`

```toml
[theme]
base                   = "dark"
backgroundColor        = "#0f1117"   # Fundo geral da página
secondaryBackgroundColor = "#1a1b26" # Fundo de cards e sidebar
primaryColor           = "#6366f1"   # Cor de destaque (botões, inputs ativos)
textColor              = "#e8eaf0"   # Cor do texto principal
font                   = "sans serif"
```

**Como trocar o tema para claro:**
```toml
base                   = "light"
backgroundColor        = "#ffffff"
secondaryBackgroundColor = "#f8fafc"
primaryColor           = "#6366f1"
textColor              = "#1e293b"
```

**Trocar a cor de destaque (roxa → azul, por exemplo):**
```toml
primaryColor = "#3b82f6"
```

---

## 2. CSS Customizado — `dashboard.py` (linha 24)

Todo o bloco de CSS está dentro de `st.markdown("""<style> ... </style>""", unsafe_allow_html=True)`.

### 2.1 Paleta de Cores Completa

Abaixo estão todas as cores usadas no projeto e onde ficam:

```
Fundo geral da página        → #0f1117   (config.toml)
Fundo de cards/sidebar       → #1a1b26   (config.toml + CSS)
Fundo de inputs              → #1e2030   (CSS, linha ~73)
Sidebar                      → #151621   (CSS, linha ~56)

Texto principal              → #e8eaf0
Texto secundário (labels)    → rgba(232,234,240,0.4)  ← mude o último número (0.0 a 1.0)

Cor de destaque (indigo)     → #6366f1   (botões, dia selecionado)
Hover do botão primário      → #4f46e5
Tags multiselect (fundo)     → rgba(99,102,241,0.18)
Tags multiselect (borda)     → rgba(99,102,241,0.30)
Tags multiselect (texto)     → #a5b4fc

Verde (receitas/sucesso)     → #22c55e
Vermelho (despesas/erro)     → #ef4444
Azul (informação)            → #3b82f6
Amarelo (alerta)             → #f59e0b
```

---

### 2.2 Cards KPI (métricas no topo)

**Localização:** `dashboard.py`, linha 33 (CSS) e linha 203 (função `kpi_card`)

**CSS do card:**
```css
div[data-testid="metric-container"] {
    background: #1a1b26;           /* cor de fundo do card */
    border: 1px solid rgba(255,255,255,0.07);  /* borda sutil */
    border-radius: 10px;           /* arredondamento dos cantos */
    padding: 16px 18px;            /* espaçamento interno */
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);   /* sombra */
}
```

**Exemplos de variações:**

```css
/* Card mais arredondado */
border-radius: 16px;

/* Card com borda colorida */
border: 1px solid rgba(99,102,241,0.3);

/* Card sem sombra */
box-shadow: none;

/* Fundo levemente mais claro */
background: #1e2030;
```

**Label do card (texto pequeno em cima):**
```css
div[data-testid="stMetricLabel"] > div {
    font-size: 11px;         /* tamanho da letra */
    color: rgba(232,234,240,0.45);  /* opacidade do texto */
    text-transform: uppercase;      /* MAIÚSCULAS — remova para normal */
    letter-spacing: 0.04em;         /* espaçamento entre letras */
}
```

**Valor do card (número grande):**
```css
div[data-testid="stMetricValue"] > div {
    font-size: 22px;         /* tamanho do número — aumente para destaque */
    font-weight: 700;        /* negrito */
    color: #e8eaf0;          /* cor do número */
}
```

---

### 2.3 Botões

**Botão Primário (azul/roxo — "Nova transação", "Salvar"):**
```css
.stButton > button[kind="primary"] {
    background: #6366f1;     /* cor de fundo — troque aqui */
    border-radius: 7px;      /* arredondamento */
    font-weight: 600;
    font-size: 13px;
}
.stButton > button[kind="primary"]:hover {
    background: #4f46e5;     /* cor quando o mouse passa por cima */
}
```

**Botão Secundário (cinza — "Cancelar", filtros):**
```css
.stButton > button[kind="secondary"],
.stButton > button:not([kind="primary"]) {
    background: #1e2030;
    border: 1px solid rgba(255,255,255,0.11);
    color: rgba(232,234,240,0.6);
    border-radius: 7px;
    font-size: 13px;
}
```

---

### 2.4 Sidebar (barra lateral de filtros)

```css
section[data-testid="stSidebar"] {
    background: #151621;                          /* cor de fundo da sidebar */
    border-right: 1px solid rgba(255,255,255,0.07); /* borda direita */
}
```

**Labels dos filtros na sidebar:**
```css
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: rgba(232,234,240,0.4);
}
```

---

### 2.5 Inputs (select, text, multiselect)

```css
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div > input {
    background: #1e2030;                        /* fundo do input */
    border: 1px solid rgba(255,255,255,0.11);   /* borda */
    border-radius: 7px;                         /* arredondamento */
    color: #e8eaf0;                             /* cor do texto digitado */
    font-size: 12px;
}
```

**Tags do multiselect (ex: múltiplos status selecionados):**
```css
span[data-baseweb="tag"] {
    background-color: rgba(99,102,241,0.18);   /* fundo da tag */
    border: 1px solid rgba(99,102,241,0.3);    /* borda da tag */
    border-radius: 100px;                      /* formato pílula */
}
span[data-baseweb="tag"] span {
    color: #a5b4fc;    /* cor do texto da tag */
    font-size: 11px;
}
```

---

### 2.6 Tabela de Transações

```css
div[data-testid="stDataEditor"],
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.07);  /* borda da tabela */
    border-radius: 10px;                       /* cantos arredondados */
    overflow: hidden;
}
```

---

### 2.7 Calendário

**Células do calendário (botões dos dias):**
```css
/* Para selecionar especificamente os botões do calendário de 7 colunas */
[data-testid="stColumns"]:has(> [data-testid="stColumn"]:nth-child(7)) .stButton > button {
    min-height: 68px;   /* altura mínima de cada dia */
    font-size: 11px;
    padding: 8px 10px;
    border-radius: 9px;
}
```

**Dia selecionado:**
```css
[data-testid="stColumns"]:has(> [data-testid="stColumn"]:nth-child(7)) .stButton > button[kind="primary"] {
    background: rgba(99,102,241,0.22);   /* fundo do dia selecionado */
    border: 1px solid #6366f1;           /* borda colorida */
    box-shadow: 0 0 0 2px rgba(99,102,241,0.18);
}
```

---

### 2.8 Títulos e Subtítulos

```css
h2, h3 {
    letter-spacing: -0.02em;
    font-weight: 700;
    color: #e8eaf0;   /* cor dos títulos — troque aqui */
}
```

---

### 2.9 Divisor (linha horizontal)

```css
hr {
    border-color: rgba(255,255,255,0.07);  /* cor da linha divisória */
    margin: 20px 0;
}
```

---

### 2.10 Alertas (mensagens de sucesso/erro)

```css
div[data-testid="stAlert"] {
    border-radius: 9px;
    border: 1px solid;   /* a cor da borda vem do tipo do alerta */
}
```

---

## 3. Fonte Tipográfica

**Localização:** `dashboard.py`, linha 26

```python
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
}
```

**Para trocar a fonte**, substitua `Inter` por qualquer fonte do [Google Fonts](https://fonts.google.com):

```python
# Exemplo: usar a fonte "Nunito"
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Nunito', sans-serif !important;
}
```

---

## 4. Título e Ícone da Aba do Navegador

**Localização:** `dashboard.py`, linha 22

```python
st.set_page_config(page_title="FinAuto", page_icon="💰", layout="wide")
```

- `page_title` → texto que aparece na aba do navegador
- `page_icon` → emoji ou URL de imagem `.ico`
- `layout` → `"wide"` ocupa toda a largura | `"centered"` centraliza o conteúdo

---

## 5. Título Principal do Dashboard

**Localização:** `dashboard.py`, linha 213

```python
st.title("💰 FinAuto — Dashboard")
st.caption("Seu controle financeiro automatizado via WhatsApp.")
```

Troque o texto diretamente aqui.

---

## 6. Cores dos Gráficos

Os gráficos usam a biblioteca **Altair**. Para mudar as cores das barras, procure por `color=alt.value(...)` no `dashboard.py`:

```python
# Gráfico de saídas (despesas) — atualmente vermelho
color=alt.value("#ef4444")

# Gráfico de entradas (receitas) — atualmente verde
color=alt.value("#22c55e")
```

Troque o valor hex pela cor desejada.

---

## 7. Esconder/Mostrar Menu e Rodapé do Streamlit

**Localização:** `dashboard.py`, linha 180

```css
#MainMenu { visibility: hidden; }   /* esconde o menu hamburger ≡ */
footer    { visibility: hidden; }   /* esconde "Made with Streamlit" */
```

Para mostrar novamente, troque `hidden` por `visible`.

---

## 8. Fluxo de Edição — Passo a Passo

```
1. Abra dashboard.py no editor
2. Localize o bloco st.markdown("""<style> ... </style>""") — linhas 24 a 184
3. Encontre o seletor CSS que controla o elemento que quer mudar (use a tabela acima)
4. Altere o valor desejado (cor, tamanho, arredondamento, etc.)
5. Salve o arquivo
6. O Streamlit recarrega automaticamente — veja o resultado no navegador
```

> **Dica:** Use `Ctrl+F` no editor e busque pelo nome do componente (ex: `KPI`, `BOTÃO`, `SIDEBAR`) — os comentários no CSS estão em maiúsculas para facilitar a busca.

---

## 9. Referência Rápida de Cores por Componente

| Componente | Propriedade | Valor atual | Linha aprox. |
|---|---|---|---|
| Fundo da página | `backgroundColor` | `#0f1117` | config.toml |
| Cards KPI | `background` | `#1a1b26` | 34 |
| Sidebar | `background` | `#151621` | 56 |
| Inputs | `background` | `#1e2030` | 73 |
| Botão primário | `background` | `#6366f1` | 93 |
| Hover botão primário | `background` | `#4f46e5` | 101 |
| Texto principal | `color` | `#e8eaf0` | 51 |
| Receitas (gráfico) | `color` | `#22c55e` | ~650 |
| Despesas (gráfico) | `color` | `#ef4444` | ~630 |
| Dia selecionado | `border` | `#6366f1` | 161 |

---

## 10. Exemplo: Trocar Tema Roxo → Verde

Para trocar toda a identidade visual de roxo (`#6366f1`) para verde (`#10b981`):

**`config.toml`:**
```toml
primaryColor = "#10b981"
```

**`dashboard.py`** — substitua todas as ocorrências de `#6366f1` por `#10b981` e `#4f46e5` por `#059669`:

Use `Ctrl+H` (substituir) no seu editor:
- Buscar: `#6366f1` → Substituir por: `#10b981`
- Buscar: `#4f46e5` → Substituir por: `#059669`
- Buscar: `99,102,241` → Substituir por: `16,185,129`
