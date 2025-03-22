# LLM Chat Indexer

![LLM-Chat-Indexer](assets/llm-chat-indexer.png)  

A tool for processing chat files in various formats, extracting topics and summaries using AI, and generating a searchable index.

## Features

- Processes chat files in multiple formats (.txt, .md, .json, .html, .csv)
- Uses AI (via LiteLLM) to extract topics and generate summaries
- Creates a JSON index and markdown summary file
- Configurable via environment variables or `.env` file
- Supports customizable logging and output directories

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/therealfredp3d/llm-chat-indexer.git
   cd llm-chat-indexer
   ```

2. Create a virtual environment:

   ```sh
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. Configure your environment:

   ```sh
   cp .env.template .env
   ```

   Edit `.env` to add your API key for the chosen LLM provider and adjust other settings.

## Usage

Run the tool with:

```sh
python chat-indexer.py
```

By default, it will:

1. Scan the current directory for supported chat files
2. Process each file to extract messages
3. Use the configured LLM to extract topics and generate summaries
4. Create a JSON index file and a markdown summary file in the `./output` directory

### Example Output

- **JSON Index**: `output/chat_index.json`
- **Markdown Summary**: `output/chat_summaries.md`

## Supported LLM Providers

Visit **[List of supported providers](https://docs.litellm.ai/docs/providers)** to choose a LLM or use
`gemini/gemini-2.0-flash` by default.

## Configuration

You can configure the tool by editing the `.env` file or setting environment variables:

- `BASE_DIR`: Directory to scan for chat files (default: current directory)
- `OUTPUT_DIR`: Directory to store output files (default: ./output)
- `SUMMARY_FILENAME`: Filename for the markdown summary (default: chat_summaries.md)
- `INDEX_FILENAME`: Filename for the JSON index (default: chat_index.json)
- `LLM_PROVIDER`: LiteLLM provider identifier (default: gemini/gemini-2.0-flash)
- `SUPPORTED_FILE_EXTENSIONS`: File extensions to process (default: .txt,.md,.json,.html,.csv)
- `MAX_TOPIC_KEYWORDS`: Maximum number of topics to extract per file (default: 5)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FILE`: Path to log file (default: chat_indexer.log)

## License

MIT

## Coming Next

- **Enhanced File Format Support**: Add support for additional file formats such as `.docx` and `.pdf` to broaden the tool's applicability.
- **Interactive Web Interface**: Develop a web-based interface for uploading chat files, configuring settings, and viewing results in real-time.
- **Advanced Summarization**: Integrate more advanced AI models for better topic extraction and summary generation.
- **Multi-Language Support**: Extend the tool's capabilities to process and summarize chats in multiple languages.
  
## About the Author

|  | |  
|  -------------  |    ------------   |
| Name    | Frederick Pellerin <fredp3d@proton.me> |  
| X | [https://x.com/therealfredp3d](@TheRealFREDP3D) |  
| GitHub | [TheRealFredP3D](https:/github.com/TherealFredP3D) |

---

## Output

### Terminal

```sh
[...]
2025-03-22 13:37:12,482 INFO Starting LLM Chat Indexer
2025-03-22 13:37:12,482 INFO Input directory: \
2025-03-22 13:37:12,482 INFO Output directory: \output
2025-03-22 13:37:12,482 INFO Supported extensions: ['.txt', '.md', '.json', '.html', '.csv']
2025-03-22 13:37:12,482 INFO LLM provider: gemini/gemini-2.0-flash
2025-03-22 13:37:12,490 INFO Found 2 chat files to process
2025-03-22 13:37:12,490 INFO Processing file: \requirements.txt
[...]
```

