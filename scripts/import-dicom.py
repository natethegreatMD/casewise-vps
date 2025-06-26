#!/usr/bin/env python3
"""
Script to import DICOM files into Orthanc
"""
import os
import requests
import time
import glob
from pathlib import Path

def wait_for_orthanc(url="https://dicom.casewisemd.org", max_retries=30):
    """Wait for Orthanc server to be ready."""
    print(f"Waiting for DICOM server at {url}...")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ DICOM server is ready at {url}")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"Attempt {attempt + 1}/{max_retries} - DICOM server not ready yet...")
        time.sleep(2)
    
    print(f"❌ DICOM server at {url} is not responding after {max_retries} attempts")
    return False

def import_dicom_files(orthanc_url="https://dicom.casewisemd.org", dicom_dir="./demo_cases"):
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