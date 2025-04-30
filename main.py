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
    base_dir = "buoyantCavity"
    
    try:
        # 1. Изменяем файл 0/T
        t_file = base_dir + "/0/T"
        if os.path.exists("base_files/" + t_file):
            with open("base_files/" + t_file, 'r') as f:
                lines = f.readlines()
            
            for i in range(len(lines)):
                lines[i] = lines[i].replace('{{hot}}', str(params['hot']))
                lines[i] = lines[i].replace('{{cold}}', str(params['cold']))
                lines[i] = lines[i].replace('{{uniform}}', str(round((params['hot'] + params['cold']) / 2)))
            
            with open(t_file, 'w') as f:
                f.writelines(lines)
        else:
            print(f"Файл {t_file} не найден!")
            return False

        # 2. Изменяем system/blockMeshDict
        block_mesh_file = base_dir + "/system/blockMeshDict"
        if os.path.exists(block_mesh_file):
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
    
def run_solution():
    work_dir = os.curdir + "/buoyantCavity"
    commands = [
        "blockMesh",
        "foamRun > log",
        "paraFoam"
    ]
    
    for cmd in commands:
        process = subprocess.Popen(
            cmd,
            cwd=work_dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        print(f"Command: {cmd}")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        
        if process.returncode != 0:
            print(f"Error in command '{cmd}': Exit code {process.returncode}")
            break
    
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
        elif command == "run":
            run_solution()
        print("PEP")
    except:
        print(format_exc())