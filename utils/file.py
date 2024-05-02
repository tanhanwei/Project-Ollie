import json

class File:
    @staticmethod
    def load_json(path: str):
        """
        Load a JSON file from a specified path.

        Args:
            path (str): The file path from which to load the JSON data.

        Returns:
            dict: The JSON object loaded from the file.
        """
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    @staticmethod
    def write_json(data, path: str):
        """
        Write a dictionary as a JSON file to a specified path.

        Args:
            data (dict): The data to write to the file.
            path (str): The file path to which the data should be written.

        Returns:
            None: The function writes data to a file and does not return anything.
        """
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def write_md(content: str, path: str):
        """
        Write a string as a Markdown (.md) file to a specified path.

        Args:
            content (str): The Markdown content to write to the file.
            path (str): The file path to which the Markdown content should be written.

        Returns:
            None: The function writes content to a file and does not return anything.
        """
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def read_md(path: str):
        """
        Read and return the content of a Markdown (.md) file from a specified path.

        Args:
            path (str): The file path from which to read the Markdown content.

        Returns:
            str: The content of the Markdown file.
        """
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
        
    def remove_spaces(strings):
        result = [string.replace(" ", "") for string in strings]
        return result

    # # Example list of strings
    # strings_list = ["Hello World", "Python Programming", "Open AI"]

    # # Removing spaces
    # result_list = remove_spaces(strings_list)
    # print(result_list)
