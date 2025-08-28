# RNA-seq nf-core pipeline on Alliance Canada servers

* [Installation](#installation)
  * [Connect to Alliance Canada server](#connect-to-alliance-canada-server)
  * [Creating directory where the pipeline will be run](#creating-directory-where-the-pipeline-will-be-run)
  * [Clone repository on server](#clone-repository-on-server)
  * [Loading modules and setting variables](#loading-modules-and-setting-variables)
  * [Creating Python virtual environment](#creating-python-virtual-environment)
  * [Downloading required containers to run the pipeline](#downloading-required-containers-to-run-the-pipeline)
* [Run the pipeline on Rorqual or Narval](#run-the-pipeline-on-rorqual-or-narval)
  * [Create tmux session](#create-tmux-session)
  * [Loading modules and activating the Python virtual environment](#loading-modules-and-activating-the-python-virtual-environment)
  * [Run the pipeline](#run-the-pipeline)
* [Run the pipeline on Cedar](#run-the-pipeline-on-cedar)
  * [Alternative using the wait script](#alternative-using-the-wait-script)
* [Output files](#output-files)
  * [Standard output files](#standard-output-files)
  * [Additional output files](#additional-output-files)

## Installation

### Connect to Alliance Canada server

While you can run nf-core pipelines on any general servers, you will find it easier to run nf-core on Rorqual or Narval.

To learn how to connect to a server, look at the [Alliance Canada Wiki about SSH](https://docs.alliancecan.ca/wiki/SSH)

### Creating directory where the pipeline will be run

```shell
# On Rorqual
cd ~/links/scratch
mkdir rnaseq
cd rnaseq
# On other servers
cd ~/scratch
mkdir rnaseq
cd rnaseq
```

### Clone repository on server

```shell
git clone https://github.com/BenMartinLab/nfcore-rnaseq
cd nfcore-rnaseq
git checkout <BRANCH>
cd ..
```

where `<BRANCH>` is the version of the pipeline you want to run, for example `3.19.0_spikein`. 

### Loading modules and setting variables

To load the required modules, you can use [nextflow_init.sh](nextflow_init.sh) script or load modules manually.

```shell
source nfcore-rnaseq/alliance_canada/nextflow_init.sh
```

or

```shell
module purge
module load StdEnv/2023
module load python/3.13
module load rust
module load postgresql
module load nextflow/25
module load apptainer/1

export SLURM_ACCOUNT=def-bmartin
export NXF_SINGULARITY_CACHEDIR=/project/def-bmartin/NXF_SINGULARITY_CACHEDIR
export NXF_OPTS="-Xms500M -Xmx8000M"
```

### Creating Python virtual environment

You can use [nextflow_create_env.sh](nextflow_create_env.sh) script or do it manually.

```shell
source nfcore-rnaseq/alliance_canada/nextflow_create_env.sh
```

```shell
python -m venv nf-core-env
source nf-core-env/bin/activate
python -m pip install nf_core==3.2.1
```

### Downloading required containers to run the pipeline

```shell
nf-core pipelines download \
    --download-configuration yes \
    --container-cache-utilisation amend \
    --container-system singularity \
    --compress none \
    --parallel-downloads 6 \
    --revision <VERSION> rnaseq
```

where `<VERSION>` is the version of the pipeline you want to run, for example `3.19.0`.

## Run the pipeline on Rorqual or Narval

### Create tmux session

You need to remember on which login node you started the tmux session in case you get disconnected from the server. If you have trouble remembering the login node, connect to the first login node. On Narval, use this command:

```shell
ssh narval1
cd ~/scratch/rnaseq
```

Start a new tmux session:

```shell
tmux new -s rnaseq
```

Once inside the tmux session, you may find it difficult to return to your regular shell. Use `Ctrl+b` than `d` to detach from the tmux session.

To reattach to the tmux session, use this command (must be executed from the same login node on which you started the session):

```shell
tmux a -t rnaseq
```

You can see active tmux sessions using this command:

```shell
tmux ls
```

For more information on tmux, see [tmux documentation](https://github.com/tmux/tmux/wiki).

Cheatsheet for tmux [https://tmuxcheatsheet.com](https://tmuxcheatsheet.com).

### Loading modules and activating the Python virtual environment

```shell
source nfcore-rnaseq/alliance_canada/nextflow_init.sh
source nf-core-env/bin/activate
```

### Run the pipeline

```shell
nextflow run nfcore-rnaseq \
    -profile alliance_canada \
    --input <SAMPLESHEET> \
    --outdir <OUTDIR> \
    --fasta <GENOME FASTA> \
    --gtf <GTF> \
    --additional_fasta <SPIKEIN_FASTA>
```

See [https://nf-co.re/rnaseq](https://nf-co.re/rnaseq) for more details about parameters.

## Run the pipeline on Cedar

Please use Rorqual or Narval when possible because running nf-core pipelines on Cedar is much less trivial because the login node virtual memory limit cannot be changed.

You can still run the pipeline by creating a bash script (named `rnaseq.sh` for example) file containing the following:

```shell
#SBATCH --account=def-bmartin
#SBATCH --time=2-00:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --mail-type=END,FAIL

# Stop if an error is encountered.
set -e

source nfcore-rnaseq/alliance_canada/nextflow_init.sh
source nf-core-env/bin/activate

nextflow run nfcore-rnaseq \
    -profile alliance_canada \
    --input <SAMPLESHEET> \
    --outdir <OUTDIR> \
    --fasta <GENOME FASTA> \
    --gtf <GTF> \
    --additional_fasta <SPIKEIN_FASTA>
```

Then submit the script for execution:

```shell
sbatch rnaseq.sh
```

The main issue of running the script this way is that the log file will be difficult to read.

### Alternative using the wait script

While this will not be recommended by anyone working at Alliance Canada, you can cheat a compute node to act in a similar way as Rorqual/Narval's login nodes.

To get this working, you need to start the `wait.sh` script.

```shell
sbatch --job-name=nfcore-rnaseq --cpus-per-task=1 --mem=4G --time=2-00:00:00 wait.sh
```

Once the job is running (check using `squeue -u $USER`), start a tmux session.

```shell
tmux new -s rnaseq
```

Connect to the compute node that is running the `wait.sh` script.

```shell
srun --pty --jobid <SLURM_JOB_ID> /bin/bash
```

Replace `<SLURM_JOB_ID>` with the job id of the `wait.sh` script.

Load the modules and activate Python virtual environment:

```shell
source nfcore-rnaseq/alliance_canada/nextflow_init.sh
source nf-core-env/bin/activate
```

Run the pipeline:

```shell
nextflow run nfcore-rnaseq \
    -profile alliance_canada \
    --input <SAMPLESHEET> \
    --outdir <OUTDIR> \
    --fasta <GENOME FASTA> \
    --gtf <GTF> \
    --additional_fasta <SPIKEIN_FASTA>
```

## Output files

### Standard output files

Most files are the same as the standard output from the [official RNA-seq pipeline from nf-core.re](https://nf-co.re/rnaseq). See [Output from RNA-seq official pipeline](https://nf-co.re/rnaseq/3.19.0/docs/output/)

### Additional output files

- `<ALIGNER>/bigwig/`
  - `*.depth_scaled.forward.bigWig`: bigWig coverage file relative to genes on the forward DNA strand scaled to sequencing depth.
  - `*.depth_scaled.reverse.bigWig`: bigWig coverage file relative to genes on the reverse DNA strand scaled to sequencing depth.
  - `*.spike_scaled.forward.bigWig`: bigWig coverage file relative to genes on the forward DNA strand scaled using spike-in genome.
  - `*.spike_scaled.reverse.bigWig`: bigWig coverage file relative to genes on the reverse DNA strand scaled using spike-in genome.

- `<ALIGNER>/`:
  - `scale_factors.txt`: scale factors used when creating bigWig files.
