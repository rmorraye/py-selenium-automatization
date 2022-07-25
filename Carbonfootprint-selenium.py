from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import time
import pandas as pd
import numpy as np


start_time = time.time()
path_df = 'footprint_Apr7.csv'
df = pd.read_csv(path_df, sep=';')


df["Airports_caught"] = " "


### tupla das posições [linha,coluna] onde tem valor NULL (no caso abaixo pegamos só o numero das linhas da coluna 5) ###
position_row_null = np.where(pd.isnull(df.iloc[:,5]))
### tranformamos essa tupla[linhas, vazio] apenas em uma lista pois só temos o primeiro valor da tupla (linhas) ###
position_rn = list(position_row_null[0])


url = "https://calculator.carbonfootprint.com/calculator.aspx?tab=3"

#search_term = "el salvador"


### tupla das posições [linha,coluna] onde tem valor NULL (no caso abaixo pegamos só o numero das linhas da coluna 5) ###
position_row_null = np.where(pd.isnull(df.iloc[:,5]))
### tranformamos essa tupla[linhas, vazio] apenas em uma lista pois só temos o primeiro valor da tupla (linhas) ###
position_rn = list(position_row_null[0])

print(f'\n Tamanho: {len(position_rn)} / Posição 0: {position_rn[0]}\n')
print(f'\n df[] na linha (0): {df.iloc[position_rn[0],:]["City"], df.iloc[position_rn[0],:]["Country"]}\n')

    
    
######## Padrao: INCIALIZAR CHROME DRIVER ########

driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))

driver.maximize_window()
driver.implicitly_wait(2)

driver.get(url)

########## 
list_no_matches = list()
previous = 1

for i in position_rn:
    search_term = df.iloc[i,:]["City"]
    
    if(str(df.iloc[previous,:]["City"]).casefold() == str(search_term).casefold()):
        df.loc[i,"Tonnes of CO2"] = df.iloc[previous,:]["Tonnes of CO2"]
        df.loc[i,"Airports_caught"] = df.iloc[previous,:]["Airports_caught"]
        print("<IGUAL O ANTERIOR> Cidade: " + str(df.iloc[i,:]["City"]) +
              " / Toneladas de CO2: " + str(df.iloc[i,:]["Tonnes of CO2"]) +
              " / Aeroporto selecionado: " + str(df.iloc[i,:]["Airports_caught"]) + "\n")
        continue
    
    driver.implicitly_wait(2)

    search_box = driver.find_element(By.NAME, 'ctl05$rcbAirportFrom')
    search_box.send_keys(search_term)

    driver.implicitly_wait(2)
    time.sleep(2)


    first_select = driver.find_element(By.XPATH, "//ul[@class = 'rcbList']/li[1]")
    first_select_str = first_select.text
    
    if(first_select_str == "(no matches)"):
        #print("\n\nVALOR: NOTMACHES -> " + first_select.text)
        list_no_matches.append(str(search_term))
        df.loc[i,"Airports_caught"] = "(no matches)"
        print(list_no_matches)
        print('\n')
        search_box.clear()
        previous = i
        continue
    else:
        first_select.click()
    
    time.sleep(2)
    driver.implicitly_wait(2)



### Colocar sempre o valor do Aeroporto de Montreal como destino para o calculo ###
    search_box2 = driver.find_element(By.NAME, 'ctl05$rcbAirportTo')
    search_box2.send_keys("Montreal")
    time.sleep(2)
    driver.implicitly_wait(2)

### SELECIONANDO O PRIMEIRO ELEMENTO DA LISTA ###
    box_appear_first_select = driver.find_element(By.XPATH, "//ul[@class = 'rcbList']/li[1]")
    box_appear_first_select_str = box_appear_first_select.text
    box_appear_first_select.click()

    ## no caso de a pesquisa ser do mesmo lugar para o mesmo lugar (Montreal, Montreal) ##
    if(first_select_str == box_appear_first_select_str):
        previous = i
        driver.refresh()
        driver.implicitly_wait(2)
        continue

    time.sleep(2)
    driver.implicitly_wait(1)

### CLICANDO NO BOTAO DE CALCULAR ###
    button_calculate = driver.find_element(By.ID, 'ctl05_btnAddFlight')
    button_calculate.click()
    
    time.sleep(2)
    driver.implicitly_wait(1)

### PEGANDO O VALOR DE tonneladas de CO2 ###
    footprint = driver.find_element(By.XPATH, "//table[@class = 'footprints']/tbody/tr[1]")
    footprint_text = footprint.text
    tons_c02 = footprint_text.split(" ")[0]
    #print("Valor de Toneladas de carbono: " + tons_c02 + " toneladas\n")
    
    tons_c02_comma = tons_c02.split(".")[0] + "," + tons_c02.split(".")[1]
    df.loc[i,"Tonnes of CO2"] = tons_c02_comma
    df.loc[i,"Airports_caught"] = first_select_str
    print("Cidade: " + str(df.iloc[i,:]["City"]) + 
          " / Toneladas de CO2: " + str(df.iloc[i,:]["Tonnes of CO2"]) +
          " / Aeroporto selecionado: " + str(df.iloc[i,:]["Airports_caught"]) + "\n")
    
### CLICANDO em "remove" ###
    button_remove = driver.find_element(By.ID, 'grvFootprint_btnRemove_0')
    button_remove.click()

    previous = i
    #time.sleep(1)
    #driver.implicitly_wait(1)

    df.to_excel("footprint_automatic-airports_matches.xlsx")


end_time = time.time()
execution_time = end_time - start_time 
print("\n\nTempo de execução: " + str(execution_time/60) + " minutos" + "\n... Done!")

driver.close()