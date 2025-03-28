# LLM Chat Indexer

![LLM Chat Indexer](assets/llm-chat-indexer.png)

A powerful tool for processing chat files in various formats, extracting topics and summaries using AI, and generating a searchable index.

## 📚 Table of Contents

- [LLM Chat Indexer](#llm-chat-indexer)
  - [📚 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🚀 Quick Start](#-quick-start)
  - [💡 Usage Examples](#-usage-examples)
    - [Basic Usage](#basic-usage)
    - [Advanced Usage](#advanced-usage)
  - [⚙️ Configuration Guide](#️-configuration-guide)
    - [Environment Variables](#environment-variables)
    - [Command Line Arguments](#command-line-arguments)
  - [📁 File Format Support](#-file-format-support)
    - [Plain Text (.txt)](#plain-text-txt)
    - [Markdown (.md)](#markdown-md)
    - [JSON (.json)](#json-json)
  - [🤖 LLM Provider Support](#-llm-provider-support)
    - [Supported Providers](#supported-providers)
    - [Provider Selection](#provider-selection)
  - [🔧 Advanced Usage](#-advanced-usage)
    - [Custom Processing Pipeline](#custom-processing-pipeline)
  - [🔍 Troubleshooting Guide](#-troubleshooting-guide)
    - [Common Issues](#common-issues)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)
  - [📊 Project Status](#-project-status)
  - [📞 Support](#-support)

## ✨ Features

- **Multi-format Support**: Process chat files in various formats:
  - Plain text (.txt)
  - Markdown (.md)
  - JSON (.json)
  - HTML (.html)
  - CSV (.csv)

- **AI-Powered Analysis**:
  - Topic extraction with customizable keyword count
  - Intelligent conversation summarization
  - Context-aware processing

- **Flexible Output**:
  - Searchable JSON index
  - Human-readable markdown summaries
  - Customizable output formats

- **Advanced Configuration**:
  - Environment variable support
  - Command-line interface
  - .env file configuration

## 🚀 Quick Start

1. **Clone and Setup**:

   ```bash
   git clone https://github.com/therealfredp3d/llm-chat-indexer.git
   cd llm-chat-indexer
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure**:

   ```bash
   cp .env.template .env
   # Edit .env with your API key and preferences
   ```

3. **Run**:

   ```bash
   python chat-indexer.py --input-dir ./input
   ```

## 💡 Usage Examples

### Basic Usage

```bash
# Process all files in input directory
python chat-indexer.py

# Specify custom directories
python chat-indexer.py --input-dir ./my_chats --output-dir ./summaries

# Use a specific LLM provider
python chat-indexer.py --llm-provider anthropic/claude-3-opus
```

### Advanced Usage

```bash
# Process specific file types
python chat-indexer.py --supported-extensions .json,.md

# Enable debug logging
python chat-indexer.py --log-level DEBUG

# Custom topic extraction
python chat-indexer.py --max-topic-keywords 10
```

## ⚙️ Configuration Guide

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LLM_PROVIDER` | LLM provider identifier | gemini/gemini-2.0-flash | Yes |
| `LLM_API_KEY` | API key for LLM service | - | Yes |
| `BASE_DIR` | Input directory path | ./input | No |
| `OUTPUT_DIR` | Output directory path | ./output | No |
| `MAX_TOPIC_KEYWORDS` | Topics per file | 5 | No |
| `LOG_LEVEL` | Logging verbosity | INFO | No |

### Command Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--input-dir` | Input directory | `--input-dir ./chats` |
| `--output-dir` | Output directory | `--output-dir ./results` |
| `--llm-provider` | LLM provider | `--llm-provider openai/gpt-4` |
| `--log-level` | Log level | `--log-level DEBUG` |

## 📁 File Format Support

### Plain Text (.txt)

```text
User: Hello there
Assistant: Hi! How can I help?
```

### Markdown (.md)

```markdown
## Conversation
**User**: Hello there
**Assistant**: Hi! How can I help?
```

### JSON (.json)

```json
{
  "messages": [
    {"role": "user", "content": "Hello there"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ]
}
```

## 🤖 LLM Provider Support

### Supported Providers

- Gemini (Default)
- OpenAI
- Anthropic
- OpenRouter
- [Full List](https://docs.litellm.ai/docs/providers)

### Provider Selection

```bash
# Using Gemini
export LLM_PROVIDER=gemini/gemini-2.0-flash

# Using OpenAI
export LLM_PROVIDER=openai/gpt-4

# Using Anthropic
export LLM_PROVIDER=anthropic/claude-3-opus
```

## 🔧 Advanced Usage

### Custom Processing Pipeline

```python
from chat_indexer import ChatIndexer

indexer = ChatIndexer(
    input_dir="./input",
    output_dir="./output",
    llm_provider="anthropic/claude-3-opus",
    max_topics=10
)

```

## 🔍 Troubleshooting Guide

### Common Issues

1. **API Key Issues**

   ```bash
   # Verify API key
   echo $LLM_API_KEY
   
   # Test API connection
   python chat-indexer.py --test-connection
   ```

2. **File Processing Errors**

   ```bash
   # Enable debug logging
   python chat-indexer.py --log-level DEBUG
   
   # Check log file
   tail -f logs/chat_indexer.log
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

## 📊 Project Status

![Processing Flow](assets/processing_flow.png)

Current Version: 0.2.0

- ✅ Core functionality
- ✅ Multiple format support
- ✅ AI-powered analysis
- 🚧 Web interface (in development)
- 🚧 API endpoints (planned)

## 📞 Support

- GitHub Issues: [Create an issue](https://github.com/therealfredp3d/llm-chat-indexer/issues)
- Email: <fredp3d@proton.me>
- X: [@TheRealFREDP3D](https://x.com/TheRealFREDP3D)
- Website: [www.therealfred.ca>](www.therealfred.ca)
