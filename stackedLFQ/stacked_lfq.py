# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 10:35:38 2024

@author: rkerrid
"""

import pandas as pd
import numpy as np
import time
from tqdm import tqdm
from icecream import ic
import warnings

from stackedLFQ.utils import manage_directories
from stackedLFQ.utils import dlfq_functions as dlfq
import os


class StackedLFQ:    
    def __init__(self, path, params, filtered_report):
        self.path = path
        self.params = params
        self.filtered_report = filtered_report
        
        self.protein_groups = None
    
    def generate_protein_groups(self):  
        start_time = time.time()        
        self.filtered_report = self.filter_data(self.filtered_report)
        self.filtered_report.to_csv(os.path.join(self.path, 'preprocessing', 'precursors.csv'), sep=',')
        precursor_ratios = self.calculate_precursor_ratios(self.filtered_report)
        
        protein_group_ratios = self.compute_protein_level_ratios(precursor_ratios)

        protein_intensities_dlfq = self.perform_lfq(precursor_ratios)      
        
        self.protein_groups = self.merge_data(protein_group_ratios, protein_intensities_dlfq)
       
        self.protein_groups = self.extract_M_and_L(self.protein_groups)
        
        end_time = time.time()
        print(f"Time taken to generate protein groups: {end_time - start_time} seconds")
        return self.protein_groups
    
    def filter_data(self, df):
        df['filter_passed_L'] = df['filter_passed_L'].astype(bool)
        df['filter_passed_pulse'] = df['filter_passed_pulse'].astype(bool)
        return  df[(df['filter_passed_L']) | (df['filter_passed_pulse'])]
    
    def calculate_precursor_ratios(self, df):
        print('Calculating SILAC ratios')
        df = df.copy()
        
        df.loc[:, 'Precursor.Quantity'] = df['precursor_quantity_L'].fillna(0) + df['precursor_quantity_pulse'].fillna(0)
        
        df.loc[:, 'precursor_quantity_pulse_L_ratio'] = df['precursor_quantity_pulse'] / df['precursor_quantity_L'] 
        # df.loc[:, 'precursor_translated_pulse_L_ratio'] = df['precursor_translated_pulse'] / df['precursor_translated_L'] 
        # df.loc[:, 'ms1_translated_pulse_L_ratio'] = df['ms1_translated_pulse'] / df['ms1_translated_L']
        
        df.loc[:, 'precursor_quantity_pulse_L_ratio'] = df['precursor_quantity_pulse_L_ratio'].replace([np.inf, 0], np.nan)
        # df.loc[:, 'precursor_translated_pulse_L_ratio'] = df['precursor_translated_pulse_L_ratio'].replace([np.inf, 0], np.nan)
        # df.loc[:, 'ms1_translated_pulse_L_ratio'] = df['ms1_translated_pulse_L_ratio'].replace([np.inf, 0], np.nan)
        
        df.loc[:, 'Lib.PG.Q.Value'] = 0
        
        return df    
    
    def compute_protein_level_ratios(self, df):
        print('Rolling up to protein level')
        runs = df['Run'].unique()
        runs_list = []
    
        for run in tqdm(runs, desc='Computing protein level ratios for each run'):
            run_df = df[df['Run'] == run]
            
            # Modify this function to return a tuple
            def combined_median(ratio, quantity_pulse, quantity_L):
                ratio = ratio.dropna()  # Remove NaNs before counting
                number_of_precursors = len(ratio)
                if number_of_precursors < int(self.params["precursor_ratios_per_protein"]):  
                    # do the thing
                    channel, number_of_precursors = self.single_channel_identifier(quantity_pulse, quantity_L)
                    return (channel, number_of_precursors)  # Return tuple with value and count
                else:
                    log2_ratio = np.log2(ratio)  # Log-transform the combined series
                    return (2**np.median(log2_ratio), number_of_precursors)  # Return tuple
            
            # Use an intermediate function that unpacks the result
            def process_group(x):
                result, count = combined_median(
                    x['precursor_quantity_pulse_L_ratio'], 
                    x['precursor_quantity_pulse'], 
                    x['precursor_quantity_L']
                )
                return pd.Series({
                    'pulse_L_ratio': result,
                    'number_of_precursors': count
                })
            
            # Group by protein group and apply the processing function
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=DeprecationWarning, 
                                      message="DataFrameGroupBy.apply operated on the grouping columns")
                grouped_run = run_df.groupby(['protein_group']).apply(process_group).reset_index()
        
            grouped_run['Run'] = run
            runs_list.append(grouped_run)
    
        result = pd.concat(runs_list, ignore_index=True)
        return result


    def single_channel_identifier(self, quantity_pulse, quantity_L):
        is_light = False
        is_pulse = False
        is_valid = False
        
        L_count = quantity_L.notna().sum()
        if L_count >= int(self.params["start_precursor_per_protein"]):
            is_light = True
            is_valid = True
        
        pulse_count = quantity_pulse.notna().sum()
        if pulse_count >= int(self.params["pulse_precursor_per_protein"]):
            is_pulse = True
            is_valid = True
            
        if is_pulse and is_light:
            is_valid = False
        
        if is_valid:
            if is_light:
                return 'L', L_count
                
            elif is_pulse:
                return 'pulse', pulse_count
            
        return "invalid", 0

    def perform_lfq(self, df):
            manage_directories.create_directory(self.path, 'directLFQ_output')
            df = df[['Run', 'protein_group', 'precursor_id', 'Precursor.Quantity', 'Lib.PG.Q.Value']]
            df = df.rename(columns={'protein_group':'Protein.Group', 'precursor_id':'Precursor.Id'})
            path = f'{self.path}directLFQ_output/'
            df.to_csv(f'{path}dflq_formatted_report.tsv', sep='\t')
            dlfq_output_file = f'{path}dlfq_protein_intensities.tsv'
            
            dlfq.run_lfq(f'{path}dflq_formatted_report.tsv', file=dlfq_output_file,min_nonan = int(self.params["directLFQ_ions_per_protein"]), num_cores=int(self.params["No_of_cores_dlfq"]))
            dlfq_df = pd.read_csv(dlfq_output_file, sep='\t')
           
            # Drop the 'Unnamed: 0' column
            dlfq_df = dlfq_df.drop(columns=['Unnamed: 0', 'protein'])
           
            # Melt the DataFrame
            result = pd.melt(dlfq_df, id_vars=['Protein.Group'], var_name='Run', value_name='Intensity')
            result = result.rename(columns={'Protein.Group':'protein_group','Intensity':'normalized_intensity'})
            result = result[result['normalized_intensity'] != 0]
            return result
    
    def merge_data(self, protein_group_ratios, protein_intensities_dlfq):
        
        protein_groups = pd.merge(protein_group_ratios, protein_intensities_dlfq,on=['protein_group','Run'], how='left')
        protein_groups = protein_groups.dropna(subset=['normalized_intensity'])
        
        protein_groups['L'] = 0.0
        protein_groups['pulse'] = 0.0
        return protein_groups
    
    def extract_M_and_L(self, df):
        # Convert columns to float64 first
        df['conversion'] = ''
        
        # For pulse_L_ratio containing float values
        df.loc[df['pulse_L_ratio'].apply(lambda x: isinstance(x, float)), 'conversion'] = 'ratio'
        
        # For pulse_L_ratio containing 'L'
        df.loc[df['pulse_L_ratio'].astype(str).str.contains('L'), 'conversion'] = 'L'
        
        # For pulse_L_ratio containing 'pulse'
        df.loc[df['pulse_L_ratio'].astype(str).str.contains('pulse'), 'conversion'] = 'pulse'
        
        # For pulse_L_ratio containing 'pulse'
        df.loc[df['pulse_L_ratio'].astype(str).str.contains('invalid'), 'conversion'] = 'invalid'
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            # Make sure df['pulse_L_ratio'] is numeric where conversion == 'ratio'
            df.loc[df['conversion'] == 'ratio', 'pulse_L_ratio'] = pd.to_numeric(
                df.loc[df['conversion'] == 'ratio', 'pulse_L_ratio'], 
                errors='coerce'
            )
        
            mask = (df['conversion'] == 'ratio') & df['pulse_L_ratio'].notna()
            df.loc[mask, 'L'] = df.loc[mask, 'normalized_intensity'] / (df.loc[mask, 'pulse_L_ratio'] + 1)
            df.loc[mask, 'pulse'] = df.loc[mask, 'normalized_intensity'] - df.loc[mask, 'L']
            
            # Handle the 'L' case
            df.loc[df['conversion'] == 'L', 'L'] = df.loc[df['conversion'] == 'L', 'normalized_intensity']
            
            # Handle the 'pulse' case
            # df.loc[df['conversion'] == 'pulse', 'pulse'] = df.loc[df['conversion'] == 'pulse', 'normalized_intensity']
            df.loc[df['conversion'] == 'pulse', 'pulse'] = (
            df.loc[df['conversion'] == 'pulse', 'normalized_intensity']
            .infer_objects(copy=False)
            )
        
            df.replace(0, np.nan, inplace=True)
        
        return df
    

    