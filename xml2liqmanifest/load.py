from pathlib import Path
from lxml import etree as ET
import warnings

# TODO: load all data from xml file to make this to individual library
class LoadData:
    def __init__(self, path):
        self.params = {
            "path": path,
            "stem": Path(path).stem,
            "file_type": Path(path).suffix.lower(),
        }
        
        if self.params["file_type"] not in [".xml", ".csv", ".xlsx"]:
            raise ValueError("Invalid file type.")
        else:
            if self.params["file_type"] == ".xml":
                self.data = self._load_xml()
            elif self.params["file_type"] == ".csv":
                self.data = self._load_csv()
            elif self.params["file_type"] == ".xlsx":
                self.data = self._load_xlsx()

    # load data from xml file            
    def _load_xml(self):
        
        # read header info including xml version, encoding, etc.
        header = []
        with open(self.params["path"], "r") as f:
            header.append(f.readline())

        xml_version = header[0].split(" ")[1].split("=")[1].replace('"', "")
        xml_encoding = header[0].split(" ")[2].split("=")[1].replace('"', "").replace("?>", "").replace("\n", "").lower()
        
        # read xml data
        parser = ET.XMLParser(encoding=xml_encoding)
        tree = ET.parse(self.params["path"], parser=parser)
        
        data = {}
        
        # parse lat and lon
        data["lat"], data["lon"] = self._load_xml_lat_lon(tree)
        
        # parse start date of borehole investigation
        data["start_date"] = self._load_xml_start_date(tree)
        
        # parse borehole info
        data["tip_elevation"] = self._load_xml_tip_elevation(tree)
        
        # parse hitting condition info
        # TODO: implement later
        
        # parse soil layer info 
        data["soil_layers"] = self._load_xml_soil_layers(tree)
        
        # parse observation note info
        data["observation_note"] = self._load_xml_observation_note(tree)
        
        # parse SPT data
        data["SPT"] = self._load_xml_SPT(tree)
        
        return data
        
    def _load_xml_lat_lon(self, tree):
        
        # find lat and lon info
        lat_deg = list(tree.iter("緯度_度"))[0].text
        lat_min = list(tree.iter("緯度_分"))[0].text
        lat_sec = list(tree.iter("緯度_秒"))[0].text
        
        lon_deg = list(tree.iter("経度_度"))[0].text
        lon_min = list(tree.iter("経度_分"))[0].text
        lon_sec = list(tree.iter("経度_秒"))[0].text
        
        if lat_deg is None or lat_min is None or lat_sec is None:
            raise warnings.warn("緯度情報が見つかりませんでした。")
        if lon_deg is None or lon_min is None or lon_sec is None:
            raise warnings.warn("経度情報が見つかりませんでした。")
        
        lat = float(lat_deg) + float(lat_min) / 60 + float(lat_sec) / 3600
        lon = float(lon_deg) + float(lon_min) / 60 + float(lon_sec) / 3600
        
        return lat, lon

    def _load_xml_start_date(self, tree):
        
        # find start date info
        start_date = list(tree.iter("調査期間_開始年月日"))[0].text
        
        if start_date is None:
            raise warnings.warn("調査開始日が見つかりませんでした。")
        
        return start_date

    def _load_xml_tip_elevation(self, tree):
        
        # find tip elevation info
        tip_elevation = float(list(tree.iter("孔口標高"))[0].text)
        
        if tip_elevation is None:
            raise warnings.warn("孔口標高が見つかりませんでした。")
        
        return tip_elevation

    def _load_xml_soil_layers(self, tree):
        
        # find soil layer info
        soil_layers = []
        for soil_layer in tree.iter("岩石土区分"):
            layer = {
                "depth": float(soil_layer.find("岩石土区分_下端深度").text),
                "class_name": soil_layer.find("岩石土区分_岩石土名").text,
                "class_code": soil_layer.find("岩石土区分_岩石土記号").text,
            }
            soil_layers.append(layer)
        
        if soil_layers is None or len(soil_layers) == 0:
            raise ValueError("地質情報が見つかりませんでした。")
        
        return soil_layers

    def _load_xml_observation_note(self, tree):
        
        # find observation note info
        observation_notes = []
        for observation_note in tree.iter("観察記事"):
            
            observation_note = {
                "upper_depth": float(observation_note.find("観察記事_上端深度").text),
                "lower_depth": float(observation_note.find("観察記事_下端深度").text),
                "note": observation_note.find("観察記事_記事").text,
            }
            observation_notes.append(observation_note)
            
        if observation_notes is None or len(observation_notes) == 0:
            raise warnings.warn("観察記事が見つかりませんでした。")
        
        return observation_notes
    
    def _load_xml_SPT(self, tree):
        
        # find SPT data
        SPTs = []
        for SPT in tree.iter("標準貫入試験"):
            
            SPT = {
                "depth": float(SPT.find("標準貫入試験_開始深度").text),
                "N_value": float(SPT.find("標準貫入試験_合計打撃回数").text),
                "penetration_length": float(SPT.find("標準貫入試験_合計貫入量").text)
            }
            SPTs.append(SPT)
            
        if SPTs is None or len(SPTs) == 0:
            raise ValueError("SPTデータが見つかりませんでした。")
        
        return SPTs
        
    def _load_csv(self):
        
        raise NotImplementedError("Method not implemented.")
    
    def _load_xlsx(self):
        
        raise NotImplementedError("Method not implemented.")


