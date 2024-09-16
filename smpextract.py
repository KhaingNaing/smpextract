import pandas as pd 
import os 
import shutil
import subprocess
from zipfile import ZipFile
from pathlib import Path
import argparse

def prepare_docker_volume(srcDir, destDir, test_ids):
    
    for root, dirnames, filenames in os.walk(srcDir):
        for dirname in dirnames:
            if dirname in test_ids:
                print(dirname)
                src_path = os.path.join(root, dirname)
                relative_path = os.path.relpath(src_path, start=srcDir)
                dest_path = os.path.join(destDir, relative_path)

                print("src: ", src_path)
                print("relative: ", relative_path)
                print("destination: ", dest_path)

                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)

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
        print(f"Error running docker-compose: {e.stderr}")

def retrieve_for_annotation(test_ids, selectedDir):
    
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
    
def main():
    parse = argparse.ArgumentParser(
        description="Extracting eye frame for SMP Annotation"
    )
    parse.add_argument(
        "csv_file", 
        type=str,
        help="Path to the product-validation-diary CSV file"
    )
    parse.add_argument(
        'option',
        choices=["prepare_docker_volume", "retrieve_for_annotation"],
        help="Option to perform: prepare_docker_volume or retrieve_for_annotation"
    )

    args = parse.parse_args()
    """Main function to execute the workflow."""
    path = args.csv_file
    task_to_perform = args.option
    try:
        diary = pd.read_csv(path)
    except FileNotFoundError:
        print("Error: The CSV file does not exist.")
        return
    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
        return
    except pd.errors.ParserError:
        print("Error: There was a parsing error with the CSV file.")
        return

    srcDir = "./results/PV_TheVersion"
    destDir = "./dockerVolume/model_outputs"
    selectedDir = "./dockerVolume/selected/SMP"
    columns = ["Trial", "test_id"]
    filter = diary[diary["Status"] == "awaiting frame extraction"][columns]
    print(filter)

    if task_to_perform == "prepare_docker_volume":
        prepare_docker_volume(srcDir, destDir, list(filter["test_id"]))
    elif task_to_perform == "retrieve_for_annotation":
        retrieve_for_annotation(filter, selectedDir)
    else:
        print("No Task to perform.")
        # run_docker_compose()

if __name__ == "__main__":
    main()
