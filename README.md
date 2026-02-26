# 🤖 PyRPA — Plataforma de Automação Inteligente

Plataforma de **Robotic Process Automation (RPA)** 100% Python, com interface Streamlit.

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
streamlit run app.py
```

## Módulos

| Módulo | Descrição |
|--------|-----------|
| 📁 **Operações de Arquivo** | Copiar, mover, renomear em lote, organizar por extensão, monitorar pasta |
| 🌐 **Web Scraping** | Extrair conteúdo e tabelas de páginas web (requests/Selenium) |
| 📊 **Excel / CSV** | Ler, consolidar, transformar e exportar planilhas |
| 📧 **E-mail** | Envio individual e em lote com templates e anexos |
| 📄 **PDF** | Extrair texto, mesclar, dividir, OCR |
| ⏰ **Agendador** | Programar execuções com frequências variadas |
| 🔗 **Workflow Builder** | Encadear etapas de diferentes módulos em pipelines |

## Funcionalidades Principais

- **Dashboard** com métricas de execução em tempo real
- **Construtor de Tarefas** com prioridade, retry e timeout
- **Workflow Builder** visual para montar pipelines de automação
- **Gerador de Scripts** — cada módulo pode exportar código Python pronto para produção
- **Logs centralizados** com filtro por nível e histórico completo
- **Agendador** com suporte a execuções únicas, periódicas, diárias, semanais e mensais

## Estrutura

```
rpa_app/
├── app.py                 # Aplicação principal Streamlit
├── requirements.txt
├── README.md
└── modules/
    ├── __init__.py
    ├── file_ops.py        # Operações de arquivo
    ├── web_scraper.py     # Web scraping
    ├── excel_ops.py       # Excel / CSV
    ├── email_ops.py       # E-mail
    ├── pdf_ops.py         # PDF
    ├── scheduler.py       # Agendamento
    ├── workflow_engine.py # Motor de workflows
    └── logger.py          # Logging centralizado
```
