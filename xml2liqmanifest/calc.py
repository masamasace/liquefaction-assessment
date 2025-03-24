import math
import numpy as np
import pandas as pd

class CalculateFL:
    
    def __init__(self, df_SPT, params):
        self.df_SPT = df_SPT
        self.params = params
        
        # Water unit weight (kN/m3)
        self.gamma_w = 9.80665
        
        if self.params["method"] == "JRA":
            self._JRA()
        elif self.params["method"] == "AIJ":
            self._AIJ()
        elif self.params["method"] == "Idriss and Boulanger":
            self._Idriss_and_Boulanger()
            
        return None
    
    def get_FL(self):
        return self.df_SPT
    
    def _JRA(self):
        if self.params["year"] in [2012, 2017]:
            self._JRA_2012_2017()
        elif self.params["year"] in [2002]:
            self._JRA_2002()
    
    def _JRA_2012_2017(self):
        for i in range(len(self.df_SPT)):
            # calculate overburden stress
            self.df_SPT.loc[i, "sigma_v"] = self._calculate_sigma_v(self.df_SPT.loc[i, "depth"])
            self.df_SPT.loc[i, "sigma_p_v"] = self._calculate_sigma_p_v(self.df_SPT.loc[i, "depth"])
        
            # calculate seismic load
            self.df_SPT.loc[i, "rd"] = 1 - 0.015 * self.df_SPT.loc[i, "depth"]
            self.df_SPT.loc[i, "L"] = self.df_SPT.loc[i, "rd"] * self.params["method_params"]["Khgl"] * self.df_SPT.loc[i, "sigma_v"] / self.df_SPT.loc[i, "sigma_p_v"]
            
            # calculate liquefaction resistance
            self.df_SPT.loc[i, "N1"] = 170 * self.df_SPT.loc[i, "N_value"] / (self.df_SPT.loc[i, "sigma_p_v"] + 70)
            
            if self.df_SPT.loc[i, "D50"] >= 2:
                self.df_SPT.loc[i, "CFc"] = 1.0
                self.df_SPT.loc[i, "Na"] = (1 - 0.36 * math.log10(self.df_SPT.loc[i, "D50"] / 2)) * self.df_SPT.loc[i, "N1"]
            else:
                self.df_SPT.loc[i, "CFc"] = self._calculate_CFc(self.df_SPT.loc[i, "Fc"])
                self.df_SPT.loc[i, "Na"] = self.df_SPT.loc[i, "CFc"] * (self.df_SPT.loc[i, "N1"] + 2.47) - 2.47
            
            if self.df_SPT.loc[i, "N1"] < 14:
                self.df_SPT.loc[i, "RL"] = 0.0882 * ((0.85 * self.df_SPT.loc[i, "Na"] + 2.1) / 1.7) ** 0.5
            else:
                self.df_SPT.loc[i, "RL"] = 0.0882 * (self.df_SPT.loc[i, "Na"] / 1.7) ** 0.5 + 1.6 * 10 ** -6 * (self.df_SPT.loc[i, "N1"] - 14) ** 4.5
            
            self.df_SPT.loc[i, "Cw"] = self._calculate_Cw()
            self.df_SPT.loc[i, "R"] = self.df_SPT.loc[i, "RL"] * self.df_SPT.loc[i, "Cw"]
            
            # calculate FL
            self.df_SPT.loc[i, "FL"] = self.df_SPT.loc[i, "R"] / self.df_SPT.loc[i, "L"]
    
    def _calculate_sigma_v(self, depth):
        """Calculate total vertical stress at given depth"""
        if not hasattr(self, 'ground_water_level'):
            # Default to conservative estimate if water level not provided
            self.ground_water_level = 0.0
            
        total_stress = 0.0
        current_depth = 0.0
        
        # Sort depths to ensure proper layer calculation
        layer_depths = sorted(self.df_SPT['depth'].unique())
        
        for layer_depth in layer_depths:
            if layer_depth > depth:
                break
                
            # Get soil properties for current layer
            layer_data = self.df_SPT[self.df_SPT['depth'] == layer_depth].iloc[0]
            
            # Calculate layer thickness
            layer_thickness = layer_depth - current_depth
            
            # Determine which unit weight to use based on water table
            if current_depth < self.ground_water_level:
                gamma = layer_data['gamma_wet']
            else:
                gamma = layer_data['gamma_sat']
                
            # Add stress from this layer
            total_stress += gamma * layer_thickness
            current_depth = layer_depth
            
        return total_stress
    
    def _calculate_sigma_p_v(self, depth):
        """Calculate effective vertical stress at given depth"""
        total_stress = self._calculate_sigma_v(depth)
        
        # Calculate water pressure
        if depth > self.ground_water_level:
            u = self.gamma_w * (depth - self.ground_water_level)
        else:
            u = 0
            
        return total_stress - u
    
    def _calculate_CFc(self, Fc):
        """Calculate correction factor for fines content"""
        if Fc <= 40:
            return 1.0
        else:
            return 1.0 + 0.004 * (Fc - 40) + 0.005 * ((Fc - 40) ** 2) / ((1 + 0.004 * (Fc - 40)) ** 2)
    
    def _calculate_Cw(self):
        """Calculate correction factor for water pressure"""
        return 1.0  # Default implementation, modify if needed based on specific requirements
    
    def _AIJ(self):
        """Stub for AIJ method implementation"""
        raise NotImplementedError("AIJ method is not implemented yet.")
    
    def _Idriss_and_Boulanger(self):
        """Stub for Idriss and Boulanger method implementation"""
        raise NotImplementedError("Idriss and Boulanger method is not implemented yet.")
