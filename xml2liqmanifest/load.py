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
    def _load_xml(self, xml_encoding = "cp932"):
        """
        XMLファイルからボーリングデータを読み込む
        
        Parameters
        ----------
        xml_encoding : str, optional
            XMLファイルのエンコーディング, by default "cp932"
            
        Returns
        -------
        dict
            ボーリングデータを格納した辞書
        """
        try:
            content_bytes = self._read_and_preprocess_file(xml_encoding)
            tree = self._parse_xml_content(content_bytes)
            data = self._extract_borehole_data(tree)
            return data
        except Exception as e:
            raise Exception(f"XMLデータの読み込み処理全体で失敗: {str(e)}")
    
    def _read_and_preprocess_file(self, xml_encoding):
        """
        XMLファイルを読み込み、CP932文字を置換する
        
        Parameters
        ----------
        xml_encoding : str
            XMLファイルのエンコーディング
            
        Returns
        -------
        bytes
            前処理済みのXMLコンテンツのバイト列
        """
        try:
            # CP932固有の文字をShift-JISで表現可能な文字に置換するマッピング
            replacements = {
                '㎜': 'mm', '㎝': 'cm', '㎞': 'km', '髙': '高', 
                '﨑': '崎', '德': '徳', '濵': '浜', '瀨': '瀬', 
                '槗': '橋', '遠': '遠', '俣': '俣', '黑': '黒',
                '戶': '戸', '邊': '辺', '沢': '澤', '～': '~',
                '－': '-', '№': 'No', '㈱': '(株)', '㈲': '(有)',
            }
            
            # ファイルを読み込んでCP932の文字をShift-JISに置換
            with open(self.params["path"], 'r', encoding=xml_encoding) as f:
                content = f.read()
                
            # CP932固有の文字を置換
            for old, new in replacements.items():
                content = content.replace(old, new)
            
            # 置換後の文字列をバイト列に変換して返す
            return content.encode("shift_jis")
        except UnicodeError as e:
            raise Exception(f"ファイルのエンコーディングエラー: {str(e)}")
        except IOError as e:
            raise Exception(f"ファイルの読み込みエラー: {str(e)}")
        except Exception as e:
            raise Exception(f"ファイルの前処理中にエラー: {str(e)}")
    
    def _parse_xml_content(self, content_bytes):
        """
        XMLコンテンツをパースしてElementTreeを生成
        
        Parameters
        ----------
        content_bytes : bytes
            パース対象のXMLコンテンツのバイト列
            
        Returns
        -------
        ElementTree
            パース済みのXML ElementTree
        """
        try:
            parser = ET.XMLParser(encoding="shift_jis", huge_tree=True, recover=True)
            tree = ET.fromstring(content_bytes, parser=parser).getroottree()
            return tree
        except ET.ParseError as e:
            raise Exception(f"XMLパースエラー: {str(e)}")
        except Exception as e:
            raise Exception(f"XMLパース中に予期せぬエラー: {str(e)}")
    
    def _extract_borehole_data(self, tree):
        """
        XML ElementTreeからボーリングデータを抽出
        
        Parameters
        ----------
        tree : ElementTree
            パース済みのXML ElementTree
            
        Returns
        -------
        dict
            ボーリングデータを格納した辞書
        """
        try:
            root = tree.getroot()
            data = {}
            
            # parse lat and lon
            data["lat"], data["lon"] = self._load_xml_lat_lon(tree)
            
            # parse start date of borehole investigation
            data["start_date"] = self._load_xml_start_date(tree)
            
            # parse borehole info
            data["tip_elevation"] = self._load_xml_tip_elevation(tree)
            
            # parse total depth
            total_depth_elem = root.find(".//総削孔長")
            if total_depth_elem is None or total_depth_elem.text is None:
                total_depth_elem = root.find(".//総掘進長")
            if total_depth_elem is not None and total_depth_elem.text is not None:
                data["total_depth"] = float(total_depth_elem.text)
            else:
                warnings.warn("総削孔長 / 総掘進長の値が見つかりませんでした。")
                
            # parse ground water level
            water_level_elem = root.find(".//孔内水位/孔内水位_孔内水位")
            if water_level_elem is not None and water_level_elem.text is not None:
                try:
                    data["ground_water_level"] = float(water_level_elem.text)
                except ValueError:
                    data["ground_water_level"] = None
                    warnings.warn(f"孔内水位の値が無効です: {water_level_elem.text}")
            else:
                data["ground_water_level"] = None
            
            # parse soil layer info 
            data["soil_layers"] = self._load_xml_soil_layers(tree)
            
            # parse observation note info
            data["observation_note"] = self._load_xml_observation_note(tree)
            
            # parse SPT data
            data["SPT"] = self._load_xml_SPT(tree)
            
            return data
        except ValueError as e:
            raise Exception(f"データの型変換エラー: {str(e)}")
        except Exception as e:
            raise Exception(f"ボーリングデータ抽出中にエラー: {str(e)}")
        
    def _load_xml_lat_lon(self, tree):
        """
        緯度経度情報を読み込む
        
        Parameters
        ----------
        tree : ElementTree
            解析済みのXML ElementTree
            
        Returns
        -------
        tuple
            (緯度, 経度)のタプル
        """
        try:
            # find lat and lon info
            lat_deg = tree.find(".//緯度_度").text
            lat_min = tree.find(".//緯度_分").text
            lat_sec = tree.find(".//緯度_秒").text
            
            lon_deg = tree.find(".//経度_度").text
            lon_min = tree.find(".//経度_分").text
            lon_sec = tree.find(".//経度_秒").text
            
            if lat_deg is None or lat_min is None or lat_sec is None:
                warnings.warn("緯度情報が見つかりませんでした。")
                return None, None
            if lon_deg is None or lon_min is None or lon_sec is None:
                warnings.warn("経度情報が見つかりませんでした。")
                return None, None
        
            lat = float(lat_deg) + float(lat_min) / 60 + float(lat_sec) / 3600
            lon = float(lon_deg) + float(lon_min) / 60 + float(lon_sec) / 3600
        
            return lat, lon
            
        except Exception as e:
            warnings.warn(f"緯度経度の変換中にエラーが発生しました: {str(e)}")
            return None, None

    def _load_xml_start_date(self, tree):
        """
        調査開始日を読み込む
        
        Parameters
        ----------
        tree : ElementTree
            解析済みのXML ElementTree
            
        Returns
        -------
        str
            調査開始日
        """
        try:
            start_date = tree.find(".//調査期間_開始年月日").text
            
            if start_date is None:
                warnings.warn("調査開始日が見つかりませんでした。")
                return None
                
            return start_date
            
        except Exception as e:
            warnings.warn(f"調査開始日の読み込み中にエラーが発生しました: {str(e)}")
            return None

    def _load_xml_tip_elevation(self, tree):
        """
        孔口標高を読み込む
        
        Parameters
        ----------
        tree : ElementTree
            解析済みのXML ElementTree
            
        Returns
        -------
        float
            孔口標高
        """
        try:
            tip_elevation_text = tree.find(".//孔口標高").text
            
            if tip_elevation_text is None:
                warnings.warn("孔口標高が見つかりませんでした。")
                return None
                
            return float(tip_elevation_text)
            
        except Exception as e:
            warnings.warn(f"孔口標高の読み込み中にエラーが発生しました: {str(e)}")
            return None

    def _load_xml_soil_layers(self, tree):
        """
        土質区分情報を読み込む
        
        Parameters
        ----------
        tree : ElementTree
            解析済みのXML ElementTree
            
        Returns
        -------
        list
            土質区分情報のリスト
        """
        try:
            soil_layers = []
            
            # possible tags are: 岩石土区分, 工学的地質区分名現場土質名
            possible_tags = ["工学的地質区分名現場土質名", "岩石土区分"]
            found_tag = None
            for tag in possible_tags:
                if tree.find(f".//{tag}") is not None:
                    found_tag = tag
                    break
            
            if found_tag is None:
                raise ValueError("土質区分の情報が見つかりませんでした。")
                
            # prepare detail tags 
            if found_tag == "工学的地質区分名現場土質名":
                depth_tag = "工学的地質区分名現場土質名_下端深度"
                class_name_tag = "工学的地質区分名現場土質名_工学的地質区分名現場土質名"
                class_code_tag = "工学的地質区分名現場土質名_工学的地質区分名現場土質名記号"
            else:  # 岩石土区分
                depth_tag = "岩石土区分_下端深度"
                class_name_tag = "岩石土区分_岩石土名"
                class_code_tag = "岩石土区分_岩石土記号"
                            
            for soil_layer in tree.findall(f".//{found_tag}"):
                try:
                    layer = {
                        "depth": float(soil_layer.find(f".//{depth_tag}").text),
                        "class_name": soil_layer.find(f".//{class_name_tag}").text,
                        "class_code": soil_layer.find(f".//{class_code_tag}").text,
                    }
                    soil_layers.append(layer)
                except (AttributeError, TypeError, ValueError) as e:
                    warnings.warn(f"土層データの解析中にエラーが発生しました: {str(e)}")
                    continue
            
            if not soil_layers:
                warnings.warn("有効な土質区分情報が見つかりませんでした。")
                return None
            
            return soil_layers
            
        except Exception as e:
            warnings.warn(f"土質区分情報の読み込み中にエラーが発生しました: {str(e)}")
            return None

    def _load_xml_observation_note(self, tree):
        """
        観察記事を読み込む
        
        Parameters
        ----------
        tree : ElementTree
            解析済みのXML ElementTree
            
        Returns
        -------
        list
            観察記事のリスト
        """
        try:
            observation_notes = []
            
            for observation_note in tree.findall(".//観察記事"):
                try:
                    note = {
                        "upper_depth": float(observation_note.find("観察記事_上端深度").text),
                        "lower_depth": float(observation_note.find("観察記事_下端深度").text),
                        "note": observation_note.find("観察記事_記事").text,
                    }
                    observation_notes.append(note)
                except (AttributeError, TypeError, ValueError) as e:
                    warnings.warn(f"観察記事データの解析中にエラーが発生しました: {str(e)}")
                    continue
                
            if not observation_notes:
                warnings.warn("観察記事が見つかりませんでした。")
                return None
            
            return observation_notes
            
        except Exception as e:
            warnings.warn(f"観察記事の読み込み中にエラーが発生しました: {str(e)}")
            return None
    
    def _detect_spt_intervals(self, spt):
        """
        標準貫入試験の区間情報を検出する
        
        Parameters
        ----------
        spt : Element
            標準貫入試験要素
            
        Returns
        -------
        list
            検出された区間のリスト（例：["0_10", "10_20", "20_30"] or ["0_100", "100_200", "200_300"]）
        """
        intervals = []
        # すべての子要素をチェック
        for elem in spt:
            # 打撃回数のタグを探す
            if "打撃回数" in elem.tag:
                # タグから区間部分を抽出（例：標準貫入試験_0_10打撃回数 → 0_10）
                interval = elem.tag.replace("標準貫入試験_", "").replace("打撃回数", "")
                intervals.append(interval)
        return sorted(intervals) if intervals else ["0_100", "100_200", "200_300"]

    def _load_xml_SPT(self, tree):
        """
        標準貫入試験データを読み込む
        
        Parameters
        ----------
        tree : ElementTree
            解析済みのXML ElementTree
            
        Returns
        -------
        list
            標準貫入試験データのリスト
        """
        try:
            SPTs = []
            
            for spt in tree.findall(".//標準貫入試験"):
                try:
                    # 区間情報を検出
                    intervals_tags = self._detect_spt_intervals(spt)
                    
                    # 各区間のデータを取得
                    intervals = []
                    for interval in intervals_tags:
                        hits = spt.find(f"標準貫入試験_{interval}打撃回数")
                        penetration = spt.find(f"標準貫入試験_{interval}貫入量")
                        
                        if hits is not None and penetration is not None:
                            # 貫入量をmm単位に変換
                            penetration_value = float(penetration.text)
                            if "_10" in interval or "_20" in interval or "_30" in interval:
                                # cm単位の場合、mm単位に変換
                                penetration_value *= 10
                                
                            intervals.append({
                                "hits": int(hits.text),
                                "penetration": penetration_value
                            })
                    
                    # 合計値を取得
                    # 合計貫入量を取得し、必要に応じて単位を変換
                    total_penetration = float(spt.find("標準貫入試験_合計貫入量").text)
                    # 区間がcm単位の場合は合計もcm単位とみなす
                    if any("_10" in i or "_20" in i or "_30" in i for i in intervals_tags):
                        total_penetration *= 10
                    
                    test_data = {
                        "depth": float(spt.find("標準貫入試験_開始深度").text),
                        "total_hits": int(spt.find("標準貫入試験_合計打撃回数").text),
                        "total_penetration": total_penetration,
                        "intervals": intervals
                    }
                    SPTs.append(test_data)
                    
                except (AttributeError, TypeError, ValueError) as e:
                    warnings.warn(f"標準貫入試験データの解析中にエラーが発生しました: {str(e)}")
                    continue
            
            if not SPTs:
                warnings.warn("標準貫入試験データが見つかりませんでした。")
                return None
                
            return SPTs
            
        except Exception as e:
            warnings.warn(f"標準貫入試験データの読み込み中にエラーが発生しました: {str(e)}")
            return None
        
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
