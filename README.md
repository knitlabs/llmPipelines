**README for Data Ingestion Module**

This module provides functions for fetching and processing data from various sources, including text, URLs, audio files, PDF documents, images, and graphs. It utilizes multiple libraries such as BeautifulSoup, OpenAI, and PyPDF to extract, transform, and analyze data.

## Functions

### Data Extraction

**`fetch_pdf`**
- **Description**: Extracts content from a PDF file, including text and optionally images.
- **Parameters**:
  - `path`: Path to the PDF file.
  - `support_image`: Whether to process images in the PDF (default: `True`).
  - `graph_mode`: Whether to convert image contents to JSON (default: `True`).
- **Return**: String containing the PDF contents.

**`fetch_url`**
- **Description**: Extracts text content from a given website.
- **Parameters**: URL of the website.
- **Return**: Extracted text from the webpage.

**`fetch_audio`**
- **Description**: Converts an audio file into a transcript.
- **Parameters**: Path to the audio file.
- **Return**: Transcribed text.

**`fetch_word`**
- **Description**: Extracts content from a Word document, including text and optionally images.
- **Parameters**:
  - `path`: Path to the Word document.
  - `support_image`: Whether to process images (default: `True`).
  - `graph_mode`: Whether to convert image contents to JSON (default: `True`).
- **Return**: String containing the document contents.

### Image and Graph Processing

**`fetch_graph_image`**
- **Description**: Converts images of graphs to JSON format.
- **Parameters**: Path to the graph image.
- **Return**: JSON representation of the graph.

**`fetch_image`**
- **Description**: Generates a detailed description of an image.
- **Parameters**: Path to the image file.
- **Return**: String containing the image description.

### Utility Functions

**`tag_visible`**
- **Description**: Identifies visible text elements from a webpage.
- **Parameters**: HTML element.
- **Return**: Boolean indicating if the element is visible.

**`text_from_html`**
- **Description**: Extracts visible text from HTML content.
- **Parameters**: HTML body.
- **Return**: Extracted text.

**`encode_image`**
- **Description**: Encodes an image file to base64.
- **Parameters**: Path to the image file.
- **Return**: Base64 encoded string of the image.

### Main Function

**`fetch_input`**
- **Description**: Processes various types of inputs and returns extracted content.
- **Parameters**:
  - `content`: Input content or path.
  - `type`: Type of input (e.g., "text", "url", "audio", "pdf", "graph", "image").
  - `input_images_pdf`: Whether to process images in PDFs (default: `True`).
  - `graph_mode`: Whether to use graph mode for images (default: `True`).
- **Return**: Extracted and processed content based on input type.

## Usage

To use this module, install the required libraries and set up your environment variables. The module supports various input types, including text, URLs, audio files, PDFs, images, and graphs.

### Environment Variables

Set up your OpenAI API key in the environment variables:

```
openai_key=your_openai_api_key_here
```

### Example Usage

```python
from data_ingestion import fetch_input

# Fetch text from a PDF file
pdf_content = fetch_input("path/to/document.pdf", "pdf")

# Fetch text from a webpage
web_content = fetch_input("https://example.com", "url")

# Fetch transcript from an audio file
transcript = fetch_input("/path/to/audio.mp3", "audio")

# Analyze a graph image
graph_data = fetch_input("path/to/graph.png", "graph")

# Get description of an image
image_description = fetch_input("path/to/image.jpg", "image")
```

## Limitations

- Audio file size is limited to 25MB for transcription.
- Image and graph analysis rely on OpenAI's capabilities and may have limitations based on the model used.

## Future Development

- Support for larger audio files.
- Enhanced multi-language support for audio transcription.
- Improved graph and image analysis capabilities.
- Integration with additional data sources and formats.
- Integration with Structured data via an automated EDA pipeline and metadata.
