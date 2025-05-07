import pandas as pd

class MergeSoilLayerIntoSPT:

    def __init__(self, data):
        
        self.data = data
        self.spt_data = data["borehole_data"]["SPT"]
        
    
    def get_merged_data(self):
        return self.data