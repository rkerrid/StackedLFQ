
# """
# Created on Sun Sep  8 14:41:41 2024

# @author: robbi
# """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)


def create_precursor_report(path):
    input_path = f'{path}preprocessing/'
    output_path = f'{path}/reports/'
    
    
    df = pd.read_csv(f'{input_path}precursors.csv', sep=',')

    # Initialize a PDF file
    with PdfPages(f'{output_path}precursor_report.pdf') as pdf:
        # Call the functions and pass the PDF object
        plot_summed_intensity(df, filtered=True, pdf=pdf)
        plot_id_counts(df, filtered=True, pdf=pdf)


def plot_summed_intensity(df, max_samples_per_plot=6, filtered=False, pdf=None):
   df_filtered = df
   metric = 'precursor_quantity'
   suffixes = ['_L', '_M', '_H', '_pulse']
   suffix_labels = {'_L': 'Light', '_M': 'Medium', '_H': 'Heavy', '_pulse': 'Pulse'}
   
   # Get unique runs and determine if we need to split
   unique_runs = df_filtered['Run'].unique()
   num_runs = len(unique_runs)
   needs_split = num_runs > max_samples_per_plot
   
   # Calculate number of rows needed and create subplot structure
   if needs_split:
       num_rows = (num_runs - 1) // max_samples_per_plot + 1
       fig = plt.figure(figsize=(10, 6 * num_rows))
   else:
       fig = plt.figure(figsize=(10, 6))
   
   # Find which suffixes are available for precursor_quantity
   cols = [metric + suffix for suffix in suffixes if metric + suffix in df_filtered.columns]
   
   # Calculate sums and prepare data for plotting
   sums = df_filtered.groupby('Run')[cols].sum()
   sums = sums.reset_index()
   sums_melted = sums.melt(id_vars=['Run'], value_vars=cols, var_name='Label', value_name='Sum')
   sums_melted['Suffix'] = sums_melted['Label'].str.extract(r'(_L|_M|_H|_pulse)$')
   
   # Get unique suffixes and create color palette
   unique_suffixes_in_data = sums_melted['Suffix'].dropna().unique()
   dynamic_palette = [sns.color_palette('Set2', len(unique_suffixes_in_data))[list(unique_suffixes_in_data).index(suffix)] 
                     for suffix in unique_suffixes_in_data]
   
   if needs_split:
       for i in range(num_rows):
           ax = fig.add_subplot(num_rows, 1, i+1)
           
           # Get subset of data for this row
           start_idx = i * max_samples_per_plot
           end_idx = min((i + 1) * max_samples_per_plot, num_runs)
           row_runs = unique_runs[start_idx:end_idx]
           row_data = sums_melted[sums_melted['Run'].isin(row_runs)]
           
           # Create the plot
           sns.barplot(x='Run', y='Sum', hue='Suffix', data=row_data, 
                      palette=dynamic_palette, ax=ax)
           ax.set_title('Sum of Intensities for Precursor Quantity', fontsize=14)
           ax.set_xlabel('Run', fontsize=12)
           ax.tick_params(axis='x', rotation=45)
           
           # Only show legend for the first plot
           if i == 0:
               handles = [mpatches.Patch(color=dynamic_palette[list(unique_suffixes_in_data).index(suffix)], 
                                       label=suffix_labels[suffix]) 
                         for suffix in unique_suffixes_in_data]
               fig.legend(handles=handles, loc='center right', title='SILAC channel', 
                         bbox_to_anchor=(1.15, 0.5), borderaxespad=0)
   else:
       ax = fig.add_subplot(111)
       sns.barplot(x='Run', y='Sum', hue='Suffix', data=sums_melted, 
                  palette=dynamic_palette, ax=ax)
       ax.set_title('Sum of Intensities for Precursor Quantity', fontsize=14)
       ax.set_xlabel('Run', fontsize=12)
       ax.tick_params(axis='x', rotation=45)
       
       handles = [mpatches.Patch(color=dynamic_palette[list(unique_suffixes_in_data).index(suffix)], 
                               label=suffix_labels[suffix]) 
                 for suffix in unique_suffixes_in_data]
       fig.legend(handles=handles, loc='center right', title='SILAC channel', 
                 bbox_to_anchor=(1.15, 0.5), borderaxespad=0)
   
   plt.tight_layout()
   
   # Save or show the plot
   if pdf:
       pdf.savefig(fig, bbox_inches='tight')
       plt.close(fig)
   else:
       plt.show()



