import os, sys, time, re
from shutil import rmtree

import click

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait as ww
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options


def picking_file():
    listd = sorted(os.listdir())
    print("\nChoose file number:")
    for q, file in enumerate(listd):
        if ".txt" in file:
            print(f"{q} = {file.replace('.txt','')}")
    picked_file_number = int(input("Put number of file: "))
    try:
        file = set(open(listd[picked_file_number]).read().splitlines())
    except:
        print("Invalid number!")
    return file


def saving_file(file_to_save):
    with open(f"output/dataset_{len(file_to_save)}.txt", "w") as to_save:
        for item in sorted(file_to_save):
            to_save.write(str(item) + "\n")
    print(
        f'You have succesfully created new dataset: {os.listdir("output/")[0]} in output folder.'
    )


@click.command()
@click.argument("input_file")
@click.argument("background")
@click.option("--output_folder", default="Gorilla_out")
@click.option("--organism", default="Mus musculus")
@click.option("--ontology", default="Process")
@click.option("--revigo_list_length", default="medium")
@click.option("--no_headless", is_flag=True, default=True)
def main(
    input_file,
    background,
    organism="Mus musculus",
    output_folder=".",
    ontology="Process",
    revigo_list_length="medium",
    no_headless=True,
):
    if os.path.exists(output_folder):
        answer = input('Folder already exists, overwriting? [y/n]')
        if answer == 'n':
            return
    else:
        os.mkdir(output_folder)
    options = Options()
    options.headless = no_headless
    driver = webdriver.Firefox(executable_path="geckodriver", options=options)
    # driver = webdriver.PhantomJS()
    path = os.getcwd()
    driver.get("http://cbl-gorilla.cs.technion.ac.il/")
    first = driver.window_handles[0]
    organism_selector = Select(
        driver.find_element_by_xpath(
            "/html/body/form/blockquote[1]/table[1]/tbody/tr[2]/td/select"
        )
    )

    organism_selector.select_by_visible_text(organism)
    # mode.send_keys(Keys.TAB)
    ontology_dict = {
        "Process": "/html/body/form/blockquote[1]/table[4]/tbody/tr[2]/td/input[1]",
        "Function": "/html/body/form/blockquote[1]/table[4]/tbody/tr[2]/td/input[2]",
        "Component": "/html/body/form/blockquote[1]/table[4]/tbody/tr[2]/td/input[3]",
    }
    ontology_selector = driver.find_element_by_xpath(ontology_dict[ontology])
    ontology_selector.send_keys(Keys.SPACE)

    # currently only with background
    mode_selector = driver.find_element_by_xpath('/html/body/form/blockquote[1]/table[2]/tbody/tr[2]/td/font[2]/input')
    mode_selector.send_keys(Keys.SPACE)

    box1 = driver.find_element_by_xpath(
        "/html/body/form/blockquote[1]/table[3]/tbody/tr[4]/td/input"
    )
    box1.send_keys(os.path.abspath(input_file))
    box2 = driver.find_element_by_xpath(
        "/html/body/form/blockquote[1]/table[3]/tbody/tr[8]/td/span/input"
    )
    box2.send_keys(os.path.abspath(background))

    revigo_on = driver.find_element_by_xpath("/html/body/form/p[7]/input")
    revigo_on.send_keys(Keys.SPACE)

    # breakpoint()
    # run analysis
    driver.find_element_by_xpath("/html/body/form/blockquote[2]/p/font/input").click()
    time.sleep(10)

    if "No GO Enrichment Found" in driver.page_source:
        driver.quit()
        print("No GO Enrichment found!")
    else:

        # this we want to do with all GOs !
        ontology_tabs = {
            "function": "/html/body/table/tbody/tr/td[3]/h2/a",
            "component": "/html/body/table/tbody/tr/td[5]/h2/a",
        }
        while True:
            try:
                if "Show genes" not in driver.page_source:
                    break
                else:
                    driver.find_element_by_partial_link_text("Show genes").click()
            except Exception:
                break
        # breakpoint()
        g_table = pd.read_html(
            driver.find_element_by_xpath('//*[@id="table1"]').get_attribute("outerHTML")
        )[0]
        g_df = pd.DataFrame(
            {
                "GO IDs": g_table.iloc[1:, 0],
                "Description": g_table.iloc[1:, 1],
                "Enrichment": g_table.iloc[1:, 4],
                "Genes": g_table.iloc[1:, 5],
            }
        )
        g_df.to_csv(f"./{output_folder}/GORILLA_table_{ontology}.csv", header=True, index=False)
        time.sleep(10)
        driver.find_element_by_tag_name("img").screenshot(
            f"./{output_folder}/screenshot_GORILLA_{ontology}.png"
        )

        # breakpoint()
        # run analysis
        driver.find_element_by_partial_link_text("Visualize output in REViGO").click()
        second = driver.window_handles[1]
        driver.switch_to.window(second)
        time.sleep(5)
        if "REVIGO error page" in driver.page_source:
            driver.quit()
            print("REVIGO is not available now.")
        else:
            database = Select(
                driver.find_element_by_xpath("/html/body/div[1]/div[4]/form/select")
            )
            database.select_by_visible_text(organism)
            driver.find_element_by_xpath(
                "/html/body/div[1]/div[4]/form/p[5]/input"
            ).click()
            driver.find_element_by_xpath(
                "/html/body/div[1]/div[1]/div[2]/form/table/tbody/tr[1]/td[1]/a"
            ).click()
            wait_table = ww(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div[1]/div[2]/form/table")
                )
            )
            # breakpoint()
            wait_table.screenshot(f"./output/screenshot_REVIGO_{ontology}.png")
            get_table = pd.read_html(
                driver.find_element_by_xpath(
                    "/html/body/div[1]/div[1]/div[2]/form/table"
                ).get_attribute("outerHTML")
            )[0]
            rev_df = pd.DataFrame(
                {
                    "GO IDs": get_table.iloc[2:, 0],
                    "GO names": get_table.iloc[2:, 1],
                    "p-value": (get_table.iloc[2:, 4]).astype(float),
                    "dispensability": (get_table.iloc[2:, 6]).astype(float),
                }
            )
            rev_df.to_csv(f"./{output_folder}/REVIGO_table_{ontology}.csv", header=True, index=False)
            time.sleep(5)
            rev_df2 = pd.read_csv(f"./{output_folder}/REVIGO_table_{ontology}.csv")
            rev_df2 = rev_df2[rev_df2["dispensability"] < 0.7]
            rev_df2 = rev_df2.sort_values(["p-value"])
            rev_df2.to_csv(
                f"./{output_folder}/REVIGO_table_{ontology}_reduced.csv", header=True, index=False
            )

            g_df["Numbers"] = g_df["Enrichment"].map(
                lambda x: x.split(" ")[1].replace("(", "").replace(")", "").split(",")
            )
            gene_ids_list = []
            for row in g_df["Genes"]:
                row = row.split(" ")
                gene_ids = []
                for word in row:
                    if re.findall(r"AT.G.....", word):
                        gene_ids.append(word)
                gene_ids_list.append(gene_ids)
            g_df2 = pd.DataFrame()
            g_df2["GO IDs"] = g_df["GO IDs"]
            g_df2["Description"] = g_df["Description"]
            g_df2["Enrichment"] = (
                g_df["Enrichment"].map(lambda x: x.split(" ")[0]).astype("float")
            )
            g_df2["Total number of reference genes"] = (
                g_df["Numbers"].map(lambda x: x[0]).astype("float")
            )
            g_df2["Number of reference genes assoc. with the GO"] = (
                g_df["Numbers"].map(lambda x: x[1]).astype("float")
            )
            g_df2["Number of input dataset genes assoc. with the GO"] = (
                g_df["Numbers"].map(lambda x: x[3]).astype("float")
            )
            g_df2.to_csv(f"{output_folder}/GORILLA_table_{ontology}.csv", index=None)
            g_df3 = pd.DataFrame(gene_ids_list).transpose()
            g_df3.to_csv(
                f"{output_folder}/GORILLA_gene_IDs_{ontology}.csv",
                header=g_df2["GO IDs"].values,
                index=None,
            )
            merge = (
                rev_df2.iloc[:, [0]]
                .merge(
                    g_df2.iloc[:, [0, 1, 2, 4, 5]], on="GO IDs", sort=False, how="inner"
                )
                .dropna()
            )
            sorted_merge = merge.sort_values(["Enrichment"], ascending=False)
            sorted_merge.to_csv(f"{output_folder}/GO_RESULTS_{ontology}.csv", index=None)
        driver.quit()


if __name__ == "__main__":
    main()
