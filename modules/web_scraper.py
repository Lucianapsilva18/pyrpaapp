"""Módulo de Web Scraping para o PyRPA."""

import io

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class WebScraperBot:

    def extract_content(self, url: str, selector: str | None = None) -> dict:
        if not HAS_DEPS:
            return {"status": "Erro", "message": "Instale: pip install requests beautifulsoup4"}
        try:
            headers = {"User-Agent": "PyRPA Bot/1.0"}
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            if selector:
                elements = soup.select(selector)
                text = "\n\n".join(el.get_text(strip=True) for el in elements)
            else:
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                text = soup.get_text(separator="\n", strip=True)

            return {"status": "Sucesso", "data": text}
        except Exception as e:
            return {"status": "Erro", "message": str(e)}

    def extract_tables(self, url: str) -> dict:
        if not HAS_DEPS or not HAS_PANDAS:
            return {"status": "Erro", "message": "Instale: pip install requests beautifulsoup4 pandas lxml"}
        try:
            tables = pd.read_html(url)
            return {"status": "Sucesso", "tables": tables}
        except ValueError:
            return {"status": "Sucesso", "tables": []}
        except Exception as e:
            return {"status": "Erro", "message": str(e)}

    def generate_script(self, url: str, use_selenium: bool = False) -> str:
        if use_selenium:
            return f'''"""
Script de Web Scraping com Selenium gerado pelo PyRPA.
Dependências: pip install selenium webdriver-manager
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

URL = "{url}"

def scrape_with_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    try:
        driver.get(URL)

        # Aguardar carregamento do conteúdo dinâmico
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(2)  # Aguardar JS

        # Exemplo: extrair todos os links
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            text = link.text.strip()
            if href and text:
                print(f"{{text}} -> {{href}}")

        # Exemplo: extrair texto de elementos específicos
        # elements = driver.find_elements(By.CSS_SELECTOR, "div.content")
        # for el in elements:
        #     print(el.text)

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_with_selenium()
'''
        else:
            return f'''"""
Script de Web Scraping com Requests + BeautifulSoup gerado pelo PyRPA.
Dependências: pip install requests beautifulsoup4 pandas lxml
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time

URL = "{url}"
HEADERS = {{"User-Agent": "PyRPA Bot/1.0"}}

def scrape_page(url: str) -> BeautifulSoup:
    """Faz a requisição e retorna o objeto BeautifulSoup."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def extract_text(soup: BeautifulSoup, selector: str = None) -> str:
    """Extrai texto de elementos ou da página inteira."""
    if selector:
        elements = soup.select(selector)
        return "\\n".join(el.get_text(strip=True) for el in elements)
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator="\\n", strip=True)

def extract_links(soup: BeautifulSoup) -> list[dict]:
    """Extrai todos os links da página."""
    links = []
    for a in soup.find_all("a", href=True):
        links.append({{"text": a.get_text(strip=True), "href": a["href"]}})
    return links

def extract_tables(url: str) -> list:
    """Extrai tabelas HTML como DataFrames."""
    try:
        return pd.read_html(url)
    except ValueError:
        return []

def save_to_csv(data: list[dict], filename: str = "output.csv"):
    """Salva lista de dicionários em CSV."""
    if not data:
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"Dados salvos em {{filename}}")

if __name__ == "__main__":
    print(f"Extraindo dados de: {{URL}}")
    soup = scrape_page(URL)

    # Extrair texto
    text = extract_text(soup)
    print(f"Texto extraído: {{len(text)}} caracteres")

    # Extrair links
    links = extract_links(soup)
    print(f"Links encontrados: {{len(links)}}")
    save_to_csv(links, "links.csv")

    # Extrair tabelas
    tables = extract_tables(URL)
    for i, df in enumerate(tables):
        df.to_csv(f"tabela_{{i+1}}.csv", index=False)
        print(f"Tabela {{i+1}}: {{df.shape[0]}} linhas x {{df.shape[1]}} colunas")
'''
