from pathlib import Path
from .load import LoadData, CheckMethodParam
from .calc import CalculateFL
from .merge import MergeSoilLayerIntoSPT
import pandas as pd


class LiquefactionManifest:
    
    def __init__(self, file_path):
        
        self.params = {
            "is_loaded": False,
            "is_set_method": False,
            "is_already_merged_from_soil_layer": False,
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
        
        self.params["is_set_method"] = True

        return kwargs

    def merge_soil_layer(self):

        self.df_SPT = MergeSoilLayerIntoSPT(self.df_SPT, self.data_from_file.data["soil_layers"]).get_merged_data()

        self.params["is_already_merged_from_soil_layer"] = True
    
    def calculate_FL(self):

        if self.params["is_already_merged_from_soil_layer"] == False:
            
            self.merge_soil_layer()

        if self.params["method"] not in ["JRA", "AIJ", "Idriss and Boulanger"]:
            raise ValueError("Method are not set or not supported. Please use set_method() to set the method.")
        
        self.df_SPT = CalculateFL(self.df_SPT, self.params).get_FL()
                
        return None
    
    def export_result(self):
            
        return None