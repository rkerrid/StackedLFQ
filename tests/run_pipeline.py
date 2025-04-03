from icecream import ic
from stackedLFQ.pipeline import Pipeline as pipeline
from stackedLFQ.gui.app import App
import pandas as pd 


if __name__ == "__main__": 
   
     


    path = 'G:/My Drive/Data/PhD results chapters/20250225 mariana organoids/400ng 2 precursor'
    import_file = 'G:/My Drive/Data/PhD results chapters/20250225 mariana organoids/400ng 2 precursor/report.tsv'
   
    
    pipeline = pipeline( path=path, import_file=import_file, metadata_file='meta_with_treatments_exclusion.csv')

    
    # result = pipeline.make_metadata()  
    result = pipeline.execute_pipeline()
    # 
    # pipeline._generate_reports()


  
    
    # app = App()
    # app.mainloop()