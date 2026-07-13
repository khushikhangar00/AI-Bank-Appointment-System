import os
import zipfile

source_dir = r'C:\Users\hp\Desktop\Antigravity & Projects\Bank'
dest_zip = r'C:\Users\hp\Desktop\SmartBank_Deployment_Ready.zip'

print("Creating zip archive...")
with zipfile.ZipFile(dest_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(source_dir):
        # Skip unnecessary heavy directories
        dirs[:] = [d for d in dirs if d not in ('venv', 'node_modules', '__pycache__', '.git', 'dist')]
        for file in files:
            # Skip existing zip files to avoid infinite recursion or bloating
            if file.endswith('.zip'):
                continue
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, source_dir)
            zipf.write(file_path, arcname)

print(f"Project successfully zipped to: {dest_zip}")
