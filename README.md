# Ortholist 2
## Overview
This project updates Ortholist ([version 1 here](http://www.greenwaldlab.org/ortholist/)) with results from both additional ortholog prediction programs and updated releases of previously included programs.

## Databases used
* Ensembl Compara (Release 87, 2016-12)
* Homologene (Build 68, 2014-05-06)
* InParanoid (8.0, 2013-12)
* OMA (May 2016)
* OrthoInspector
* OrthoMCL (Version 5, 2015-07-23)

## Instructions
### Pre-requisites
This project makes use of Python 3 and MySQL. If you're on OS X / macOS, you can get these by first installing [Homebrew](https://brew.sh/) by putting the following on your Terminal:
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Then running
```
brew install python3
brew install mysql
```

Once MySQL installation is complete, get the service started with `mysql.server start`. You can connect to the service using `mysql -uroot` anytime to check the databases within.

### Code
The majority of the code is located under `src/run.py`, which processes the both raw and pre-processed data from ortholog prediction programs stored under `results`.

## Methodology
### WormBase
The different databases used for Ortholist were generated at different dates. As a result, worm genes are sometimes not up to date with the most current WormBase database. We keep track of every changed WormBase ID and update it to the most current version or to none if deprecated. The WormBase version used for this version of Ortholist is WS255, available [here](ftp://ftp.wormbase.org/pub/wormbase/species/c_elegans/annotation/geneIDs/c_elegans.PRJNA13758.WS255.geneIDs.txt.gz).

This WormBase ID updating is done through [`get_ce_wb_updated()`](https://github.com/woojink/ortholist/blob/master/src/helper/wb_map.py#L49) under `helper.wb_map`

### OrthoMCL
Version 5 (2015-07-23) of OrthoMCL is obtained [here](http://orthomcl.org/common/downloads/release-5/pairs/orthologs.txt.gz). Worm genes are provided as WormBase IDs and human genes are provided as ENSP IDs. Version 5 of OrthoMCL uses [Ensembl release 56](ftp://ftp.ensembl.org/pub/release-56/mysql/homo_sapiens_core_56_37a/)

1. First, the orthologs are read from OrthoMCL, provided on [this page](http://orthomcl.org/common/downloads/release-5/pairs/orthologs.txt.gz). Each line of this file indicates an ortholog here. Each human and worm gene is preceded with "`hsap|`" and "`cele|`" respectively.
2. The included `cleanup.sh` file filters for only lines that have both "`hsap|`" and "`cele|`", indicating a human-worm ortholog. Further editing is done to result in a clean CSV for the subsequent steps.
3. Human genes are provided as ENSP IDs, which needs to be converted to ENSG IDs for the purpose of this project. Using four tables from Ensembl (`translation_stable_id.txt.gz`, `translation.txt.gz`, `transcript.txt.gz`, `gene_stable_id.txt.gz`), we are able to obtain ENSG ID that correspond to each ENSP ID.
4. WormBase ID changes are dealt with using `get_ce_wb_updated()` (see [above](#wormbase))

### OMA
May 2016 release of OMA is used.

1. Orthologs are directly obtained from [this endpoint](http://omabrowser.org/cgi-bin/gateway.pl?f=PairwiseOrthologs&p1=CAEEL&p2=HUMAN&p3=EnsemblGene). Each line of this file indicates an ortholog: worm genes are provided as OMA IDs and human genes as ENSG IDs.
2. OMA IDs for worm genes are first mapped to Wormpep IDs using the provided [map file](http://omabrowser.org/All/oma-wormbase.txt.gz) from OMA. The Wormpep IDs are from WS235 and they are translated to Wormbase IDs using the `wormpep.table235` from Wormbase ([download here](ftp://ftp.wormbase.org/pub/wormbase/species/c_elegans/sequence/protein/c_elegans.WS235.wormpep_package.tar.gz)).
3. WormBase ID changes are dealt with using `get_ce_wb_updated()` (see [above](#wormbase))

### Ensembl Compara
Release 87 (2016-12) of Ensembl is used for Ortholist.

1. Orthologs are directly obtained from [December 2016 BioMart](http://dec2016.archive.ensembl.org/biomart/martview). Worm genes were obtained as Wormbase IDs and human genes as ENSG IDs.
2. WormBase ID changes are dealt with using `get_ce_wb_updated()` (see [above](#wormbase))

### InParanoid
Release 8.0 (2013-12) of InParanoid is used for Ortholist.

1. Raw SQL table (`sqltable.C.elegans-H.sapiens`) for the orthologs is downloaded from [this link](http://inparanoid.sbc.su.se/download/8.0_current/Orthologs_other_formats/C.elegans/InParanoid.C.elegans-H.sapiens.tgz). Both worm and human genes are provided as UniProt IDs. The orthologs are provided as groupings, so combinations are generated using [`generate_combinations()`](https://github.com/woojink/ortholist/blob/master/src/helper/misc.py#L41) under `helper.misc`. We first generate a more tractable ortholog file `orthologs.tsv` under the InParanoid data folder using the above method.
2. For the worm genes:
    * The majority of the UniProt IDs are mapped using the ID mapping tool from UniProt available [here](http://www.uniprot.org/uploadlists/). As release 8.0 was released in 2013-12, there are many IDs no longer mappable.
    * For the rest, we look at the UniProt ID history pages to determine the last known entry (e.g. [`http://www.uniprot.org/uniprot/A4UVJ9?version=*`](http://www.uniprot.org/uniprot/A4UVJ9?version=*) shows 47 is the latest for `A4UVJ9`)
    * Then using that latest entry, we access the actual entry page to scrape the last known WormBase ID for the particular UniProt ID (e.g. [`http://www.uniprot.org/uniprot/A4UVJ9.txt?version=47`](http://www.uniprot.org/uniprot/A4UVJ9.txt?version=47) shows `WBGene00019439` is the last known correspondent with `A4UVJ9`)
3. For the human genes:
    * As with the worm genes, the majority of the UniProt IDs are mapped using the [ID mapping tool](http://www.uniprot.org/uploadlists/)
    * The ones that could not be found at this point are then searched through the [BioMart tool for Ensembl 74](http://dec2013.archive.ensembl.org/biomart/martview/) (2013-12), which is the closest release to InParanoid 8.0 (also 2013-12). Both SwissPort and TrEMBL entries are looked at.
    * At this point, the remaining 135 IDs are scraped through the history pages as with the worm genes previously, yield 9 more entries.
4. Lastly, the WormBase ID changes are dealt with using `get_ce_wb_updated()` (see [above](#wormbase))

### OrthoInspector
For OrthoInspector, "Quest for Orthologs (QfO) 04_2013" (2013-04) was used.

1. The raw worm orthologs are available on [this `gzip`-ed CSV file](http://lbgi.fr/orthoinspector/dbquery_qfo/data/CSV/62.csv.gz) (warning: large 1.22 GB file). Each line in this file represents an ortholog. Only the UniProt IDs are extracted from each line, then filtered for only lines containing human orthologs (see [`preprocess.sh`](https://github.com/woojink/ortholist/blob/master/data/orthoinspector/preprocess.sh) for more details)
2. The rest of the process for OrthoInspector is identical, where
    * Worm genes were first mapped through UniProt's ID mapping tool, then scraped through history pages
    * Human genes were also first mapped through UniProt's ID mapping tool, then the [BioMart tool for Ensembl 74](http://dec2013.archive.ensembl.org/biomart/martview/) (2013-12), which is the closest release to 2013-04, then lastly through scraping. 11 of 13 remaining ID correspondents are found after scraping.
3. Lastly, the WormBase ID changes are dealt with using `get_ce_wb_updated()` (see [above](#wormbase))
