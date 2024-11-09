import xml2liqmanifest as x2lm

temp_file_path = r"src\01_000701.XML"
temp = x2lm.LiquefactionManifest(file_path=temp_file_path)

params_JRA = {"year": 2017, 
              "EQ_level": 2, 
              "EQ_type": 1,
              "is_given_Khgl": False,
              "Khgl": 0.2,
              "regional_class": "C",
              "ground_type": 1,
              }

temp.set_method(method="JRA", params=params_JRA)