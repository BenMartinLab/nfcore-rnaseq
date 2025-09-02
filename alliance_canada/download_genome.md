# Download genome

To simplify examples, the main genome is assumed to be human (hg38) and the spike-in genome is assumed to be fly (dm6).

## Main genome

Download the FASTA file of the main genome. Since the whole genome contains many chromosomes, I am keeping only the main ones using a white list [human-chromosome-white-list.txt](human-chromosome-white-list.txt). 

```shell
wget https://ftp.ensembl.org/pub/release-114/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
gunzip Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
python filter-chromosome.py \
  --white human-chromosome-white-list.txt \
  Homo_sapiens.GRCh38.dna.primary_assembly.fa \
  Homo_sapiens.GRCh38.dna.primary_assembly.filtered.fa
```

If necessary, download the GTF (or GFF3) file. I am using Ensembl because the Genome Browser does not include `gene` entries in their GTF files.

```shell
wget https://ftp.ensembl.org/pub/release-114/gtf/homo_sapiens/Homo_sapiens.GRCh38.114.gtf.gz
gunzip Homo_sapiens.GRCh38.114.gtf.gz
python filter-chromosome.py \
  --white human-chromosome-white-list.txt \
  Homo_sapiens.GRCh38.114.gtf \
  Homo_sapiens.GRCh38.114.filtered.gtf
```

To simplify the use of the analysis output files, I am converting the chromosomes to the names used on the Genome Browser.

```shell
wget https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/chromAlias.txt.gz
gunzip chromAlias.txt.gz
python replace-chromosome.py --delete \
  --mapping chromAlias.txt \
  Homo_sapiens.GRCh38.dna.primary_assembly.filtered.fa \
  hg38.fa
python replace-chromosome.py --delete \
  --mapping chromAlias.txt \
  Homo_sapiens.GRCh38.114.filtered.gtf \
  hg38.gtf
```

## Spike-in genome

Download the FASTA file of the spike-in genome. Since the whole genome contains many chromosomes, I am keeping only the main ones using a white list [fly-chromosome-white-list.txt](fly-chromosome-white-list.txt).

```shell
wget https://s3ftp.flybase.org/genomes/Drosophila_melanogaster/dmel_r6.62_FB2025_01/fasta/dmel-all-chromosome-r6.62.fasta.gz
gunzip dmel-all-chromosome-r6.62.fasta.gz
python filter-chromosome.py \
  --white fly-chromosome-white-list.txt \
  dmel-all-chromosome-r6.62.fasta \
  dmel-all-chromosome-r6.62.filtered.fasta
```

If necessary, download the GTF (or GFF3) file.

```shell
wget https://s3ftp.flybase.org/genomes/Drosophila_melanogaster/dmel_r6.62_FB2025_01/gtf/dmel-all-r6.62.gtf.gz
gunzip dmel_r6.62_FB2025_01/gtf/dmel-all-r6.62.gtf.gz
python filter-chromosome.py \
  --white fly-chromosome-white-list.txt \
  dmel-all-r6.62.gtf \
  dmel-all-r6.62.filtered.gtf
```

To simplify the use of the analysis output files, I am converting the chromosomes to the names used on the Genome Browser.

```shell
wget https://hgdownload.soe.ucsc.edu/goldenPath/dm6/database/chromAlias.txt.gz
sed -i.bak '1s/^/mitochondrion_genome\tchrM\tensembl\n/' chromAlias.txt
python replace-chromosome.py --delete \
  --mapping chromAlias.txt \
  dmel-all-chromosome-r6.62.filtered.fasta \
  dm6.fa
python replace-chromosome.py --delete \
  --mapping chromAlias.txt \
  dmel-all-r6.62.filtered.gtf \
  dm6.gtf
```

Since some chromosomes are shared between human and fly, I am renaming all the fly chromosomes.  It also makes them easier to distinguish.

```shell
sed -r -i.bak 's/(^>[^ ]*)/\1_fly/g' dm6.fa
mv dm6.gtf dm6.gtf.bak
awk -F '\t' -v OFS="\t" '{if ($0 ~ /#!/) {print $0} else {$1=$1"_fly"; print $0}}' \
    dm6.gtf.bak \
    > dm6.gtf
```

### Merging both genomes together

Just merge the FASTA and GTF files together and run the analysis pipeline.

```shell
cat hg38.fa dm6.fa > hg38__dm6.fa
cat hg38.gtf dm6.gtf > hg38__dm6.gtf
```

### Keeping both genomes separate

You will need to run the analysis pipeline for both genomes unless the pipeline supports having a spike-in genome.
