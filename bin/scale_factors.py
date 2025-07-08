#!/usr/bin/env python3

import argparse
import re
from sys import stdout, stderr
from typing import TextIO, Iterator

import pysam


BASE_SCALE = 10000000


def main(argv: list[str] = None):
    parser = argparse.ArgumentParser(description="Compute scale factors based on reads aligning to main genome and spike-in genome.")
    parser.add_argument("-b", "--bam", nargs="+", type=argparse.FileType('r'),
                        help="BAM files")
    parser.add_argument("-o", "--output", type=argparse.FileType('w'), default=stdout,
                        help="Tab delimited file containing multiple scale factor options  (default: standard output)")
    parser.add_argument("-s", "--spike_fasta", type=argparse.FileType('r'), default=None,
                        help="FASTA file containing spike-in genome")
    parser.add_argument("-l", "--labels", nargs="*", default=None,
                        help="Labels to use instead of BAM filename in BAM output column")
    parser.add_argument("-S", "--scale", type=int, default=BASE_SCALE,
                        help="Base scale to use to compute scale factors  (default: %(default)s)")

    args = parser.parse_args(argv)
    scale_factors(bam_files=args.bam, output_file=args.output, spike_fasta_file=args.spike_fasta, labels=args.labels, scale=args.scale)


def scale_factors(bam_files: list[TextIO], output_file: TextIO, spike_fasta_file: TextIO, labels: list[str],
    scale: int = BASE_SCALE):
    """
    Compute scale factors based on reads aligning to main genome and spike-in genome.

    :param bam_files: BAM files
    :param output_file: Tab delimited file containing multiple scale factor options
    :param spike_fasta_file: FASTA file containing spike-in genome
    :param labels: Labels to use instead of BAM filename in BAM output column
    :param scale: Base scale to use to compute scale factors
    """
    if labels and len(bam_files) != len(labels):
        print(f"Warning: the number of labels does not match the number of BAM files - \n"
              f"{len(bam_files)} BAM files vs {len(labels)} labels", file=stderr)

    spike_chromosomes = parse_chromosomes(spike_fasta_file) if spike_fasta_file else None

    # Header
    output_file.write(f"BAM\tMain genome reads count\tScale factors - {scale:.2e} / main genome reads count")
    if spike_fasta_file:
        output_file.write(f"\tSpike-in reads count\tSpike-in scale factors - {scale:.2e} / spike-in reads count"
                          f"\tTotal size scale factors - {scale:.2e} / (spike-in * main genome)")
    output_file.write("\n")

    for i in range(0, len(bam_files)):
        bam_file = bam_files[i]
        align = pysam.AlignmentFile(bam_file, "rb")
        read_filter = lambda read : (read.is_proper_pair and not read.is_qcfail
                                     and not read.is_secondary and not read.is_supplementary)
        read_count = align.count(read_callback=read_filter)
        spike_read_count = 0
        for chromosome in spike_chromosomes:
            spike_read_count += align.count(contig=chromosome, read_callback=read_filter)
        read_count -= spike_read_count
        if labels and i < len(labels):
            label = labels[i]
        else:
            label = bam_file.name
        output_file.write(f"{label}\t{read_count}\t{scale/read_count if read_count else 'NA'}")
        if spike_fasta_file:
            output_file.write(f"\t{spike_read_count}\t{scale/spike_read_count if spike_read_count else 'NA'}"
                              f"\t{scale/(spike_read_count*read_count) if spike_read_count and read_count else 'NA'}")
        output_file.write("\n")


def parse_chromosomes(fasta_file: TextIO) -> list[str]:
    """
    Parses chromosome names present in FASTA file.

    :param fasta_file: FASTA file
    :return: chromosome names present in FASTA file
    """
    chromosomes = []
    chromosome_regex = re.compile(r"^>(\S*)(\s?)(.*)")
    for line in fasta_file:
        match = chromosome_regex.match(line)
        if match:
            chromosome = match.group(1)
            chromosomes.append(chromosome)
    return chromosomes


if __name__ == '__main__':
    main()
