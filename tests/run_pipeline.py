from icecream import ic
from stackedLFQ.pipeline import Pipeline as pipeline
from stackedLFQ.gui.app import App
import pandas as pd 


if __name__ == "__main__": 
   
     


    path = 'G:/My Drive/Data/main experiments/20250210 96 sample poc'
    # path = 'G:/My Drive/Data/main experiments/20250210 G1 starvation'
    
    pipeline = pipeline( path=path, metadata_file='meta.csv')

    
    # result = pipeline.make_metadata()  
    result = pipeline.execute_pipeline()
    # 
    # pipeline._generate_reports()


  
    
    app = App()
    app.mainloop()