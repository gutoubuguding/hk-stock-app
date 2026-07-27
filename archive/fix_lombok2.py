#!/usr/bin/env python3
"""Replace @RequiredArgsConstructor with @Autowired field injection"""
import os
import re

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if no @RequiredArgsConstructor
    if '@RequiredArgsConstructor' not in content:
        return
    
    # Remove @RequiredArgsConstructor and import
    content = content.replace('@RequiredArgsConstructor\n', '')
    content = content.replace('import lombok.RequiredArgsConstructor;\n', '')
    
    # Add @Autowired import if not present
    if 'import org.springframework.beans.factory.annotation.Autowired;' not in content:
        # Find a good place to insert import
        if 'import org.springframework.stereotype.' in content:
            content = content.replace(
                'import org.springframework.stereotype.',
                'import org.springframework.beans.factory.annotation.Autowired;\nimport org.springframework.stereotype.'
            )
        elif 'import org.springframework.web.bind.annotation' in content:
            content = content.replace(
                'import org.springframework.web.bind.annotation',
                'import org.springframework.beans.factory.annotation.Autowired;\nimport org.springframework.web.bind.annotation'
            )
    
    # Change 'private final' to 'private @Autowired' for service/mapper fields
    content = re.sub(
        r'private final (\w+)\s+(\w+);',
        r'private @Autowired \1 \2;',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Fixed: {os.path.basename(file_path)}')

def main():
    base = r'C:\Users\34596\.openclaw\workspace\hk-stock-app\backend\src\main\java\com\hkstock'
    for subdir in ['controller', 'service', 'task']:
        path = os.path.join(base, subdir)
        for f in os.listdir(path):
            if f.endswith('.java'):
                fix_file(os.path.join(path, f))

if __name__ == '__main__':
    main()
