import json

def load_json(filename):
    """Load JSON data from a file."""
    with open(filename, 'r') as file:
        return json.load(file)

def write_markdown(data, output_filename):
    """Write markdown data to a file."""
    with open(output_filename, 'w') as file:
        file.write(data)

path = "output/manager_agent"
filename = "response.json"

def main():
    # Name of the JSON file containing markdown data
    
    # Name of the markdown output file
    markdown_filename = 'output.md'
    
    # Load the markdown data from the JSON file
    markdown_data = load_json(f"{path}/{filename}")
    
    # Write the markdown data to the markdown file
    write_markdown(markdown_data, f"{path}/{markdown_filename}")
    
    print(f"Markdown file '{markdown_filename}' has been created successfully.")

if __name__ == '__main__':
    main()
