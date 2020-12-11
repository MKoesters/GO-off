import os, sys, time, re
import pandas as pd
from shutil import rmtree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait as ww
from selenium.webdriver.support import expected_conditions as EC


def new_dir():
    if "output" in os.listdir():
        input('Old "output" folder will be deleted. Press Enter to continue.\n')
        rmtree("./output")
    os.mkdir("./output")
    print('New "output" folder was created in the script directory.')
        
        
def picking_file():
    listd = sorted(os.listdir())
    print('\nChoose file number:')
    for q, file in enumerate(listd):
        if '.txt' in file:
            print(f"{q} = {file.replace('.txt','')}")
    picked_file_number = int(input("Put number of file: "))
    try:
        file = set(open(listd[picked_file_number]).read().splitlines())
    except:
        print('Invalid number!')
    return file


def merging(file1, file2):
    print("""
MERGING SYMBOLS:
& is for inner merge (performs intersection of files)
^ is for outer merge (performs inversed intersection of files)
- is for subtraction (takes all from first file that is not in second file)
| is for union (takes all from both files)
----------------------------------------------------------------------------
To merge your files, type one of the merging symbols and press Enter.""")
    merge_method = str(input('Choose symbol: '))
    if merge_method == '&' or merge_method == '^' or merge_method == '-' or merge_method == '|':
        return eval(f'{file1} {merge_method} {file2}')
    else:
        print('Invalid action!')


def saving_file(file_to_save):
    with open(f"output\dataset({len(file_to_save)}).txt", "w") as to_save:
        for item in sorted(file_to_save):
            to_save.write(str(item)+'\n')
        to_save.close()
    print(f'You have succesfully created new dataset: {os.listdir("output/")[0]} in output folder.')


while True:
    if os.name == 'nt':
        new_dir()
        picked_file = picking_file()
        saving_file(picked_file)

        while True:
            decision = input('Merge your dataset with another file? (y/n)\n')
            if decision == 'y':
                picked_file = picking_file()
                out_file = set(open('output/'+os.listdir("output/")[0]).read().splitlines())
                try:
                    merged_file = merging(picked_file, out_file)
                    new_dir()
                    saving_file(merged_file)
                except:
                    print('Merging failed!')
            elif decision == 'n':
                print('Proceeding to GO analysis. Please wait...')
                break
            else:
                print('Incorrect value. Please type either "y" or "n".')
                continue
        try:
            driver = webdriver.Firefox(executable_path="geckodriver")
            path = os.getcwd()
            driver.get('http://cbl-gorilla.cs.technion.ac.il/')
            first = driver.window_handles[0]
            organism = Select(driver.find_element_by_xpath('/html/body/form/blockquote[1]/table[1]/tbody/tr[2]/td/select'))
            organism.select_by_visible_text('Arabidopsis thaliana')
            mode = driver.find_element_by_xpath('/html/body/form/blockquote[1]/table[2]/tbody/tr[2]/td/font[2]/input')
            mode.send_keys(Keys.SPACE)
            box1 = driver.find_element_by_xpath('/html/body/form/blockquote[1]/table[3]/tbody/tr[4]/td/input')
            box1.send_keys(f'{path}\output\{os.listdir("output")[0]}')
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
                    g_df2['Total number of reference genes'] = g_df['Numbers'].map(lambda x: x[0]).astype('float')
                    g_df2['Number of reference genes assoc. with the GO'] = g_df['Numbers'].map(lambda x: x[1]).astype('float')
                    g_df2['Number of input dataset genes assoc. with the GO'] = g_df['Numbers'].map(lambda x: x[3]).astype('float')
                    g_df2.to_excel('output/GORILLA_table.xlsx', index=None)
                    g_df3 = pd.DataFrame(gene_ids_list).transpose()
                    g_df3.to_excel('output/GORILLA_gene_IDs.xlsx', header=g_df2['GO IDs'].values, index=None)
                    merge = rev_df2.iloc[:,[0]].merge(g_df2.iloc[:,[0, 1, 2, 4, 5]], on='GO IDs', sort=False, how='inner').dropna()
                    sorted_merge = merge.sort_values(['Enrichment'], ascending=False)
                    sorted_merge.to_excel('output/GO_RESULTS.xlsx', index=None)
            driver.quit()
        except:
            print('Sorry, something went wrong. Please try again.')
        finally:
            x = input('\nTo quit press "n" and Enter.\nTo start again press only Enter.\n\n')
            if x == 'n':
                break
                sys.exit()
            else:
                continue
