import os
import re
import json
import hashlib
from pathlib import Path
import argparse
from datetime import datetime
import markdown
from bs4 import BeautifulSoup
import google.generativeai as genai
import textwrap

class ConversationIndexer:
    def __init__(self, base_dir=None, gemini_api_key=None):
        self.base_dir = base_dir or os.getcwd()
        self.index_file = os.path.join(self.base_dir, 'conversation_index.json')
        self.summary_file = os.path.join(self.base_dir, 'conversation_summary.md')
        self.index = self._load_index()
        
        # Initialize Gemini API if key is provided
        self.gemini_model = None
        self.use_gemini = False
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                self.use_gemini = True
                print("✅ Gemini API initialized successfully")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini API: {e}")
                print("Falling back to rule-based summarization")
        
    def _load_index(self):
        """Load existing index or create a new one."""
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "files": {},
            "topics": {},
            "models": {},
            "last_updated": None
        }
    
    def _save_index(self):
        """Save the index to disk."""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2)
    
    def _get_file_hash(self, file_path):
        """Get the MD5 hash of a file."""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _extract_model_name(self, content, filename):
        """Try to extract the LLM model name from content or filename."""
        model_patterns = [
            r'(GPT-4|GPT-3\.5|Claude|Claude 2|Claude 3|Claude Opus|Claude Sonnet|Claude Haiku|Llama|Llama 2|Gemini|Gemini Pro|Gemini Ultra|Gemma|Gemma 2|Grok|grok|Falcon|Mistral|Mixtral|Phi|Phi-2|Phi-3)',
            r'model[:\s]*([\w\.-]+)',
            r'using[:\s]*([\w\.-]+)',
        ]
        
        # First check the content
        for pattern in model_patterns:
            matches = re.search(pattern, content, re.IGNORECASE)
            if matches:
                return matches.group(1).strip()
        
        # Then check the filename
        for model in ["gpt", "claude", "llama", "gemini", "gemma", "grok", "falcon", "mistral", "mixtral", "phi"]:
            if model.lower() in filename.lower():
                return model.capitalize()
        
        return "Unknown Model"
    
    def _extract_topics_with_gemini(self, content, max_topics=10):
        """Extract key topics from the content using Gemini."""
        if not self.use_gemini or not self.gemini_model:
            return self._extract_topics(content)
            
        try:
            prompt = f"""
            Extract the key topics from this conversation transcript. 
            Return ONLY a list of 5-10 specific topics, with each topic being 1-3 words.
            Format your response as a JSON array of strings.
            
            Here is the transcript:
            {textwrap.shorten(content, width=4000, placeholder="...")}
            """
            
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text
            
            # Try to extract JSON array from the response
            try:
                # Look for JSON array in the response
                match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if match:
                    topics_json = match.group(0)
                    topics = json.loads(topics_json)
                    return topics[:max_topics]
                else:
                    # Fallback to line parsing if JSON not found
                    topics = []
                    for line in response_text.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('[') and not line.startswith(']'):
                            # Remove bullets, numbers, quotes, etc.
                            clean_line = re.sub(r'^[\d\-\*\"\'\.\s]+', '', line)
                            if clean_line:
                                topics.append(clean_line)
                    return topics[:max_topics]
            except json.JSONDecodeError:
                # If JSON parsing fails, extract topics line by line
                topics = []
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('[') and not line.startswith(']'):
                        # Remove bullets, numbers, quotes, etc.
                        clean_line = re.sub(r'^[\d\-\*\"\'\.\s]+', '', line)
                        if clean_line:
                            topics.append(clean_line)
                return topics[:max_topics]
        except Exception as e:
            print(f"⚠️ Gemini topic extraction failed: {e}")
            # Fall back to rule-based extraction
            return self._extract_topics(content)
    
    def _extract_topics(self, content):
        """Extract key topics from the content using rule-based methods."""
        # Get potential topics from content (this is simplified and could be enhanced with NLP)
        topics = set()
        
        # Look for section headers in markdown
        header_matches = re.findall(r'#+\s+(.+)', content)
        for match in header_matches:
            topics.add(match.strip())
        
        # Look for bullet points which often contain key concepts
        bullet_matches = re.findall(r'[*-]\s+(.+)', content)
        for match in bullet_matches:
            if len(match.split()) <= 5:  # Only short phrases, likely topics
                topics.add(match.strip())
        
        # Look for capitalized phrases which might be important concepts
        concept_matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b', content)
        for match in concept_matches:
            topics.add(match.strip())
        
        return list(topics)[:10]  # Limit to top 10 topics
    
    def _summarize_with_gemini(self, content, max_length=500):
        """Generate a summary of the content using Gemini."""
        if not self.use_gemini or not self.gemini_model:
            return self._summarize_content(content, max_length)
            
        try:
            # Trim content to avoid token limits
            trimmed_content = textwrap.shorten(content, width=7000, placeholder="...")
            
            prompt = f"""
            Summarize this conversation transcript concisely in 2-3 sentences (maximum 500 characters).
            Focus on the main topic and key points discussed. 
            
            Here is the transcript:
            {trimmed_content}
            """
            
            response = self.gemini_model.generate_content(prompt)
            summary = response.text.strip()
            
            # Ensure summary is not too long
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
                
            return summary
        except Exception as e:
            print(f"⚠️ Gemini summarization failed: {e}")
            # Fall back to rule-based summarization
            return self._summarize_content(content, max_length)
    
    def _summarize_content(self, content, max_length=500):
        """Generate a summary of the content using rule-based methods."""
        # This is a simple extraction-based approach
        
        # Try to find sections that are likely summaries
        summary_sections = re.findall(r'(?:summary|conclusion|key\s+points|tldr)[\s\n]*[:;-]\s*(.*?)(?:\n\n|\n#|\Z)', 
                                       content, re.IGNORECASE | re.DOTALL)
        
        if summary_sections:
            summary = summary_sections[0].strip()
            if len(summary) > max_length:
                return summary[:max_length] + "..."
            return summary
        
        # If no summary section, take first paragraph after headers
        paragraphs = re.split(r'\n\s*\n', content)
        for para in paragraphs:
            # Skip headers, code blocks, and very short paragraphs
            if not re.match(r'^#', para) and len(para) > 100:
                if len(para) > max_length:
                    return para[:max_length] + "..."
                return para
        
        # Fallback to first part of content
        if len(content) > max_length:
            return content[:max_length] + "..."
        return content
    
    def _extract_conversation_structure(self, content, file_path):
        """Extract the conversation structure (turns, participants)."""
        # Handle markdown vs plain text
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.md':
            # For markdown, try to find headers or pattern matches
            human_parts = re.findall(r'(?:^|\n)(?:User|Human|Me|Question)[:>\s]+(.*?)(?=\n(?:Assistant|AI|Bot|GPT|Claude|Gemini|Answer|Response)[:>\s]+|\Z)', 
                                    content, re.DOTALL | re.IGNORECASE)
            
            ai_parts = re.findall(r'(?:^|\n)(?:Assistant|AI|Bot|GPT|Claude|Gemini|Answer|Response)[:>\s]+(.*?)(?=\n(?:User|Human|Me|Question)[:>\s]+|\Z)', 
                                 content, re.DOTALL | re.IGNORECASE)
        else:
            # For text files, fall back to simple pattern matching
            human_parts = re.findall(r'(?:^|\n)(?:User|Human|Me|Question)[:>\s]+(.*?)(?=\n(?:Assistant|AI|Bot|Answer|Response)[:>\s]+|\Z)', 
                                    content, re.DOTALL | re.IGNORECASE)
            
            ai_parts = re.findall(r'(?:^|\n)(?:Assistant|AI|Bot|Answer|Response)[:>\s]+(.*?)(?=\n(?:User|Human|Me|Question)[:>\s]+|\Z)', 
                                 content, re.DOTALL | re.IGNORECASE)
        
        return {
            "turns": max(len(human_parts), len(ai_parts)),
            "human_messages": len(human_parts),
            "ai_messages": len(ai_parts),
            "first_question": human_parts[0][:100] + "..." if human_parts else "Unknown",
        }
    
    def process_file(self, file_path):
        """Process a single file and update the index."""
        file_hash = self._get_file_hash(file_path)
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        # Check if file is already indexed and unchanged
        if rel_path in self.index["files"] and self.index["files"][rel_path]["hash"] == file_hash:
            print(f"Skipping unchanged file: {rel_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Extract key information
        model = self._extract_model_name(content, os.path.basename(file_path))
        
        # Use Gemini for topic extraction and summarization if available
        if self.use_gemini:
            topics = self._extract_topics_with_gemini(content)
            summary = self._summarize_with_gemini(content)
        else:
            topics = self._extract_topics(content)
            summary = self._summarize_content(content)
            
        conversation = self._extract_conversation_structure(content, file_path)
        
        # Update the index
        file_info = {
            "path": rel_path,
            "hash": file_hash,
            "model": model,
            "topics": topics,
            "summary": summary,
            "conversation": conversation,
            "size": os.path.getsize(file_path),
            "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            "indexed_at": datetime.now().isoformat(),
            "summarization_method": "gemini-2.0-flash" if self.use_gemini else "rule-based"
        }
        
        self.index["files"][rel_path] = file_info
        
        # Update model index
        if model not in self.index["models"]:
            self.index["models"][model] = []
        if rel_path not in self.index["models"][model]:
            self.index["models"][model].append(rel_path)
        
        # Update topics index
        for topic in topics:
            if topic not in self.index["topics"]:
                self.index["topics"][topic] = []
            if rel_path not in self.index["topics"][topic]:
                self.index["topics"][topic].append(rel_path)
        
        print(f"Indexed: {rel_path} (Model: {model}, Summarization: {'Gemini' if self.use_gemini else 'Rule-based'})")
        return True
    
    def scan_directory(self, directory=None, recursive=True):
        """Scan a directory for conversation files to index."""
        target_dir = directory or self.base_dir
        changed = False
        
        extensions = ['.md', '.txt', '.markdown']
        
        if recursive:
            for root, _, files in os.walk(target_dir):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, file)
                        if self.process_file(file_path):
                            changed = True
        else:
            for file in os.listdir(target_dir):
                if any(file.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(target_dir, file)
                    if self.process_file(file_path):
                        changed = True
        
        if changed:
            self._save_index()
            self.generate_summary()
        
        return changed
    
    def generate_summary(self):
        """Generate a markdown summary of all indexed conversations."""
        summary = f"# Conversation Index Summary\n\n"
        summary += f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        if self.use_gemini:
            summary += f"*Summaries generated using Gemini 2.0 Flash*\n\n"
        
        # Summary by model
        summary += "## Models\n\n"
        for model, files in sorted(self.index["models"].items()):
            summary += f"### {model} ({len(files)} conversations)\n\n"
            for file_path in files:
                file_info = self.index["files"][file_path]
                summary += f"- [{os.path.basename(file_path)}]({file_path.replace(' ', '%20')}) - {file_info['summary'][:100]}...\n"
            summary += "\n"
        
        # Top topics
        summary += "## Key Topics\n\n"
        sorted_topics = sorted(self.index["topics"].items(), key=lambda x: len(x[1]), reverse=True)
        for topic, files in sorted_topics[:15]:  # Top 15 topics
            summary += f"### {topic} ({len(files)} conversations)\n\n"
            for file_path in files[:5]:  # Show top 5 files per topic
                file_info = self.index["files"][file_path]
                summary += f"- [{os.path.basename(file_path)}]({file_path.replace(' ', '%20')}) ({file_info['model']})\n"
            if len(files) > 5:
                summary += f"- *...and {len(files) - 5} more*\n"
            summary += "\n"
        
        # Recent conversations
        summary += "## Recent Conversations\n\n"
        recent_files = sorted(
            self.index["files"].items(), 
            key=lambda x: x[1]["last_modified"], 
            reverse=True
        )[:10]  # Most recent 10
        
        for file_path, file_info in recent_files:
            date = datetime.fromisoformat(file_info["last_modified"]).strftime("%Y-%m-%d")
            model = file_info["model"]
            summary += f"- [{os.path.basename(file_path)}]({file_path.replace(' ', '%20')}) - {date} ({model})\n"
            summary += f"  - {file_info['summary'][:150]}...\n"
        
        # Write the summary to a file
        with open(self.summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Generated summary: {self.summary_file}")
        return summary

def main():
    parser = argparse.ArgumentParser(description='Index and summarize LLM conversations')
    parser.add_argument('--dir', type=str, default=None, help='Directory to scan (default: current directory)')
    parser.add_argument('--no-recursive', action='store_true', help='Do not scan subdirectories')
    parser.add_argument('--generate-only', action='store_true', help='Only generate summary without scanning')
    parser.add_argument('--gemini-key', type=str, default=None, help='Gemini API key for improved summaries')
    parser.add_argument('--gemini-key-file', type=str, default=None, help='Path to file containing Gemini API key')
    
    args = parser.parse_args()
    
    # Get Gemini API key from file if specified
    gemini_api_key = args.gemini_key
    if not gemini_api_key and args.gemini_key_file:
        try:
            with open(args.gemini_key_file, 'r') as f:
                gemini_api_key = f.read().strip()
        except Exception as e:
            print(f"⚠️ Failed to read Gemini API key file: {e}")
    
    # Get API key from environment variable if not specified
    if not gemini_api_key:
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
    
    indexer = ConversationIndexer(args.dir, gemini_api_key=gemini_api_key)
    
    if not args.generate_only:
        indexer.scan_directory(recursive=not args.no_recursive)
    else:
        indexer.generate_summary()

if __name__ == "__main__":
    main()
