"""
Funções responsáveis pela autenticação no sistema legado.
"""

from selenium import webdriver, common
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from utils.config import (
    ACESSO_AUTOMATICO,
    TAMANHO_DA_TELA,
    CAMINHO_CHROME,
    URL_PARA_LOGIN,
    SENHA,
    USUARIO
)

def acessar_servico() -> dict[str, str]:
    """Realiza a autenticação e retorna os cookies da sessão."""
    opcoes_chrome = Options()
    if ACESSO_AUTOMATICO:
        opcoes_chrome.add_argument("--headless")
    else:
        opcoes_chrome.add_argument("--window-size=%s" % TAMANHO_DA_TELA)

    opcoes_chrome.binary_location = CAMINHO_CHROME
    driver = webdriver.Chrome(options=opcoes_chrome)
    driver.get(URL_PARA_LOGIN)

    if ACESSO_AUTOMATICO:
        driver.find_element(By.XPATH, '//*[@id="txtLogin"]').send_keys(USUARIO)
        driver.find_element(By.XPATH, '//*[@id="txtSenha"]').send_keys(SENHA)
        driver.find_element(By.XPATH, '//*[@id="btnLogin"]').click()

    cookies: dict[str, str] = {}
    while not cookies:
        try:
            cookies_do_driver = driver.get_cookies()
            if not cookies_do_driver or len(cookies_do_driver) < 10:
                if ACESSO_AUTOMATICO:
                    driver.find_element(By.XPATH, '//*[@id="btnAtualizar"]').click()
            else:
                driver.quit()
                for item in cookies_do_driver:
                    cookies[item['name'].strip()] = item['value'].strip()
        except common.UnexpectedAlertPresentException:
            if ACESSO_AUTOMATICO:
                alerta = driver.switch_to.alert
                alerta.accept()
            else:
                continue
        except (common.exceptions.NoSuchElementException,
                common.exceptions.StaleElementReferenceException):
            continue

    return cookies