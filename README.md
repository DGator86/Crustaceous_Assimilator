# Moltbot Repository Scout

A Python tool for discovering, analyzing, and indexing GitHub repositories related to Moltbot and trading bots.

## Features

- 🔍 **Repository Discovery**: Searches GitHub for repositories related to Moltbot and trading bots
- ⭐ **Trustworthiness Scoring**: Evaluates repositories based on stars, age, commits, license, and activity
- 🔒 **Safe Cloning**: Clones repositories without executing any code (hooks disabled)
- 🛡️ **Security Scanning**: Performs static analysis to detect secrets and suspicious patterns
- 📊 **AST-based Parsing**: Extracts strategies, indicators, and risk logic without importing code
- 📝 **JSON Specifications**: Normalizes findings into standardized JSON specs
- 📚 **Artifact Indexing**: Maintains an organized index of analyzed repositories
- 🖥️ **CLI Interface**: Easy-to-use command-line interface

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/DGator86/Crustaceous_Assimilator.git
cd Crustaceous_Assimilator

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Requirements

- Python 3.8 or higher
- Git installed on the system
- GitHub API token (optional, but recommended for higher rate limits)

## Quick Start

### 1. Initialize Configuration

```bash
moltbot-scout init-config
```

This creates a `config.yaml` file with default settings.

### 2. Set GitHub Token (Optional)

For better API rate limits, set your GitHub token:

```bash
export GITHUB_TOKEN="your_github_token_here"
```

Or edit `config.yaml` and add your token.

### 3. Discover and Analyze Repositories

```bash
# Basic usage
moltbot-scout discover

# With custom queries
moltbot-scout discover -q "moltbot" -q "trading bot python" --max-results 10

# With minimum score filter
moltbot-scout discover --min-score 0.5
```

### 4. View Results

```bash
# Show statistics
moltbot-scout stats

# List all indexed repositories
moltbot-scout list-repos

# List high-quality repositories only
moltbot-scout list-repos --min-score 0.7 --max-issues 5
```

## Usage

### Discovery Command

The `discover` command searches for repositories and performs full analysis:

```bash
moltbot-scout discover [OPTIONS]

Options:
  -c, --config PATH       Path to config file
  -t, --token TEXT        GitHub API token
  -q, --query TEXT        Search query (multiple allowed)
  -m, --max-results INT   Maximum results per query (default: 5)
  -s, --min-score FLOAT   Minimum trustworthiness score (default: 0.3)
  --cleanup/--no-cleanup  Clean up cloned repos after analysis (default: True)
```

### Statistics Command

View overall statistics:

```bash
moltbot-scout stats [OPTIONS]

Options:
  -a, --artifacts-dir PATH  Artifacts directory (default: artifacts)
```

### List Repositories Command

List indexed repositories with filtering:

```bash
moltbot-scout list-repos [OPTIONS]

Options:
  -a, --artifacts-dir PATH  Artifacts directory (default: artifacts)
  -s, --min-score FLOAT     Minimum trustworthiness score
  -i, --max-issues INT      Maximum security issues
```

## Configuration

The `config.yaml` file controls all aspects of the tool:

### GitHub Settings
- `token`: GitHub API token
- `search_queries`: List of search terms
- `max_results_per_query`: Number of results per query

### Scoring Settings
- `weights`: Relative importance of scoring factors
- `min_score`: Minimum threshold for analysis

### Cloner Settings
- `clone_dir`: Where to clone repositories
- `max_depth`: Git clone depth (shallow clone)
- `timeout`: Clone operation timeout

### Security Settings
- `scan_secrets`: Enable/disable secret scanning
- `scan_patterns`: Enable/disable suspicious code scanning
- `secret_patterns`: Regex patterns for secrets
- `suspicious_patterns`: Regex patterns for suspicious code

### Parser Settings
- `file_extensions`: Which files to parse
- `max_file_size`: Maximum file size for parsing
- Feature toggles for extraction

### Output Settings
- `artifacts_dir`: Where to save results
- `index_file`: Path to index file

## Output Structure

After running discovery, you'll find:

```
artifacts/
├── index.json              # Master index of all repositories
├── INDEX.md                # Human-readable index report
├── owner_repo.json         # JSON spec for each repository
└── owner_repo.md           # Markdown documentation for each repository
```

### JSON Specification Format

Each repository gets a JSON spec with:
- **metadata**: Repository information
- **trustworthiness**: Overall score and component scores
- **security**: Scan results and issues
- **code_analysis**: Strategies, indicators, and risk management functions

### Markdown Documentation

Human-readable documentation including:
- Repository information
- Trustworthiness analysis
- Security scan results
- Code analysis summary
- Detailed listings of strategies and indicators

## Architecture

The tool is organized into focused modules:

- **discovery**: GitHub API integration for repository search
- **scoring**: Multi-factor trustworthiness evaluation
- **cloner**: Safe repository cloning without execution
- **security**: Static security scanning
- **parser**: AST-based code analysis
- **normalizer**: JSON specification generation
- **indexer**: Artifact organization and indexing
- **cli**: Command-line interface

## Safety Features

- **No Code Execution**: Clones repositories without running any code
- **Hook Disabling**: Automatically disables Git hooks
- **Shallow Clones**: Uses minimal depth to reduce attack surface
- **Static Analysis**: Only analyzes code structure via AST
- **No Imports**: Never imports or executes discovered code
- **Sandboxed**: All operations are file-system based

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Formatting

```bash
black src/
flake8 src/
```

### Type Checking

```bash
mypy src/
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security

If you discover a security vulnerability, please email security@example.com instead of using the issue tracker.

## Credits

Created by DGator86 for the Moltbot trading bot community.