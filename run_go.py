# This is a simple Python script to get GO enrichment results from GORILLA and REVIGO (with default settings)
# geckodriver operates firefox browser, so you have to install Firefox browser before running this script
# Please run it only with Windows 10, and in case it is not working, please let me know
# Expected inputs are text (.txt) lists with Arabidopsis gene IDs separated by newlines - located in same folder as the script
# Expected outputs (saved in foled "output") are:
    # one text (.txt) list with Arabidopsis gene IDs coming from user-defined merge (see instructions during running the script)
    # two screenshot (.png) images from GORILLA and REVIGO webpages
    # six excel tables: 
        # GORILLA table with calculated enrichment, etc.
        # GORILLA gene IDs extracted from GORILLA table GO categories
        # REVIGO table
        # REVIGO reduced table (dispensability <= 0.7)
        # GO RESULTS = most important file - contains REVIGO-reduced GO IDs and GORILLA-counted numbers (enrichment, ...)
# //this is just my spaghetti code... if you do not understand any part, please ask me
# This script can be run multiple times in a loop, but keep in mind that the content in folder "output" is overwritten every time

import os, sys, time, re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait as ww
from selenium.webdriver.support import expected_conditions as EC

while True:
    if os.name == 'nt':
        path = os.getcwd()
        if "output" not in os.listdir():
            os.mkdir("./output")
        listd = sorted(os.listdir())
        for q, file in enumerate(listd):
            if '.txt' in file:
                print(f"Number {q} for file {file.replace('.txt','')}")
        a = int(input("First file number: "))
        print(listd[a], end='')
        b = int(input("Second file number: "))
        print(listd[b])
        sfile1 = set(open(listd[a]).read().splitlines())
        sfile2 = set(open(listd[b]).read().splitlines())
        print("""
Type & for inner merge (Takes intersection)
Type ^ for outer merge (Takes inversed intersection)
Type - for subtraction (Takes data from first file that are not in second file)
Type | for union (Takes all data from both files)
---------------------------------
Confirm by pressing Enter.
---------------------------------""")
        i = input("Comparison symbol: ")
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
        with open(f"output\sets({len(set_operation)}).txt", "w") as sets:
            for item in sorted(set_operation):
                sets.write(str(item)+'\n')
            sets.close()
        driver = webdriver.Firefox(executable_path="geckodriver")

        try:
            driver.get('http://cbl-gorilla.cs.technion.ac.il/')
            first = driver.window_handles[0]
            organism = Select(driver.find_element_by_xpath('/html/body/form/blockquote[1]/table[1]/tbody/tr[2]/td/select'))
            organism.select_by_visible_text('Arabidopsis thaliana')
            mode = driver.find_element_by_xpath('/html/body/form/blockquote[1]/table[2]/tbody/tr[2]/td/font[2]/input')
            mode.send_keys(Keys.SPACE)
            box1 = driver.find_element_by_xpath('/html/body/form/blockquote[1]/table[3]/tbody/tr[4]/td/input')
            box1.send_keys(f'{path}\output\sets({len(set_operation)}).txt')
            box2 = driver.find_element_by_xpath('/html/body/form/blockquote[1]/table[3]/tbody/tr[8]/td/span/input')
            box2.send_keys(f'{path}\TAIR10.txt')
            revigo_on = driver.find_element_by_xpath('/html/body/form/p[7]/input')
            revigo_on.send_keys(Keys.SPACE)
            driver.find_element_by_xpath('/html/body/form/blockquote[2]/p/font/input').click()
            time.sleep(10)
            if 'No GO Enrichment Found' in driver.page_source:
                driver.quit()
                print("No GO Enrichment found!")
            else:
                while True:
                    try:
                        if 'Show genes' not in driver.page_source:
                            break
                        else:
                            driver.find_element_by_partial_link_text('Show genes').click()
                    except:
                        break
                g_table = pd.read_html(driver.find_element_by_xpath('//*[@id="table1"]').get_attribute('outerHTML'))[0]
                g_df =pd.DataFrame(
                    {'GO IDs': g_table.iloc[1:, 0],
                     'Description': g_table.iloc[1:, 1],
                     'Enrichment': g_table.iloc[1:, 4],
                     'Genes': g_table.iloc[1:, 5]})
                g_df.to_excel('./output/GORILLA_table.xlsx', header=True, index=False)
                time.sleep(5)
                driver.find_element_by_tag_name('img').screenshot('./output/screenshot_GORILLA.png')
                driver.find_element_by_partial_link_text('Visualize output in REViGO').click()
                second = driver.window_handles[1]
                driver.switch_to.window(second)
                time.sleep(10)
                if 'REVIGO error page' in driver.page_source:
                    driver.quit()
                    print('REVIGO is not available now.')
                else:
                    database = Select(driver.find_element_by_xpath('/html/body/div[1]/div[4]/form/select'))
                    database.select_by_visible_text('Arabidopsis thaliana')
                    driver.find_element_by_xpath('/html/body/div[1]/div[4]/form/p[5]/input').click()
                    driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/form/table/tbody/tr[1]/td[1]/a').click()
                    wait_table = ww(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[2]/form/table')))
                    wait_table.screenshot('./output/screenshot_REVIGO.png')
                    get_table = pd.read_html(driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/form/table').get_attribute('outerHTML'))[0]
                    rev_df = pd.DataFrame(
                        {'GO IDs': get_table.iloc[2:,0],
                         'GO names': get_table.iloc[2:,1],
                         'p-value': (get_table.iloc[2:,4]).astype(float),
                         'dispensability': (get_table.iloc[2:,6]).astype(float)})
                    rev_df.to_excel('./output/REVIGO_table.xlsx', header=True, index=False)
                    time.sleep(5)
                    rev_df2 = pd.read_excel('./output/revigo_table.xlsx')
                    rev_df2 = rev_df2[rev_df2['dispensability']<0.7]
                    rev_df2 = rev_df2.sort_values(['p-value'])
                    rev_df2.to_excel('./output/REVIGO_table_reduced.xlsx', header=True, index=False)

                    g_df['Numbers'] = g_df['Enrichment'].map(lambda x: x.split(' ')[1].replace('(','').replace(')','').split(','))
                    gene_ids_list = []
                    for row in g_df['Genes']:
                        row = row.split(' ')
                        gene_ids = []
                        for word in row:
                            if re.findall(r'AT.G.....', word):
                                gene_ids.append(word)
                        gene_ids_list.append(gene_ids)
                    g_df2 = pd.DataFrame()
                    g_df2['GO IDs'] = g_df['GO IDs']
                    g_df2['Description'] = g_df['Description']
                    g_df2['Enrichment'] = g_df['Enrichment'].map(lambda x: x.split(' ')[0]).astype('float')
                    g_df2['Total number of genes'] = g_df['Numbers'].map(lambda x: x[0]).astype('float')
                    g_df2['Total number of genes assoc. with this GO term'] = g_df['Numbers'].map(lambda x: x[1]).astype('float')
                    g_df2['Number of my genes inside this GO'] = g_df['Numbers'].map(lambda x: x[3]).astype('float')
                    g_df2.to_excel('output/GORILLA_table.xlsx', index=None)
                    g_df3 = pd.DataFrame(gene_ids_list).transpose()
                    g_df3.to_excel('output/GORILLA_gene_IDs.xlsx', header=g_df2['GO IDs'].values, index=None)
                    merge = rev_df2.iloc[:,[0,2]].merge(g_df2, on='GO IDs', sort=False, how='inner').dropna()
                    sorted_merge = merge.sort_values(['Enrichment'], ascending=False)
                    sorted_merge.to_excel('output/GO_RESULTS.xlsx', index=None)
        finally:
            driver.quit()
        x = input('\nTo quit press "n" and Enter.\nTo start again press only Enter.\n\n')
        if x == 'n':
            break
            sys.exit()
        else:
            continue
