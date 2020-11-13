# This is a simple Python script to get GO enrichment results from GORILLA and REVIGO
# expected inputs are .txt text lists with Arabidopsis gene IDs separated by newlines - located in same folder as the script (TAIR.txt file is indispensable)
# expected outputs are 2 .png images (screenshots) and 2 .xlsx tables (GO categories with enrichment) saved in foled "output"
# Please run it on Windows, in case it is not working, please let me know
# geckodriver operates firefox browser, please install firefox before running this script
# this is just my spaghetti code... if you do not understand any part, please ask me

import os, sys, time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait as ww
from selenium.webdriver.support import expected_conditions as EC

if os.name == 'nt':
    path = os.getcwd()
    if "output" not in os.listdir():
        os.mkdir("./output")
    listd = sorted(os.listdir())
    for q, file in enumerate(listd):
        if '.txt' in file:
            print(f"Number {q} for file {file.replace('.txt','')}")
    print("---------------------------------")
    a = int(input("First file number: "))
    print(listd[a])
    b = int(input("Second file number: "))
    print(listd[b])
    print("---------------------------------")
    sfile1 = set(open(listd[a]).read().splitlines())
    sfile2 = set(open(listd[b]).read().splitlines())
    print("""
Type & for inner merge (Takes intersection)
Type ^ for outer merge (Takes inversed intersection)
Type - for subtraction (Takes data from first file that are not in second file)
Type | for union (Takes all data from both files)

Confirm by pressing Enter.
---------------------------------
""")
    i = input("\nComparison number: ")
    if i == "&":
        set_operation = sfile1 & sfile2
    elif i == "^":
        set_operation = sfile1 ^ sfile2
    elif i == "-":
        set_operation = sfile1 - sfile2
    elif i == "|":
        set_operation = sfile1 | sfile2
    else:
        print('Invalid action!')
        time.sleep(5)
        sys.exit()
    with open("sets.txt", "w") as sets:
        for item in sorted(set_operation):
            sets.write(str(item)+'\n')
        sets.close()
    driver = webdriver.Firefox(
        executable_path="geckodriver")
    # driver.minimize_window()

    try:
        driver.get('http://cbl-gorilla.cs.technion.ac.il/')
        first = driver.window_handles[0]
        organism = Select(driver.find_element_by_xpath(
            '/html/body/form/blockquote[1]/table[1]/tbody/tr[2]/td/select'))
        organism.select_by_visible_text('Arabidopsis thaliana')
        mode = driver.find_element_by_xpath(
            '/html/body/form/blockquote[1]/table[2]/tbody/tr[2]/td/font[2]/input')
        mode.send_keys(Keys.SPACE)
        box1 = driver.find_element_by_xpath(
            '/html/body/form/blockquote[1]/table[3]/tbody/tr[4]/td/input')
        box1.send_keys(f'{path}\sets.txt')
        box2 = driver.find_element_by_xpath(
            '/html/body/form/blockquote[1]/table[3]/tbody/tr[8]/td/span/input')
        box2.send_keys(f'{path}\TAIR10.txt')
        revigo_on = driver.find_element_by_xpath(
            '/html/body/form/p[7]/input')
        revigo_on.send_keys(Keys.SPACE)
        driver.find_element_by_xpath(
            '/html/body/form/blockquote[2]/p/font/input').click()
        time.sleep(10)
        if 'No GO Enrichment Found' in driver.page_source:
            driver.quit()
            print("No GO Enrichment found!")
        else:
            driver.find_element_by_tag_name('img').screenshot('./output/GORILLA_tree.png')
            driver.find_element_by_partial_link_text('Visualize output in REViGO').click()
            second = driver.window_handles[1]
            driver.switch_to.window(second)
            time.sleep(5)
            database = Select(driver.find_element_by_xpath(
                '/html/body/div[1]/div[4]/form/select'))
            database.select_by_visible_text(
                'Arabidopsis thaliana')
            driver.find_element_by_xpath(
                '/html/body/div[1]/div[4]/form/p[5]/input').click()
            driver.find_element_by_xpath(
                '/html/body/div[1]/div[1]/div[2]/form/table/tbody/tr[1]/td[1]/a').click()
            wait_table = ww(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, '/html/body/div[1]/div[1]/div[2]/form/table')))
            wait_table.screenshot('./output/REVIGO_table.png')
            get_table = pd.read_html(driver.find_element_by_xpath(
                '/html/body/div[1]/div[1]/div[2]/form/table').get_attribute('outerHTML'))[0]
            df = pd.DataFrame(
                {'GO IDs': get_table.iloc[2:,0],
                 'GO names': get_table.iloc[2:,1],
                 'p-value': (get_table.iloc[2:,4]).astype(float),
                 'dispensability': (get_table.iloc[2:,6]).astype(float)})
            df.to_excel('./output/result_table.xlsx', header=True, index=False)
            df2 = pd.read_excel('./output/result_table.xlsx')
            df2 = df2[df2['dispensability']<0.7]
            df2 = df2.sort_values(['p-value'])
            df.to_excel('./output/result_table_reduced_by_REVIGO.xlsx', header=True, index=False)

    finally:
        driver.quit()
