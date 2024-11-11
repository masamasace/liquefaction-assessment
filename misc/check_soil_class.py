import os
from pathlib import Path
import lxml.etree as ET
import openai

src_dir = "/Users/ms/Library/CloudStorage/OneDrive-nagaokaut.ac.jp/01_Research/08_Github/10_liquefaction_assessment/src"
src_dir = src_dir.replace("\\", "/")
src_dir = Path(src_dir).resolve()

# get all xml files in src directory
xml_files = sorted(list(src_dir.glob("*.XML")))

soil_class_name = []
soil_class_code = []

for xml_file in xml_files:

    # set parser with cp932 encoding
    parser = ET.XMLParser(encoding="cp932")

    # parse xml file
    tree = ET.parse(xml_file, parser=parser)

    # get soil class name
    temp_soil_class = tree.iter("岩石土区分_岩石土名")

    for soil_class in temp_soil_class:
        soil_class_name.append(soil_class.text)

    temp_soil_class_code = tree.iter("岩石土区分_岩石土記号")

    for soil_class_code_each in temp_soil_class_code:
        soil_class_code.append(soil_class_code_each.text)
    

soil_class_name = list(set(soil_class_name))
soil_class_code = list(set(soil_class_code))

# remove None
soil_class_name = [soil_class for soil_class in soil_class_name if soil_class is not None]
soil_class_code = [soil_class for soil_class in soil_class_code if soil_class is not None]

# sort
soil_class_name = sorted(soil_class_name)
soil_class_code = sorted(soil_class_code)

# replace "," with "、"
soil_class_name = [soil_class.replace(",", "、") for soil_class in soil_class_name]

for i, temp_soil_class_code in enumerate(soil_class_code):
    print(str(i).rjust(3, '0'), temp_soil_class_code)

print(soil_class_name)
# raise ValueError("End of script")

# set open ai api key
openai.api_key = os.environ.get("OPENAI_API_KEY")

sample_soil_class_dict = { "soil_type": ["表土", "シルト", "砂質シルト", "シルト質細砂",
                                         "微細砂", "細砂", "中砂", "粗砂", "砂礫"],
                           "gamma_sat": [17.0, 17.5, 18, 18, 18.5, 19.5, 20, 20, 21],
                           "gamma_wet": [15.0, 15.5, 16, 16, 16.5, 17.5, 18, 18, 19],
                           "D50": [0.02, 0.025, 0.04, 0.07, 0.1, 0.15, 0.35, 0.6, 2.0],
                           "Fc": [80, 75, 65, 50, 40, 30, 10, 0, 0]
                         }

# set prompt
client = openai.OpenAI()

response = client.chat.completions.create(
    model = "gpt-4o",
    messages = [
        {"role": "system", "content": "You are the best geotechnical engineer in the world. I am sending a sample soil class name and represetative physical properties. \
         By reffereing to the sample, please provide the sample values of gamma_sat, gamma_wet, D50, and Fc for the following given soil class names. Please provide only the values, without any explanation or discussion. \
         The output should be csv file format, with the following columns: soil_class_name, gamma_sat, gamma_wet, D50, Fc. Please estimate the values as accurately as possible. Blank values are basically not allowed. "},
        {"role": "system", "content": str(sample_soil_class_dict)},
        {"role": "user", "content": str(soil_class_name)},
    ],
    seed = 1
)

print(response.choices[0].message.content)

# save response to csv file
response_csv = response.choices[0].message.content
response_csv = response_csv.replace("\n", "\r\n")
response_csv = response_csv.replace("```", "")
response_csv = response_csv.replace("csv\r\n", "")

with open("./xml2liqmanifest/response.csv", "w") as f:
    f.write(response_csv)


raise ValueError("End of script")


# find longest string
max_len = 0
for soil_class in soil_class_name:
    if soil_class is not None and len(soil_class) > max_len:
        max_len = len(soil_class)

max_len += 5

default_soil_class_name = ["表土", "シルト", "細砂", "微細砂", "細砂", "中砂", "粗砂", "砂礫"]
sub1_soil_class_name = ["粘土質", "シルト質", "砂質", "礫質"]
sub2_soil_class_name = ["粘土混じり", "シルト混じり", "砂混じり", "礫混じり"]
other_soil_class_name = ["盛土", "コンクリート", "埋木", "有機質土", "耕作土", "表土"]

for i, soil_class in enumerate(soil_class_name):

    default_soil_class_index = -1
    sub1_soil_class_index = -1
    sub2_soil_class_index = -1
    other_soil_class_index = -1

    for default_soil_class in default_soil_class_name:
        if default_soil_class in soil_class:
            default_soil_class_index = default_soil_class_name.index(default_soil_class)
            break
    
    for sub1_soil_class in sub1_soil_class_name:
        if sub1_soil_class in soil_class:
            sub1_soil_class_index = sub1_soil_class_name.index(sub1_soil_class)
            break
    
    for sub2_soil_class in sub2_soil_class_name:
        if sub2_soil_class in soil_class:
            sub2_soil_class_index = sub2_soil_class_name.index(sub2_soil_class)
            break
    
    for other_soil_class in other_soil_class_name:
        if other_soil_class in soil_class:
            other_soil_class_index = other_soil_class_name.index(other_soil_class)
            break
    
    if soil_class in default_soil_class_name:
        print(str(i).rjust(3, '0'), soil_class)

    else:
        print(str(i).rjust(3, '*'), soil_class.ljust(max_len, " "), "その他")

