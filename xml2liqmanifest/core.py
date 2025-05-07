from pathlib import Path
from .load import LoadData, CheckMethodParam
from .calc import CalculateFL
from .merge import MergeSoilLayerIntoSPT
import pandas as pd
import pickle


class LiquefactionManifest:
    
    def __init__(self, file_path, temp_dir=None, res_dir=None, force_read_file=False):
        
        if temp_dir is None:
            self.temp_dir = Path(__file__).parent / "temp"
            if not self.temp_dir.exists():
                self.temp_dir.mkdir(exist_ok=True)
        else:
            self.temp_dir = Path(temp_dir).resolve()
        
        if res_dir is None:
            self.res_dir = Path(__file__).parent / "res"
            if not self.res_dir.exists():
                self.res_dir.mkdir(exist_ok=True)
        else:
            self.res_dir = Path(res_dir).resolve()           
        
        
        self.data = {
            "temp_dir": self.temp_dir,
            "res_dir": self.res_dir,
            "file_path": file_path,
            "file_type": Path(file_path).suffix.lower(),
            "pickle_path": self.temp_dir / f"{Path(file_path).stem}.pkl",
        }
        
        self._read_file(file_path, force_read_file, self.data["pickle_path"])
        
        # save class instance by pickle
        self._save_pickle()
        
        return None

    def _read_file(self, file_path, force_read_file, pickle_path):
        
        if force_read_file or not pickle_path.exists():
            
            print(f"Loading data from {file_path.name}... ", end="")
            self.data["borehole_data"] = LoadData(file_path).data
            print("Done.")
            
        else:
            print(f"Loading data from {pickle_path.name}... ", end="")
            with open(pickle_path, "rb") as f:
                self.data = pickle.load(f).data
            print("Done.")
            

    def _save_pickle(self):
        
        with open(self.data["pickle_path"], "wb") as f:
            pickle.dump(self, f)
        
        return None
    
    # set which method to use for liquefaction manifestation
    # JRA, AIJ, Idriss and Boulanger, etc. 
    def set_method(self, **kwargs):
        
        self._read_file(self.data["file_path"], False, self.data["pickle_path"])
        
        self.data["method"] = kwargs["method"]
        self.data["method_params"] = kwargs["params"]
        
        self.data["method_params"] = CheckMethodParam(self.data["method"], self.data["method_params"]).get_params()
        
        self._save_pickle()
        
        return None

    def merge_soil_layer(self):
        
        self._read_file(self.data["file_path"], False, self.data["pickle_path"])

        self.data = MergeSoilLayerIntoSPT(self.data).get_merged_data()
        
        self._save_pickle()

    
    def calculate_FL(self):

        pass
    
    def export_result(self):
            
        return None