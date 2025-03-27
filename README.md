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

   Example `.env` file:

   ```sh
   # LLM Configuration
   LLM_PROVIDER=gemini/gemini-2.0-flash
   LLM_API_KEY=your_api_key_here
   
   # Directory Settings
   BASE_DIR=./chats
   OUTPUT_DIR=./output
   
   # Output File Names
   SUMMARY_FILENAME=chat_summaries.md
   INDEX_FILENAME=chat_index.json
   
   # Processing Settings
   SUPPORTED_FILE_EXTENSIONS=.txt,.md,.json,.html,.csv
   MAX_TOPIC_KEYWORDS=5
   
   # Logging Configuration
   LOG_LEVEL=INFO
   LOG_FILE=chat_indexer.log
   ```

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

#### Example JSON Index Structure

```json
{
  "files": [
    {
      "filename": "chat_with_support.txt",
      "path": "/path/to/chat_with_support.txt",
      "topics": ["account setup", "password reset", "billing issue"],
      "summary": "Conversation with customer support about account setup issues and billing questions. The support agent helped reset the password and explained the billing cycle.",
      "message_count": 24,
      "processed_at": "2025-03-22T13:37:12.482"
    },
    {
      "filename": "team_discussion.md",
      "path": "/path/to/team_discussion.md",
      "topics": ["project timeline", "resource allocation", "milestone planning"],
      "summary": "Team discussion about project timelines and resource allocation for the Q2 deliverables. The team agreed on new milestones and assigned responsibilities.",
      "message_count": 45,
      "processed_at": "2025-03-22T13:38:05.123"
    }
  ],
  "metadata": {
    "generated_at": "2025-03-22T13:40:22.789",
    "file_count": 2,
    "llm_provider": "gemini/gemini-2.0-flash"
  }
}
```

#### Example Markdown Summary

![Markdown Summary Example](assets/summary_example.png)

The markdown summary provides a clean, readable format with:

- File information and statistics
- Key topics extracted from each conversation
- Detailed summaries of the chat content
- Links to the original files

## Command-Line Parameters

You can customize the behavior of the tool by passing command-line arguments when running the script. These parameters override the corresponding environment variables and configuration settings.

```sh
python chat-indexer.py --input-dir ./my_chats --output-dir ./my_output --llm-provider openai/gpt-4
```

### Available Parameters

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| `--input-dir` | Directory containing chat files to process | Config.BASE_DIR (usually current directory) |
| `--output-dir` | Directory to store output files | Config.OUTPUT_DIR (usually './output') |
| `--supported-extensions` | Comma-separated list of supported file extensions | The comma-separated string derived from Config.SUPPORTED_FILE_EXTENSIONS (typically '.txt,.md,.json,.html,.csv') |
| `--llm-provider` | LLM provider to use | Config.LLM_PROVIDER (typically 'gemini/gemini-2.0-flash') |
| `--log-level` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | Config.LOG_LEVEL (typically 'INFO') |

### Examples

Process files from a specific directory:

```sh
python chat-indexer.py --input-dir ./my_chat_archives
```

Use a different LLM provider:

```sh
python chat-indexer.py --llm-provider anthropic/claude-3-opus
```

Process only specific file types:

```sh
python chat-indexer.py --supported-extensions .json,.md
```

Change the output directory and enable detailed logging:

```sh
python chat-indexer.py --output-dir ./summaries --log-level DEBUG
```

