process SCALE_FACTORS {
    label "process_single"

    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/pysam:0.22.1--py39hdd5828d_3' :
        'biocontainers/pysam:0.23.3--py39hdd5828d_0' }"

    input:
    tuple val(meta), path (bam, arity: '1..*'), path (bai, arity: '1..*')
    tuple val(meta2), path(fasta)

    output:
    path "scale_factors.txt", emit: scale_factors
    path "versions.yml"   , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script: // scale_factors.py is bundled with the pipeline, in nf-core/rnaseq/bin/
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "scale_factors"
    """
    scale_factors.py \\
        $args \\
        --spike_fasta $fasta \\
        --output ${prefix}.txt \\
        --bam $bam

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
        pysam: \$(pip show pysam | sed -rn 's/^Version: (.*)/\\1/p')
    END_VERSIONS
    """

    stub:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "scale_factors"
    """
    touch ${prefix}.txt

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
        pysam: \$(pip show pysam | sed -rn 's/^Version: (.*)/\\1/p')
    END_VERSIONS
    """
}
