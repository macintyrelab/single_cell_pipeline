'''
Created on Jun 6, 2018

@author: dgrewal
'''
import collections

import yaml
from single_cell.config import config_reference


def override_config(config, override):
    def update(d, u):
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                d[k] = update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    if not override:
        return config

    cfg = update(config, override)

    return cfg


def get_config_params(override=None):
    input_params = {
        "cluster": "azure", "refdir": None,
        "reference": "grch37", "smoothing_function": "modal",
        "bin_size": 500000, "copynumber_bin_size": 1000,
        'memory': {'high': 16, 'med': 6, 'low': 2},
        'version': None
    }

    input_params = override_config(input_params, override)

    return input_params


def write_config(params, filepath):
    with open(filepath, 'w') as outputfile:
        yaml.safe_dump(params, outputfile, default_flow_style=False)


def get_hmmcopy_params(reference_dir, reference, binsize, smoothing_function):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    params = {
        'multipliers': [1, 2, 3, 4, 5, 6],
        'map_cutoff': 0.9,
        'bin_size': binsize,
        'e': 0.999999,
        'eta': 50000,
        'g': 3,
        'lambda': 20,
        'min_mqual': 20,
        'nu': 2.1,
        'num_states': 12,
        's': 1,
        'strength': 1000,
        'kappa': '100,100,700,100,25,25,25,25,25,25,25,25',
        'm': '0,1,2,3,4,5,6,7,8,9,10,11',
        'mu': '0,1,2,3,4,5,6,7,8,9,10,11',
        'smoothing_function': smoothing_function,
        'exclude_list': referencedata['exclude_list'],
        'gc_wig_file': referencedata['gc_wig_file'][binsize],
        'map_wig_file': referencedata['map_wig_file'][binsize],
        'chromosomes': referencedata['chromosomes'],
        'ref_genome': referencedata['ref_genome'],
        'igv_segs_quality_threshold': 0.75,
        'memory': {'med': 6},
        'good_cells': [
            ['median_hmmcopy_reads_per_bin', 'ge', 50],
            ['is_contaminated', 'in', ['False', 'false', False]],
        ]
    }

    return {"hmmcopy": params}


def get_align_params(reference_dir, reference):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)
    refdata_callback = config_reference.get_cluster_reference_data

    params = {
        'ref_genome': referencedata['ref_genome'],
        'memory': {'med': 6},
        'adapter': 'CTGTCTCTTATACACATCTCCGAGCCCACGAGAC',
        'adapter2': 'CTGTCTCTTATACACATCTGACGCTGCCGACGA',
        'picard_wgs_params': {
            "min_bqual": 20,
            "min_mqual": 20,
            "count_unpaired": False,
        },
        'chromosomes': referencedata['chromosomes'],
        'gc_windows': referencedata['gc_windows'],
        'fastq_screen_params': {
            'aligner': 'bwa',
            'filter_tags': None,
            'genomes': [
                {
                    'name': 'grch37',
                    'paths': refdata_callback(reference_dir, 'grch37')['ref_genome'],
                },
                {
                    'name': 'mm10',
                    'paths': refdata_callback(reference_dir, 'mm10')['ref_genome'],
                },
                {
                    'name': 'salmon',
                    'paths': refdata_callback(reference_dir, 'GCF_002021735')['ref_genome'],
                },
            ]
        }
    }

    return {"alignment": params}


def get_annotation_params(reference_dir, reference):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    params = {
        'memory': {'med': 6},
        'classifier_training_data': referencedata['classifier_training_data'],
        'fastqscreen_training_data': referencedata['fastqscreen_training_data'],
        'reference_gc': referencedata['reference_gc_qc'],
        'chromosomes': referencedata['chromosomes'],
        'num_states': 12,
        'map_cutoff': 0.9,
        'ref_type': reference,
        'corrupt_tree_params': {
            'neighborhood_size': 2,
            'lower_fraction': 0.05,
            'engine_nchains': 1,
            'engine_nscans': 10000,
            'model_fpr_bound': 0.1,
            'model_fnr_bound': 0.5
        },
        'good_cells': [
            ['quality', 'ge', 0.75],
            ['experimental_condition', 'notin', ["NTC", "NCC", "gDNA", "GM"]],
            ['cell_call', 'in', ['C1']],
            ['is_contaminated', 'in', ['False', 'false', False]],
        ],
        'fastqscreen_genomes': ['grch37', 'mm10', 'salmon']
    }

    return {"annotation": params}


