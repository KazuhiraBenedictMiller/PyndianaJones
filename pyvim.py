import subprocess
import tempfile
import os

# Define the code to be pre-populated in the editor
code = '''def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
'''

# Create a temporary file with the code
with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as tmp:
    tmp.write(code)
    tmp_path = tmp.name

# Open the temporary file with nano
subprocess.call(['nano', tmp_path])

# Read the contents after editing
with open(tmp_path, 'r') as tmp_file:
    edited_content = tmp_file.read()

# Clean up the temporary file
os.unlink(tmp_path)

# Use the edited content as needed
print(edited_content)
