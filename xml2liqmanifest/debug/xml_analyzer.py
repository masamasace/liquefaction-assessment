from bs4 import BeautifulSoup

def read_and_print_xml(file_path):
    try:
        with open(file_path, 'rb') as file:
            content = file.read().decode("cp932")
            soup = BeautifulSoup(content, 'lxml-xml')
            print(soup.prettify())
    except FileNotFoundError:
        print(f"Error: {file_path} が見つかりません。")
    except Exception as e:
        print(f"Error: {str(e)}")

# 使用例
read_and_print_xml('ref/01_002611.XML')
