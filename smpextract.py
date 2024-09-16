import pandas as pd 
import os 
import shutil
import subprocess
import tempfile
from zipfile import ZipFile
from pathlib import Path

diary = pd.read_csv("./product-validation-diary.csv")
srcDir = "./results/PV_TheVersion"
destDir = "./dockerVolume/model_outputs"
selectedDir = "./dockerVolume/selected/SMP"

def prepare_docker_volume(srcDir, destDir):
    
    for item in os.listdir(srcDir):
        item_path = os.path.join(srcDir, item)
        dest_path = os.path.join(destDir, item)

        if os.path.isdir(item_path):
            shutil.copytree(item_path, dest_path, dirs_exist_ok=True)
        else:
            shutil.copy2(item_path, dest_path)

'''
check=True: Raises an exception if the command returns a non-zero exit code. a CalledProcessError exception will be raised
stdout=subprocess.PIPE and stderr=subprocess.PIPE: Capture the output and error messages.
text=True: Returns output as a string rather than bytes.
'''
def run_docker_compose():
    try:
        result = subprocess.run(
            ["docker-compose", "up", "-d"], 
            check=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, 
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")

def retrieve_for_annotation(test_ids):
    
    zip_file = "smp_annotation.zip"
    with ZipFile(zip_file, "w") as myzip:
        for _, row in test_ids.iterrows():
            test_id = row["test_id"]
            folder_path = os.path.join(selectedDir, test_id)
            if os.path.isdir(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = Path(root) / file
                        relative_path = os.path.relpath(file_path, start=folder_path)
                        myzip.write(file_path, arcname=os.path.join(test_id, relative_path))
            else:
                print(f"Directory {folder_path} does not exist.")
    print(f"Created zip file: {zip_file}")
        

if __name__ == "__main__":
    columns = ["Trial", "test_id"]
    filter = diary[diary["Status"] == "awaiting frame extraction"][columns]
    print(filter)
    prepare_docker_volume(srcDir, destDir)
    run_docker_compose()
    retrieve_for_annotation(filter)
    