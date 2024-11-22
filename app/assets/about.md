#### What's inside the nucleus of your cells?

This app was born from the idea that everyone should be able to browse, interpret, and understand their own source code.

A very small percentage of humans alive today posses fundamental knowledge in molecular biology and genetics.
However, right now we have capabilities that could have been considered science fiction until only some years ago:

* **reading DNA has become extremely cheap**.
  Reading a human genome can be done commercially, B2C, for a few hundred bucks.
* **writing DNA has become routine**.
  Tools to stably modify DNA in living organisms, so that the changes can be passed on to the offspring, are now established and frequently used in the lab.

The technologies behind these and other advancements allow us, every day and right now,
to discover causes of disease, to make powerful diagnostic tools and targeted therapeutics, to design efficient biomanufacturing processes, to engineer crops and foods with ideal properties, and more.

They also have an additional consequence.

_Before_, any modification of the human genome, and of allele frequencies in human populations that occurred through history, could exclusively be attributed to mating, natural selection, and migrations.

From now on, this is no longer necessarily the case. By unlocking the "writing permissions" on the genome, we have now reached the point in our short history where we can potentially take conscius decisions to alter our DNA and the DNA of our offspring with targeted changes. 
**Humans have evolved to a point in which they are potentially capable of controlling and accelerating their own evolution.**
While all previously mentioned evolutionary processes will continue to act as usual, the possibility to alter our genetic pool at will needs to be considered into the equation. 

This is not likely to happen for a long while, at least not at scale. The reason is because our understanding of how genetic information and other molecular features translate into physical traits is still limited.
Nonetheless, we possess the ability to functionally characterise the variations in our DNA to an extent that for most people would be highly surprising. Likewise, it is possible to predict a likely functional outcome for many hypothetical DNA changes.

Our capabilities to interpret and work with our DNA are constantly improving. This app aims at bringing these capabilities to any individual so that they can take a look at their genome and learn something about it.


#### Features

`self.dna` provides tools for genomic data analysis, listed below. _Ticks identify currently implemented functionalities._

- [x]   [Variants upload and processing](#variants-upload-and-processing)
- [x]   [GWAS catalog exploration](#gwas-catalog-exploration)
- [ ]   [Variant pathogenicity predictions](#variant-pathogenicity-predictions)
- [ ]   [Genome-wide statistics](#genome-wide-statistics)
- [ ]   [Polygenic Risk Scores](#polygenic-risk-scores)
- [ ]   [Curated knowledgebase](#curated-knowledgebase)

##### Variants upload and processing

Start here by uploading your genetic data.
The currently accepted format to represent human genetic variants is [VCF](https://www.ebi.ac.uk/training/online/courses/human-genetic-variation-introduction/variant-identification-and-analysis/understanding-vcf-format/).
Your VCF file will be stored locally and processed, which can take a long time depending on the available computing resources.
During processing, an SQLite database is built containing all the information related to your DNA that can be browsed using the app.
From the VCF itself the following information for each variant is retained:

* Chromosome
* Position
* ID
* Reference allele
* Alternate allele
* Quality score
* Filter

##### GWAS catalog exploration

Each individual genetic variant reported in the uploaded data is searched on the [GWAS Catalog](https://www.ebi.ac.uk/gwas/home) using its reference variant ID ([rsID](https://www.ncbi.nlm.nih.gov/snp/docs/RefSNP_about/)), if available.
The GWAS Catalog is queried via the RESTful API to fetch the following information about the variant:

* **Functional class**: the genomic functional context, e.g. coding variant, intron, regulatory, intergenic, etc.
* **Region**: the [chromosome band](https://www.ncbi.nlm.nih.gov/books/NBK22266/) defined the cytogenetic mapping. E.g. a variant at 11p15.4 lies on the short arm (p) of chromosome 11 and is found at the band labeled 15.4.
* **Minimum _p_ value**: the minimum _p_ value ever reported for the variant for any trait association.
* **Associations**: a list of traits reported as being associated with the variant according to Genome-wide association studies ([GWAS](https://www.genome.gov/genetics-glossary/Genome-Wide-Association-Studies-GWAS)).
                    Each association is accompanied by a _p_ value and the [PubMed ID](https://pubmed.ncbi.nlm.nih.gov) identifying the study where the association has been reported.

The information above is reported in a interactive table that can be filtered by column content.

##### Variant pathogenicity predictions

\[...\]

##### Genome-wide statistics

\[...\]

##### Polygenic Risk Scores

\[...\]

##### Curated knowledgebase

\[...\]

#### Self hosting

When it comes to personal genomic data, privacy can be an issue.
This application is meant to be portable and it can be depolyed anywhere with minimal effort. You can host `self.dna` on your own computer by cloning the repository and following these steps:

1. Build the Docker image

   `docker build -t self.dna .`

2. Choose the local storage directories and port
   
   `UPLOADS_DIR="$(pwd)/uploads"`
  
   `DB_DIR="$(pwd)/databases"`

   `SELF_DNA_PORT="8050"`

3. Run the container

   `docker run -p ${SELF_DNA_PORT}:8050 -v ${UPLOADS_DIR}:/app/uploads -v ${DB_DIR}:/app/databases self.dna`

4. Connect

   Your `self.dna` instance is reachable at [http://localhost:8050](http://localhost:8050) (or the port set by `${SELF_DNA_PORT}`).

#### Developed by

Alessandro Lussana, [http://alussana.xyz](http://alussana.xyz)

EMBL-EBI, Wellcome Genome Campus, Hinxton, Cambridge CB10 1SD, UK

#### Licence

This work is distributed under the [Apache-2.0 license](https://www.apache.org/licenses/LICENSE-2.0.txt).

Copyright 2024 Alessandro Lussana