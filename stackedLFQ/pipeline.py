# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 17:53:34 2024

@author: robbi
"""

import os
import pandas as pd
from icecream import ic
import tkinter as tk
import json

from stackedLFQ.utils import manage_directories
from stackedLFQ.reporting import precursor_report
from stackedLFQ.reporting import protein_groups_report

from stackedLFQ.preprocessor import Preprocessor 
from stackedLFQ.stacked_lfq import StackedLFQ
from stackedLFQ.meta_data_entry import MetaDataEntry


class Pipeline:
    def __init__(self, path=None, metadata_file=None): # check method input is valid otherwise print method options
        #load params
        self.path = f'{path}/'
        self.params = self._load_params(self.path)
                    
        self.metadata_file = f'{self.path}meta.csv'
        
        # Initialize class variables
        # self.relable_with_meta = self._confirm_metadata()
        self.meta_data = self._load_meta_data() #if self.relable_with_meta else None
       
        # Placeholder variables 
        self.filtered_report = None
        self.contaminants = None
        self.protein_groups = None
        
    def _load_params(self, path):
        # json_path = os.path.join(os.path.dirname(__file__), 'configs', 'params.json')
        json_path = f'{path}/params.json'
        print(json_path)
        with open(json_path, 'r') as file:
            params = json.load(file)
            
            # Print the types of all values in the JSON
            def print_types(obj, path=''):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key
                        print(f"{new_path}: {type(value)}")
                        print_types(value, new_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        new_path = f"{path}[{i}]"
                        print(f"{new_path}: {type(item)}")
                        print_types(item, new_path)
            
            print_types(params, f'{path}')
            return params

    def _confirm_metadata(self):
        if self.metadata_file is None:
            print("No metadata added, filtering will continue without relabeling")
            return False
        if not isinstance(self.metadata_file, str):
            print("File name is not a string, filtering will continue without relabeling")
            return False
        print("Metadata added, looking for the following file:", self.metadata_file)
        return self._check_directory()

    def _check_directory(self):
        file_list = os.listdir(self.path)
        if self.metadata_file in file_list:
            print(f"CSV file '{self.metadata_file}' found in {self.path}")
            return True
        print(f"CSV file '{self.metadata_file}' not found in the directory.")
        return False

    def _load_meta_data(self):
        return pd.read_csv(os.path.join(self.path, self.metadata_file), sep=',')       
    
    def execute_pipeline(self, generate_report=True):
        manage_directories.create_directory(self.path, 'preprocessing')
        
        self.preprocessor = Preprocessor(self.path, self.params, self.meta_data)
        self.filtered_report, self.contaminants = self.preprocessor.preprocess()
       
        self.contaminants.to_csv(os.path.join(self.path, 'preprocessing', 'contaminants.csv'), sep=',')
        self.filtered_report.to_csv(os.path.join(self.path, 'preprocessing', 'formatted_precursors.csv'), sep=',')
        
        self.precursor_rollup = StackedLFQ(self.path, self.params, self.filtered_report)
        self.protein_groups = self.precursor_rollup.generate_protein_groups()
        
        self._format_and_save_protein_groups(self.protein_groups)
     
        self._generate_reports()
        return self.protein_groups

    def _format_and_save_protein_groups(self, protein_groups):
        ''' this function should format protein groups into csv files for light, pulse,and ratios'''

        protein_groups[['protein_group', 'genes']] = protein_groups['protein_group'].str.split(':', expand=True)
        
        def _format_data(protein_groups, subset):
            df = protein_groups.copy(deep=True)
            df = df[['Run','protein_group','genes', f'{subset}']]
            df = df.dropna()
            df = df.pivot_table(
            index=['protein_group', 'genes'], 
            columns ='Run',                                
            values = f'{subset}'                          
            ).reset_index()
            return df
        
        manage_directories.create_directory(self.path, 'protein_groups')
        protein_groups.to_csv(os.path.join(self.path, 'protein_groups', 'protein_groups.csv'), sep=',')
        
        df_l = _format_data(protein_groups, 'L')
        df_l.to_csv(os.path.join(self.path, 'protein_groups', 'light.csv'), sep=',')
        
        df_p = _format_data(protein_groups, 'pulse')
        df_p.to_csv(os.path.join(self.path, 'protein_groups', 'pulse.csv'), sep=',')
        
        # drop non-float (ie invalid, L, and pulse labels) values from ratios col before formatting
        protein_groups = protein_groups[pd.to_numeric(protein_groups['pulse_L_ratio'], errors='coerce').notna()]
        
        df_r = _format_data(protein_groups, 'pulse_L_ratio')
        df_r.to_csv(os.path.join(self.path, 'protein_groups', 'ratios.csv'), sep=',')
        
    def _generate_reports(self):
        '''this function should call functions from the report module to plot data ralated to IDs, ratios, correlation etc. as well as log data about the run and version etc.'''        
        manage_directories.create_directory(self.path, 'reports')
        precursor_report.create_precursor_report(self.path)
        protein_groups_report.protein_groups_report(self.path)
       
    def make_metadata(self):
       print("Searching report.tsv for unique runs for metadata, use pop up to enter metadata or copy and past selected runs to a spreadsheet and save as .csv file")
       root = tk.Tk()
       app = MetaDataEntry(self.path, root)
       root.protocol("WM_DELETE_WINDOW", app.on_closing)
       app.pack(fill="both", expand=True)  # Ensure the app fills the root window
       root.mainloop()