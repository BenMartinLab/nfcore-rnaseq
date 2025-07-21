process NEGATE_BEDGRAPH_SCORE {
    tag "$meta.id"
    label "process_single"

    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/gawk:5.3.0' :
        'biocontainers/gawk:5.3.1' }"

    input:
    tuple val(meta), path(bedgraph)

    output:
    tuple val(meta), path("*.negated.bedGraph"), emit: bedgraph
    path "versions.yml"                        , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    awk '{if (\$0 ~ /^[ \\t]*#/ || \$1 == "browser" && \$1 == "track") {print} else {\$4 = -\$4; print}}' \\
        $args \\
        $bedgraph \\
        > ${prefix}.negated.bedGraph

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        awk: \$(awk --version | sed -rn 's/^GNU Awk ([0-9\\.]*).*/\\1/p')
    END_VERSIONS
    """

    stub:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    touch ${prefix}.negated.bedGraph

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        awk: \$(awk --version | sed -rn 's/^GNU Awk (.*)/\\1/p')
    END_VERSIONS
    """
}
