#!/usr/bin/env python3
"""
Script to import DICOM files into Orthanc
"""
import os
import requests
import time
import glob
from pathlib import Path

def wait_for_orthanc(url="http://localhost:8042", max_retries=30):
    """Wait for Orthanc to be ready"""
    for i in range(max_retries):
        try:
            response = requests.get(f"{url}/system", timeout=5)
            if response.status_code == 200:
                print("✅ Orthanc is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"⏳ Waiting for Orthanc... ({i+1}/{max_retries})")
        time.sleep(2)
    return False

def import_dicom_files(orthanc_url="http://localhost:8042", dicom_dir="./demo_cases"):
    """Import DICOM files into Orthanc"""
    if not wait_for_orthanc(orthanc_url):
        print("❌ Orthanc is not responding")
        return False
    
    # Find all DICOM files
    dicom_files = []
    for ext in ['*.dcm', '*.DCM']:
        dicom_files.extend(glob.glob(os.path.join(dicom_dir, '**', ext), recursive=True))
    
    if not dicom_files:
        print("❌ No DICOM files found in", dicom_dir)
        return False
    
    print(f"📁 Found {len(dicom_files)} DICOM files")
    
    # Import each file
    imported = 0
    for dicom_file in dicom_files:
        try:
            with open(dicom_file, 'rb') as f:
                response = requests.post(
                    f"{orthanc_url}/instances",
                    data=f.read(),
                    headers={'Content-Type': 'application/dicom'}
                )
                if response.status_code == 200:
                    imported += 1
                    print(f"✅ Imported: {os.path.basename(dicom_file)}")
                else:
                    print(f"❌ Failed to import: {os.path.basename(dicom_file)}")
        except Exception as e:
            print(f"❌ Error importing {dicom_file}: {e}")
    
    print(f"🎉 Successfully imported {imported}/{len(dicom_files)} files")
    return imported > 0

if __name__ == "__main__":
    import_dicom_files() 