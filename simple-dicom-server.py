#!/usr/bin/env python3
"""
Simple DICOMweb server that serves DICOM files directly from demo_cases directory.
This provides a lightweight alternative to the Docker-based DICOMweb server.
"""

import os
import json
import glob
from pathlib import Path
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import pydicom
from datetime import datetime

app = Flask(__name__)
# Configure CORS for production domains
CORS(app, origins=[
    'https://app.casewisemd.org',
    'https://viewer.casewisemd.org', 
    'https://api.casewisemd.org',
    'https://casewisemd.org',
    'https://www.casewisemd.org',
    # Keep localhost for development
    'http://localhost:3000',
    'http://localhost:5173',
    'http://localhost:8001',
    'http://localhost:8081'
])

# Configuration
DEMO_CASES_DIR = "demo_cases"
PORT = 8042

def dicom_to_json(ds):
    """Convert DICOM dataset to DICOMweb JSON format."""
    result = {}
    
    # Add required DICOM tags in proper DICOMweb JSON format
    for elem in ds:
        if elem.tag == (0x7FE0, 0x0010):  # Skip pixel data
            continue
            
        tag_str = f"{elem.tag.group:04X}{elem.tag.element:04X}"
        
        try:
            # Handle different VR types properly
            if elem.VR in ['FL', 'FD']:  # Float types
                if hasattr(elem.value, '__len__') and not isinstance(elem.value, str):
                    # MultiValue - convert each value
                    values = [float(v) for v in elem.value]
                else:
                    # Single value
                    values = [float(elem.value)]
            elif elem.VR in ['SL', 'SS', 'UL', 'US']:  # Integer types
                if hasattr(elem.value, '__len__') and not isinstance(elem.value, str):
                    # MultiValue - convert each value
                    values = [int(v) for v in elem.value]
                else:
                    # Single value
                    values = [int(elem.value)]
            elif elem.VR == 'DS':  # Decimal String
                if hasattr(elem.value, '__len__') and not isinstance(elem.value, str):
                    # MultiValue - convert each value to string then float
                    values = [float(str(v)) for v in elem.value]
                else:
                    # Single value
                    values = [float(str(elem.value))]
            elif elem.VR == 'IS':  # Integer String
                if hasattr(elem.value, '__len__') and not isinstance(elem.value, str):
                    # MultiValue - convert each value to string then int
                    values = [int(str(v)) for v in elem.value]
                else:
                    # Single value
                    values = [int(str(elem.value))]
            else:
                # String types and others
                if hasattr(elem.value, '__len__') and not isinstance(elem.value, str):
                    # MultiValue - convert each value to string
                    values = [str(v) for v in elem.value]
                else:
                    # Single value
                    values = [str(elem.value)]
            
            result[tag_str] = {
                "vr": elem.VR,
                "Value": values
            }
            
        except (ValueError, TypeError, AttributeError) as e:
            # If conversion fails, store as string
            print(f"Warning: Could not convert {tag_str} ({elem.VR}): {e}")
            try:
                if hasattr(elem.value, '__len__') and not isinstance(elem.value, str):
                    values = [str(v) for v in elem.value]
                else:
                    values = [str(elem.value)]
                result[tag_str] = {
                    "vr": elem.VR,
                    "Value": values
                }
            except Exception as e2:
                print(f"Error: Could not process {tag_str}: {e2}")
                continue
    
    return result

