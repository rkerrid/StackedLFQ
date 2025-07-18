# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 05:35:15 2025

@author: robbi
"""
import pandas as pd
import time
import os
import operator
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor


class Preprocessor:
    def __init__(self, path, import_file, params, meta_data=None):
        self.path = path
        self.import_file = import_file
        self.params = params
        self.meta_data = meta_data
        self.chunk_size = 1000000  # Adjusted chunk size for better performance
        self.pulse_channel = self.params["silac_pulse_channel"]
        
    def preprocess(self):
        
        print('Importing')
        start_time = time.time()
        filtered_report, contaminants_df = self.import_report()
        print('Finished import')
        end_time = time.time()
        print(f"Time taken for import: {end_time - start_time} seconds")
        
        print('Reformating')
        start_time = time.time()
        filtered_report = self.reformat_table(filtered_report, self.pulse_channel)
        print('Finished reformating')
        end_time = time.time()
        print(f"Time taken for reformating: {end_time - start_time} seconds")
        
        return filtered_report, contaminants_df
    def import_report(self):
        """
        Import report based on file extension and DIANN version
        """
        print()
        # Get file extension
        file_extension = os.path.splitext(self.import_file)[1].lower()
        
        if self.params["diann_version"] == "1.8.1":
            print(f'Importing DIANN 1.8.1 file with {file_extension} extension')
            if file_extension == '.tsv':
                return self._import_tsv_report()
            elif file_extension == '.parquet':
                return self._import_parquet_report()
            else:
                raise ValueError(f"Unsupported file extension: {file_extension} for DIANN 1.8.1. Supported extensions are '.tsv' and '.parquet'")
        
        elif self.params["diann_version"] == "2":
            if file_extension != '.parquet':
                print(f"Warning: DIANN 2 typically uses parquet format, but found {file_extension}. Attempting to import anyway.")
            return self._import_parquet_report()
            
        else:
            raise ValueError("Unsupported DIANN version. Supported versions are '1.8.1' and '2'.")
            
    # def import_report(self):
        
    #     if self.params["diann_version"] == "1.8.1":
    #         print('importing DIANN 1.8.1 .tsv file')
    #         return self._import_tsv_report()
        
    #     elif self.params["diann_version"] == "2":
    #         return self._import_parquet_report()
            
    #     else:
    #         raise ValueError("Unsupported file type: Supported types are 'tsv' and 'parquet', check directroy and DIANN report is correct.")
    
    def _import_tsv_report(self):
        file_path = f"{self.path}report.tsv"
      
        file_size_bytes = os.path.getsize(file_path)
        average_row_size_bytes = 1100  # This is an example; you'll need to adjust this based on your data
        
        # Estimate the number of rows
        estimated_rows = file_size_bytes / average_row_size_bytes
        total_chunks = estimated_rows/self.chunk_size
        
        # Use ProcessPoolExecutor for parallel processing
        with ProcessPoolExecutor() as executor:
            futures = []
            with tqdm(total=total_chunks, desc="Processing file in chunks") as pbar:
                for chunk in pd.read_table(file_path, sep="\t", chunksize=self.chunk_size):
                   
                    futures.append(executor.submit(self.process_chunk, chunk))
                    pbar.update(1) 
            
            # Gather results from futures
            results = [f.result() for f in futures]
            
            # Concatenate chunks into final DataFrame
            filtered_report = pd.concat([res[0] for res in results], ignore_index=True)
            contaminants_df = pd.concat([res[1] for res in results], ignore_index=True)
    
        
        return filtered_report, contaminants_df
    
    def _import_parquet_report(self):
        file_path = f"{self.path}report.parquet"
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Parquet file not found: {file_path}")
        
        # Parquet files can be read directly without chunking, but for large files,
        # we'll still process in chunks for consistency with the TSV approach
        try:
            # Read parquet file metadata to get number of row groups
            parquet_file = pd.read_parquet(file_path, engine='pyarrow')
            total_rows = len(parquet_file)
            
            # For very large files, we'll process in chunks
            if total_rows > self.chunk_size:
                total_chunks = (total_rows + self.chunk_size - 1) // self.chunk_size  # Ceiling division
                
                with ProcessPoolExecutor() as executor:
                    futures = []
                    with tqdm(total=total_chunks, desc="Processing parquet file in chunks") as pbar:
                        for i in range(0, total_rows, self.chunk_size):
                            chunk = parquet_file.iloc[i:i+self.chunk_size]
                            futures.append(executor.submit(self.process_chunk, chunk))
                            pbar.update(1)
                        
                    # Gather results from futures
                    results = [f.result() for f in futures]
                    
                    # Concatenate chunks into final DataFrame
                    filtered_report = pd.concat([res[0] for res in results], ignore_index=True)
                    contaminants_df = pd.concat([res[1] for res in results], ignore_index=True)
            else:
                # For smaller files, process directly
                filtered_report, contaminants_df = self.process_chunk(parquet_file)
                
        except Exception as e:
            print(f"Error processing parquet file: {e}")
            raise
            
        return filtered_report, contaminants_df
    
    def process_chunk(self, chunk):
        # Process the chunk in parallel
        if self.meta_data is not None:
            chunk = self.subset_based_on_metadata(chunk)
            chunk = self.relabel_run(chunk)
        
        chunk = self.add_label_col(chunk)
  
        chunk = self.add_passes_filter_col(chunk, self.params)
        
        chunk = self.drop_cols(chunk)
     
        chunk, contam_chunk = self.remove_contaminants(chunk, self.params["contaminant_pattern"])
        
        return chunk, contam_chunk
    
    
    def reformat_table(self, df, pulse_channel):
        df = df.rename(columns={'Protein.Group':'protein_group', 'Precursor.Id': 'precursor_id'})
        index_cols = ['Run', 'protein_group','precursor_id']
                 
        df_light = df[df['Label']=='L']
        df_pulse = df[df['Label']==pulse_channel]
        df_light = df_light.drop(['Label'], axis=1)
        df_pulse = df_pulse.drop(['Label'], axis=1)
 
        df_light = df_light.rename(columns={'Precursor.Quantity':'precursor_quantity_L','filter_passed':'filter_passed_L'})
        df_pulse = df_pulse.rename(columns={'Precursor.Quantity':'precursor_quantity_pulse','filter_passed':'filter_passed_pulse'})
       
        df = pd.merge(df_light, df_pulse,on=index_cols, how='outer')
        
        df['filter_passed_pulse'] = df['filter_passed_pulse'].fillna(0)
        df['filter_passed_L'] = df['filter_passed_L'].fillna(0)
        
        return df
    
    def subset_based_on_metadata(self, df):   
        df = df.copy()
        filtered_df = df[df['Run'].isin(self.meta_data['Run'])]
        return filtered_df
    
    def relabel_run(self, df):
        df = df.copy()
        
        run_to_sample = dict(zip(self.meta_data['Run'], self.meta_data['Sample']))
    
        # Apply the mapping to df2['Run'] and raise an error if a 'Run' value doesn't exist in df1
        df['Run'] = df['Run'].map(run_to_sample)
        if df['Run'].isna().any():
            raise ValueError("Some Run values in the report are not found in the metadata, please ensure metadata is correct.")
            
        return df

    def add_label_col(self, df):
        df = df.copy()
        
        if self.params["diann_version"] == "1.8.1":
            # Extract the label and add it as a new column
            df['Label'] = df['Precursor.Id'].str.extract(r'\(SILAC-(K|R)-([HML])\)')[1]
            # Remove the '(SILAC-K|R-([HML]))' part from the 'Precursor.Id' string
            df['Precursor.Id'] = df['Precursor.Id'].str.replace(r'\(SILAC-(K|R)-[HML]\)', '', regex=True)
            
        elif self.params["diann_version"] == "2":
            df = df.rename(columns={'Channel': 'Label'})
            df['Precursor.Id'] = df['Precursor.Id'].str.replace(r'\(SILAC\)', '', regex=True)
        
        return df
    
    def add_passes_filter_col(self, df, params):
        """
        DF annotated with pas or fail based on filtering criteria in the params file.
        """
        df = df.copy()
        
        ops = {
            "==": operator.eq, "<": operator.lt, "<=": operator.le,
            ">": operator.gt, ">=": operator.ge
        }
        
        df['filter_passed'] = True
        mask = df['filter_passed']
        
        for column, condition in self.params['filters'].items():
            op = ops[condition['op']]
            
            # Make sure the column exists in parquet file
            if column not in df.columns:
                print(f"Warning: Filter column '{column}' not found in the file. Skipping this filter.")
                continue
            
            # Update the mask to keep chanel rows that meet the condition
            mask &= op(df[column], condition['value'])
          
        # # Filter out chanel rows that do not meet all conditions
        df['filter_passed'] = mask
        
        # set to 0 or 1 for IO consistency
        df['filter_passed'] = df['filter_passed'].astype(int)
        
        return df
    
    def drop_cols(self, df):
        df = df.copy()
        
        # what cols to keep for future workflow
        cols = ['Run',
                'Protein.Group',
                'Precursor.Id',
                'Precursor.Quantity',
                'Label',
                'filter_passed']
        
        # Check if all required columns exist
        missing_cols = [col for col in cols if col not in df.columns]
        if missing_cols:
            raise ValueError("Missing required columns in  file: {missing_cols}")
        
        df['Protein.Group'] = df['Protein.Group'] + ':' + df['Genes']
        # drop all other cols
        df = df[cols]
        return df

    def remove_contaminants(self, df, contam_annotation):
        df = df.copy()
        
        contams_mask = df['Protein.Group'].str.contains(contam_annotation, case=False, na=False)
        df_filtered = df.loc[~contams_mask].reset_index(drop=True)
        contams = df.loc[contams_mask].reset_index(drop=True)
   
        return df_filtered, contams