def get_aneufinder_params(reference_dir, reference):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    params = {
        'memory': {'med': 6},
        'chromosomes': referencedata['chromosomes'],
        'ref_genome': referencedata['ref_genome']
    }

    return {'aneufinder': params}


def get_merge_bams_params(reference_dir, reference, cluster):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    if cluster in ['azure', 'aws']:
        one_split_job = True
    else:
        one_split_job = False

    params = {
        'memory': {'low': 4, 'med': 6, 'high': 16},
        'max_cores': 8,
        'ref_genome': referencedata['ref_genome'],
        'split_size': 10000000,
        'chromosomes': referencedata['chromosomes'],
        'one_split_job': one_split_job
    }
    return {'merge_bams': params}


def get_split_bam_params(reference_dir, reference):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    params = {
        'memory': {'low': 4, 'med': 6, 'high': 16},
        'max_cores': 8,
        'ref_genome': referencedata['ref_genome'],
        'split_size': 10000000,
        'chromosomes': referencedata['chromosomes'],
        'one_split_job': True
    }

    return {'split_bam': params}


def get_germline_calling_params(reference_dir, reference):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    params = {
        'memory': {'low': 4, 'med': 6, 'high': 16},
        'max_cores': 8,
        'ref_genome': referencedata['ref_genome'],
        'chromosomes': referencedata['chromosomes'],
        'split_size': 10000000,
        'databases': {
            'mappability': {
                'url': 'http://hgdownload-test.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeMapability/release3'
                       '/wgEncodeCrgMapabilityAlign50mer.bigWig',
                'local_path': referencedata['databases']['mappability']['local_path'],
            },
            'snpeff': {
                "db": 'GRCh37.75',
                "data_dir": referencedata['databases']['snpeff']['local_path']
            },
        },
    }

    return {'germline_calling': params}


def get_variant_calling_params(reference_dir, reference):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    additional_dbs = {}
    for k, v in referencedata['databases'].items():
        if k == 'mappability' or k == 'snpeff':
            continue
        additional_dbs[k] = {'path': v['local_path']}

    params = {
        'memory': {'low': 4, 'med': 6, 'high': 16},
        'max_cores': 8,
        'ref_genome': referencedata['ref_genome'],
        'chromosomes': referencedata['chromosomes'],
        'use_depth_thresholds': True,
        'split_size': int(1e7),
        'databases': {
            'mappability': {"path": referencedata['databases']['mappability']['local_path']},
            'snpeff': {
                'db': referencedata["databases"]["snpeff"]["db"],
                "path": referencedata["databases"]["snpeff"]["local_path"]
            },
            'additional_databases': additional_dbs,
        },
        'museq_params': {
            'threshold': 0.5,
            'verbose': True,
            'purity': 70,
            'coverage': 4,
            'buffer_size': '2G',
            'mapq_threshold': 10,
            'indl_threshold': 0.05,
            'normal_variant': 25,
            'tumour_variant': 2,
            'baseq_threshold': 10,
        }

    }

    return {'variant_calling': params}


def get_copy_number_calling_params(reference_dir, reference, binsize):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    params = {
        'memory': {'low': 4, 'med': 6, 'high': 16},
        'ref_genome': referencedata['ref_genome'],
        'chromosomes': referencedata['chromosomes'],
        'split_size': 10000000,
        'max_cores': None,
        'chromosomes': referencedata['chromosomes'],
        'extract_seqdata': {},
        'ref_data_dir': referencedata['copynumber_ref_data'],
        'titan_params': {
            "normal_contamination": [0.2, 0.4, 0.6, 0.8],
            'num_clusters': [1, 2],
            'ploidy': [1, 2, 3, 4, 5, 6],
            'chrom_info_filename': referencedata['chrom_info_filename'],
            'window_size': binsize,
            'gc_wig': referencedata['gc_wig_file'][binsize],
            'mappability_wig': referencedata['gc_wig_file'][binsize],
        }
    }

    return {'copy_number_calling': params}


