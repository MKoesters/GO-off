<h1>
    GO-off
</h1>
<h3>This is a Python script for automation of steps for running GORILLA (http://cbl-gorilla.cs.technion.ac.il/) and REVIGO (http://revigo.irb.hr/index.jsp) online tools (with default settings) to perform GO enrichment on datasets of Arabidopsis thaliana gene IDs.</h3>
<pre>
Expected input dataset is a text file (located in the folder with script) containing gene IDs separated by newlines.
    As an example of input data, I provided two datasets (dataset_1 and dataset_2). Reference dataset cannot be replaced.
Expected outputs (saved in foled "output") are:
    text (.txt) file of Arabidopsis gene IDs dataset used for GO analysis (parentheses of the file name shoe the number of IDs)
    two screenshot (.png) images from GORILLA and REVIGO webpages
    excel tables: 
        GORILLA table with calculated enrichment, etc.
        GORILLA gene IDs extracted from GORILLA table GO categories REVIGO table
        REVIGO reduced table (dispensability <= 0.7)
        GO RESULTS = contains REVIGO-reduced GO category IDs and counted numbers (enrichment, ...)
</pre>
<h4>
Important notes:
The geckodriver operates Firefox browser, so you have to install this browser before running the script.
Please run the script only with Windows 10. Let me know, in case it is not working on your machine.
Keep in mind that the content in folder "output" is overwritten with each iteration.
</h4>
<h3>Comments:</h3>
<h5>The aim of the last update is to give the user more freedom in selecting and merging user's input datasets.
Now there is no limit for the number of merges of user's input files, so the user can create various merging workflow.
This script can be run multiple times in a loop but each merging prompt takes always only two files.
<br><br>
This update  includes warning messages whenever the "output" folder and its content is going to be overwritten.
The user needs to confirm it each time by pressing Enter. This gives a space for quickly placing the content somewhere else to save it, if needed.
In the future I am planning to modify the script to provide an extra file with history of the user's merging workflow steps,
so the user will get more information about the merging actions that have been done on the output dataset.
<br><br>
Also, I apologize for my spaghetti code... Please ask me, if you do not understand any part of the script.
</h5>
<br><br>
<h6>
Eran Eden*, Roy Navon*, Israel Steinfeld, Doron Lipson and Zohar Yakhini. "GOrilla: A Tool For Discovery And Visualization of Enriched GO Terms in Ranked Gene Lists", BMC Bioinformatics 2009, 10:48.<br>
Eran Eden, Doron Lipson, Sivan Yogev, Zohar Yakhini. "Discovering Motifs in Ranked Lists of DNA sequences", PLoS Computational Biology, 3(3):e39, 2007.<br>
Supek F, Bošnjak M, Škunca N, Šmuc T. "REVIGO summarizes and visualizes long lists of Gene Ontology terms", PLoS ONE 2011. doi:10.1371/journal.pone.0021800
</h6>
