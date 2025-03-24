import pandas as pd
import os

class MergeSoilLayerIntoSPT:
    def __init__(self, spt, soil_layers):
        self.spt = spt
        self.soil_layers = soil_layers
        
        # Read soil properties from CSV
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.soil_properties = pd.read_csv(os.path.join(current_dir, 'soil_properties.csv'))
        
        # Process soil layers to include upper depth
        self._process_soil_layers()
        
        # Merge soil properties with SPT data
        self._merge_data()
        
    def _process_soil_layers(self):
        """Process soil layers to include upper depths"""
        processed_layers = []
        prev_depth = 0.0
        
        for layer in self.soil_layers:
            processed_layer = layer.copy()
            processed_layer["upper_depth"] = prev_depth
            processed_layer["lower_depth"] = layer["depth"]
            
            # Get soil properties
            soil_props = self._get_soil_properties(layer["class_name"])
            processed_layer.update(soil_props)
            
            processed_layers.append(processed_layer)
            prev_depth = layer["depth"]
            
        self.soil_layers = processed_layers
    
    def _get_soil_properties(self, soil_class_name):
        """Get soil properties from soil_properties.csv"""
        try:
            props = self.soil_properties[self.soil_properties['soil_class_name'] == soil_class_name].iloc[0]
            return {
                'gamma_sat': props['gamma_sat'],
                'gamma_wet': props['gamma_wet'],
                'D50': props['D50'] if not pd.isna(props['D50']) else 0.0,
                'Fc': props['Fc']
            }
        except (IndexError, KeyError):
            # If soil class not found, use default conservative values
            return {
                'gamma_sat': 18.0,  # Conservative estimate
                'gamma_wet': 16.0,  # Conservative estimate
                'D50': 0.0,
                'Fc': 50.0  # Middle range value
            }
    
    def _merge_data(self):
        """Merge soil properties with SPT data"""
        for i in range(len(self.spt)):
            depth = self.spt.loc[i, "depth"]
            
            # Find corresponding soil layer
            for layer in self.soil_layers:
                if layer["upper_depth"] <= depth <= layer["lower_depth"]:
                    # Add soil properties to SPT data
                    self.spt.loc[i, "soil_type"] = layer["class_name"]
                    self.spt.loc[i, "gamma_sat"] = layer["gamma_sat"]
                    self.spt.loc[i, "gamma_wet"] = layer["gamma_wet"]
                    self.spt.loc[i, "D50"] = layer["D50"]
                    self.spt.loc[i, "Fc"] = layer["Fc"]
                    break
            else:
                # If no layer found, use values from closest layer
                closest_layer = min(self.soil_layers, 
                                 key=lambda x: min(abs(x["upper_depth"] - depth),
                                                 abs(x["lower_depth"] - depth)))
                self.spt.loc[i, "soil_type"] = closest_layer["class_name"]
                self.spt.loc[i, "gamma_sat"] = closest_layer["gamma_sat"]
                self.spt.loc[i, "gamma_wet"] = closest_layer["gamma_wet"]
                self.spt.loc[i, "D50"] = closest_layer["D50"]
                self.spt.loc[i, "Fc"] = closest_layer["Fc"]
    
    def get_merged_data(self):
        """Return the merged DataFrame"""
        return self.spt