class CheckMethodParam:
    
    def __init__(self, method, params):
        
        self.params = {
            "method": method,
            "params": params,
        }
        
        self._check_method_params()
    
    def get_params(self):
        
        return self.params["params"]
        
    def _check_method_params(self):
        
        if self.params["method"] == "JRA":
            self._check_JRA_params()
            self.params["params"] = self._calculate_Khgl()
        elif self.params["method"] == "AIJ":
            self._check_AIJ_params()
        elif self.params["method"] == "Idriss and Boulanger":
            self._check_Idriss_and_Boulanger_params()
        else:
            raise ValueError("Invalid method.")
        
        return self.params["params"]

    def _check_JRA_params(self):
            
            if self.params["params"]["year"] not in [2017, 2012, 2002]:
                raise ValueError("Input year", self.params["params"]["year"], "is not valid.")
            
            elif self.params["params"]["year"] in [2017, 2012]:
                if self.params["params"]["EQ_level"] not in [1, 2]:
                    raise ValueError("Input EQ_level", self.params["params"]["EQ_level"], "is not valid.")
                elif self.params["params"]["EQ_level"]  == 2:
                    if self.params["params"]["EQ_type"] not in [1, 2]:
                        raise ValueError("Input EQ_type", self.params["params"]["EQ_type"], "is not valid.")
                
                if self.params["params"]["is_given_Khgl"] not in [True, False]:
                    raise ValueError("Input is_given_Khgl", self.params["params"]["is_given_Khgl"], "is not valid.")
                elif self.params["params"]["is_given_Khgl"] == True:
                    if self.params["params"]["Khgl"] is float:
                        raise ValueError("Khgl is not given.")
                else:
                    if self.params["params"]["regional_class"] not in ["A1", "A2", "B1", "B2", "C"]:
                        raise ValueError("Input regional_class", self.params["params"]["regional_class"], "is not valid.")
                    
                    if self.params["params"]["ground_type"] not in [1, 2, 3]:
                        raise ValueError("Input ground_type", self.params["params"]["ground_type"], "is not valid.")
                    
            elif self.params["params"]["year"] == 2002:
                warnings.warn("JRA2002の入力チェックは未実装です。")
            
            return None
    
    def _calculate_Khgl(self):        

        if self.params["params"]["year"] in [2017, 2012] and self.params["params"]["is_given_Khgl"] == False:
            
            Khgl0_list = [[0.12, 0.15, 0.18],  
                          [0.50, 0.45, 0.40],
                          [0.80, 0.70, 0.60]]
            
            Coeffs_list = [[1.0, 1.2, 1.0],
                           [1.0, 1.0, 1.0],
                           [0.85, 1.2, 0.85],
                           [0.85, 1.0, 0.85],
                           [0.7, 0.8, 0.7]]
            
            regional_class_list = ["A1", "A2", "B1", "B2", "C"]
            
            if self.params["params"]["EQ_level"] == 1:
                LT_index = 0
            elif self.params["params"]["EQ_level"] == 2 and self.params["params"]["EQ_type"] == 1:
                LT_index = 1
            elif self.params["params"]["EQ_level"] == 2 and self.params["params"]["EQ_type"] == 2:
                LT_index = 2
            
            regional_class_index = regional_class_list.index(self.params["params"]["regional_class"])
            
            
            self.params["params"]["Khgl"] = Khgl0_list[LT_index][self.params["params"]["ground_type"]-1] * Coeffs_list[regional_class_index][LT_index]
            
            print("Khgl:", self.params["params"]["Khgl"])
            
            return self.params["params"]
    
        elif self.params["params"]["year"] == 2002:
            warnings.warn("JRA2002のKhgl計算は未実装です。")
        
        return None

    def _check_AIJ_params(self):
        
        raise NotImplementedError("Method not implemented.")
    
    def _check_Idriss_and_Boulanger_params(self):
        
        raise NotImplementedError("Method not implemented.")