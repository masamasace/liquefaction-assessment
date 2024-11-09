import math

class CalculateFL:
    
    def __init__(self, df_SPT, params):
        
        self.df_SPT = df_SPT
        self.params = params
        
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
            self.df_SPT.loc[i, "N1"] = 170 * self.df_SPT.loc[i, "N"] / (self.df_SPT.loc[i, "sigma_p_v"] + 70)
            
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
        
        pass
    
    def _AIJ(self):
        
        raise NotImplementedError("AIJ method is not implemented yet.")
    
    def _Idriss_and_Boulanger(self):
        
        raise NotImplementedError("Idriss and Boulanger method is not implemented yet.")
    