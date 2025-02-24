# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 10:15:43 2024

@author: rkerrid
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import os


def plot_sample_counts(light_df, pulse_df, ratios_df, meta_df, max_samples_per_plot=45, pdf=None):
    # Get samples from metadata
    samples = meta_df['Sample'].unique()
    
    # Initialize DataFrame to store counts
    counts_data = []
    
    # Count non-NA values for each sample in each dataframe
    for sample in samples:
        sample_cols = [col for col in light_df.columns if col.startswith(sample)]
        
        # Get counts for each type
        light_count = light_df[sample_cols].notna().sum().sum()
        pulse_count = pulse_df[sample_cols].notna().sum().sum() if pulse_df is not None else 0
        ratio_count = ratios_df[sample_cols].notna().sum().sum() if ratios_df is not None else 0
        
        # Add to data list
        counts_data.extend([
            {'Sample': sample, 'Type': 'Light', 'Count': light_count},
            {'Sample': sample, 'Type': 'Pulse', 'Count': pulse_count},
            {'Sample': sample, 'Type': 'Ratio', 'Count': ratio_count}
        ])
    
    # Create DataFrame from counts
    counts_df = pd.DataFrame(counts_data)
    
    # Determine if we need to split the plot
    num_samples = len(samples)
    needs_split = num_samples > max_samples_per_plot
    
    if needs_split:
        num_rows = (num_samples - 1) // max_samples_per_plot + 1
        fig = plt.figure(figsize=(12, 6 * num_rows))
    else:
        fig = plt.figure(figsize=(12, 6))
    
    # Create color palette
    palette = sns.color_palette('Set2', 3)
    
    if needs_split:
        for i in range(num_rows):
            ax = fig.add_subplot(num_rows, 1, i+1)
            
            # Get subset of samples for this row
            start_idx = i * max_samples_per_plot
            end_idx = min((i + 1) * max_samples_per_plot, num_samples)
            row_samples = samples[start_idx:end_idx]
            row_data = counts_df[counts_df['Sample'].isin(row_samples)]
            
            # Create the plot
            sns.barplot(x='Sample', y='Count', hue='Type', data=row_data, 
                       palette=palette, ax=ax)
            ax.set_title('Number of IDs per Sample', fontsize=14)
            ax.set_xlabel('Sample', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            
            if i == 0:  # Only show legend for first plot
                ax.legend(title='Data Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        ax = fig.add_subplot(111)
        sns.barplot(x='Sample', y='Count', hue='Type', data=counts_df, 
                   palette=palette, ax=ax)
        ax.set_title('Number of IDs per Sample', fontsize=14)
        ax.set_xlabel('Sample', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.legend(title='Data Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    
    # Save or show the plot
    if pdf:
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    else:
        plt.show()

def plot_sample_intensities(light_df, pulse_df, meta_df, max_samples_per_plot=45, pdf=None):
    # Get samples from metadata
    samples = meta_df['Sample'].unique()
    
    # Initialize DataFrame to store intensities
    intensity_data = []
    
    # Sum intensities for each sample in each dataframe
    for sample in samples:
        sample_cols = [col for col in light_df.columns if col.startswith(sample)]
        
        # Get total intensity for each type
        light_intensity = light_df[sample_cols].sum().sum()
        pulse_intensity = pulse_df[sample_cols].sum().sum() if pulse_df is not None else 0
        
        # Add to data list
        intensity_data.extend([
            {'Sample': sample, 'Type': 'Light', 'Intensity': light_intensity},
            {'Sample': sample, 'Type': 'Pulse', 'Intensity': pulse_intensity}
        ])
    
    # Create DataFrame from intensities
    intensity_df = pd.DataFrame(intensity_data)
    
    # Determine if we need to split the plot
    num_samples = len(samples)
    needs_split = num_samples > max_samples_per_plot
    
    if needs_split:
        num_rows = (num_samples - 1) // max_samples_per_plot + 1
        fig = plt.figure(figsize=(12, 6 * num_rows))
    else:
        fig = plt.figure(figsize=(12, 6))
    
    # Create color palette - only need 2 colors now
    palette = sns.color_palette('Set2', 2)
    
    if needs_split:
        for i in range(num_rows):
            ax = fig.add_subplot(num_rows, 1, i+1)
            
            # Get subset of samples for this row
            start_idx = i * max_samples_per_plot
            end_idx = min((i + 1) * max_samples_per_plot, num_samples)
            row_samples = samples[start_idx:end_idx]
            row_data = intensity_df[intensity_df['Sample'].isin(row_samples)]
            
            # Create the plot
            sns.barplot(x='Sample', y='Intensity', hue='Type', data=row_data, 
                       palette=palette, ax=ax)
            ax.set_title('Total Intensity per Sample', fontsize=14)
            ax.set_xlabel('Sample', fontsize=12)
            ax.set_ylabel('Total Intensity', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            
            # Format y-axis to use scientific notation
            ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
            ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
            
            if i == 0:  # Only show legend for first plot
                ax.legend(title='Data Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        ax = fig.add_subplot(111)
        sns.barplot(x='Sample', y='Intensity', hue='Type', data=intensity_df, 
                   palette=palette, ax=ax)
        ax.set_title('Total Intensity per Sample', fontsize=14)
        ax.set_xlabel('Sample', fontsize=12)
        ax.set_ylabel('Total Intensity', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        # Format y-axis to use scientific notation
        ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        
        ax.legend(title='Data Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    
    # Save or show the plot
    if pdf:
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    else:
        plt.show()

def plot_correlation_matrices(light_df, pulse_df, meta_df, pdf=None):
    # Get samples from metadata
    samples = meta_df['Sample'].unique()
    
    # Function to create and plot correlation matrix for a dataframe
    def create_corr_matrix(df, title, samples):
        # Initialize a DataFrame to store sample intensities
        intensity_data = {}
        
        # Extract and sum intensities for each sample
        for sample in samples:
            sample_cols = [col for col in df.columns if col.startswith(sample)]
            if sample_cols:
                # Sum intensities for this sample across all proteins
                intensity_data[sample] = df[sample_cols].sum(axis=1)
        
        # Create correlation DataFrame
        intensity_df = pd.DataFrame(intensity_data)
        
        # Calculate correlation matrix
        corr_matrix = intensity_df.corr(method='pearson')
        
        # Create the plot
        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))  # Create mask for upper triangle
        
        # Plot heatmap
        ax = sns.heatmap(
            corr_matrix, 
            mask=mask,
            vmin=0, vmax=1, 
            annot=True,  # Show correlation values
            cmap='YlGnBu',
            square=True,
            linewidths=.5
        )
        
        plt.title(title, fontsize=16)
        plt.tight_layout()
        
        # Save or show the plot
        if pdf:
            pdf.savefig(plt.gcf(), bbox_inches='tight')
            plt.close()
        
        return corr_matrix
    
    # Create correlation matrices for light and pulse data
    light_corr = None
    pulse_corr = None
    
    # Process light data
    if light_df is not None:
        print("Creating Light intensity correlation matrix...")
        light_corr = create_corr_matrix(light_df, 'Light Intensity Correlation Matrix', samples)
    
    # Process pulse data
    if pulse_df is not None:
        print("Creating Pulse intensity correlation matrix...")
        pulse_corr = create_corr_matrix(pulse_df, 'Pulse Intensity Correlation Matrix', samples)
    
    if pdf is None:
        plt.show()
    
    return light_corr, pulse_corr

def protein_groups_report(path):
    output_path = f'{path}/reports/'
    # Read your data files
    light_df = pd.read_csv(f'{path}/protein_groups/light.csv')
    pulse_df = pd.read_csv(f'{path}/protein_groups/pulse.csv')  # if you have this file
    ratios_df = pd.read_csv(f'{path}/protein_groups/ratios.csv')  # if you have this file
    meta_df = pd.read_csv(f'{path}/meta.csv')
    # Initialize a PDF file
    with PdfPages(f'{output_path}protein_groups_report.pdf') as pdf:
        # Call the functions and pass the PDF object
        
        # Create the plot
        plot_sample_counts(light_df, pulse_df, ratios_df, meta_df, max_samples_per_plot=6, pdf=pdf)
        plot_sample_intensities(light_df, pulse_df, meta_df, max_samples_per_plot=6, pdf=pdf)
        plot_correlation_matrices(light_df, pulse_df, meta_df, pdf=pdf)