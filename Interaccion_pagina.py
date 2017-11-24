import urllib.request
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from PIL import Image
from datetime import datetime
import sqlite3
import cv2

##DESCARGAR EL CHROMEDRIVER DE https://chromedriver.storage.googleapis.com/index.html
##EXTRAER EL chromedriver.exe EN EL DIRECTORIO DONDE ESTA EL PYTHON (p.e. C:\python36-32)
##SI ESTA TODO BIEN, EN CMD EL COMANDO chromedriver -v DEBERIA DAR LA VERSION, SINO AGREGAR LA RUTA AL PATH

#### Never do this -- insecure!
##symbol = 'RHAT'
##c.execute("SELECT * FROM stocks WHERE symbol = '%s'" % symbol)
##
#### Do this instead
##t = ('RHAT',)
##c.execute('SELECT * FROM stocks WHERE symbol=?', t)
##print(c.fetchone())
##
#### Larger example that inserts many records at a time
##purchases = [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
##             ('2006-04-05', 'BUY', 'MSFT', 1000, 72.00),
##             ('2006-04-06', 'SELL', 'IBM', 500, 53.00),
##            ]
##c.executemany('INSERT INTO stocks VALUES (?,?,?,?,?)', purchases)

##CREATE TABLE artist();
##CREATE TABLE track(
##FOREIGN KEY (trackartist) REFERENCES artist(artistid));

##PRIMARY KEY (column1, column2)

