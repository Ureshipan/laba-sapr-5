import sys, os, subprocess
from traceback import format_exc

params = {
    "hot": 305,
    "cold": 295,
    "square": 100
}

def clean():
    subprocess.Popen("buoyantCavity/Clean.sh".split())
    
def write_files():
    base_dir = os.Path("buoyantCavity/")
    
    try:
        # 1. Изменяем файл 0/T
        t_file = base_dir + "/0/T"
        if t_file.exists():
            with open(t_file, 'r') as f:
                lines = f.readlines()
            
            # Меняем строки (нумерация с 0, поэтому 18, 19, 21 вместо 19, 20, 22)
            if len(lines) > 18:
                lines[18] = f"hot {params['hot']};\n"
            if len(lines) > 19:
                lines[19] = f"cold {params['cold']};\n"
            if len(lines) > 21:
                lines[21] = f"internalField uniform {round((params['hot'] - params['cold']) / 2)};\n"
            
            with open(t_file, 'w') as f:
                f.writelines(lines)
        else:
            print(f"Файл {t_file} не найден!")
            return False

        # 2. Изменяем system/blockMeshDict
        block_mesh_file = base_dir + "/system/blockMeshDict"
        if block_mesh_file.exists():
            with open(block_mesh_file, 'r') as f:
                lines = f.readlines()
            
            if len(lines) > 16:  
                lines[16] = f"b {params['square']};\n"
            
            with open(block_mesh_file, 'w') as f:
                f.writelines(lines)
        else:
            print(f"Файл {block_mesh_file} не найден!")
            return False

        print("changed")
        return True

    except Exception as e:
        print(f"Ошибка: {e}")
        return False
    
# Main loop
while True:
    try:
        command = input(">>").lower()
        if command == "exit":
            break
        elif command == "clean":
            clean()
        elif command == "write":
            write_files()
        print("PEP")
    except:
        print(format_exc())