def get_dicom_files():
    """Scan demo_cases directory for DICOM files."""
    dicom_files = []
    
    for case_dir in Path(DEMO_CASES_DIR).glob("*"):
        if case_dir.is_dir():
            case_id = case_dir.name
            for dcm_file in case_dir.rglob("*.dcm"):
                try:
                    # Read DICOM metadata
                    ds = pydicom.dcmread(str(dcm_file))
                    
                    # Extract study info
                    study_instance_uid = getattr(ds, 'StudyInstanceUID', 'unknown')
                    series_instance_uid = getattr(ds, 'SeriesInstanceUID', 'unknown')
                    sop_instance_uid = getattr(ds, 'SOPInstanceUID', 'unknown')
                    
                    # Get relative path from demo_cases
                    rel_path = dcm_file.relative_to(DEMO_CASES_DIR)
                    
                    dicom_files.append({
                        'case_id': case_id,
                        'file_path': str(rel_path),
                        'study_instance_uid': study_instance_uid,
                        'series_instance_uid': series_instance_uid,
                        'sop_instance_uid': sop_instance_uid,
                        'file_size': dcm_file.stat().st_size,
                        'modality': getattr(ds, 'Modality', 'unknown'),
                        'study_date': getattr(ds, 'StudyDate', ''),
                        'patient_name': str(getattr(ds, 'PatientName', 'Unknown')),
                        'dataset': ds  # Store the full dataset for metadata
                    })
                except Exception as e:
                    print(f"Error reading {dcm_file}: {e}")
                    continue
    
    return dicom_files

@app.route('/studies', methods=['GET'])
def get_studies():
    """Get list of studies (DICOMweb QIDO-RS)."""
    try:
        dicom_files = get_dicom_files()
        
        # Group by study
        studies = {}
        for file_info in dicom_files:
            study_uid = file_info['study_instance_uid']
            if study_uid not in studies:
                # Get one dataset from this study for metadata
                ds = file_info['dataset']
                
                # Create DICOMweb JSON format
                study_json = {
                    "0020000D": {"vr": "UI", "Value": [study_uid]},  # StudyInstanceUID
                    "00080020": {"vr": "DA", "Value": [file_info['study_date']]},  # StudyDate
                    "00100010": {"vr": "PN", "Value": [{"Alphabetic": file_info['patient_name']}]},  # PatientName
                    "00100020": {"vr": "LO", "Value": [getattr(ds, 'PatientID', 'Unknown')]},  # PatientID
                    "00200010": {"vr": "SH", "Value": [getattr(ds, 'StudyID', '')]},  # StudyID
                    "00081030": {"vr": "LO", "Value": [getattr(ds, 'StudyDescription', '')]},  # StudyDescription
                    "00080061": {"vr": "CS", "Value": []},  # ModalitiesInStudy
                    "00201206": {"vr": "IS", "Value": [0]},  # NumberOfStudyRelatedSeries
                    "00201208": {"vr": "IS", "Value": [0]},  # NumberOfStudyRelatedInstances
                }
                
                studies[study_uid] = {
                    'json': study_json,
                    'series': {},
                    'modalities': set()
                }
            
            # Count series and instances
            series_uid = file_info['series_instance_uid']
            if series_uid not in studies[study_uid]['series']:
                studies[study_uid]['series'][series_uid] = {
                    'instances': []
                }
                studies[study_uid]['json']["00201206"]["Value"][0] += 1  # Increment series count
            
            studies[study_uid]['series'][series_uid]['instances'].append(file_info)
            studies[study_uid]['json']["00201208"]["Value"][0] += 1  # Increment instance count
            studies[study_uid]['modalities'].add(file_info['modality'])
        
        # Update modalities in study
        for study_uid, study_data in studies.items():
            study_data['json']["00080061"]["Value"] = list(study_data['modalities'])
        
        # Convert to list format expected by OHIF
        study_list = [study_data['json'] for study_data in studies.values()]
        
        return jsonify(study_list)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/studies/<study_uid>/series', methods=['GET'])
