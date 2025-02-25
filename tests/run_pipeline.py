from icecream import ic
from stackedLFQ.pipeline import Pipeline as pipeline
from stackedLFQ.gui.app import App
import pandas as pd 


if __name__ == "__main__": 
   
     

    path = r'G:\My Drive\Data\main experiments\20250220 testing stackedLFQ with evoAstral 40SPD\\'
    path = r'G:\My Drive\Data\data\20250225 mariana organoids\400ng 1 precursor\\'
    
    # pipeline = pipeline(path=path, metadata_file='meta.csv')
    
    # result = pipeline.make_metadata()  
    # result = pipeline.execute_pipeline()
    # 
    # pipeline._generate_reports()


  
    
    app = App()
    app.mainloop()