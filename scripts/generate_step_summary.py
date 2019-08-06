import pandas as pd
from counter import SequenceCounter

def write_summary(steps,prelim_counts,clustering_thresholds):
    
    # Get list of sample names
    prelim_count_df = pd.DataFrame(prelim_counts)
    sample_names = prelim_count_df.index

    # Retrieve summaries generated by R
    denoising_step = (pd.read_csv("count_summary.tsv", sep='\t', dtype={'Sample':str})
                      .set_index('Sample')
                      .reindex(sample_names)
                      .fillna('0'))

    # Fill the first counts
    res_all_samples = { id_threshold: [prelim_count_df,denoising_step]
                        for id_threshold in clustering_thresholds }

    # Loop over the remaining steps
    for name,pattern in steps:
        if pattern == -1:
            continue
        if pattern is None:
            summary_i = [ pd.Series("N/A", index=sample_names,name=name) ]
        if type(pattern) is str:
            if "*" in pattern:
                summary_i = [ SequenceCounter(name,pattern.replace("*",str(id_threshold)))
                              .run()
                              for id_threshold in clustering_thresholds ]
            else:
                summary_i = [ SequenceCounter(name,pattern).run() ]
        if len(summary_i) == 1:
            summary_i *= len(clustering_thresholds)
            
        for id_threshold,summary_i_thresh in zip(clustering_thresholds,summary_i):
            res_all_samples[id_threshold].append(summary_i_thresh)

    for id_threshold in clustering_thresholds:
        summary = pd.concat(res_all_samples[id_threshold],axis=1)

        columns_order = sorted(summary.columns,key=lambda x: float(x.split('-')[0]))

        summary = summary.reindex(columns=columns_order)

        for i,col in enumerate(summary.columns):
            if summary[col][0] =='N/A':
                summary[col] = summary[summary.columns[i-1]]

        # Set to "-" if the value does not change from one step to the next
        summary_clean = summary[ (summary.shift(1,axis=1) != summary) | (summary == 0) ].fillna('-')
        # But we keep the last column
        summary_clean.iloc[:,-1] = summary.iloc[:,-1]
        summary_clean.to_csv("sequences_per_sample_per_step_{}.tsv".format(id_threshold),sep="\t")