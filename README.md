**README for Data Ingestion Module**

This module provides functions for fetching and processing data from various sources, including text, URLs, YouTube videos, and PDF files. It utilizes various libraries such as BeautifulSoup, YouTube, and OpenAI to extract and transform data.

### Functions

1. **`fetch_pdf`**:
   - **Description**: Fetches content from a PDF file.
   - **Parameters**:
     - `path`: Path to the PDF file.
     - `support_image`: Whether to extract images from the PDF (default: `True`).
     - `base_path`: Base directory for temporary files (default: `"Data/"`).
   - **Return**: The content of the PDF file.

2. **`tag_visible`**:
   - **Description**: Identifies visible text elements from a given webpage.
   - **Parameters**: None
   - **Return**: A boolean indicating whether the element is visible.

3. **`text_from_html`**:
   - **Description**: Extracts text from a webpage.
   - **Parameters**: The HTML content of the webpage.
   - **Return**: The extracted text.

4. **`extract_text_from_website`**:
   - **Description**: Extracts text content from a given website.
   - **Parameters**: The URL of the website.
   - **Return**: The extracted text.

5. **`download_audio`**:
   - **Description**: Downloads an audio file from a YouTube video.
   - **Parameters**:
     - `url`: The URL of the YouTube video.
     - `base_path`: Base directory for the downloaded file (default: `"Data/"`).
   - **Return**: The path of the downloaded file.

6. **`youtube_to_transcript`**:
   - **Description**: Converts a YouTube video into a transcript.
   - **Parameters**:
     - `url`: The URL of the YouTube video.
     - `del_audio`: Whether to delete the audio file after transcription (default: `True`).
     - `base_path`: Base directory for the audio file (default: `"Data/"`).
   - **Return**: The transcript of the video.

7. **`fetch_input`**:
   - **Description**: Returns text from a given input. The input could be either text or a URL.
   - **Parameters**:
     - `content`: The input content.
     - `type`: The type of input (default: `"text"`).
     - `input_images_pdf`: Whether to include images from PDF files (default: `False`).
   - **Return**: The extracted text.

### Usage

To use this module, you need to install the required libraries and set up your environment variables. The module supports various types of inputs, including text, URLs, YouTube videos, and PDF files. Each function has its own set of parameters and return values, which are documented above.

### Environment Variables

The module uses environment variables to store API keys and other configuration settings. You need to set these variables in a `.env` file in the root directory of your project.

### Example Usage

Here are some examples of how to use the functions in this module:

```python
# Fetch text from a PDF file
pdf_content = fetch_pdf("path/to/pdf.pdf")

# Fetch text from a webpage
web_content = extract_text_from_website("https://example.com")

# Fetch transcript from a YouTube video
transcript = youtube_to_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
```

### Limitations

- The module currently supports only English videos for transcription.
- The audio size is limited to 25MB as of now.
- The module does not support other languages for transcription.

### Future Development

- Support for other languages for transcription.
- Support for larger audio files.
- Additional features for handling different types of inputs.
