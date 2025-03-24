from pathlib import Path
import json
import pandas as pd
from .load import LoadData, CheckMethodParam
from .calc import CalculateFL
from .merge import MergeSoilLayerIntoSPT

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

    def set_method(self, **kwargs):
        """Set which method to use for liquefaction assessment"""
        self.params["method"] = kwargs["method"]
        self.params["method_params"] = kwargs["params"]
        
        self.params["method_params"] = CheckMethodParam(self.params["method"], self.params["method_params"]).get_params()
        
        self.params["is_set_method"] = True
        
        return kwargs

    def merge_soil_layer(self):
        """Merge soil layer information with SPT data"""
        self.df_SPT = MergeSoilLayerIntoSPT(self.df_SPT, self.data_from_file.data["soil_layers"]).get_merged_data()
        self.params["is_already_merged_from_soil_layer"] = True
    
    def calculate_FL(self):
        """Calculate liquefaction potential"""
        if not self.params["is_already_merged_from_soil_layer"]:
            self.merge_soil_layer()

        if self.params["method"] not in ["JRA", "AIJ", "Idriss and Boulanger"]:
            raise ValueError("Method are not set or not supported. Please use set_method() to set the method.")
        
        self.df_SPT = CalculateFL(self.df_SPT, self.params).get_FL()
                
        return None
    
    def export_result(self, output_dir=None):
        """Export calculation results to CSV and JSON files"""
        if output_dir is None:
            output_dir = Path(self.params["file_path"]).parent
        else:
            output_dir = Path(output_dir)
            
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export CSV with depth, N-value, and FL distribution
        csv_columns = ['depth', 'N_value', 'FL', 'soil_type']
        csv_path = output_dir / 'liquefaction_results.csv'
        self.df_SPT[csv_columns].to_csv(csv_path, index=False)
        
        # Prepare JSON summary
        summary = {
            "site_info": {
                "latitude": self.data_from_file.data["lat"],
                "longitude": self.data_from_file.data["lon"],
                "investigation_date": self.data_from_file.data["start_date"],
                "ground_level": self.data_from_file.data["tip_elevation"]
            },
            "calculation_method": {
                "name": self.params["method"],
                "parameters": self.params["method_params"]
            },
            "results": {
                "min_FL": float(self.df_SPT["FL"].min()),
                "max_FL": float(self.df_SPT["FL"].max()),
                "critical_depth": float(self.df_SPT.loc[self.df_SPT["FL"].idxmin(), "depth"]),
                "liquefaction_risk": self._assess_liquefaction_risk(),
                "analysis_depth_range": {
                    "start": float(self.df_SPT["depth"].min()),
                    "end": float(self.df_SPT["depth"].max())
                }
            },
            "soil_profile": self._generate_soil_profile()
        }
        
        # Export JSON summary
        json_path = output_dir / 'liquefaction_summary.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=4)
            
        return {
            "csv_path": str(csv_path),
            "json_path": str(json_path)
        }
    
    def _assess_liquefaction_risk(self):
        """Assess overall liquefaction risk based on FL values"""
        min_FL = self.df_SPT["FL"].min()
        
        if min_FL < 1.0:
            return "high"
        elif min_FL < 1.2:
            return "medium"
        else:
            return "low"
    
    def _generate_soil_profile(self):
        """Generate summary of soil layers with average properties"""
        profile = []
        
        # Group by soil type
        soil_groups = self.df_SPT.groupby("soil_type")
        
        for soil_type, group in soil_groups:
            layer = {
                "depth_range": [float(group["depth"].min()), float(group["depth"].max())],
                "soil_type": soil_type,
                "average_N": float(group["N_value"].mean()),
                "average_FL": float(group["FL"].mean())
            }
            profile.append(layer)
            
        return profile