def plot_id_counts(df, max_samples_per_plot=6, filtered=False, pdf=None):
    df_filtered = df
    metric = 'precursor_quantity'
    suffixes = ['_L', '_M', '_H', '_pulse']
    suffix_labels = {'_L': 'Light', '_M': 'Medium', '_H': 'Heavy', '_pulse': 'Pulse'}
    
    # Get unique runs and determine if we need to split
    unique_runs = df_filtered['Run'].unique()
    num_runs = len(unique_runs)
    needs_split = num_runs > max_samples_per_plot
    
    # Calculate number of rows needed and create subplot structure
    if needs_split:
        num_rows = (num_runs - 1) // max_samples_per_plot + 1
        fig = plt.figure(figsize=(10, 6 * num_rows))
    else:
        fig = plt.figure(figsize=(10, 6))
    
    # Find which suffixes are available for precursor_quantity
    cols = [metric + suffix for suffix in suffixes if metric + suffix in df_filtered.columns]
    
    # Calculate counts
    counts = df_filtered.groupby('Run')[cols].apply(lambda x: (x != 0).sum())
    counts = counts.reset_index()
    counts_melted = counts.melt(id_vars=['Run'], value_vars=cols, var_name='Label', value_name='Count')
    counts_melted['Suffix'] = counts_melted['Label'].str.extract(r'(_L|_M|_H|_pulse)$')
    
    # Get unique suffixes and create color palette
    unique_suffixes_in_data = counts_melted['Suffix'].dropna().unique()
    dynamic_palette = [sns.color_palette('Set2', len(unique_suffixes_in_data))[list(unique_suffixes_in_data).index(suffix)] 
                      for suffix in unique_suffixes_in_data]
    
    if needs_split:
        for i in range(num_rows):
            ax = fig.add_subplot(num_rows, 1, i+1)
            
            # Get subset of data for this row
            start_idx = i * max_samples_per_plot
            end_idx = min((i + 1) * max_samples_per_plot, num_runs)
            row_runs = unique_runs[start_idx:end_idx]
            row_data = counts_melted[counts_melted['Run'].isin(row_runs)]
            
            # Create the plot
            sns.barplot(x='Run', y='Count', hue='Suffix', data=row_data, 
                       palette=dynamic_palette, ax=ax)
            ax.set_title('Non-Zero Counts for Precursor Quantity', fontsize=14)
            ax.set_xlabel('Run', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            
            # Only show legend for the first plot
            if i == 0:
                handles = [mpatches.Patch(color=dynamic_palette[list(unique_suffixes_in_data).index(suffix)], 
                                        label=suffix_labels[suffix]) 
                          for suffix in unique_suffixes_in_data]
                fig.legend(handles=handles, loc='center right', title='SILAC channel', 
                          bbox_to_anchor=(1.15, 0.5), borderaxespad=0)
    else:
        ax = fig.add_subplot(111)
        sns.barplot(x='Run', y='Count', hue='Suffix', data=counts_melted, 
                   palette=dynamic_palette, ax=ax)
        ax.set_title('Non-Zero Counts for Precursor Quantity', fontsize=14)
        ax.set_xlabel('Run', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        handles = [mpatches.Patch(color=dynamic_palette[list(unique_suffixes_in_data).index(suffix)], 
                                label=suffix_labels[suffix]) 
                  for suffix in unique_suffixes_in_data]
        fig.legend(handles=handles, loc='center right', title='SILAC channel', 
                  bbox_to_anchor=(1.15, 0.5), borderaxespad=0)
    
    plt.tight_layout()
    
    # Save or show the plot
    if pdf:
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    else:
        plt.show()
        
        

if __name__ == '__main__':
    path = r'G:\My Drive\Data\analysis\20240824 BM pilot 2 vs 3 channel analysis\astral\data\no spike\preprocessing\\'
    df = pd.read_csv(f'{path}precursors.csv', sep=',')

    # Initialize a PDF file
    with PdfPages(f'{path}output_plots2.pdf') as pdf:
        # Call the functions and pass the PDF object
        plot_summed_intensity(df, filtered=True, pdf=pdf)
        plot_id_counts(df, filtered=True, pdf=pdf)
