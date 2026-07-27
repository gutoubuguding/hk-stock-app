#!/usr/bin/env python3
"""
Script to remove Lombok annotations and add getter/setter methods to Java entities
"""
import os
import re

def remove_lombok_from_entity(file_path):
    """Remove @Data annotation and add getter/setter methods"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove @Data annotation
    content = content.replace('@Data\n', '')
    content = content.replace('import lombok.Data;\n', '')
    
    # Find the class name
    class_match = re.search(r'public class (\w+)', content)
    if not class_match:
        return
    
    class_name = class_match.group(1)
    
    # Find all fields
    field_pattern = r'private\s+(\w+(?:<[^>]+>)?)\s+(\w+);'
    fields = re.findall(field_pattern, content)
    
    # Generate getter/setter methods
    getter_setter_methods = []
    for field_type, field_name in fields:
        # Capitalize first letter for method name
        method_name = field_name[0].upper() + field_name[1:]
        
        # Getter
        getter = f"""
    public {field_type} get{method_name}() {{
        return {field_name};
    }}"""
        
        # Setter
        setter = f"""
    public void set{method_name}({field_type} {field_name}) {{
        this.{field_name} = {field_name};
    }}"""
        
        getter_setter_methods.append(getter)
        getter_setter_methods.append(setter)
    
    # Find the position to insert methods (before the closing brace)
    last_brace_pos = content.rfind('}')
    if last_brace_pos != -1:
        methods_code = '\n'.join(getter_setter_methods)
        content = content[:last_brace_pos] + methods_code + '\n' + content[last_brace_pos:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def remove_lombok_from_service(file_path):
    """Remove @Slf4j annotation and add logger"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove @Slf4j annotation
    content = content.replace('@Slf4j\n', '')
    content = content.replace('import lombok.extern.slf4j.Slf4j;\n', '')
    
    # Add logger import and field if not exists
    if 'private static final Logger log = LoggerFactory.getLogger' not in content:
        # Add import
        if 'import org.slf4j.Logger;' not in content:
            content = content.replace('import lombok.RequiredArgsConstructor;', 
                                    'import lombok.RequiredArgsConstructor;\nimport org.slf4j.Logger;\nimport org.slf4j.LoggerFactory;')
        
        # Add logger field after class declaration
        class_match = re.search(r'public class (\w+)', content)
        if class_match:
            class_name = class_match.group(1)
            logger_field = f'\n    private static final Logger log = LoggerFactory.getLogger({class_name}.class);\n'
            
            # Find the position to insert logger (after the class declaration line)
            class_line_end = content.find('{', content.find(f'public class {class_name}'))
            if class_line_end != -1:
                content = content[:class_line_end + 1] + logger_field + content[class_line_end + 1:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    base_path = r'C:\Users\34596\.openclaw\workspace\hk-stock-app\backend\src\main\java\com\hkstock'
    
    # Fix entities
    entity_path = os.path.join(base_path, 'entity')
    for filename in os.listdir(entity_path):
        if filename.endswith('.java'):
            file_path = os.path.join(entity_path, filename)
            print(f'Fixing entity: {filename}')
            remove_lombok_from_entity(file_path)
    
    # Fix services
    service_path = os.path.join(base_path, 'service')
    for filename in os.listdir(service_path):
        if filename.endswith('.java'):
            file_path = os.path.join(service_path, filename)
            print(f'Fixing service: {filename}')
            remove_lombok_from_service(file_path)

if __name__ == '__main__':
    main()