def get_series(study_uid):
    """Get series for a specific study."""
    try:
        dicom_files = get_dicom_files()
        
        # Filter by study
        study_files = [f for f in dicom_files if f['study_instance_uid'] == study_uid]
        
        # Group by series
        series = {}
        for file_info in study_files:
            series_uid = file_info['series_instance_uid']
            if series_uid not in series:
                # Get one dataset from this series for metadata
                ds = file_info['dataset']
                
                # Create DICOMweb JSON format
                series_json = {
                    "0020000E": {"vr": "UI", "Value": [series_uid]},  # SeriesInstanceUID
                    "00080060": {"vr": "CS", "Value": [file_info['modality']]},  # Modality
                    "00200011": {"vr": "IS", "Value": [getattr(ds, 'SeriesNumber', 1)]},  # SeriesNumber
                    "0008103E": {"vr": "LO", "Value": [getattr(ds, 'SeriesDescription', '')]},  # SeriesDescription
                    "00201209": {"vr": "IS", "Value": [0]},  # NumberOfSeriesRelatedInstances
                }
                
                series[series_uid] = {
                    'json': series_json,
                    'instances': []
                }
            
            series[series_uid]['instances'].append(file_info)
            series[series_uid]['json']["00201209"]["Value"][0] += 1  # Increment instance count
        
        series_list = [series_data['json'] for series_data in series.values()]
        return jsonify(series_list)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/studies/<study_uid>/series/<series_uid>/instances', methods=['GET'])
def get_instances(study_uid, series_uid):
    """Get instances for a specific series."""
    try:
        dicom_files = get_dicom_files()
        
        # Filter by study and series
        instances = []
        for file_info in dicom_files:
            if (file_info['study_instance_uid'] == study_uid and 
                file_info['series_instance_uid'] == series_uid):
                
                ds = file_info['dataset']
                
                # Create DICOMweb JSON format
                instance_json = {
                    "00080018": {"vr": "UI", "Value": [file_info['sop_instance_uid']]},  # SOPInstanceUID
                    "00080016": {"vr": "UI", "Value": [getattr(ds, 'SOPClassUID', '')]},  # SOPClassUID
                    "00200013": {"vr": "IS", "Value": [getattr(ds, 'InstanceNumber', 1)]},  # InstanceNumber
                    "00280010": {"vr": "US", "Value": [getattr(ds, 'Rows', 512)]},  # Rows
                    "00280011": {"vr": "US", "Value": [getattr(ds, 'Columns', 512)]},  # Columns
                    "00280100": {"vr": "US", "Value": [getattr(ds, 'BitsAllocated', 16)]},  # BitsAllocated
                    "00280101": {"vr": "US", "Value": [getattr(ds, 'BitsStored', 16)]},  # BitsStored
                    "00280102": {"vr": "US", "Value": [getattr(ds, 'HighBit', 15)]},  # HighBit
                    "00280103": {"vr": "US", "Value": [getattr(ds, 'PixelRepresentation', 0)]},  # PixelRepresentation
                }
                
                # Add optional fields if they exist
                if hasattr(ds, 'ImagePositionPatient'):
                    instance_json["00200032"] = {"vr": "DS", "Value": [float(x) for x in ds.ImagePositionPatient]}
                if hasattr(ds, 'ImageOrientationPatient'):
                    instance_json["00200037"] = {"vr": "DS", "Value": [float(x) for x in ds.ImageOrientationPatient]}
                if hasattr(ds, 'PixelSpacing'):
                    instance_json["00280030"] = {"vr": "DS", "Value": [float(x) for x in ds.PixelSpacing]}
                if hasattr(ds, 'SliceThickness'):
                    instance_json["00180050"] = {"vr": "DS", "Value": [float(ds.SliceThickness)]}
                if hasattr(ds, 'WindowCenter'):
                    if isinstance(ds.WindowCenter, (list, tuple)):
                        instance_json["00281050"] = {"vr": "DS", "Value": [float(x) for x in ds.WindowCenter]}
                    else:
                        instance_json["00281050"] = {"vr": "DS", "Value": [float(ds.WindowCenter)]}
                if hasattr(ds, 'WindowWidth'):
                    if isinstance(ds.WindowWidth, (list, tuple)):
                        instance_json["00281051"] = {"vr": "DS", "Value": [float(x) for x in ds.WindowWidth]}
                    else:
                        instance_json["00281051"] = {"vr": "DS", "Value": [float(ds.WindowWidth)]}
                
                instances.append(instance_json)
        
        return jsonify(instances)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/studies/<study_uid>/series/<series_uid>/metadata', methods=['GET'])
