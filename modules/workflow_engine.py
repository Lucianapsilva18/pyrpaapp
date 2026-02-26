"""Motor de execução de workflows para o PyRPA."""

import time
from datetime import datetime


class WorkflowEngine:

    def __init__(self, logger=None):
        self.logger = logger

    def execute_workflow(self, workflow: dict) -> dict:
        results = []
        start = time.time()

        for step in workflow.get("steps", []):
            step_start = time.time()
            try:
                result = self._execute_step(step)
                step_duration = time.time() - step_start
                results.append({
                    "step_id": step["id"],
                    "type": step["type"],
                    "status": "Sucesso",
                    "duration": f"{step_duration:.1f}s",
                    "result": result,
                })
                if self.logger:
                    self.logger.log(
                        f"Etapa {step['id']} ({step['type']}) concluída em {step_duration:.1f}s",
                        "INFO",
                    )
            except Exception as e:
                step_duration = time.time() - step_start
                results.append({
                    "step_id": step["id"],
                    "type": step["type"],
                    "status": "Erro",
                    "duration": f"{step_duration:.1f}s",
                    "error": str(e),
                })
                if self.logger:
                    self.logger.log(f"Erro na etapa {step['id']}: {e}", "ERROR")
                break

        total_duration = time.time() - start
        all_ok = all(r["status"] == "Sucesso" for r in results)

        return {
            "workflow": workflow.get("name", "Sem nome"),
            "status": "Sucesso" if all_ok else "Erro",
            "duration": f"{total_duration:.1f}s",
            "steps_results": results,
            "executed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _execute_step(self, step: dict) -> str:
        step_type = step.get("type", "")
        params = step.get("params", {})

        if "Aguardar" in step_type:
            seconds = int(params.get("segundos", 5))
            time.sleep(min(seconds, 10))  # Limitar a 10s no app
            return f"Aguardou {seconds}s"

        if "Copiar" in step_type or "Mover" in step_type:
            from modules.file_ops import FileOperations
            fops = FileOperations()
            op = "copiar" if "Copiar" in step_type else "mover"
            result = fops.copy_or_move(
                params.get("origem", ""),
                params.get("destino", ""),
                params.get("filtro") or None,
                op,
            )
            return result["message"]

        if "Web" in step_type:
            from modules.web_scraper import WebScraperBot
            scraper = WebScraperBot()
            result = scraper.extract_content(
                params.get("url", ""),
                params.get("seletor") or None,
            )
            if result["status"] == "Sucesso":
                return f"Extraído {len(result['data'])} caracteres"
            return result["message"]

        if "Script" in step_type:
            code = params.get("codigo", "")
            if code:
                exec_globals = {}
                exec(code, exec_globals)
                return "Script executado"
            return "Script vazio"

        # Simulação para outros tipos
        time.sleep(0.3)
        return f"Etapa '{step_type}' executada (simulação)"
