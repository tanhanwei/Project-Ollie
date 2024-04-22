import os

def should_ignore(path, ignore_patterns):
    for pattern in ignore_patterns:
        if pattern in path:
            return True
    return False

def generate_project_structure(root_dir, ignore_patterns):
    project_structure = "Folder Structure:\n"
    code_blocks = "\nCode Blocks:\n"

    # Traverse the directory tree
    for root, dirs, files in os.walk(root_dir):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_patterns)]

        level = root.replace(root_dir, '').count(os.sep)
        indent = '  ' * level
        project_structure += f"{indent}|-- {os.path.basename(root)}/\n"
        subindent = '  ' * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".py") and not should_ignore(file_path, ignore_patterns):
                project_structure += f"{subindent}|-- {file}\n"
                with open(file_path, "r") as f:
                    file_content = f.read()
                    code_blocks += f"\n{file}\n```python\n{file_content}\n```\n"

    return project_structure + code_blocks

# Specify the root directory of your project
project_root = "/Users/hanweitan/Documents/GithubProject/GeminiAgent"

# Read the .gitignore file
gitignore_file = os.path.join(project_root, ".gitignore")
gitignore_patterns = []
if os.path.exists(gitignore_file):
    with open(gitignore_file, "r") as f:
        gitignore_patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read the ignored_folders.txt file
ignored_folders_file = os.path.join(project_root, "ignored_folders.txt")
ignored_folders_patterns = []
if os.path.exists(ignored_folders_file):
    with open(ignored_folders_file, "r") as f:
        ignored_folders_patterns = [line.strip() for line in f if line.strip()]

# Combine the patterns from .gitignore and ignored_folders.txt
ignore_patterns = gitignore_patterns + ignored_folders_patterns

# Generate the project structure and file contents
project_structure = generate_project_structure(project_root, ignore_patterns)

# Create the "output" folder if it doesn't exist
output_folder = os.path.join(project_root, "output")
os.makedirs(output_folder, exist_ok=True)

# Save the project structure to a text file in the "output" folder
output_file = os.path.join(output_folder, "project_structure.txt")
with open(output_file, "w") as f:
    f.write(project_structure)