def crear_bd() :
    conn = sqlite3.connect("MEF.db")
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS UUEE(
            cod_uuee INTEGER PRIMARY KEY,
            descr_uuee  TEXT
        ) WITHOUT ROWID;
        
        CREATE TABLE IF NOT EXISTS Expediente(
            cod_expediente INTEGER,
            ano_ejecucion INTEGER,
            cod_uuee INTEGER,
            tipo_operacion TEXT,
            descr_operacion TEXT,
            mod_compra TEXT,
            descr_mod_compra TEXT,
            tipo_proceso TEXT,
            descr_tipo_proceso TEXT,
            FOREIGN KEY (cod_uuee) REFERENCES UUEE(cod_uuee),
            PRIMARY KEY (cod_expediente, ano_ejecucion, cod_uuee)
        ) WITHOUT ROWID;
        
        CREATE TABLE IF NOT EXISTS DatosExpediente(
            cod_expediente INTEGER,
            ano_ejecucion INTEGER,
            cod_uuee INTEGER,
            cod_secuencial INTEGER,
            ciclo TEXT,
            fase TEXT,
            num_sec INTEGER,
            num_corr INTEGER,
            cod_doc TEXT,
            num_doc INTEGER,
            fecha TEXT,
            ff TEXT,
            moneda TEXT,
            monto REAL,
            estado TEXT,
            fecha_proceso TEXT,
            id_trx TEXT,
            FOREIGN KEY (cod_expediente, ano_ejecucion, cod_uuee) REFERENCES Expediente(cod_expediente, ano_ejecucion, cod_uuee),
            PRIMARY KEY (cod_expediente, ano_ejecucion, cod_uuee, cod_secuencial)
        ) WITHOUT ROWID;
        """)
    conn.commit()
    cur.close()
    conn.close()


def insertar_datos(uuee, expediente, datos_expediente) :
    conn = sqlite3.connect("MEF.db")
    cur = conn.cursor()
    cur.executemany('INSERT INTO UUEE VALUES (?,?)', uuee)
    cur.executemany('INSERT INTO Expediente VALUES (?,?,?,?,?,?,?,?,?)', expediente)
    cur.executemany('INSERT INTO DatosExpediente VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', datos_expediente)
    conn.commit()
    cur.close()
    conn.close()


def bajar_registros(driver) :
    consulta = driver.find_elements_by_tag_name('input')
    uuee = [(int(consulta[1].get_attribute('value')), str(consulta[2].get_attribute('value')))]
    expediente = []
    expediente += (int(consulta[3].get_attribute('value')),)  ##Codigo del expediente
    expediente += (int(consulta[0].get_attribute('value')),) ##Ano del expediente
    expediente += (uuee[0][0],) ##Codigo de entidad (UUEE)
    expediente += (consulta[4].get_attribute('value'),)  ##Tipo de operacion
    expediente += (consulta[5].get_attribute('value'),)  ##Nombre de operacion
    expediente += (consulta[6].get_attribute('value'),)  ##Modalidad de compra
    expediente += (consulta[7].get_attribute('value'),)  ##Descripcion de la modalidad
    expediente += (consulta[8].get_attribute('value'),)  ##Tipo de seleccion
    expediente += (consulta[9].get_attribute('value'),)  ##Descripcion de seleccion
    ##Esperar, por si acaso
    time.sleep(1)
    consulta = driver.find_elements_by_tag_name('td')
    datos_expediente = []
    for num_fila in range(len(consulta)//14) :
        datos_expediente.append(()) ##Crear tupla en la lista
        datos_expediente[num_fila] += (expediente[0],)  ##Codigo del expediente
        datos_expediente[num_fila] += (expediente[1],) ##Ano del expediente
        datos_expediente[num_fila] += (expediente[2],) ##Codigo de entidad (UUEE)
        datos_expediente[num_fila] += ((num_fila+1),)  ##NUMERO SECUENCIAL
        datos_expediente[num_fila] += (str(consulta[num_fila*14].text),)  ##Ciclo
        datos_expediente[num_fila] += (str(consulta[num_fila*14+1].text),)  ##Fase
        datos_expediente[num_fila] += (int(consulta[num_fila*14+2].text),)  ##Num Secuencia
        datos_expediente[num_fila] += (int(consulta[num_fila*14+3].text),)  ##Num Correlativo
        datos_expediente[num_fila] += (str(consulta[num_fila*14+4].text),)  ##Cod Documento
        datos_expediente[num_fila] += (str(consulta[num_fila*14+5].text),)  ##Num Documento
        ##datos_expediente[num_fila].append(datetime.strptime(consulta[num_fila*14+6].text, "%d/%m/%y"))  ##Fecha
        datos_expediente[num_fila] += (str(consulta[num_fila*14+6].text).replace("/", "-"),)  ##Fecha
        datos_expediente[num_fila] += (str(consulta[num_fila*14+7].text),)  ##FF
        datos_expediente[num_fila] += (str(consulta[num_fila*14+8].text),)  ##Moneda
        datos_expediente[num_fila] += (float(str(consulta[num_fila*14+9].text).replace(",", "")),)  ##Monto
        datos_expediente[num_fila] += (str(consulta[num_fila*14+10].text),)  ##Estado
        ##datos_expediente[num_fila].append(datetime.strptime(consulta[num_fila*14+11].text, "%d/%m/%y %H:%M:%S"))  ##Fecha hora proceso
        datos_expediente[num_fila] += (str(consulta[num_fila*14+11].text).replace("/", "-"),)  ##Fecha hora proceso
        datos_expediente[num_fila] += (str(consulta[num_fila*14+12].text),)  ##ID_TRX

    expediente = [expediente]
    return uuee, expediente, datos_expediente



def ingresar_datos(driver, captcha_ans, cod_exp, ano_ejec, cod_uuee) :
    #ano_eje = Select(driver.find_element_by_name('anoEje'))
    #ano_eje.select_by_value(2017)
    sec_eje = driver.find_element_by_name('secEjec')
    sec_eje.send_keys(cod_uuee)
    expediente = driver.find_element_by_name('expediente')
    expediente.send_keys(cod_exp)
    captcha_form = driver.find_element_by_name('j_captcha')
    captcha_form.send_keys(captcha_ans)
    captcha_form.submit()


def resolver_captcha(driver) :##Falta mejorar
    driver.save_screenshot("screenshot.png")
    img=Image.open('screenshot.png')
    ##Como solo hay un elemento con tag 'img' (el captcha), es sencillo
    captcha_img =img.crop((315,518,515,578))
    captcha_img.save('captcha_img.png')
    #captcha_img.show()
    img = cv2.imread('captcha_img.png')
    cv2.imshow('Imagen', img)  
    cv2.waitKey(5000)
    cv2.destroyAllWindows()
    captcha_ans = input("Escriba el contenido del captcha: ")

    return captcha_ans


def conseguir_datos(driver, cod_exp, ano_ejec, cod_uuee) :
    driver.get('http://apps2.mef.gob.pe/consulta-vfp-webapp/consultaExpediente.jspx')
    driver.maximize_window()
    captcha_ans = resolver_captcha(driver)
    ingresar_datos(driver, captcha_ans, cod_exp, ano_ejec, cod_uuee)
    time.sleep(5)
    if (len(driver.find_elements_by_tag_name('blockquote')) != 0) :
        print("El registro no existe")
        return False
    else :
        uuee, expediente, datos_expediente = bajar_registros(driver)
        insertar_datos(uuee, expediente, datos_expediente)
        return True


crear_bd()
driver = webdriver.Chrome()
ano_ejec = 2017
cod_uuee = 1423
for i in range(1) :
    if (conseguir_datos(driver, i+1, ano_ejec, cod_uuee)) :
        print("Registro extraido con exito")

driver.quit()







