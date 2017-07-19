'''
Created on Jul 6, 2017

@author: dgrewal
'''
import os
import pypeliner
import pypeliner.managed as mgd
import tasks


def create_summary_workflow(hmm_segments, hmm_reads, hmm_metrics, metrics_summary, gc_matrix, cn_matrix, config, args, sample_ids):


    scripts_directory = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'scripts')
    plot_hmmcopy_script = os.path.join(scripts_directory, 'plot_hmmcopy.py')
    plot_heatmap_script = os.path.join(scripts_directory, 'plot_heatmap.py')
    merge_tables_script = os.path.join(scripts_directory, 'merge.py')
    filter_hmmcopy_script = os.path.join(scripts_directory, 'filter_data.py')
    plot_metrics_script = os.path.join(scripts_directory, 'plot_metrics.py')
    plot_kernel_density_script = os.path.join(scripts_directory, 'plot_kernel_density.py')
    summary_metrics_script = os.path.join(scripts_directory, 'summary_metrics.py')

    results_dir = os.path.join(args['out_dir'], 'results')

    hmmcopy_segments_filename = os.path.join(results_dir, 'segments.csv')
    hmmcopy_reads_filename = os.path.join(results_dir, 'reads.csv')
    hmmcopy_hmm_reads_filt_filename = os.path.join(results_dir, 'filtered_reads.csv')
    hmmcopy_hmm_segs_filt_filename = os.path.join(results_dir, 'filtered_segs.csv')
    all_metrics_heatmap_filename = os.path.join(results_dir, 'all_metrics_summary_hmap.csv')
    gc_metrics_filename = os.path.join(results_dir, 'gc_metrics_summary.csv')
    cn_matrix_filename = os.path.join(results_dir, 'summary', 'cn_matrix.csv')

    reads_plot_filename = os.path.join(results_dir, 'plots', 'corrected_reads.pdf')
    bias_plot_filename = os.path.join(results_dir, 'plots', 'bias.pdf')
    segs_plot_filename = os.path.join(results_dir, 'plots', 'segments.pdf')

    reads_plot_filename_mad = os.path.join(results_dir, 'plots', 'corrected_reads_mad_0.2.pdf')
    bias_plot_filename_mad = os.path.join(results_dir, 'plots', 'bias_mad_0.2.pdf')
    segs_plot_filename_mad = os.path.join(results_dir, 'plots', 'segments_mad_0.2.pdf')

    plot_heatmap_all_output = os.path.join(results_dir, 'plots', 'plot_heatmap_all.pdf')
    order_data_all_output = os.path.join(results_dir, 'plots', 'plot_heatmap_all.csv')



    plot_heatmap_ec_output = os.path.join(results_dir, 'plots', 'plot_heatmap_ec.pdf')
    plot_heatmap_ec_mad_output = os.path.join(results_dir, 'plots', 'plot_heatmap_ec_mad.pdf')
    plot_heatmap_ec_numreads_output = os.path.join(results_dir, 'plots', 'plot_heatmap_ec_numreads.pdf')

    plot_heatmap_st_output = os.path.join(results_dir, 'plots', 'plot_heatmap_st.pdf')
    plot_heatmap_st_mad_output = os.path.join(results_dir, 'plots', 'plot_heatmap_st_mad.pdf')
    plot_heatmap_st_numreads_output = os.path.join(results_dir, 'plots', 'plot_heatmap_st_numreads.pdf')


    plot_metrics_output = os.path.join(results_dir, 'plots', 'plot_metrics.pdf')
    plot_kernel_density_output = os.path.join(results_dir, 'plots', 'plot_kernel_density.pdf')
    summary_metrics_output = os.path.join(results_dir, 'plots', 'summary_metrics.txt')


    workflow = pypeliner.workflow.Workflow()

    workflow.setobj(
        obj=mgd.OutputChunks('sample_id'),
        value=sample_ids,
    )
    
    workflow.transform(
        name='merge_tables',
        ctx={'mem': config['med_mem']},
        func=tasks.concatenate_csv,
        args=(
            mgd.InputFile('hmm_segments', 'sample_id', fnames=hmm_segments),
            mgd.OutputFile(hmmcopy_segments_filename),
        ),
    )

    workflow.transform(
        name='merge_reads',
        ctx={'mem': config['high_mem']},
        func=tasks.concatenate_csv,
        args=(
            mgd.InputFile('hmm_reads', 'sample_id', fnames=hmm_reads),
            mgd.OutputFile(hmmcopy_reads_filename),
        ),
    )

    workflow.transform(
        name='merge_hmm_metrics',
        ctx={'mem': config['low_mem']},
        func=tasks.concatenate_csv,
        args=(
            mgd.InputFile('hmm_metrics', 'sample_id', fnames=hmm_metrics),
            mgd.TempOutputFile('hmmcopy_hmm_metrics.csv'),
        ),
    )

    workflow.transform(
        name='merge_summary_metrics',
        ctx={'mem': config['low_mem']},
        func=tasks.concatenate_csv,
        args=(
            mgd.InputFile('metrics_summary', 'sample_id', fnames=metrics_summary),
            mgd.TempOutputFile('metrics_summary.csv'),
        ),
    )

    workflow.transform(
        name='merge_gc_metrics',
        ctx={'mem': config['low_mem']},
        func=tasks.merge_csv,
        args=(
            mgd.InputFile('gc_matrix', 'sample_id', fnames=gc_matrix),
            mgd.OutputFile(gc_metrics_filename),
            'outer',
            'gc'
        ),
    )

    workflow.transform(
        name='merge_cn_metrics',
        ctx={'mem': config['low_mem']},
        func=tasks.merge_csv,
        args=(
            mgd.InputFile('cn_matrix', 'sample_id', fnames=cn_matrix),
            mgd.OutputFile(cn_matrix_filename),
            'outer',
            'chr,start,end,width'
        ),
    )

    workflow.commandline(
        name='filter_hmmcopy_results',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            filter_hmmcopy_script,
            '--corrected_reads', mgd.InputFile(hmmcopy_reads_filename),
            '--segments', mgd.InputFile(hmmcopy_segments_filename),
            '--quality_metrics', mgd.TempInputFile('hmmcopy_hmm_metrics.csv'),
            '--reads_output', mgd.OutputFile(hmmcopy_hmm_reads_filt_filename),
            '--segs_output', mgd.OutputFile(hmmcopy_hmm_segs_filt_filename),
            '--mad_threshold', '0.2'
            )
        )



    workflow.commandline(
        name='merge_all_metrics',
        ctx={'mem': config['low_mem']},
        args=(
            config['python'],
            merge_tables_script,
            '--merge_type', 'outer',
            '--nan_value', 'NA',
            '--input', mgd.TempInputFile('metrics_summary.csv'), mgd.TempInputFile('hmmcopy_hmm_metrics.csv'),
            '--key_cols', 'cell_id',
            '--separator', 'comma',
            '--type', 'merge',
            '--output', mgd.TempOutputFile('all_metrics.csv'),
            )
        )

    workflow.commandline(
        name='plot_heatmap_all',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            plot_heatmap_script,
            '--metrics', mgd.TempInputFile('all_metrics.csv'),
            '--separator', 'comma',
            '--plot_title', 'QC pipeline metrics',
            '--input', mgd.InputFile(hmmcopy_reads_filename),
            '--order_data', mgd.OutputFile(order_data_all_output),
            '--column_name', 'integer_copy_number'
            )
        )

    workflow.commandline(
        name='merge_all_metrics_heatmap',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            merge_tables_script,
            '--merge_type', 'outer',
            '--nan_value', 'NA',
            '--input', mgd.TempInputFile('all_metrics.csv'), mgd.InputFile(order_data_all_output),
            '--key_cols', 'cell_id',
            '--separator', 'comma',
            '--type', 'merge',
            '--output', mgd.OutputFile(all_metrics_heatmap_filename),
            )
        )

    workflow.commandline(
        name='plot_hmm_copy',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            plot_hmmcopy_script,
            '--corrected_reads', mgd.InputFile(hmmcopy_reads_filename),
            '--segments', mgd.InputFile(hmmcopy_segments_filename),
            '--quality_metrics', mgd.InputFile(all_metrics_heatmap_filename),
            '--ref_genome', mgd.InputFile(config['ref_genome']),
            '--num_states', config['num_states'],
            '--reads_output', mgd.OutputFile(reads_plot_filename),
            '--bias_output', mgd.OutputFile(bias_plot_filename),
            '--segs_output', mgd.OutputFile(segs_plot_filename),
            '--plot_title', 'QC pipeline metrics',
        ),
    )

    workflow.commandline(
        name='plot_hmm_copy_mad',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            plot_hmmcopy_script,
            '--corrected_reads', mgd.InputFile(hmmcopy_reads_filename),
            '--segments', mgd.InputFile(hmmcopy_segments_filename),
            '--quality_metrics', mgd.InputFile(all_metrics_heatmap_filename),
            '--ref_genome', mgd.InputFile(config['ref_genome']),
            '--num_states', config['num_states'],
            '--reads_output', mgd.OutputFile(reads_plot_filename_mad),
            '--bias_output', mgd.OutputFile(bias_plot_filename_mad),
            '--segs_output', mgd.OutputFile(segs_plot_filename_mad),
            '--plot_title', 'QC pipeline metrics',
            '--mad_threshold', config['hmmcopy_plot_mad_threshold'],
        ),
    )



    workflow.commandline(
        name='plot_metrics',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            plot_metrics_script,
            mgd.InputFile(all_metrics_heatmap_filename),
            mgd.OutputFile(plot_metrics_output),
            '--plot_title', 'QC pipeline metrics',
            '--gcbias_matrix', mgd.InputFile(gc_metrics_filename),
            '--gc_content_data', mgd.InputFile(config['gc_windows'])
            )
        )

    workflow.commandline(
        name='plot_kernel_density',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            plot_kernel_density_script,
            '--separator', 'comma',
            '--input', mgd.InputFile(all_metrics_heatmap_filename),
            '--plot_title', 'QC pipeline metrics',
            '--output', mgd.OutputFile(plot_kernel_density_output),
            '--column_name', 'mad_neutral_state'
            )
        )

    workflow.commandline(
        name='summary_metrics',
        ctx={'mem': config['low_mem']},
        args=(
            config['python'],
            summary_metrics_script,
            '--input', mgd.InputFile(all_metrics_heatmap_filename),
            '--summary_metrics', mgd.OutputFile(summary_metrics_output),
            )
        )

    workflow.commandline(
        name='plot_heatmap_ec',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            plot_heatmap_script,
            '--output', mgd.OutputFile(plot_heatmap_ec_output),
            '--metrics', mgd.InputFile(all_metrics_heatmap_filename),
            '--separator', 'comma',
            '--plot_title', 'QC pipeline metrics',
            '--input', mgd.InputFile(hmmcopy_reads_filename),
            '--column_name', 'integer_copy_number',
            '--plot_by_col','experimental_condition',
            )
        )

    workflow.commandline(
        name='plot_heatmap_ec_mad',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            plot_heatmap_script,
            '--output', mgd.OutputFile(plot_heatmap_ec_mad_output),
            '--metrics', mgd.InputFile(all_metrics_heatmap_filename),
            '--separator', 'comma',
            '--plot_title', 'QC pipeline metrics',
            '--input', mgd.InputFile(hmmcopy_reads_filename),
            '--column_name', 'integer_copy_number',
            '--plot_by_col','experimental_condition',
            '--mad_threshold', config['heatmap_plot_mad_threshold']
            )
        )


    workflow.commandline(
        name='plot_heatmap_ec_nreads',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            plot_heatmap_script,
            '--output', mgd.OutputFile(plot_heatmap_ec_numreads_output),
            '--metrics', mgd.InputFile(all_metrics_heatmap_filename),
            '--separator', 'comma',
            '--plot_title', 'QC pipeline metrics',
            '--input', mgd.InputFile(hmmcopy_reads_filename),
            '--column_name', 'integer_copy_number',
            '--plot_by_col','experimental_condition',
            '--numreads_threshold', config['heatmap_plot_numreads_threshold']
            )
        )



    workflow.commandline(
        name='plot_heatmap_st',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            plot_heatmap_script,
            '--output', mgd.OutputFile(plot_heatmap_st_output),
            '--metrics', mgd.InputFile(all_metrics_heatmap_filename),
            '--separator', 'comma',
            '--plot_title', 'QC pipeline metrics',
            '--input', mgd.InputFile(hmmcopy_reads_filename),
            '--column_name', 'integer_copy_number',
            '--plot_by_col','sample_type',
            )
        )

    workflow.commandline(
        name='plot_heatmap_st_mad',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            plot_heatmap_script,
            '--output', mgd.OutputFile(plot_heatmap_st_mad_output),
            '--metrics', mgd.InputFile(all_metrics_heatmap_filename),
            '--separator', 'comma',
            '--plot_title', 'QC pipeline metrics',
            '--input', mgd.InputFile(hmmcopy_reads_filename),
            '--column_name', 'integer_copy_number',
            '--plot_by_col','sample_type',
            '--mad_threshold', config['heatmap_plot_mad_threshold']
            )
        )


    workflow.commandline(
        name='plot_heatmap_st_nreads',
        ctx={'mem': config['high_mem']},
        args=(
            config['python'],
            plot_heatmap_script,
            '--output', mgd.OutputFile(plot_heatmap_st_numreads_output),
            '--metrics', mgd.InputFile(all_metrics_heatmap_filename),
            '--separator', 'comma',
            '--plot_title', 'QC pipeline metrics',
            '--input', mgd.InputFile(hmmcopy_reads_filename),
            '--column_name', 'integer_copy_number',
            '--plot_by_col','sample_type',
            '--numreads_threshold', config['heatmap_plot_numreads_threshold']
            )
        )


    return workflow



