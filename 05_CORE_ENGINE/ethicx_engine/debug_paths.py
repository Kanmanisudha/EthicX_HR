import os
import sys

print("--- DIAGNOSTIC START ---")
print(f"1. Current Working Directory: {os.getcwd()}")

# Check if logic folder exists
if os.path.exists("logic"):
    print("2. ✅ 'logic' folder found.")
    
    # Check contents of logic folder
    files = os.listdir("logic")
    print(f"3. Files inside 'logic': {files}")
    
    # Check for specific file
    if "bias_detector.py" in files:
        print("4. ✅ 'bias_detector.py' exists.")
    else:
        print("4. ❌ 'bias_detector.py' NOT found. Check for typos or hidden .txt extensions!")

    # Check for __init__.py
    if "__init__.py" in files:
        print("5. ✅ '__init__.py' exists.")
    else:
        print("5. ⚠️ '__init__.py' MISSING. Python needs this to treat the folder as a package.")

else:
    print("2. ❌ 'logic' folder NOT found. You might be running this from the wrong terminal path.")

print("--- DIAGNOSTIC END ---")