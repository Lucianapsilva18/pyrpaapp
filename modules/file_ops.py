"""Módulo de operações com arquivos para o PyRPA."""

import os
import shutil
import glob
from datetime import datetime
from pathlib import Path


class FileOperations:

    def copy_or_move(self, src: str, dst: str, ext: str | None, operation: str) -> dict:
        try:
            src_path = Path(src)
            dst_path = Path(dst)

            if not src_path.exists():
                return {"status": "Erro", "message": f"Pasta de origem não encontrada: {src}"}

            dst_path.mkdir(parents=True, exist_ok=True)

            pattern = f"*{ext}" if ext else "*"
            files = list(src_path.glob(pattern))
            files = [f for f in files if f.is_file()]

            if not files:
                return {"status": "Sucesso", "message": "Nenhum arquivo encontrado com o filtro informado."}

            count = 0
            for f in files:
                dest_file = dst_path / f.name
                if operation == "copiar":
                    shutil.copy2(f, dest_file)
                else:
                    shutil.move(str(f), str(dest_file))
                count += 1

            verb = "copiado(s)" if operation == "copiar" else "movido(s)"
            return {"status": "Sucesso", "message": f"{count} arquivo(s) {verb} para {dst}"}
        except Exception as e:
            return {"status": "Erro", "message": str(e)}

    def batch_rename(self, folder: str, prefix: str, add_date: bool, add_seq: bool) -> dict:
        try:
            folder_path = Path(folder)
            if not folder_path.exists():
                return {"status": "Erro", "message": f"Pasta não encontrada: {folder}"}

            files = sorted([f for f in folder_path.iterdir() if f.is_file()])
            if not files:
                return {"status": "Sucesso", "message": "Nenhum arquivo encontrado na pasta."}

            count = 0
            for i, f in enumerate(files, 1):
                new_name = prefix or ""
                if add_date:
                    new_name += datetime.now().strftime("%Y%m%d_")
                if add_seq:
                    new_name += f"{i:03d}"
                new_name += f.suffix
                f.rename(folder_path / new_name)
                count += 1

            return {"status": "Sucesso", "message": f"{count} arquivo(s) renomeado(s)."}
        except Exception as e:
            return {"status": "Erro", "message": str(e)}

    def organize_by_extension(self, folder: str) -> dict:
        try:
            folder_path = Path(folder)
            if not folder_path.exists():
                return {"status": "Erro", "message": f"Pasta não encontrada: {folder}"}

            files = [f for f in folder_path.iterdir() if f.is_file()]
            moved = 0
            for f in files:
                ext = f.suffix.lstrip(".").lower() or "sem_extensao"
                dest_dir = folder_path / ext
                dest_dir.mkdir(exist_ok=True)
                shutil.move(str(f), str(dest_dir / f.name))
                moved += 1

            return {"status": "Sucesso", "message": f"{moved} arquivo(s) organizados por extensão."}
        except Exception as e:
            return {"status": "Erro", "message": str(e)}

    def generate_watcher_script(self, folder: str, ext: str, action: str) -> str:
        return f'''"""
Script de monitoramento de pasta gerado pelo PyRPA.
Dependência: pip install watchdog
"""
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_FOLDER = r"{folder}"
WATCH_EXT    = "{ext}"
ACTION       = "{action}"

class RPAHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if WATCH_EXT and not event.src_path.endswith(WATCH_EXT):
            return

        print(f"[PyRPA] Novo arquivo detectado: {{event.src_path}}")

        if ACTION == "Copiar para destino":
            dest = WATCH_FOLDER + "/processados"
            import os; os.makedirs(dest, exist_ok=True)
            shutil.copy2(event.src_path, dest)
            print(f"[PyRPA] Copiado para {{dest}}")

        elif ACTION == "Notificar":
            print(f"[PyRPA] NOTIFICAÇÃO: Arquivo novo -> {{event.src_path}}")

        elif ACTION == "Executar script":
            import subprocess
            subprocess.run(["python", "process.py", event.src_path])

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(RPAHandler(), WATCH_FOLDER, recursive=False)
    observer.start()
    print(f"[PyRPA] Monitorando {{WATCH_FOLDER}} ...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
'''