def get_infer_haps_params(reference_dir, reference):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    params = {
        'memory': {'low': 4, 'med': 6, 'high': 16},
        'max_cores': None,
        'chromosomes': referencedata['chromosomes'],
        'extract_seqdata': {
            'genome_fasta_template': referencedata['ref_genome'],
            'genome_fai_template': referencedata['ref_genome'] + '.fai',
        },
        'ref_data_dir': referencedata['copynumber_ref_data'],
    }

    return {'infer_haps': params}


def get_count_haps_params(reference_dir, reference):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    params = {
        'memory': {'low': 4, 'med': 6, 'high': 16},
        'max_cores': None,
        'chromosomes': referencedata['chromosomes'],
        'extract_seqdata': {
            'genome_fasta_template': referencedata['ref_genome'],
            'genome_fai_template': referencedata['ref_genome'] + '.fai',
        },
        'ref_data_dir': referencedata['copynumber_ref_data'],
    }

    return {'count_haps': params}


def get_breakpoint_params(reference_dir, reference):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    params = {
        'memory': {'low': 4, 'med': 6, 'high': 16},
        'ref_data_directory': referencedata['destruct_ref_data'],
        'destruct_config': {
            'genome_fasta': referencedata['ref_genome'],
            'genome_fai': referencedata['ref_genome'] + '.fai',
            'gtf_filename': referencedata['destruct_gtf_file'],
        },
    }

    return {'breakpoint_calling': params}


def get_sv_genotyping_params(reference_dir, reference):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    params = {
        'ref_genome': referencedata['ref_genome'],
        'memory': {'low': 4, 'med': 6, 'high': 16},
    }
    return {'sv_genotyping': params}


def get_qc_params(reference_dir, reference):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    params = {
        'ref_genome': referencedata['ref_genome'],
        'vep': referencedata['vep'],
        'memory': {'low': 4, 'med': 6, 'high': 16},
    }
    return {'qc': params}


def get_cohort_qc_params(reference_dir, reference):
    referencedata = config_reference.get_cluster_reference_data(reference_dir, reference)

    non_synonymous_labels = ["Frame_Shift_Del", "Frame_Shift_Ins", "Splice_Site",
                             "Translation_Start_Site", "Nonsense_Mutation", "Nonstop_Mutation",
                             "In_Frame_Del", "In_Frame_Ins", "Missense_Mutation"
                             ]

    params = {
        'ref_genome': referencedata['ref_genome'],
        'vep': referencedata['vep'],
        'gtf': referencedata['qc_gtf_file'],
        'non_synonymous_labels': non_synonymous_labels,
        'memory': {'low': 4, 'med': 6, 'high': 16},
    }
    return {'cohort_qc': params}


def get_singlecell_pipeline_config(config_params, override=None):
    reference = config_params["reference"]
    reference_dir = config_params['refdir']
    cluster = config_params["cluster"]
    if not reference_dir:
        reference_dir = config_reference.get_reference_dir(cluster)

    params = {}

    params.update(
        get_hmmcopy_params(
            reference_dir, reference, config_params["bin_size"],
            config_params["smoothing_function"]
        )
    )

    params.update(
        get_align_params(
            reference_dir, reference,

        )
    )

    params.update(get_annotation_params(reference_dir, reference))

    params.update(get_aneufinder_params(reference_dir, reference))

    params.update(get_merge_bams_params(reference_dir, reference, cluster))

    params.update(get_split_bam_params(reference_dir, reference))

    params.update(get_germline_calling_params(reference_dir, reference))

    params.update(get_variant_calling_params(reference_dir, reference))

    params.update(get_copy_number_calling_params(
        reference_dir, reference, config_params['copynumber_bin_size'])
    )

    params.update(get_infer_haps_params(reference_dir, reference))

    params.update(get_count_haps_params(reference_dir, reference))

    params.update(get_breakpoint_params(reference_dir, reference))

    params.update(get_sv_genotyping_params(reference_dir, reference))

    params.update(get_qc_params(reference_dir, reference))

    params.update(get_cohort_qc_params(reference_dir, reference))

    params = override_config(params, override)

    return params
