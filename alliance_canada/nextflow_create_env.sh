#!/bin/bash

python -m venv nf-core-env
source nf-core-env/bin/activate
python -m pip install nf_core==3.2.1

echo
echo

echo "Activate nf-core virtual environment:"
echo "source nf-core-env/bin/activate"
echo
echo "Example to download chipseq pipeline:"
echo "nf-core pipelines download --download-configuration yes \\"
echo "    --container-cache-utilisation amend --container-system singularity \\"
echo "    --compress none -d 6 -r 3.19.0 rnaseq"
echo
echo "Example to run the chipseq pipeline:"
echo "nextflow run nf-core-rnaseq_3.19.0/3_19_0/ \\"
echo "    -profile test,alliance_canada \\"
echo "    --outdir output"
