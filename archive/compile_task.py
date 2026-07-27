"""
Compile and update ScheduledTasks.class in the hk-stock-app JAR
"""
import zipfile
import os
import subprocess
import shutil

BASE_DIR = "C:/Users/34596/.openclaw/workspace/hk-stock-app/backend"
SRC_FILE = BASE_DIR + "/src/main/java/com/hkstock/task/ScheduledTasks.java"
JAR_FILE = BASE_DIR + "/target/hk-stock-app-1.0.0.jar"
JAVAC = "C:/Program Files/Java/latest/jdk-25/bin/javac.exe"

LIBS_DIR = BASE_DIR + "/target/boot-libs"
CLASSES_DIR = BASE_DIR + "/target/boot-classes"

def main():
    print("=== 1. Extract fat JAR for dependencies ===")
    os.makedirs(LIBS_DIR, exist_ok=True)
    os.makedirs(CLASSES_DIR, exist_ok=True)
    
    with zipfile.ZipFile(JAR_FILE, 'r') as zf:
        for name in zf.namelist():
            if name.startswith('BOOT-INF/lib/') and not name.endswith('/'):
                out_path = os.path.join(LIBS_DIR, name[14:])
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with zf.open(name) as src, open(out_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
            elif name.startswith('BOOT-INF/classes/') and not name.endswith('/'):
                out_path = os.path.join(CLASSES_DIR, name[17:])
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with zf.open(name) as src, open(out_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
    
    jar_count = len([f for f in os.listdir(LIBS_DIR) if f.endswith('.jar')])
    print(f"  Extracted {jar_count} JARs to boot-libs")
    
    # Build classpath
    cp_parts = [CLASSES_DIR]
    for jar in os.listdir(LIBS_DIR):
        if jar.endswith('.jar'):
            cp_parts.append(os.path.join(LIBS_DIR, jar))
    classpath = ';'.join(cp_parts)
    
    print(f"\n=== 2. Compile ScheduledTasks.java (target Java 21) ===")
    result = subprocess.run(
        [JAVAC, '-encoding', 'UTF-8', '-source', '21', '-target', '21', '-cp', classpath, '-d', CLASSES_DIR, SRC_FILE],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"  COMPILATION FAILED:\n{result.stderr}")
        return
    print(f"  Compilation successful!")
    
    # Find compiled class - check both possible locations
    possible_paths = [
        os.path.join(CLASSES_DIR, 'com', 'hkstock', 'task', 'ScheduledTasks.class'),
        os.path.join(BASE_DIR, 'target', 'classes', 'com', 'hkstock', 'task', 'ScheduledTasks.class'),
    ]
    class_out = None
    for p in possible_paths:
        if os.path.exists(p):
            class_out = p
            break
    
    if not class_out:
        print(f"  ERROR: Compiled .class file not found!")
        print(f"  Searched in: {possible_paths}")
        # List what was actually compiled
        for root, dirs, files in os.walk(CLASSES_DIR):
            for f in files:
                if 'Scheduled' in f:
                    print(f"  Found: {os.path.join(root, f)}")
        for root, dirs, files in os.walk(os.path.join(BASE_DIR, 'target', 'classes')):
            for f in files:
                if 'Scheduled' in f:
                    print(f"  Found: {os.path.join(root, f)}")
        return
    
    print(f"  Class file: {class_out} ({os.path.getsize(class_out)} bytes)")
    
    print(f"\n=== 3. Update fat JAR ===")
    with open(class_out, 'rb') as f:
        new_class_data = f.read()
    
    # Rewrite JAR with updated class
    temp_jar = JAR_FILE + '.updating.tmp'
    with zipfile.ZipFile(JAR_FILE, 'r') as zf_in:
        with zipfile.ZipFile(temp_jar, 'w', zipfile.ZIP_DEFLATED) as zf_out:
            for item in zf_in.infolist():
                if item.filename == 'BOOT-INF/classes/com/hkstock/task/ScheduledTasks.class':
                    zf_out.writestr(item, new_class_data)
                    print(f"  Updated: {item.filename}")
                elif item.filename == 'com/hkstock/task/ScheduledTasks.class':
                    zf_out.writestr(item, new_class_data)
                    print(f"  Updated: {item.filename}")
                elif item.filename == 'ScheduledTasks.class':
                    zf_out.writestr(item, new_class_data)
                    print(f"  Updated: {item.filename}")
                else:
                    zf_out.writestr(item, zf_in.read(item.filename))
    
    os.replace(temp_jar, JAR_FILE)
    new_size = os.path.getsize(JAR_FILE)
    print(f"  JAR updated: {JAR_FILE} ({new_size/1024/1024:.1f} MB)")
    print(f"\n=== DONE ===")
    print(f"Restart Java backend to apply changes")

if __name__ == '__main__':
    main()
