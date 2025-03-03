from icecream import ic
from stackedLFQ.pipeline import Pipeline as pipeline
from stackedLFQ.gui.app import App
import pandas as pd 


if __name__ == "__main__": 
   
     


    # path = 'G:/My Drive/Data/main experiments/20250210 96 sample poc'
    # import_file = 'G:/My Drive/Data/main experiments/20250210 96 sample poc/report.parquet'
   
    
    # pipeline = pipeline( path=path, import_file=import_file, metadata_file='meta_remove_dropouts.csv')

    
    # result = pipeline.make_metadata()  
    # result = pipeline.execute_pipeline()
    # 
    # pipeline._generate_reports()


  
    
    app = App()
    app.mainloop()