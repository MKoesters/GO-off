<h1>
    GO-off
</h1>
<h3>This is a simple Python script for running GO enrichment by GORILLA (http://cbl-gorilla.cs.technion.ac.il/) and REVIGO (http://revigo.irb.hr/index.jsp) online tools with default settings.</h3>

<pre>
Notes:
geckodriver operates firefox browser, so you have to install Firefox browser before 
    running this script
Please run it only with Windows 10, and in case it is not working, please let me know
Expected inputs are text (.txt) lists with Arabidopsis gene IDs separated 
    by newlines - located in same folder as the script
Expected outputs (saved in foled "output") are:
    one text (.txt) file containing Arabidopsis gene IDs made by user-defined 
        merge (inside parentheses is the number of gene IDs)
    two screenshot (.png) images from GORILLA and REVIGO webpages
    excel tables: 
        GORILLA table with calculated enrichment, etc.
        GORILLA gene IDs extracted from GORILLA table GO categories
        REVIGO table
        REVIGO reduced table (dispensability <= 0.7)
        GO RESULTS = most important file - contains REVIGO-reduced GO IDs and 
            GORILLA-counted numbers (enrichment, ...)
This script can be run multiple times in a loop, but keep in mind that the content 
    in folder "output" is overwritten every time
I apologize for the script. This is still just my spaghetti code... if you do not 
    understand any part, please ask me
<br>
Eran Eden, Roy Navon, Israel Steinfeld, Doron Lipson and Zohar Yakhini. "GOrilla: 
    A Tool For Discovery And Visualization of Enriched GO Terms in Ranked Gene Lists",
    BMC Bioinformatics 2009, 10:48.
Eran Eden, Doron Lipson, Sivan Yogev, Zohar Yakhini. "Discovering Motifs in Ranked Lists
    of DNA sequences", PLoS Computational Biology, 3(3):e39, 2007.
Supek F, Bošnjak M, Škunca N, Šmuc T. "REVIGO summarizes and visualizes long lists of Gene 
    Ontology terms", PLoS ONE 2011. doi:10.1371/journal.pone.0021800
</pre>
