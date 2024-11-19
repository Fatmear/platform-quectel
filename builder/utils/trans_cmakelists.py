import re  
  
def parse_cmake_minimum_required(content):  
    match = re.search(r'cmake_minimum_required\s*\(VERSION\s+(\d+)\.(\d+)\)', content)  
    if match:  
        return int(match.group(1)), int(match.group(2))  
    return None  
  
def parse_project_name(content):  
    match = re.search(r'project\s*\(([^)]+)\)', content)  
    if match:  
        return match.group(1).strip()  
    return None  
  
def find_exec(content):
    # 正则表达式模式：匹配 add_executable(...) 中的 ${...} 内容  
    pattern = r'add_executable\((.*?)\)'  
    inner_pattern = r'\$\{([^}]+)\}'  
    matches = []
    # 查找 add_executable(...) 块  
    match = re.search(pattern, content, re.DOTALL)  
    if match:  
        # 提取 add_executable(...) 块中的内容  
        inner_content = match.group(1)  
        
        # 查找所有 ${...} 之间的内容  
        matches = re.findall(inner_pattern, inner_content)  
        matches.remove("target")

    return matches

def extract_paths(content, kw, fpath):  
    find_paths = []  
    
    pattern = re.compile(kw)  
    matches = pattern.findall(content)  
      
    for match in matches:  
        # 匹配可能包含多个路径的情况，它们由空格分隔  
        paths = re.split(r'\n\s+', match.strip())  
        for path in paths:  
            if '#' in path:
                continue
            # 去除可能存在的变量替换标记，如 ${CMAKE_CURRENT_LIST_DIR}  
            cleaned_path = re.sub(r'\$\{[^}]+\}/..', '', path)  
            # 如果路径不是空的，就添加到列表中  
            if cleaned_path:  
                find_paths.append(fpath + cleaned_path)  
      
    return find_paths  
  
def parse_cmakelists(file_path, fpath):  
    with open(file_path, 'r') as file:  
        content = file.read()  
    
    cmake_info = {}

    cmake_min_required = parse_cmake_minimum_required(content)  
    project_name = parse_project_name(content)  

    # 匹配 list(APPEND include_files ...) 中的路径 
    include_files = extract_paths(content, r'list\(APPEND\s+include_files\s+([^)]+)\)', fpath)  

    # 匹配 list(APPEND ftp_include_file ...) 中的路径 
    include_files += extract_paths(content, r'list\(APPEND\s+ftp_include_file\s+([^)]+)\)', fpath)  

    # 匹配 list(APPEND ble_include_file ...) 中的路径 
    include_files += extract_paths(content, r'list\(APPEND\s+ble_include_file\s+([^)]+)\)', fpath)  

    cmake_info['include_files'] = include_files

    exec=find_exec(content)
    source_files = []
    cmake_info['execs'] = {}
    for i in exec:
        # 匹配 list(APPEND quectel_demo_source_file ...) 中的路径 
        source_file = extract_paths(content, r'list\(APPEND\s'+i+'\s+([^)]+)\)', fpath)  
        cmake_info['execs'][i] = source_file
        source_files += source_file

    cmake_info['source_files'] = source_files

    return cmake_info
