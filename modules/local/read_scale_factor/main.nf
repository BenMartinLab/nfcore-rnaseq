process READ_SCALE_FACTOR {
    label "process_single"

    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.9--1' :
        'biocontainers/python:3.9--1' }"

    input:
    tuple val(meta), path(scale_factors), val(row), val(column)

    output:
    tuple val(meta), env("scale_factor"), emit: scale_factor
    path "versions.yml"                 , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script: // read_scale_factor.py is bundled with the pipeline, in nf-core/rnaseq/bin/
    def args = task.ext.args ?: ''
    """
    scale_factor=\$(read_scale_factor.py \\
        $args \\
        --scales $scale_factors \\
        --row '$row' \\
        --column '$column')

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """

    stub:
    def args = task.ext.args ?: ''
    """
    echo "1.0"

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
