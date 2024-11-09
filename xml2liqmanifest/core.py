from pathlib import Path
from .load import LoadData, CheckMethodParam
from .calc import CalculateFL
import pandas as pd


class LiquefactionManifest:
    
    def __init__(self, file_path):
        
        self.params = {
            "is_loaded": False,
        }
        
        self.params["file_path"] = file_path
        self.params["file_type"] = Path(file_path).suffix.lower()
        
        self.data_from_file = LoadData(file_path)
        self.params["is_loaded"] = True
        
        self.df_SPT = pd.DataFrame(self.data_from_file.data["SPT"])
        
        return None

    
    # set which method to use for liquefaction manifestation
    # JRA, AIJ, Idriss and Boulanger, etc. 
    def set_method(self, **kwargs):
        
        self.params["method"] = kwargs["method"]
        self.params["method_params"] = kwargs["params"]
        
        self.params["method_params"] = CheckMethodParam(self.params["method"], self.params["method_params"]).get_params()
        
        print(self.params) 
        
        return kwargs
    
    def calculate_FL(self):
        
        if self.params["method"] not in ["JRA", "AIJ", "Idriss and Boulanger"]:
            raise ValueError("Method are not set or not supported. Please use set_method() to set the method.")
        
        self.df_SPT = CalculateFL(self.df_SPT, self.params).get_FL()
                
        return None
    
    def export_result(self):
            
        return None