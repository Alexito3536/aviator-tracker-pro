# ==========================================
# CASILLAS 1, 2, 9: INSTALACIÓN Y DEPENDENCIAS
# ==========================================
!pip install undetected-chromedriver selenium pandas

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DEL ENGINE (CASILLAS 2, 9, 11)
# ==========================================
def iniciar_bot(proxy=None):
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
        
    try:
        # El driver autodetecta la versión del navegador (Solución Casilla 9)
        driver = uc.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"[-] Error al inicializar el Driver: {e}")
        return None

# ==========================================
# LÓGICA DE EXTRACCIÓN (CASILLAS 3, 4, 7, 8)
# ==========================================
def obtener_historial(driver):
    # Inyección de JS para extraer datos del Shadow DOM / Angular (Casilla 8)
    script_js = """
    var items = document.querySelectorAll('app-payout-item, .payout-item, .bubble-multiplier');
    return Array.from(items).map(el => el.innerText.trim().replace('x', ''));
    """
    try:
        return driver.execute_script(script_js)
    except:
        return []

def navegar_al_juego(driver, url):
    driver.get(url)
    print("[+] Accediendo a 1win... Esperando carga inicial.")
    time.sleep(15)
    
    # Tomar captura para debug (Casilla 10)
    driver.save_screenshot("estado_inicial.png")
    
    try:
        # Intento de click en Demo Mode si existe (Casilla 12)
        wait = WebDriverWait(driver, 10)
        btn_demo = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Demo')]")))
        btn_demo.click()
        print("[+] Click en Modo Demo realizado.")
        time.sleep(5)
    except:
        print("[!] Botón Demo no encontrado o no necesario.")

    # Salto al Iframe (Casilla 3 y 7)
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
            print("[+] Foco cambiado al Iframe del juego.")
            return True
    except Exception as e:
        print(f"[-] Error al entrar al iframe: {e}")
    return False

# ==========================================
# BUCLE DE MONITOREO (CASILLA 6)
# ==========================================
def ejecutar_scraper(url, duracion_mins=5):
    driver = iniciar_bot()
    if not driver: return
    
    if navegar_al_juego(driver, url):
        ultimo_registro = None
        data_log = []
        
        print(f"[*] Iniciando monitoreo por {duracion_mins} minutos...")
        fin = time.time() + (duracion_mins * 60)
        
        while time.time() < fin:
            numeros = obtener_historial(driver)
            
            if numeros:
                actual = numeros[0] # El más reciente
                if actual != ultimo_registro:
                    ahora = datetime.now().strftime("%H:%M:%S")
                    print(f"[{ahora}] NUEVO MULTIPLICADOR: {actual}x")
                    data_log.append({"hora": ahora, "valor": actual})
                    ultimo_registro = actual
                    
                    # Guardado persistente
                    pd.DataFrame(data_log).to_csv("aviator_data.csv", index=False)
            
            time.sleep(3) # Frecuencia de muestreo
            
    driver.quit()
    print("[*] Proceso finalizado. Datos guardados en aviator_data.csv")

# ==========================================
# EJECUCIÓN
# ==========================================
URL_TARGET = "https://1wjlnz.com/casino/play/v_spribe:aviator?p=136g"
ejecutar_scraper(URL_TARGET, duracion_mins=10)

