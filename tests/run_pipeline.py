from icecream import ic
from stackedLFQ.pipeline import Pipeline as pipeline
from stackedLFQ.gui.app import App
import pandas as pd 


if __name__ == "__main__": 
   
     


    path = 'G:/My Drive/Data/data/20250505 daniela/1k2p5k'
    import_file = 'G:/My Drive/Data/data/20250505 daniela/1k2p5k/report.tsv'
   
    
    pipeline = pipeline( path=path, import_file=import_file, metadata_file='meta.csv')

    
    # result = pipeline.make_metadata()  
    result = pipeline.execute_pipeline()
    # 
    # pipeline._generate_reports()


  
    
    # app = App()
    # app.mainloop()