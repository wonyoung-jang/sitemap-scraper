import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QListWidget,
)
import helper

class SitemapGeneratorGUI(QWidget):
    """
    A graphical user interface (GUI) for generating sitemaps.
    Attributes:
        url_label (QLabel): A label for the website URL input field.
        url_input (QLineEdit): A text input field for the website URL.
        add_url_button (QPushButton): A button to add a URL to the list.
        url_list (QListWidget): A list to display added URLs.
        generate_button (QPushButton): A button to generate the sitemaps.
        sitemap_output (QTextEdit): A text edit field to display the generated sitemap.
        save_button (QPushButton): A button to save the sitemaps as Markdown files.
    """
    def __init__(self):
        """
        Initializes the GUI.
        """
        super().__init__()
        self.setWindowTitle("Multi-Sitemap Generator")
        self.setGeometry(100, 100, 600, 500)
        layout = QVBoxLayout()

        self.url_label = QLabel("Website URL:")
        layout.addWidget(self.url_label)

        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        self.add_url_button = QPushButton("Add URL")
        self.add_url_button.clicked.connect(self.add_url)
        layout.addWidget(self.add_url_button)

        self.url_list = QListWidget()
        layout.addWidget(self.url_list)

        self.generate_button = QPushButton("Generate Sitemaps")
        self.generate_button.clicked.connect(self.generate_sitemaps)
        layout.addWidget(self.generate_button)

        self.sitemap_output = QTextEdit()
        self.sitemap_output.setReadOnly(True)
        layout.addWidget(self.sitemap_output)

        self.save_button = QPushButton("Save Sitemaps as Markdown (*.md)")
        self.save_button.clicked.connect(self.save_sitemaps)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.sitemaps = {}  # Dictionary to store generated sitemaps

    def add_url(self):
        """
        Adds a URL to the list of URLs to process.
        """
        url = self.url_input.text().strip()
        if url:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url
            self.url_list.addItem(url)
            self.url_input.clear()
        else:
            QMessageBox.warning(self, "Warning", "Please enter a website URL.")

    def generate_sitemaps(self):
        """
        Generates sitemaps for all the specified website URLs.
        """
        self.sitemaps.clear()
        self.sitemap_output.clear()

        for index in range(self.url_list.count()):
            url = self.url_list.item(index).text()
            try:
                sitemap_xml = helper.get_sitemap_xml(url)
                sitemap_content = helper.get_sitemap_content(sitemap_xml)
                parsed_content = helper.parse_sitemap(sitemap_content, sitemap_xml)
                organized_content = helper.organize_sitemap(parsed_content)
                sitemap_text = helper.generate_sitemap_text(organized_content)
                self.sitemaps[url] = sitemap_text
                self.sitemap_output.append(f"Sitemap for {url}:\n{sitemap_text}\n\n")
            except Exception as e:
                self.sitemap_output.append(f"Error generating sitemap for {url}: {str(e)}\n\n")

        if not self.sitemaps:
            QMessageBox.warning(self, "Warning", "No sitemaps were generated. Please check the URLs and try again.")

    def save_sitemaps(self):
        """
        Saves the generated sitemaps as separate Markdown files.
        """
        if self.sitemaps:
            directory = QFileDialog.getExistingDirectory(self, "Select Directory to Save Sitemaps")
            if directory:
                for url, sitemap_text in self.sitemaps.items():
                    file_name = helper.url_to_filename(url)
                    file_path = f"{directory}/{file_name}.md"
                    helper.save_to_file(sitemap_text, file_path)
                QMessageBox.information(self, "Success", f"Sitemaps saved in {directory}")
        else:
            QMessageBox.warning(self, "Warning", "No sitemaps generated. Please generate sitemaps first.")

def main():
    """
    The main function to run the GUI application.
    """
    app = QApplication(sys.argv)
    window = SitemapGeneratorGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()