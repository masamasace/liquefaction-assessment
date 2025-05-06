import pandas as pd

class MergeSoilLayerIntoSPT:

    def __init__(self, spt, soil_layer):
        self.spt = spt
        self.soil_layer = soil_layer

        self.JRA_standard_params = pd.DataFrame({
            "soil_type": ["表土", "シルト", "砂質シルト", "シルト質細砂",
                          "微細砂", "細砂", "中砂", "粗砂", "砂礫"],
            "gamma_sat": [17.0, 17.5, 18, 18, 18.5, 19.5, 20, 20, 21],
            "gamma_wet": [15.0, 15.5, 16, 16, 16.5, 17.5, 18, 18, 19],
            "D50": [0.02, 0.025, 0.04, 0.07, 0.1, 0.15, 0.35, 0.6, 2.0],
            "Fc": [80, 75, 65, 50, 40, 30, 10, 0, 0]
        })

        print(self.JRA_standard_params)

        self._merge_data()

    def _merge_data(self):

        for i in range(len(self.spt)):
            for j in range(len(self.soil_layer)):
                if self.spt.loc[i, "depth"] >= self.soil_layer[j]["upper_depth"] and self.spt.loc[i, "depth"] <= self.soil_layer[j]["lower_depth"]:
                    self.spt.loc[i, "soil_type"] = self.soil_layer[j]["soil_type"]
                    self.spt.loc[i, "Fc"] = self.soil_layer[j]["Fc"]
                    self.spt.loc[i, "D50"] = self.soil_layer[j]["D50"]
                    self.spt.loc[i, "note"] = self.soil_layer[j]["note"]
                    break

    
    def get_merged_data(self):
        
        return self.spt