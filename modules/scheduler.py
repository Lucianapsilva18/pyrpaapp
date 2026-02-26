"""Módulo de agendamento de tarefas para o PyRPA."""

from datetime import datetime, timedelta


class TaskScheduler:

    def calc_next_run(self, frequency: str, run_time, interval: int | None = None) -> str:
        now = datetime.now()
        time_str = str(run_time)

        if frequency == "Uma vez":
            target = now.replace(
                hour=int(time_str.split(":")[0]),
                minute=int(time_str.split(":")[1]),
                second=0,
            )
            if target <= now:
                target += timedelta(days=1)
            return target.strftime("%Y-%m-%d %H:%M")

        if frequency == "A cada X minutos":
            target = now + timedelta(minutes=interval or 30)
            return target.strftime("%Y-%m-%d %H:%M")

        if frequency == "Diário":
            target = now.replace(
                hour=int(time_str.split(":")[0]),
                minute=int(time_str.split(":")[1]),
                second=0,
            )
            if target <= now:
                target += timedelta(days=1)
            return target.strftime("%Y-%m-%d %H:%M")

        if frequency == "Semanal":
            target = now + timedelta(days=(7 - now.weekday()) % 7 or 7)
            return target.strftime("%Y-%m-%d") + f" {time_str[:5]}"

        if frequency == "Mensal":
            month = now.month % 12 + 1
            year = now.year + (1 if month == 1 else 0)
            return f"{year}-{month:02d}-01 {time_str[:5]}"

        return "N/A"

    def generate_cron_script(self, tasks: list) -> str:
        task_blocks = []
        for t in tasks:
            task_blocks.append(
                f'    schedule_task("{t["name"]}", "{t["frequency"]}", '
                f'"{t["time"]}", task_function)'
            )

        tasks_code = "\n".join(task_blocks) if task_blocks else '    print("Nenhuma tarefa configurada.")'

        return f'''"""
Agendador de tarefas RPA — gerado pelo PyRPA.
Dependência: pip install schedule
"""
import schedule
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("rpa_scheduler.log"),
        logging.StreamHandler(),
    ],
)

def task_function():
    """Função executada pela tarefa agendada. Customize conforme necessário."""
    logging.info("Executando tarefa RPA...")
    # Coloque aqui a lógica da sua automação
    # Exemplo:
    # from modules.file_ops import FileOperations
    # fops = FileOperations()
    # fops.copy_or_move("/origem", "/destino", ".xlsx", "copiar")
    logging.info("Tarefa concluída!")

def schedule_task(name: str, frequency: str, run_time: str, func):
    """Agenda uma tarefa baseada na frequência."""
    hh_mm = run_time[:5]

    if frequency == "Diário":
        schedule.every().day.at(hh_mm).do(func)
    elif frequency == "A cada X minutos":
        schedule.every(30).minutes.do(func)
    elif frequency == "Semanal":
        schedule.every().monday.at(hh_mm).do(func)
    elif frequency == "Mensal":
        # schedule não suporta "mensal" nativamente; use APScheduler para isso
        schedule.every().day.at(hh_mm).do(
            lambda: func() if datetime.now().day == 1 else None
        )

    logging.info(f"Tarefa agendada: {{name}} ({{frequency}} às {{hh_mm}})")

def main():
    logging.info("Iniciando agendador PyRPA...")

{tasks_code}

    logging.info(f"{{len(schedule.get_jobs())}} tarefa(s) agendada(s)")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
'''