These command-line parameters work in conjunction with the environment variables described in the [Configuration](#configuration) section. Command-line arguments take precedence over environment variables and default settings.

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

### Setting Environment Variables

You can set environment variables in different ways depending on your operating system:

#### Using Command Line (before running the tool)

**Windows (Command Prompt)**:

```sh
set LLM_PROVIDER=openai/gpt-4
set BASE_DIR=C:\Users\username\chat_files
python chat-indexer.py
```

**Windows (PowerShell)**:

```powershell
$env:LLM_PROVIDER = "openai/gpt-4"
$env:BASE_DIR = "C:\Users\username\chat_files"
python chat-indexer.py
```

**macOS/Linux**:

```bash
export LLM_PROVIDER=openai/gpt-4
export BASE_DIR=/home/username/chat_files
python chat-indexer.py
```

#### Using Command Line Arguments

You can also pass configuration options directly as command line arguments:

```sh
python chat-indexer.py --base-dir ./my_chats --llm-provider anthropic/claude-3-opus
```

Check the help documentation for all available command line options:

```sh
python chat-indexer.py --help
```

## License

MIT

## Supported Chat File Formats

The tool supports various chat file formats, each with specific structure requirements:

### Text (.txt)

- Simple text files with conversation content
- Expected format: Each message on a new line, optionally with sender information
- Example:

  ```txt
  User: Hello there
  Assistant: Hi! How can I help you today?
  User: I need information about your services
  ```

### Markdown (.md)

- Markdown files with formatted conversation content
- Expected format: Messages with headers, lists, or other markdown formatting
- Example:

  ```markdown
  ## Conversation with Support

  **User**: Hello there  
  **Assistant**: Hi! How can I help you today?  
  **User**: I need information about your services
  ```

### JSON (.json)

- Structured JSON files containing conversation data
- Expected format: Array of message objects with sender and content fields
- Example:

  ```json
  {
    "conversation": [
      {
        "sender": "User",
        "message": "Hello there",
        "timestamp": "2025-03-22T13:37:12.482"
      },
      {
        "sender": "Assistant",
        "message": "Hi! How can I help you today?",
        "timestamp": "2025-03-22T13:37:15.123"
      }
    ]
  }
  ```

### HTML (.html)

- HTML files with conversation content
- Expected format: HTML elements containing messages, typically with class or id attributes
- Example:

  ```html
  <div class="conversation">
    <div class="message user">
      <span class="sender">User:</span>
      <span class="content">Hello there</span>
    </div>
    <div class="message assistant">
      <span class="sender">Assistant:</span>
      <span class="content">Hi! How can I help you today?</span>
    </div>
  </div>
  ```

### CSV (.csv)

- Comma-separated values files with tabular conversation data
- Expected format: Columns for sender, message content, and optional timestamp
- Example:

  ```json
  timestamp,sender,message
  2025-03-22T13:37:12.482,User,Hello there
  2025-03-22T13:37:15.123,Assistant,Hi! How can I help you today?
  ```

## Troubleshooting

### Common Errors and Solutions

#### "Unable to generate summary due to an error"

This error appears in the output files when the LLM fails to process a chat file. Common causes include:

1. **Token Limit Exceeded**
   - **Problem**: The chat file is too large for the LLM's context window
   - **Solution**:
     - Try using a model with a larger context window (e.g., `anthropic/claude-3-opus` instead of `gemini/gemini-2.0-flash`)
     - Split very large chat files into smaller ones

2. **Rate Limit Exceeded**
   - **Problem**: Too many requests sent to the LLM provider in a short time
   - **Solution**:
     - Process fewer files at once
     - Add a delay between processing files by setting `PROCESSING_DELAY=5` (in seconds) in your `.env` file
     - Upgrade your API plan with the provider

3. **API Key Issues**
   - **Problem**: Invalid or expired API key
   - **Solution**:
     - Verify your API key is correct in the `.env` file
     - Check if your API key has sufficient credits/quota
     - Generate a new API key if necessary

4. **Malformed Chat Files**
   - **Problem**: The chat file doesn't match the expected format
   - **Solution**:
     - Check if your file follows the expected structure for its format (see "Supported Chat File Formats" section)
     - Try converting the file to a different format (e.g., from HTML to JSON)
     - Manually fix formatting issues in the file

#### Checking Logs for More Information

For detailed error information, check the log file (default: `logs/chat_indexer.log`):

```sh
tail -f chat_indexer.log
```

Look for error messages that provide more context about what went wrong during processing.

### Known Limitations

1. **Large File Processing**
   - Files exceeding the LLM's token limit may result in incomplete or failed summaries
   - Very large files (>10MB) may cause memory issues or timeout errors

2. **Complex Formatting**
   - Chat files with complex formatting, embedded media, or non-standard structures may not parse correctly
   - Custom or proprietary chat formats may require manual preprocessing

3. **Language Support**
   - Performance may vary for non-English content depending on the LLM provider
   - Some languages may result in lower quality summaries or topic extraction

4. **Topic Extraction Accuracy**
   - Topic extraction quality depends on the conversation content and the LLM's capabilities
   - Technical or specialized conversations may result in generic or imprecise topics

## Best Practices

1. **Optimize File Size**
   - Keep individual chat files under 100KB for best results
   - For large conversations, consider splitting into multiple files by date or topic

2. **Choose the Right LLM**
   - For high-quality summaries: `anthropic/claude-3-opus` or `openai/gpt-4`
   - For faster processing: `gemini/gemini-2.0-flash` or `openai/gpt-3.5-turbo`
   - For large files: Models with larger context windows like `anthropic/claude-3-sonnet`

3. **Standardize Chat Formats**
   - Use consistent formatting within your chat files
   - JSON format typically provides the most reliable parsing results
   - Include clear speaker/role identifiers in your chat content

4. **Monitor API Usage**
   - Keep track of token usage to manage costs
   - Consider implementing caching for repeated processing of the same files

## Coming Next

- **Enhanced File Format Support**: Add support for additional file formats such as `.docx` and `.pdf` to broaden the tool's applicability.
- **Interactive Web Interface**: Develop a web-based interface for uploading chat files, configuring settings, and viewing results in real-time.
  
  ![Web Interface Mockup](assets/web_interface_mockup.png)
  
- **Advanced Summarization**: Integrate more advanced AI models for better topic extraction and summary generation.
- **Multi-Language Support**: Extend the tool's capabilities to process and summarize chats in multiple languages.
- **Batch Processing**: Add support for processing multiple directories or specific file patterns.
- **Custom Templates**: Allow users to define custom templates for the output formats.
  
## About the Author

|  | |  
|  -------------  |    ------------   |
| Name    | Frederick Pellerin <fredp3d@proton.me> |  
| X | [https://x.com/therealfredp3d](@TheRealFREDP3D) |  
| GitHub | [TheRealFredP3D](https:/github.com/TherealFredP3D) |

---

## Output Examples

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

### Processing Flow

![Processing Flow](assets/processing_flow.png)

The tool follows this workflow:

1. **Scan** - Find all supported chat files in the specified directory
2. **Parse** - Extract messages from each file based on its format
3. **Analyze** - Use the LLM to identify topics and generate summaries
4. **Index** - Create a searchable JSON index with all the extracted information
5. **Summarize** - Generate a human-readable markdown summary

### Advanced Usage Examples

### Processing Specific File Types

```sh
# Process only markdown and text files
export SUPPORTED_FILE_EXTENSIONS=.md,.txt
python chat-indexer.py
```

### Using Different LLM Providers

```sh
# Use OpenAI's GPT-4
export LLM_PROVIDER=openai/gpt-4
export LLM_API_KEY=your_openai_api_key
python chat-indexer.py

# Use Anthropic's Claude
export LLM_PROVIDER=anthropic/claude-3-opus
export LLM_API_KEY=your_anthropic_api_key
python chat-indexer.py
```

### Custom Output Directories

```sh
# Specify input and output directories
python chat-indexer.py --base-dir ./my_chats --output-dir ./my_summaries
```

### Processing Files with Specific Patterns

```sh
# Process only files containing "meeting" in the filename
python chat-indexer.py --file-pattern "*meeting*"
```

### Adjusting Topic Extraction

```sh
# Extract more topics per file
export MAX_TOPIC_KEYWORDS=10
python chat-indexer.py
```

### Debugging Processing Issues

```sh
# Enable debug logging for more detailed information
export LOG_LEVEL=DEBUG
python chat-indexer.py
```
