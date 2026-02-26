"""
╔══════════════════════════════════════════════════════════════╗
║              🤖 PyRPA - Automação Inteligente               ║
║         Plataforma RPA 100% Python com Streamlit            ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import json
import os
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# ── Módulos internos ──
from modules.file_ops import FileOperations
from modules.web_scraper import WebScraperBot
from modules.excel_ops import ExcelOperations
from modules.email_ops import EmailOperations
from modules.pdf_ops import PDFOperations
from modules.scheduler import TaskScheduler
from modules.workflow_engine import WorkflowEngine
from modules.logger import RPALogger

# ══════════════════════════════════════════════════════════════
# Configuração da Página
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PyRPA - Automação Inteligente",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Personalizado ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 50%, #4a90d9 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
    }
    .main-header h1 {
        margin: 0; font-size: 2rem; font-weight: 700;
    }
    .main-header p {
        margin: 0.3rem 0 0; opacity: 0.85; font-size: 0.95rem;
    }

    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-card .number {
        font-size: 2rem; font-weight: 700; color: #1e3a5f;
    }
    .metric-card .label {
        font-size: 0.85rem; color: #64748b; margin-top: 0.3rem;
    }
    .metric-card .icon { font-size: 1.5rem; margin-bottom: 0.3rem; }

    .task-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2d6a9f;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .task-card .task-name {
        font-weight: 600; color: #1e293b; font-size: 1rem;
    }
    .task-card .task-meta {
        font-size: 0.8rem; color: #94a3b8; margin-top: 0.3rem;
    }

    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-success { background: #dcfce7; color: #166534; }
    .status-running { background: #dbeafe; color: #1e40af; }
    .status-error   { background: #fee2e2; color: #991b1b; }
    .status-pending { background: #f1f5f9; color: #475569; }

    .log-entry {
        font-family: 'Courier New', monospace;
        font-size: 0.82rem;
        padding: 0.3rem 0;
        border-bottom: 1px solid #f1f5f9;
    }
    .log-info  { color: #2563eb; }
    .log-warn  { color: #d97706; }
    .log-error { color: #dc2626; }
    .log-ok    { color: #16a34a; }

    .module-btn {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    .module-btn:hover {
        border-color: #2d6a9f;
        box-shadow: 0 4px 12px rgba(45,106,159,0.15);
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }

    .step-container {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# Estado da Sessão
# ══════════════════════════════════════════════════════════════
DEFAULTS = {
    "tasks": [],
    "logs": [],
    "workflows": [],
    "current_workflow_steps": [],
    "execution_history": [],
    "scheduler_tasks": [],
    "running_task": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v if not isinstance(v, list) else list(v)

logger = RPALogger()
engine = WorkflowEngine(logger)

# ══════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🤖 PyRPA")
    st.markdown("---")

    page = st.radio(
        "Navegação",
        [
            "📊 Dashboard",
            "🔧 Construtor de Tarefas",
            "🔗 Workflow Builder",
            "📁 Operações de Arquivo",
            "🌐 Web Scraping",
            "📊 Excel / CSV",
            "📧 E-mail",
            "📄 PDF",
            "⏰ Agendador",
            "📋 Logs & Histórico",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        f"**Tarefas criadas:** {len(st.session_state.tasks)}  \n"
        f"**Workflows:** {len(st.session_state.workflows)}  \n"
        f"**Execuções:** {len(st.session_state.execution_history)}"
    )

# ══════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════
def add_log(msg: str, level: str = "INFO"):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "message": msg,
    }
    st.session_state.logs.insert(0, entry)
    if len(st.session_state.logs) > 500:
        st.session_state.logs = st.session_state.logs[:500]


def add_execution(name, status, duration, details=""):
    st.session_state.execution_history.insert(
        0,
        {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "status": status,
            "duration": f"{duration:.1f}s",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": details,
        },
    )


def badge(status):
    m = {
        "Sucesso": "status-success",
        "Executando": "status-running",
        "Erro": "status-error",
        "Pendente": "status-pending",
    }
    cls = m.get(status, "status-pending")
    return f'<span class="status-badge {cls}">{status}</span>'


# ══════════════════════════════════════════════════════════════
# PÁGINAS
# ══════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────────
# 📊 Dashboard
# ──────────────────────────────────────────────────────────────
if page == "📊 Dashboard":
    st.markdown(
        '<div class="main-header">'
        "<h1>🤖 PyRPA — Automação Inteligente</h1>"
        "<p>Plataforma de Robotic Process Automation 100 % Python</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    total   = len(st.session_state.execution_history)
    success = sum(1 for e in st.session_state.execution_history if e["status"] == "Sucesso")
    errors  = sum(1 for e in st.session_state.execution_history if e["status"] == "Erro")
    pend    = len(st.session_state.scheduler_tasks)

    c1, c2, c3, c4 = st.columns(4)
    for col, icon, num, lbl in [
        (c1, "🚀", total,   "Total de Execuções"),
        (c2, "✅", success, "Sucesso"),
        (c3, "❌", errors,  "Erros"),
        (c4, "⏳", pend,    "Agendadas"),
    ]:
        col.markdown(
            f'<div class="metric-card">'
            f'<div class="icon">{icon}</div>'
            f'<div class="number">{num}</div>'
            f'<div class="label">{lbl}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("### Módulos Disponíveis")
    modules = [
        ("📁", "Arquivos",      "Copiar, mover, renomear, organizar"),
        ("🌐", "Web Scraping",  "Extrair dados de websites"),
        ("📊", "Excel / CSV",   "Manipulação de planilhas"),
        ("📧", "E-mail",        "Envio automatizado de e-mails"),
        ("📄", "PDF",           "Extrair, mesclar, converter"),
        ("⏰", "Agendador",     "Programar execuções"),
    ]
    cols = st.columns(3)
    for i, (icon, name, desc) in enumerate(modules):
        cols[i % 3].markdown(
            f'<div class="module-btn">'
            f'<div style="font-size:2rem">{icon}</div>'
            f'<div style="font-weight:600;margin:0.5rem 0">{name}</div>'
            f'<div style="font-size:0.8rem;color:#64748b">{desc}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    if st.session_state.execution_history:
        st.markdown("### Execuções Recentes")
        for ex in st.session_state.execution_history[:8]:
            st.markdown(
                f'<div class="task-card">'
                f'<div class="task-name">{ex["name"]} {badge(ex["status"])}</div>'
                f'<div class="task-meta">⏱ {ex["duration"]} · 📅 {ex["timestamp"]}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

# ──────────────────────────────────────────────────────────────
# 🔧 Construtor de Tarefas
# ──────────────────────────────────────────────────────────────
elif page == "🔧 Construtor de Tarefas":
    st.markdown("## 🔧 Construtor de Tarefas")
    st.markdown("Crie tarefas automatizadas configurando os parâmetros abaixo.")

    with st.form("task_form"):
        name = st.text_input("Nome da Tarefa", placeholder="Ex: Backup diário de relatórios")
        desc = st.text_area("Descrição", placeholder="O que essa tarefa faz?")
        category = st.selectbox(
            "Categoria",
            ["Operação de Arquivo", "Web Scraping", "Excel/CSV", "E-mail", "PDF", "Custom Script"],
        )

        st.markdown("#### ⚙️ Configuração")
        col1, col2 = st.columns(2)
        with col1:
            retry = st.number_input("Retentativas em caso de erro", 0, 5, 1)
            timeout = st.number_input("Timeout (segundos)", 10, 600, 60)
        with col2:
            notify_email = st.text_input("E-mail para notificação (opcional)")
            priority = st.select_slider("Prioridade", ["Baixa", "Média", "Alta", "Crítica"], "Média")

        submitted = st.form_submit_button("💾 Salvar Tarefa", use_container_width=True)
        if submitted and name:
            task = {
                "id": str(uuid.uuid4())[:8],
                "name": name,
                "description": desc,
                "category": category,
                "retry": retry,
                "timeout": timeout,
                "notify_email": notify_email,
                "priority": priority,
                "status": "Pendente",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state.tasks.append(task)
            add_log(f"Tarefa criada: {name}", "INFO")
            st.success(f"✅ Tarefa **{name}** criada com sucesso!")

    if st.session_state.tasks:
        st.markdown("### 📋 Tarefas Cadastradas")
        for t in st.session_state.tasks:
            with st.expander(f"{'🔴' if t['priority']=='Crítica' else '🟡' if t['priority']=='Alta' else '🔵'} {t['name']} — {t['category']}"):
                st.markdown(f"**ID:** `{t['id']}`  \n**Descrição:** {t['description']}")
                st.markdown(f"**Prioridade:** {t['priority']} · **Timeout:** {t['timeout']}s · **Retentativas:** {t['retry']}")
                c1, c2 = st.columns(2)
                if c1.button("▶️ Executar", key=f"run_{t['id']}"):
                    start = time.time()
                    add_log(f"Executando tarefa: {t['name']}", "INFO")
                    time.sleep(0.5)  # Simulação
                    t["status"] = "Sucesso"
                    duration = time.time() - start
                    add_execution(t["name"], "Sucesso", duration, t["description"])
                    add_log(f"Tarefa concluída: {t['name']} ({duration:.1f}s)", "SUCCESS")
                    st.success("Tarefa executada com sucesso!")
                if c2.button("🗑️ Remover", key=f"del_{t['id']}"):
                    st.session_state.tasks = [x for x in st.session_state.tasks if x["id"] != t["id"]]
                    add_log(f"Tarefa removida: {t['name']}", "WARN")
                    st.rerun()

# ──────────────────────────────────────────────────────────────
# 🔗 Workflow Builder
# ──────────────────────────────────────────────────────────────
elif page == "🔗 Workflow Builder":
    st.markdown("## 🔗 Workflow Builder")
    st.markdown("Monte fluxos de automação encadeando etapas sequenciais.")

    wf_name = st.text_input("Nome do Workflow", placeholder="Ex: Processo mensal de relatórios")

    st.markdown("#### Adicionar Etapa")
    col1, col2 = st.columns([2, 1])
    with col1:
        step_type = st.selectbox(
            "Tipo da Etapa",
            [
                "📁 Copiar Arquivos",
                "📁 Mover Arquivos",
                "📁 Renomear Arquivos",
                "🌐 Extrair Dados Web",
                "📊 Processar Excel",
                "📊 Consolidar CSVs",
                "📧 Enviar E-mail",
                "📄 Extrair Texto PDF",
                "📄 Mesclar PDFs",
                "⏳ Aguardar (delay)",
                "🐍 Script Python Custom",
            ],
        )
    with col2:
        step_desc = st.text_input("Descrição curta", placeholder="Detalhe da etapa")

    params: dict = {}
    if "Copiar" in step_type or "Mover" in step_type:
        params["origem"] = st.text_input("Pasta de origem", key="wf_src")
        params["destino"] = st.text_input("Pasta de destino", key="wf_dst")
        params["filtro"] = st.text_input("Filtro de extensão (ex: .xlsx)", key="wf_filt")
    elif "Web" in step_type:
        params["url"] = st.text_input("URL", key="wf_url")
        params["seletor"] = st.text_input("Seletor CSS", key="wf_sel")
    elif "Excel" in step_type or "CSV" in step_type:
        params["arquivo"] = st.text_input("Caminho do arquivo", key="wf_xl")
        params["operacao"] = st.selectbox("Operação", ["Ler", "Filtrar", "Agregar", "Pivotar"], key="wf_xlop")
    elif "E-mail" in step_type:
        params["destinatario"] = st.text_input("Destinatário", key="wf_em")
        params["assunto"] = st.text_input("Assunto", key="wf_sub")
    elif "Aguardar" in step_type:
        params["segundos"] = st.number_input("Segundos", 1, 300, 5, key="wf_wait")
    elif "Script" in step_type:
        params["codigo"] = st.text_area("Código Python", height=150, key="wf_code")

    if st.button("➕ Adicionar Etapa"):
        step = {
            "id": len(st.session_state.current_workflow_steps) + 1,
            "type": step_type,
            "description": step_desc or step_type,
            "params": params,
        }
        st.session_state.current_workflow_steps.append(step)
        add_log(f"Etapa adicionada ao workflow: {step_type}", "INFO")
        st.success(f"Etapa **{step_type}** adicionada!")

    if st.session_state.current_workflow_steps:
        st.markdown("#### 📐 Pipeline Atual")
        for i, s in enumerate(st.session_state.current_workflow_steps):
            st.markdown(
                f'<div class="step-container">'
                f"<strong>Etapa {s['id']}</strong> — {s['type']}<br/>"
                f"<span style='color:#64748b;font-size:0.85rem'>{s['description']}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        col1, col2, col3 = st.columns(3)
        if col1.button("💾 Salvar Workflow", use_container_width=True):
            if wf_name:
                wf = {
                    "id": str(uuid.uuid4())[:8],
                    "name": wf_name,
                    "steps": list(st.session_state.current_workflow_steps),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                st.session_state.workflows.append(wf)
                st.session_state.current_workflow_steps = []
                add_log(f"Workflow salvo: {wf_name}", "SUCCESS")
                st.success(f"Workflow **{wf_name}** salvo!")
            else:
                st.warning("Informe o nome do workflow.")

        if col2.button("▶️ Executar Pipeline", use_container_width=True):
            start = time.time()
            bar = st.progress(0)
            total = len(st.session_state.current_workflow_steps)
            for i, step in enumerate(st.session_state.current_workflow_steps):
                st.info(f"⏳ Executando etapa {step['id']}: {step['type']}…")
                time.sleep(0.6)
                bar.progress((i + 1) / total)
                add_log(f"Etapa {step['id']} concluída: {step['type']}", "INFO")
            duration = time.time() - start
            add_execution(wf_name or "Pipeline Ad-hoc", "Sucesso", duration)
            add_log(f"Pipeline concluído em {duration:.1f}s", "SUCCESS")
            st.success(f"✅ Pipeline concluído em **{duration:.1f}s**!")

        if col3.button("🗑️ Limpar Etapas", use_container_width=True):
            st.session_state.current_workflow_steps = []
            st.rerun()

    if st.session_state.workflows:
        st.markdown("### 📂 Workflows Salvos")
        for wf in st.session_state.workflows:
            with st.expander(f"🔗 {wf['name']} ({len(wf['steps'])} etapas)"):
                for s in wf["steps"]:
                    st.markdown(f"**{s['id']}.** {s['type']} — {s['description']}")
                if st.button("▶️ Executar", key=f"runwf_{wf['id']}"):
                    start = time.time()
                    for s in wf["steps"]:
                        time.sleep(0.4)
                    duration = time.time() - start
                    add_execution(wf["name"], "Sucesso", duration)
                    add_log(f"Workflow '{wf['name']}' concluído ({duration:.1f}s)", "SUCCESS")
                    st.success(f"Workflow executado em {duration:.1f}s!")

# ──────────────────────────────────────────────────────────────
# 📁 Operações de Arquivo
# ──────────────────────────────────────────────────────────────
elif page == "📁 Operações de Arquivo":
    st.markdown("## 📁 Operações de Arquivo")
    fops = FileOperations()

    tab1, tab2, tab3, tab4 = st.tabs(["Copiar / Mover", "Renomear em Lote", "Organizar por Extensão", "Monitorar Pasta"])

    with tab1:
        st.markdown("#### Copiar ou Mover Arquivos")
        op = st.radio("Operação", ["Copiar", "Mover"], horizontal=True, key="fop_op")
        src = st.text_input("Pasta de Origem", key="fop_src")
        dst = st.text_input("Pasta de Destino", key="fop_dst")
        ext = st.text_input("Filtrar extensão (ex: .pdf)", key="fop_ext")
        if st.button("▶️ Executar", key="fop_run"):
            if src and dst:
                start = time.time()
                result = fops.copy_or_move(src, dst, ext or None, op.lower())
                duration = time.time() - start
                add_execution(f"{op} arquivos", result["status"], duration, result["message"])
                add_log(result["message"], "SUCCESS" if result["status"] == "Sucesso" else "ERROR")
                if result["status"] == "Sucesso":
                    st.success(result["message"])
                else:
                    st.error(result["message"])

    with tab2:
        st.markdown("#### Renomear Arquivos em Lote")
        folder = st.text_input("Pasta", key="ren_dir")
        pattern = st.text_input("Prefixo", placeholder="relatorio_", key="ren_pat")
        add_date = st.checkbox("Adicionar data ao nome", key="ren_date")
        add_seq = st.checkbox("Adicionar sequencial", value=True, key="ren_seq")
        if st.button("▶️ Renomear", key="ren_run"):
            if folder:
                start = time.time()
                result = fops.batch_rename(folder, pattern, add_date, add_seq)
                duration = time.time() - start
                add_execution("Renomear em lote", result["status"], duration, result["message"])
                add_log(result["message"], "SUCCESS" if result["status"] == "Sucesso" else "ERROR")
                st.info(result["message"])

    with tab3:
        st.markdown("#### Organizar Pasta por Extensão")
        folder = st.text_input("Pasta para organizar", key="org_dir")
        if st.button("▶️ Organizar", key="org_run"):
            if folder:
                start = time.time()
                result = fops.organize_by_extension(folder)
                duration = time.time() - start
                add_execution("Organizar por extensão", result["status"], duration, result["message"])
                add_log(result["message"], "SUCCESS" if result["status"] == "Sucesso" else "ERROR")
                st.info(result["message"])

    with tab4:
        st.markdown("#### Monitorar Pasta (Watcher)")
        watch_folder = st.text_input("Pasta a monitorar", key="watch_dir")
        watch_ext = st.text_input("Extensão de interesse (ex: .csv)", key="watch_ext")
        watch_action = st.selectbox("Ação ao detectar", ["Copiar para destino", "Notificar", "Executar script"], key="watch_act")
        st.info("💡 Em produção, use `watchdog` para monitoramento contínuo em background.")
        if st.button("📋 Gerar Script de Monitoramento", key="watch_gen"):
            code = fops.generate_watcher_script(watch_folder, watch_ext, watch_action)
            st.code(code, language="python")
            add_log("Script de monitoramento gerado", "INFO")

# ──────────────────────────────────────────────────────────────
# 🌐 Web Scraping
# ──────────────────────────────────────────────────────────────
elif page == "🌐 Web Scraping":
    st.markdown("## 🌐 Web Scraping")
    scraper = WebScraperBot()

    tab1, tab2, tab3 = st.tabs(["Extração Simples", "Extração de Tabelas", "Gerar Script"])

    with tab1:
        st.markdown("#### Extrair Conteúdo de Página")
        url = st.text_input("URL", placeholder="https://example.com", key="ws_url")
        sel = st.text_input("Seletor CSS (opcional)", placeholder="div.content", key="ws_sel")
        if st.button("🔍 Extrair", key="ws_run"):
            if url:
                start = time.time()
                result = scraper.extract_content(url, sel or None)
                duration = time.time() - start
                add_execution("Web Scraping", result["status"], duration)
                add_log(f"Scraping: {url}", "SUCCESS" if result["status"] == "Sucesso" else "ERROR")
                if result["status"] == "Sucesso":
                    st.success(f"Extraído com sucesso em {duration:.1f}s")
                    st.text_area("Conteúdo", result["data"], height=300)
                else:
                    st.error(result["message"])

    with tab2:
        st.markdown("#### Extrair Tabelas HTML")
        url = st.text_input("URL com tabela", placeholder="https://example.com/data", key="ws_tab_url")
        if st.button("📊 Extrair Tabelas", key="ws_tab_run"):
            if url:
                start = time.time()
                result = scraper.extract_tables(url)
                duration = time.time() - start
                add_execution("Extração de Tabelas", result["status"], duration)
                if result["status"] == "Sucesso" and result.get("tables"):
                    st.success(f"{len(result['tables'])} tabela(s) encontrada(s)")
                    for i, df in enumerate(result["tables"]):
                        st.markdown(f"**Tabela {i+1}**")
                        st.dataframe(df, use_container_width=True)
                elif result["status"] == "Sucesso":
                    st.warning("Nenhuma tabela encontrada na página.")
                else:
                    st.error(result["message"])

    with tab3:
        st.markdown("#### Gerar Script de Scraping")
        url = st.text_input("URL alvo", key="ws_gen_url")
        include_selenium = st.checkbox("Incluir suporte a Selenium (páginas dinâmicas)")
        if st.button("🐍 Gerar Script", key="ws_gen_run"):
            code = scraper.generate_script(url, include_selenium)
            st.code(code, language="python")
            add_log("Script de scraping gerado", "INFO")

# ──────────────────────────────────────────────────────────────
# 📊 Excel / CSV
# ──────────────────────────────────────────────────────────────
elif page == "📊 Excel / CSV":
    st.markdown("## 📊 Excel / CSV")
    xl = ExcelOperations()

    tab1, tab2, tab3, tab4 = st.tabs(["Ler e Visualizar", "Consolidar Arquivos", "Transformações", "Gerar Script"])

    with tab1:
        st.markdown("#### Upload de Arquivo")
        uploaded = st.file_uploader("Escolha um arquivo Excel ou CSV", type=["xlsx", "xls", "csv"], key="xl_up")
        if uploaded:
            result = xl.read_file(uploaded)
            if result["status"] == "Sucesso":
                df = result["data"]
                st.dataframe(df, use_container_width=True)
                c1, c2, c3 = st.columns(3)
                c1.metric("Linhas", df.shape[0])
                c2.metric("Colunas", df.shape[1])
                c3.metric("Células vazias", int(df.isnull().sum().sum()))
                st.markdown("**Tipos de dados:**")
                st.json({str(k): str(v) for k, v in df.dtypes.items()})

    with tab2:
        st.markdown("#### Consolidar Múltiplos Arquivos")
        files = st.file_uploader("Upload de vários arquivos", type=["xlsx", "csv"], accept_multiple_files=True, key="xl_multi")
        if files and st.button("🔗 Consolidar", key="xl_cons"):
            start = time.time()
            result = xl.consolidate(files)
            duration = time.time() - start
            if result["status"] == "Sucesso":
                st.success(f"Consolidado: {result['data'].shape[0]} linhas, {result['data'].shape[1]} colunas")
                st.dataframe(result["data"], use_container_width=True)
                add_execution("Consolidar Excel", "Sucesso", duration)
            else:
                st.error(result["message"])

    with tab3:
        st.markdown("#### Transformações de Dados")
        uploaded = st.file_uploader("Arquivo para transformar", type=["xlsx", "csv"], key="xl_tr_up")
        if uploaded:
            result = xl.read_file(uploaded)
            if result["status"] == "Sucesso":
                df = result["data"]
                transform = st.multiselect(
                    "Transformações",
                    ["Remover duplicatas", "Preencher vazios", "Converter tipos", "Filtrar linhas", "Remover colunas vazias"],
                )
                if st.button("⚡ Aplicar", key="xl_tr_run"):
                    start = time.time()
                    new_df = xl.apply_transforms(df, transform)
                    duration = time.time() - start
                    st.dataframe(new_df, use_container_width=True)
                    st.success(f"Transformações aplicadas em {duration:.1f}s")
                    add_execution("Transformação Excel", "Sucesso", duration)

    with tab4:
        st.markdown("#### Gerar Script de Processamento")
        ops = st.multiselect(
            "Operações desejadas",
            ["Leitura", "Limpeza", "Filtro", "Agregação", "Pivot", "Exportação"],
            key="xl_gen_ops",
        )
        if st.button("🐍 Gerar Script", key="xl_gen_run"):
            code = xl.generate_script(ops)
            st.code(code, language="python")

# ──────────────────────────────────────────────────────────────
# 📧 E-mail
# ──────────────────────────────────────────────────────────────
elif page == "📧 E-mail":
    st.markdown("## 📧 Automação de E-mail")
    email_ops = EmailOperations()

    tab1, tab2, tab3 = st.tabs(["Enviar E-mail", "Envio em Lote", "Gerar Script"])

    with tab1:
        st.markdown("#### Configuração SMTP")
        with st.expander("⚙️ Servidor SMTP", expanded=True):
            c1, c2 = st.columns(2)
            smtp_host = c1.text_input("Servidor", value="smtp.gmail.com", key="em_host")
            smtp_port = c2.number_input("Porta", value=587, key="em_port")
            smtp_user = c1.text_input("Usuário", key="em_user")
            smtp_pass = c2.text_input("Senha", type="password", key="em_pass")

        to = st.text_input("Destinatário(s) — separar por `;`", key="em_to")
        subject = st.text_input("Assunto", key="em_sub")
        body = st.text_area("Corpo do e-mail", height=200, key="em_body")
        attachment = st.file_uploader("Anexo (opcional)", key="em_att")

        if st.button("📤 Enviar", key="em_send"):
            if all([smtp_host, smtp_user, smtp_pass, to, subject]):
                start = time.time()
                result = email_ops.send_email(
                    smtp_host, smtp_port, smtp_user, smtp_pass,
                    to.split(";"), subject, body, attachment,
                )
                duration = time.time() - start
                add_execution("Enviar E-mail", result["status"], duration)
                add_log(f"E-mail: {result['message']}", "SUCCESS" if result["status"] == "Sucesso" else "ERROR")
                if result["status"] == "Sucesso":
                    st.success(result["message"])
                else:
                    st.error(result["message"])
            else:
                st.warning("Preencha todos os campos obrigatórios.")

    with tab2:
        st.markdown("#### Envio em Lote com Template")
        template = st.text_area(
            "Template do e-mail (use `{nome}`, `{empresa}`, etc.)",
            value="Olá {nome},\n\nSegue em anexo o relatório de {mes}.\n\nAtenciosamente,\nEquipe PyRPA",
            height=150,
            key="em_tpl",
        )
        contacts_file = st.file_uploader("CSV de contatos (colunas: email, nome, empresa, …)", type=["csv"], key="em_csv")
        st.info("💡 O envio em lote real requer configuração SMTP. Use 'Gerar Script' para obter o código pronto.")

    with tab3:
        st.markdown("#### Gerar Script de E-mail")
        use_tls = st.checkbox("Usar TLS", value=True)
        use_template = st.checkbox("Com template e envio em lote")
        if st.button("🐍 Gerar Script", key="em_gen"):
            code = email_ops.generate_script(use_tls, use_template)
            st.code(code, language="python")

# ──────────────────────────────────────────────────────────────
# 📄 PDF
# ──────────────────────────────────────────────────────────────
elif page == "📄 PDF":
    st.markdown("## 📄 Operações com PDF")
    pdf_ops = PDFOperations()

    tab1, tab2, tab3, tab4 = st.tabs(["Extrair Texto", "Mesclar PDFs", "Info e Metadados", "Gerar Script"])

    with tab1:
        st.markdown("#### Extrair Texto de PDF")
        pdf_file = st.file_uploader("Upload de PDF", type=["pdf"], key="pdf_ext")
        if pdf_file and st.button("📖 Extrair Texto", key="pdf_ext_run"):
            start = time.time()
            result = pdf_ops.extract_text(pdf_file)
            duration = time.time() - start
            add_execution("Extrair texto PDF", result["status"], duration)
            if result["status"] == "Sucesso":
                st.text_area("Texto extraído", result["data"], height=400)
            else:
                st.error(result["message"])

    with tab2:
        st.markdown("#### Mesclar Múltiplos PDFs")
        pdfs = st.file_uploader("Upload de PDFs", type=["pdf"], accept_multiple_files=True, key="pdf_merge")
        if pdfs and len(pdfs) > 1 and st.button("🔗 Mesclar", key="pdf_merge_run"):
            start = time.time()
            result = pdf_ops.merge_pdfs(pdfs)
            duration = time.time() - start
            add_execution("Mesclar PDFs", result["status"], duration)
            if result["status"] == "Sucesso":
                st.success("PDFs mesclados com sucesso!")
                st.download_button("⬇️ Baixar PDF Mesclado", result["data"], "merged.pdf", "application/pdf")
            else:
                st.error(result["message"])

    with tab3:
        st.markdown("#### Informações do PDF")
        pdf_info = st.file_uploader("Upload de PDF", type=["pdf"], key="pdf_info")
        if pdf_info and st.button("ℹ️ Obter Info", key="pdf_info_run"):
            result = pdf_ops.get_info(pdf_info)
            if result["status"] == "Sucesso":
                st.json(result["data"])

    with tab4:
        st.markdown("#### Gerar Script para PDFs")
        pdf_action = st.selectbox("Ação", ["Extrair texto", "Mesclar", "Dividir", "Converter para imagem", "OCR"])
        if st.button("🐍 Gerar Script", key="pdf_gen"):
            code = pdf_ops.generate_script(pdf_action)
            st.code(code, language="python")

# ──────────────────────────────────────────────────────────────
# ⏰ Agendador
# ──────────────────────────────────────────────────────────────
elif page == "⏰ Agendador":
    st.markdown("## ⏰ Agendador de Tarefas")
    scheduler = TaskScheduler()

    st.markdown("#### Nova Tarefa Agendada")
    with st.form("schedule_form"):
        s_name = st.text_input("Nome", key="sch_name")
        s_type = st.selectbox("Tipo", ["Workflow", "Operação de Arquivo", "Web Scraping", "Script Python"], key="sch_type")
        c1, c2 = st.columns(2)
        s_freq = c1.selectbox("Frequência", ["Uma vez", "A cada X minutos", "Diário", "Semanal", "Mensal"], key="sch_freq")
        s_time = c2.time_input("Horário", key="sch_time")
        if s_freq == "A cada X minutos":
            s_interval = st.number_input("Intervalo (min)", 1, 1440, 30, key="sch_int")
        else:
            s_interval = None
        s_active = st.checkbox("Ativa", value=True, key="sch_active")

        if st.form_submit_button("💾 Agendar", use_container_width=True):
            if s_name:
                task = {
                    "id": str(uuid.uuid4())[:8],
                    "name": s_name,
                    "type": s_type,
                    "frequency": s_freq,
                    "time": str(s_time),
                    "interval": s_interval,
                    "active": s_active,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "last_run": None,
                    "next_run": scheduler.calc_next_run(s_freq, s_time, s_interval),
                }
                st.session_state.scheduler_tasks.append(task)
                add_log(f"Tarefa agendada: {s_name} ({s_freq})", "INFO")
                st.success(f"✅ Tarefa **{s_name}** agendada!")

    if st.session_state.scheduler_tasks:
        st.markdown("### 📅 Tarefas Agendadas")
        for t in st.session_state.scheduler_tasks:
            status = "🟢" if t["active"] else "🔴"
            with st.expander(f"{status} {t['name']} — {t['frequency']}"):
                st.markdown(
                    f"**Tipo:** {t['type']}  \n"
                    f"**Horário:** {t['time']}  \n"
                    f"**Próxima execução:** {t['next_run']}  \n"
                    f"**Última execução:** {t['last_run'] or 'Nunca'}"
                )
                c1, c2 = st.columns(2)
                if c1.button("⏸️ Desativar" if t["active"] else "▶️ Ativar", key=f"sch_toggle_{t['id']}"):
                    t["active"] = not t["active"]
                    st.rerun()
                if c2.button("🗑️ Remover", key=f"sch_del_{t['id']}"):
                    st.session_state.scheduler_tasks = [x for x in st.session_state.scheduler_tasks if x["id"] != t["id"]]
                    st.rerun()

    st.markdown("---")
    st.markdown("#### 🐍 Gerar Script de Agendamento (cron / schedule)")
    if st.button("Gerar Script", key="sch_gen"):
        code = scheduler.generate_cron_script(st.session_state.scheduler_tasks)
        st.code(code, language="python")

# ──────────────────────────────────────────────────────────────
# 📋 Logs & Histórico
# ──────────────────────────────────────────────────────────────
elif page == "📋 Logs & Histórico":
    st.markdown("## 📋 Logs & Histórico de Execução")

    tab1, tab2 = st.tabs(["📜 Logs", "📊 Histórico de Execução"])

    with tab1:
        c1, c2 = st.columns([3, 1])
        with c2:
            level_filter = st.multiselect("Filtrar por nível", ["INFO", "SUCCESS", "WARN", "ERROR"], default=["INFO", "SUCCESS", "WARN", "ERROR"])
            if st.button("🗑️ Limpar Logs"):
                st.session_state.logs = []
                st.rerun()

        logs = [l for l in st.session_state.logs if l["level"] in level_filter]
        if logs:
            for log in logs[:100]:
                cls_map = {"INFO": "log-info", "SUCCESS": "log-ok", "WARN": "log-warn", "ERROR": "log-error"}
                cls = cls_map.get(log["level"], "log-info")
                st.markdown(
                    f'<div class="log-entry {cls}">'
                    f"<strong>[{log['timestamp']}]</strong> "
                    f"<strong>[{log['level']}]</strong> {log['message']}"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("Nenhum log registrado.")

    with tab2:
        if st.session_state.execution_history:
            for ex in st.session_state.execution_history:
                st.markdown(
                    f'<div class="task-card">'
                    f'<div class="task-name">{ex["name"]} {badge(ex["status"])}</div>'
                    f'<div class="task-meta">⏱ {ex["duration"]} · 📅 {ex["timestamp"]} · ID: {ex["id"]}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("Nenhuma execução registrada.")

        if st.session_state.execution_history:
            st.markdown("#### 📈 Resumo")
            total = len(st.session_state.execution_history)
            ok = sum(1 for e in st.session_state.execution_history if e["status"] == "Sucesso")
            st.progress(ok / total if total else 0)
            st.markdown(f"**Taxa de sucesso:** {ok}/{total} ({ok/total*100:.0f}%)" if total else "")