def get_series_metadata(study_uid, series_uid):
    """Get metadata for all instances in a series."""
    try:
        dicom_files = get_dicom_files()
        
        # Filter by study and series
        metadata_list = []
        for file_info in dicom_files:
            if (file_info['study_instance_uid'] == study_uid and 
                file_info['series_instance_uid'] == series_uid):
                
                ds = file_info['dataset']
                metadata_json = dicom_to_json(ds)
                metadata_list.append(metadata_json)
        
        return jsonify(metadata_list)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/wado/<case_id>/<path:file_path>', methods=['GET'])
def serve_dicom_file(case_id, file_path):
    """Serve DICOM file (WADO-URI)."""
    try:
        full_path = os.path.join(DEMO_CASES_DIR, case_id, file_path)
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            full_path,
            mimetype='application/dicom',
            as_attachment=False
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dicom-web/studies/<study_uid>/series/<series_uid>/instances/<instance_uid>', methods=['GET'])
def serve_instance_wado_rs(study_uid, series_uid, instance_uid):
    """Serve DICOM instance (WADO-RS) - proper DICOMweb endpoint."""
    try:
        dicom_files = get_dicom_files()
        
        # Find the file for this instance
        for file_info in dicom_files:
            if (file_info['study_instance_uid'] == study_uid and
                file_info['series_instance_uid'] == series_uid and
                file_info['sop_instance_uid'] == instance_uid):
                
                full_path = os.path.join(DEMO_CASES_DIR, file_info['file_path'])
                
                if not os.path.exists(full_path):
                    return jsonify({'error': 'File not found'}), 404
                
                return send_file(
                    full_path,
                    mimetype='application/dicom',
                    as_attachment=False
                )
        
        return jsonify({'error': 'Instance not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dicom-web/studies/<study_uid>/series/<series_uid>/instances/<instance_uid>/frames/<int:frame_number>', methods=['GET', 'OPTIONS'])
def serve_frame_wado_rs(study_uid, series_uid, instance_uid, frame_number):
    """Serve DICOM frame pixel data (WADO-RS) - critical endpoint for OHIF image rendering."""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        from flask import Response
        return Response(
            '',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': '*'
            }
        )
    
    try:
        dicom_files = get_dicom_files()
        
        # Find the file for this instance
        for file_info in dicom_files:
            if (file_info['study_instance_uid'] == study_uid and
                file_info['series_instance_uid'] == series_uid and
                file_info['sop_instance_uid'] == instance_uid):
                
                full_path = os.path.join(DEMO_CASES_DIR, file_info['file_path'])
                
                # Load DICOM file
                ds = pydicom.dcmread(full_path)
                
                if not hasattr(ds, 'PixelData'):
                    from flask import jsonify
                    return jsonify({'error': 'No pixel data found'}), 404
                
                # Get pixel array (this handles decompression automatically)
                try:
                    pixel_array = ds.pixel_array
                    
                    # Handle multi-frame images
                    if len(pixel_array.shape) == 3:  # Multi-frame
                        if frame_number > pixel_array.shape[0]:
                            from flask import jsonify
                            return jsonify({'error': f'Frame {frame_number} not found'}), 404
                        frame_data = pixel_array[frame_number - 1]  # 1-based indexing
                    else:  # Single frame
                        if frame_number != 1:
                            from flask import jsonify
                            return jsonify({'error': f'Frame {frame_number} not found, only frame 1 exists'}), 404
                        frame_data = pixel_array
                    
                    # Convert to proper format for OHIF/WebGL
                    # Ensure data is in the right dtype and byte order
                    if ds.BitsAllocated == 16:
                        # Convert to uint16 for 16-bit data
                        if ds.PixelRepresentation == 1:  # Signed
                            # Convert signed to unsigned for WebGL
                            frame_data = frame_data.astype('int16')
                            # Shift to unsigned range
                            frame_data = (frame_data.astype('int32') + 32768).astype('uint16')
                        else:  # Unsigned
                            frame_data = frame_data.astype('uint16')
                    else:  # 8-bit or other
                        frame_data = frame_data.astype('uint8')
                    
                    # Convert to bytes in little-endian format
                    pixel_bytes = frame_data.tobytes('C')  # C order, little-endian
                    
                    # Create multipart response as per WADO-RS standard
                    boundary = "frame_boundary_123456789"
                    
                    # Build multipart content
                    multipart_content = f"""--{boundary}\r
Content-Type: application/octet-stream\r
Content-Length: {len(pixel_bytes)}\r
\r
""".encode('utf-8') + pixel_bytes + f"\r\n--{boundary}--\r\n".encode('utf-8')
                    
                    from flask import Response
                    return Response(
                        multipart_content,
                        mimetype=f'multipart/related; boundary={boundary}',
                        headers={
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, OPTIONS',
                            'Access-Control-Allow-Headers': '*',
                            'Content-Length': str(len(multipart_content)),
                            'Cache-Control': 'public, max-age=86400'
                        }
                    )
                    
                except Exception as e:
                    print(f"Error processing pixel data: {e}")
                    from flask import jsonify
                    return jsonify({'error': f'Error processing pixel data: {str(e)}'}), 500
        
        from flask import jsonify
        return jsonify({'error': 'Instance not found'}), 404
        
    except Exception as e:
        print(f"Error in serve_frame_wado_rs: {e}")
        from flask import jsonify
        return jsonify({'error': str(e)}), 500

