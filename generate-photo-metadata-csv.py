# Import necessary libraries for the script
import os  # For interacting with the operating system
import shutil  # For file operations like moving files
import sys  # Access to some variables used or maintained by the interpreter
import requests  # To make HTTP requests to a specified URL
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QProgressBar, QFileDialog, QTextEdit
import csv # For reading and writing CSV files

# Variable to store your API token for authentication
api_token = "" # Replace with your API token

def get_image_metadata(image_path, custom_context):
    """
    Fetches metadata for an image using the PhotoTag.ai API.

    :param image_path: The path to the image file.
    :param custom_context: A string of custom context to improve API results.
    """
    # The URL of the API endpoint
    url = "https://server.phototag.ai/api/keywords"
    # Headers for the request, including the authorization token
    headers = {"Authorization": f"Bearer {api_token}"}
    # The payload of the request, including language, maximum keywords, and custom context
    payload = {
        "language": "en",
        "maxKeywords": 40,
        "customContext": custom_context
    }
    # Open the image file in binary mode and send the request
    with open(image_path, 'rb') as img_file:
        files = {"file": img_file}
        response = requests.post(url, headers=headers, data=payload, files=files)

    # If the request is successful (status code 200), process the data
    if response.status_code == 200:
        data = response.json().get("data")
        if data:
            # Extract the title, description, and keywords from the response
            title = data.get("title", "")
            description = data.get("description", "")
            keywords = data.get("keywords", [])
            # Log the fetched metadata
            print(f"Metadata fetched for image: {image_path}")
            print(f"Title: {title}")
            print(f"Description: {description}")
            print(f"Keywords: {keywords}")
            return title, description, keywords
    else:
        # Log failure if the request was unsuccessful
        print(f"Failed to fetch metadata. Check your API token. Status code: {response.status_code}")
    return None, None, []

class ImageKeywordingTool(QWidget):
    """
    A graphical user interface (GUI) tool for processing a folder of images,
    fetching metadata for each, and writing it back to the images.
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set up the window title and size
        self.setWindowTitle('Image Keywording Tool')
        self.resize(600, 400)
        layout = QVBoxLayout()

        # Create UI elements: a text box for status messages, a button to select folders, and a progress bar
        self.status_message = QTextEdit()
        self.status_message.setPlainText("Processing Not Started")
        self.status_message.setReadOnly(True)
        self.select_folder_button = QPushButton('Select Folder')
        self.select_folder_button.clicked.connect(self.start_processing)
        self.progress_bar = QProgressBar()

        # Add the UI elements to the layout
        layout.addWidget(self.status_message)
        layout.addWidget(self.select_folder_button)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def start_processing(self):
        # Function to handle the folder selection and start processing images
        selected_folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if selected_folder:
            self.status_message.setPlainText("Processing Running...")
            self.process_images_in_folder(selected_folder)
            self.status_message.append("Processing Completed")
            self.status_message.append("Close Window to Exit")

    def process_images_in_folder(self, folder_path):
        images_to_process = [filename for filename in os.listdir(folder_path) if filename.lower().endswith(('.jpg', '.jpeg'))]
        total_images = len(images_to_process)
        processed_images = 0

        # Open a CSV file to write the metadata
        with open(os.path.join(folder_path, 'image_metadata.csv'), mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            # Write the header row
            writer.writerow(['Image Name', 'Title', 'Description', 'Keywords'])

            for filename in images_to_process:
                image_path = os.path.join(folder_path, filename)
                custom_context = ' '.join([c for c in filename.split('.')[0].split('_') if c != 'g' and not c.isdigit()])
                title, description, keywords = get_image_metadata(image_path, custom_context)
                if title and keywords:
                    # Write the image's metadata to the CSV file
                    writer.writerow([filename, title, description, ', '.join(keywords)])

                processed_images += 1
                progress = processed_images / total_images * 100
                self.progress_bar.setValue(int(round(progress)))
                QApplication.processEvents()

def main():
    # Initialize and run the application
    app = QApplication(sys.argv)
    ex = ImageKeywordingTool()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
