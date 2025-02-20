from icecream import ic
from silac_dia_tools.workflow.pipeline import Pipeline as pipeline
import pandas as pd 


if __name__ == "__main__": 
   
     

    path = r'G:\My Drive\Data\main experiments\20250220 testing stackedLFQ with evoAstral 40SPD\\'
    
    pipeline = pipeline( f'{path}',  method = 'dynamic_silac_dia', pulse_channel="H", metadata_file='meta.csv')
    
    # result = pipeline.make_metadata()  
    result = pipeline.execute_pipeline()