# Add DICOMweb QIDO-RS endpoints that OHIF expects
@app.route('/dicom-web/studies', methods=['GET'])
def get_studies_dicomweb():
    """Get list of studies (DICOMweb QIDO-RS) - OHIF compatible endpoint."""
    return get_studies()

@app.route('/dicom-web/studies/<study_uid>/series', methods=['GET'])
def get_series_dicomweb(study_uid):
    """Get series for a specific study (DICOMweb QIDO-RS) - OHIF compatible endpoint."""
    return get_series(study_uid)

@app.route('/dicom-web/studies/<study_uid>/series/<series_uid>/instances', methods=['GET'])
def get_instances_dicomweb(study_uid, series_uid):
    """Get instances for a specific series (DICOMweb QIDO-RS) - OHIF compatible endpoint."""
    return get_instances(study_uid, series_uid)

@app.route('/dicom-web/studies/<study_uid>/series/<series_uid>/metadata', methods=['GET'])
def get_series_metadata_dicomweb(study_uid, series_uid):
    """Get metadata for all instances in a series (DICOMweb) - OHIF compatible endpoint."""
    return get_series_metadata(study_uid, series_uid)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'simple-dicom-server',
        'dicom_files_found': len(get_dicom_files())
    })

if __name__ == '__main__':
    print(f"🚀 Starting Simple DICOMweb Server on port {PORT}")
    print(f"📁 Serving DICOM files from: {DEMO_CASES_DIR}")
    
    # Check if demo_cases directory exists
    if not os.path.exists(DEMO_CASES_DIR):
        print(f"❌ Error: {DEMO_CASES_DIR} directory not found!")
        print("Please create the directory and add DICOM files.")
        exit(1)
    
    # Count DICOM files
    dicom_files = get_dicom_files()
    print(f"📊 Found {len(dicom_files)} DICOM files")
    
    if len(dicom_files) == 0:
        print("⚠️  Warning: No DICOM files found!")
        print(f"Please add .dcm files to the {DEMO_CASES_DIR} directory.")
    
    app.run(host='0.0.0.0', port=PORT, debug=True) 