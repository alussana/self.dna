#!/usr/bin/env python3


import uuid
import requests
import pysam
import sqlite3
import os


GWAS_CATALOG_BASE_URL = "https://www.ebi.ac.uk/gwas/rest/api/"
GWAS_CATALOG_SNP = "singleNucleotidePolymorphisms/"


class Self(pysam.libcbcf.VariantFile):
    """
    A class to read and interact with VCF files using pysam.
    [...]

    Inherits from pysam.libcbcf.VariantFile and adds methods for
    providing the features of self.dna
    """

    def __init__(self, file_path: str, db_dir: str = None):
        """
        Initializes the Self class by opening the VCF file.
        [...]

        Parameters:
            file_path (str): Path to the VCF file.
            db_dir (str, optional): Path to the database directory.
        """
        # Initialize the parent class
        super().__init__(file_path)

        # Initialize attributes
        self.vcf_path = file_path
        self.sample_id_list = list(self.header.samples)
        self.internal_id_dict = dict(
            [(str(uuid.uuid4()), x) for x in self.sample_id_list]
        )

        # Define Self DB directory if None
        if db_dir == None:
            db_dir = "databases"

        self.db_dir = db_dir

        self.db_file_dict = dict(
            [(x, f"{db_dir}/{x}.db") for x in list(self.internal_id_dict.keys())]
        )

        # build a Self DB for each sample included in the VCF
        # for internal_id in list(self.internal_id_dict.keys()):
        #    self.vcf_to_sqlite(self.vcf_path, self.db_file_dict[internal_id])

    def vcf_to_sqlite(self, vcf_file, db_file, progress_callback=None):
        """
        Converts a VCF file to a SQLite database.

        Parameters:
        - vcf_file: Path to the input VCF file.
        - db_file: Path to the output SQLite database file.
        - progress_callback: Function to report progress (optional).
        """
        db_dir = os.path.dirname(db_file)

        # Make Self DB directory if not existing
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # Connect to SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create a table for the VCF data
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS variants (
                CHROM TEXT,
                POS INTEGER,
                ID TEXT,
                REF TEXT,
                ALT TEXT,
                QUAL REAL,
                FILTER TEXT,
                REGION TEXT,
                FUNCTION TEXT,
                MINPVALUE REAL,
                ASSOCIATIONS TEXT,
                PATHOGENICITY TEXT
            )
        """
        )

        # Parse VCF file and insert data
        with open(vcf_file, "r") as file:

            total_lines = sum(1 for _ in file if not _.startswith("#"))
            file.seek(0)

            processed_lines = 0

            for line in file:

                # Skip header lines
                if line.startswith("#"):
                    continue

                # Split the line by tab
                columns = line.strip().split("\t")
                chrom, pos, id_, ref, alt, qual, filter_, info = columns[:8]

                # Query the GWAS Catalog
                functionalClass, region, min_pvalue, associations = (
                    self.add_gwas_catalog_variant_data(id_, alt)
                )

                # Insert row into SQLite table
                cursor.execute(
                    """
                    INSERT INTO variants (CHROM, POS, ID, REF, ALT, QUAL, FILTER, REGION, FUNCTION, MINPVALUE, ASSOCIATIONS)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    # INSERT INTO variants (CHROM, POS, ID, REF, ALT, QUAL, FILTER)
                    # VALUES (?, ?, ?, ?, ?, ?, ?)
                    # """,
                    (
                        chrom,
                        int(pos),
                        id_,
                        ref,
                        alt,
                        float(qual) if qual != "." else None,
                        filter_,
                        region,
                        functionalClass,
                        min_pvalue,
                        associations,
                    ),
                )

                processed_lines += 1
                if progress_callback:
                    progress_callback(processed_lines, total_lines)

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

    def fetch_vcf_records(self, sample_id=None, region=None):
        """
        Fetches records for a specific sample, optionally limited to a genomic region.

        Parameters:
            sample_id (str, optional): The ID of the sample to fetch records for.
                                       Defaults to the first reported sample.
            region (str, optional): The genomic region to restrict the query to,
                                    in "chrom:start-end" format or "chrom".

        Yields:
            pysam.VariantRecord: Variant records for the specified sample.
        """
        if sample_id not in self.sample_id_list:
            raise ValueError(f"Sample '{sample_id}' not found in VCF.")

        # Fetch records from the specified region, if given
        iterator = self.fetch(region=region) if region else self.fetch()

        # Yield records for the specified sample
        for record in iterator:
            if sample_id in record.samples:
                yield record

    # def get_variant_ids(self, sample_id=None):
    #    if sample_id == None:
    #        sample_id = self.sample_id_list[0]
    #    variant_id_list = [
    #        record.id for record in self.fetch_by_sample(sample_id)
    #        if record.id is not None
    #    ]
    #    return variant_id_list
    def add_gwas_catalog_variant_data(self, rsid: str, alt: str):
        # print(f"Processing add_gwas_catalog_variant_data({rsid}, {alt})")
        functionalClass = None
        region = None
        min_pvalue = None
        associations = None
        url = (
            f"{GWAS_CATALOG_BASE_URL}{GWAS_CATALOG_SNP}{rsid}"  # e.g. rsid="rs6016399"
        )
        try:
            response = requests.get(url)
            data = response.json()
            functionalClass = data["functionalClass"]  # e.g. regulatory_region_variant
            region = data["locations"][0]["region"]["name"]  # e.g. 20q12
            associations_url = data["_links"]["associations"][
                "href"
            ]  # e.g. https://www.ebi.ac.uk/gwas/rest/api/singleNucleotidePolymorphisms/rs6016399/associations
            associations_response = requests.get(associations_url)
            associations_data = associations_response.json()
            associations_list = []
            pvalue_list = []
            for association in associations_data["_embedded"]["associations"]:
                p_value = float(association["pvalue"])
                risk_allele_id_nt = association["loci"][0]["strongestRiskAlleles"][0][
                    "riskAlleleName"
                ].split("-")
                study_url = association["_links"]["study"]["href"]
                study_response = requests.get(study_url)
                study_data = study_response.json()
                association = study_data["diseaseTrait"]["trait"]
                pubmedId = study_data["publicationInfo"]["pubmedId"]
                pvalue_list.append(p_value)
                associations_list.append(
                    f"{association} [p = {p_value}] [PubMed: {pubmedId}]"
                )
            associations = " | ".join(associations_list)
            min_pvalue = min(pvalue_list)
        except:
            pass
        return functionalClass, region, min_pvalue, associations


if __name__ == "__main__":
    # Example usage:
    self = Self("local/vcf/platon_header5000rows.vcf")
    print("Individual IDs:", self.sample_id_list)

    # Fetching records for a specific sample and region
    sample_id = "SAMPLE_ID"
    for record in self.fetch_vcf_records(sample_id, region="chr1:1000000-2000000"):
        genotype = record.samples[sample_id]["GT"]
        print(f"{record.chrom}:{record.pos} - Genotype: {genotype}")

    # Fetch All Records
    for record in self.fetch():
        print(record)

    # Fetch by Genomic Region
    # If your VCF file is compressed and indexed (e.g., file.vcf.gz with a .tbi index), you can access specific regions:
    for record in self.fetch("chr1", 1000000, 2000000):
        print(record)

    # Extract Information for a Specific Individual
    # To get genotype information for a specific individual, you can access the samples dictionary in each record:
    individual_id = "SAMPLE_ID"
    for record in self.fetch():
        genotype = record.samples[individual_id]["GT"]
        print(f"{record.chrom}:{record.pos} - Genotype: {genotype}")
