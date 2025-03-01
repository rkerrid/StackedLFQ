import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os

def convert_tsv_to_parquet(file_path, output_path=None, chunk_size=100000):
    """
    Convert a TSV file to Parquet format, handling schema inconsistencies.
    
    Parameters:
    -----------
    file_path : str
        Path to the TSV file
    output_path : str, optional
        Path for the output Parquet file. If None, will use the same path as input with .parquet extension
    chunk_size : int, optional
        Size of chunks to process at once, default is 100,000 rows
    
    Returns:
    --------
    str
        Path to the created Parquet file
    """
    if output_path is None:
        output_path = os.path.splitext(file_path)[0] + '.parquet'
    
    print(f"Converting {file_path} to {output_path}")
    print(f"Using chunk size of {chunk_size}")
    
    # Read the entire file once to get a consistent schema
    print("Reading the full file to determine schema (this might take a while for large files)...")
    full_df = pd.read_csv(file_path, sep='\t')
    
    # Save to parquet directly if the file is small enough
    if len(full_df) <= chunk_size:
        print(f"File is small enough to process in one go ({len(full_df)} rows)")
        full_df.to_parquet(output_path, engine='pyarrow')
        print(f"Conversion complete. Parquet file saved to {output_path}")
        return output_path
    
    # For larger files, process in chunks but use the full schema
    print(f"File is large ({len(full_df)} rows). Processing in chunks...")
    
    # Convert to PyArrow table and get schema
    table = pa.Table.from_pandas(full_df)
    schema = table.schema
    
    # Free up memory
    del table
    del full_df
    
    # Process in chunks with consistent schema
    with pq.ParquetWriter(output_path, schema) as writer:
        for chunk_number, chunk in enumerate(pd.read_csv(file_path, sep='\t', chunksize=chunk_size)):
            print(f"Processing chunk {chunk_number+1}...")
            
            # Ensure all columns from the schema are present
            for col in schema.names:
                if col not in chunk.columns:
                    chunk[col] = None
            
            # Ensure no extra columns
            chunk = chunk[schema.names]
            
            # Convert to PyArrow table with the same schema
            table = pa.Table.from_pandas(chunk, schema=schema)
            writer.write_table(table)
    
    print(f"Conversion complete. Parquet file saved to {output_path}")
    return output_path

# Example usage
if __name__ == "__main__":
    # Define your file paths
    tsv_path = r"G:\My Drive\Data\main experiments\20250210 96 sample poc\report.tsv"
    parquet_path = r"G:\My Drive\Data\main experiments\20250210 96 sample poc\report.parquet"
    
    # Call the function
    result_path = convert_tsv_to_parquet(
        file_path=tsv_path, 
        output_path=parquet_path,
        chunk_size=100000  # Optional: adjust chunk size as needed
    )

    print(f"Parquet file created at: {result_path}")


    # import argparse
    # python convert_to_parquet.py "G:\My Drive\Data\main experiments\20250220 testing stackedLFQ with evoAstral 40SPD\report.tsv"
    # parser = argparse.ArgumentParser(description='Convert TSV file to Parquet format')
    # parser.add_argument('file_path', help='Path to the TSV file')
    # parser.add_argument('--output', '-o', help='Path for the output Parquet file (optional)')
    # parser.add_argument('--chunk-size', '-c', type=int, default=100000, 
    #                     help='Size of chunks to process at once (default: 100,000)')
    
    # args = parser.parse_args()
    
    # convert_tsv_to_parquet(args.file_path, args.output, args.chunk_size)