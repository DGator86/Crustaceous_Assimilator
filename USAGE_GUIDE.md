# Moltbot Repository Scout - Usage Guide

This guide provides detailed examples of how to use moltbot-repo-scout for discovering and analyzing trading bot repositories.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Basic Usage](#basic-usage)
4. [Advanced Usage](#advanced-usage)
5. [Output Artifacts](#output-artifacts)
6. [Programmatic Usage](#programmatic-usage)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- Git installed on your system
- GitHub account (optional, but recommended)

### Install from Source

```bash
git clone https://github.com/DGator86/Crustaceous_Assimilator.git
cd Crustaceous_Assimilator
pip install -r requirements.txt
pip install -e .
```

### Verify Installation

```bash
moltbot-scout --version
# Output: moltbot-scout, version 0.1.0
```

## Configuration

### Generate Default Configuration

```bash
moltbot-scout init-config
# Creates config.yaml in current directory
```

### Set GitHub Token

For better API rate limits (5000 requests/hour instead of 60):

**Option 1: Environment Variable (Recommended)**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

**Option 2: Configuration File**
Edit `config.yaml`:
```yaml
github:
  token: "ghp_your_token_here"
```

### Customize Configuration

Edit `config.yaml` to customize:

- **Search Queries**: What repositories to search for
- **Scoring Weights**: How to evaluate trustworthiness
- **Security Patterns**: What patterns to detect
- **Output Paths**: Where to save results

## Basic Usage

### Discover Repositories

**Basic discovery with default settings:**
```bash
moltbot-scout discover
```

**Discover with custom query:**
```bash
moltbot-scout discover -q "trading bot python" -q "algorithmic trading"
```

**Limit results:**
```bash
moltbot-scout discover -m 3
# Discover max 3 repositories per query
```

**Filter by score:**
```bash
moltbot-scout discover --min-score 0.5
# Only analyze repos with trust score >= 0.5
```

**Keep cloned repositories:**
```bash
moltbot-scout discover --no-cleanup
# Don't delete cloned repos after analysis
```

### View Statistics

```bash
moltbot-scout stats
```

**Output:**
```
📊 Repository Statistics

Total Repositories: 5
Total Strategies: 12
Total Indicators: 8
Total Security Issues: 3
```

### List Analyzed Repositories

**List all:**
```bash
moltbot-scout list-repos
```

**Filter by quality:**
```bash
moltbot-scout list-repos --min-score 0.7 --max-issues 2
# Show only high-quality, secure repos
```

**Use custom artifacts directory:**
```bash
moltbot-scout list-repos -a /path/to/artifacts
```

## Advanced Usage

### Full Analysis Pipeline

```bash
# Step 1: Initialize configuration
moltbot-scout init-config -c my-config.yaml

# Step 2: Edit configuration to your needs
nano my-config.yaml

# Step 3: Run discovery with custom config
moltbot-scout discover -c my-config.yaml -q "moltbot" --min-score 0.6

# Step 4: Review results
moltbot-scout stats -a artifacts
moltbot-scout list-repos -a artifacts --min-score 0.7
```

### Focused Search Examples

**Find popular Python trading bots:**
```bash
moltbot-scout discover \
  -q "trading bot python stars:>100" \
  -m 5 \
  --min-score 0.5
```

**Find recently updated bots:**
```bash
moltbot-scout discover \
  -q "algorithmic trading pushed:>2025-01-01" \
  -m 10
```

**Find bots with specific features:**
```bash
moltbot-scout discover \
  -q "trading bot backtesting machine learning" \
  -m 5 \
  --min-score 0.4
```

### Custom Configuration Examples

**High Security Settings:**
```yaml
security:
  scan_secrets: true
  scan_patterns: true
  secret_patterns:
    - '(?i)(api[_-]?key|apikey)\s*[:=]\s*[''"][a-zA-Z0-9]{20,}[''"]'
    - '(?i)(secret|password)\s*[:=]\s*[''"][^''"]{8,}[''"]'
    - '(?i)(private[_-]?key|aws[_-]?access)'
  suspicious_patterns:
    - 'eval\s*\('
    - 'exec\s*\('
    - '__import__\s*\('
    - 'subprocess\.'
    - 'os\.system'
```

**Strict Quality Requirements:**
```yaml
scoring:
  weights:
    stars: 0.4        # Emphasize popularity
    license: 0.3      # Emphasize proper licensing
    activity: 0.2     # Emphasize recent activity
    age: 0.05
    commits: 0.05
  min_score: 0.7      # Only high-quality repos
```

## Output Artifacts

After running `discover`, you'll find:

### Directory Structure
```
artifacts/
├── index.json                      # Machine-readable index
├── INDEX.md                        # Human-readable summary
├── username_reponame.json          # Detailed spec for each repo
└── username_reponame.md            # Documentation for each repo
```

### JSON Specification Format

Each repository gets a comprehensive JSON spec:

```json
{
  "metadata": {
    "spec_version": "1.0",
    "generated_at": "2026-01-31T18:00:00Z",
    "repository": {
      "name": "user/trading-bot",
      "url": "https://github.com/user/trading-bot",
      "description": "...",
      "language": "Python",
      "license": "MIT License"
    }
  },
  "trustworthiness": {
    "overall_score": 0.85,
    "level": "high",
    "components": {
      "stars_score": 0.9,
      "age_score": 0.8,
      "commits_score": 0.85,
      "license_score": 1.0,
      "activity_score": 0.95
    }
  },
  "security": {
    "total_issues": 2,
    "secrets_found": 1,
    "suspicious_code_found": 1,
    "issues": { ... }
  },
  "code_analysis": {
    "files_parsed": 15,
    "strategies": [...],
    "indicators": [...],
    "risk_management": [...],
    "summary": {
      "total_strategies": 3,
      "total_indicators": 5,
      "total_risk_functions": 2
    }
  }
}
```

### Markdown Documentation

Human-readable documentation includes:

- Repository metadata and links
- Trustworthiness analysis breakdown
- Security scan summary
- Detailed code analysis
- Lists of discovered strategies and indicators

### Index Report

The `INDEX.md` file provides a summary of all analyzed repositories:

```markdown
# Moltbot Repository Scout - Index Report

## Statistics
- Total Repositories: 5
- Total Strategies: 12
- Total Indicators: 8

## Repositories

### user/high-quality-bot
- Trust Score: 0.85 (high)
- Security Issues: 1
- Strategies: 3
- Indicators: 2

### user/another-bot
...
```

## Programmatic Usage

### Python API Example

```python
from moltbot_scout.config import Config
from moltbot_scout.discovery import RepoDiscovery
from moltbot_scout.scoring import RepoScorer
from moltbot_scout.cloner import SafeCloner
from moltbot_scout.security import SecurityScanner
from moltbot_scout.parser import StrategyParser
from moltbot_scout.normalizer import SpecNormalizer
from moltbot_scout.indexer import ArtifactIndexer

# Initialize components
config = Config()
discovery = RepoDiscovery(github_token="your_token")
scorer = RepoScorer()
cloner = SafeCloner()
scanner = SecurityScanner()
parser = StrategyParser()
normalizer = SpecNormalizer()
indexer = ArtifactIndexer()

# Discover repositories
repos = discovery.discover(['trading bot python'])

# Analyze first repository
repo = repos[0]

# Score it
score_info = scorer.score_repository(repo)
print(f"Score: {score_info['overall_score']}")

# Clone it
clone_result = cloner.clone_repository(repo['clone_url'], repo['full_name'])

if clone_result['success']:
    # Scan for security issues
    security_info = scanner.scan_repository(clone_result['path'])
    
    # Parse code
    parsed_info = parser.parse_repository(clone_result['path'])
    
    # Create spec
    spec = normalizer.normalize(repo, score_info, security_info, parsed_info)
    
    # Save artifacts
    normalizer.save_spec(spec, f"artifacts/{repo['full_name']}.json")
    normalizer.save_markdown_doc(spec, f"artifacts/{repo['full_name']}.md")
    
    # Add to index
    indexer.add_repository(repo['full_name'], spec, 
                          f"artifacts/{repo['full_name']}.json",
                          f"artifacts/{repo['full_name']}.md")
    
    # Cleanup
    cloner.cleanup_repository(repo['full_name'])
```

### Custom Scoring Example

```python
from moltbot_scout.scoring import RepoScorer

# Create scorer with custom weights
custom_scorer = RepoScorer(weights={
    'stars': 0.5,      # Very important
    'license': 0.3,    # Important
    'activity': 0.2,   # Somewhat important
    'age': 0.0,        # Not important
    'commits': 0.0     # Not important
})

repo_info = {
    'stars': 200,
    'license': 'MIT License',
    'pushed_at': '2026-01-30T12:00:00Z',
    # ... other fields
}

score = custom_scorer.score_repository(repo_info)
print(f"Custom score: {score['overall_score']}")
```

## Troubleshooting

### Common Issues

**Issue: GitHub API Rate Limit**
```
Error: 403 Forbidden
```
**Solution:** Set a GitHub token via environment variable or config file.

**Issue: Clone Timeout**
```
Error: Clone timeout exceeded
```
**Solution:** Increase timeout in config.yaml:
```yaml
cloner:
  timeout: 600  # 10 minutes
```

**Issue: No Repositories Found**
```
Found 0 repositories
```
**Solution:** 
- Check your search query is valid
- Ensure GitHub token is set (if using)
- Try broader search terms

**Issue: Permission Denied**
```
Permission denied: artifacts/
```
**Solution:** Ensure the output directory is writable or specify a different path.

### Debug Mode

Run with verbose output:
```bash
# Enable Python logging
export PYTHONVERBOSE=1
moltbot-scout discover -q "test" -m 1
```

### Testing Without GitHub API

Use the test script to verify functionality:
```bash
python test_functionality.py
```

## Best Practices

1. **Always use a GitHub token** for better rate limits
2. **Start with small result sets** (`-m 2`) to test queries
3. **Use meaningful search queries** to find relevant repositories
4. **Review security scan results** before using any code
5. **Check trustworthiness scores** to prioritize quality repositories
6. **Keep artifacts organized** by using descriptive output directories
7. **Clean up cloned repos** unless you need them for further analysis

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/DGator86/Crustaceous_Assimilator/issues
- Documentation: See README.md
- Examples: See example.py and test_functionality.py

## License

MIT License - See LICENSE file for details
