# Moltbot Repository Scout - Architecture

This document describes the architecture and design of moltbot-repo-scout.

## Overview

Moltbot Repository Scout is a modular Python application designed to discover, analyze, and catalog GitHub repositories related to trading bots and algorithmic trading strategies. It follows a pipeline architecture with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface (cli.py)                   │
│  Commands: discover, init-config, stats, list-repos         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Configuration (config.py)                   │
│  - YAML-based configuration                                  │
│  - Environment variable support                              │
│  - Default settings management                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Pipeline Modules                           │
├──────────────────┬──────────────────────┬───────────────────┤
│   Discovery      │      Scoring         │    Cloning        │
│  (discovery/)    │     (scoring/)       │   (cloner/)       │
│                  │                      │                   │
│ - GitHub API     │ - Multi-factor       │ - Safe clone      │
│ - Search repos   │   scoring            │ - Hook disable    │
│ - Extract info   │ - Trustworthiness    │ - Cleanup         │
└──────────────────┴──────────────────────┴───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Analysis Modules                            │
├──────────────────┬──────────────────────┬───────────────────┤
│    Security      │      Parser          │   Normalizer      │
│  (security/)     │     (parser/)        │  (normalizer/)    │
│                  │                      │                   │
│ - Secret scan    │ - AST parsing        │ - JSON specs      │
│ - Pattern match  │ - Strategy extract   │ - Markdown docs   │
│ - Static only    │ - No imports         │ - Normalization   │
└──────────────────┴──────────────────────┴───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Indexing & Output (indexer/)                 │
│  - Repository index management                               │
│  - Artifact organization                                     │
│  - Report generation                                         │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Output Artifacts                          │
│  - JSON specifications                                       │
│  - Markdown documentation                                    │
│  - Master index                                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. CLI Interface (`src/moltbot_scout/cli.py`)

**Purpose**: Provides command-line interface for all functionality.

**Commands**:
- `discover`: Main pipeline for finding and analyzing repositories
- `init-config`: Generate default configuration file
- `stats`: Display statistics from indexed repositories
- `list-repos`: List and filter analyzed repositories

**Technology**: Click framework for CLI management

### 2. Configuration System (`src/moltbot_scout/config.py`)

**Purpose**: Centralized configuration management.

**Features**:
- YAML-based configuration
- Environment variable overrides
- Default settings
- Dot-notation access (e.g., `config.get('github.token')`)
- Validation and persistence

**Configuration Sections**:
- GitHub API settings
- Scoring weights
- Clone parameters
- Security patterns
- Parser settings
- Output paths

### 3. Discovery Module (`src/moltbot_scout/discovery/`)

**Purpose**: Find relevant repositories on GitHub.

**Functionality**:
- GitHub API integration via PyGithub
- Repository search with custom queries
- Metadata extraction
- Rate limit handling
- Deduplication

**Key Methods**:
- `discover(queries)`: Search for repositories
- `_search_repos(query)`: Execute single query
- `_extract_repo_info(repo)`: Extract repository metadata

### 4. Scoring Module (`src/moltbot_scout/scoring/`)

**Purpose**: Evaluate repository trustworthiness.

**Scoring Factors**:
- **Stars**: Popularity (logarithmic scale)
- **Age**: Repository maturity
- **Commits**: Development activity (proxy via size)
- **License**: Presence and type
- **Activity**: Recent updates

**Algorithm**:
- Weighted combination of normalized scores (0-1)
- Configurable weights
- Logarithmic scaling for stars/commits
- Time-based scoring for age/activity

**Output**:
- Overall score (0-1)
- Component scores
- Trustworthiness level (low, medium, high, etc.)

### 5. Cloner Module (`src/moltbot_scout/cloner/`)

**Purpose**: Safely clone repositories without code execution.

**Safety Features**:
- Shallow clones (depth=1)
- Git hook disabling
- No code execution
- Configurable timeout
- Cleanup support

**Key Methods**:
- `clone_repository(url, name)`: Clone with safety checks
- `_disable_hooks(path)`: Prevent hook execution
- `cleanup_repository(name)`: Remove cloned repo

### 6. Security Scanner (`src/moltbot_scout/security/`)

**Purpose**: Static security analysis of cloned repositories.

**Detection Types**:
- **Secrets**: API keys, passwords, tokens (regex-based)
- **Suspicious Code**: eval, exec, system calls (pattern matching)

**Features**:
- File-by-file scanning
- Regex pattern matching
- Line number tracking
- Context extraction
- Configurable patterns

**Output**:
- Files scanned count
- Secrets found with locations
- Suspicious code with patterns
- Total issues count

### 7. Parser Module (`src/moltbot_scout/parser/`)

**Purpose**: Extract trading strategies and indicators from Python code.

**Technology**: Python AST (Abstract Syntax Tree) parsing

**Extraction Targets**:
- Strategy classes and functions
- Technical indicators (SMA, EMA, RSI, etc.)
- Risk management functions
- General classes and functions

**Safety**:
- No code execution
- No imports
- Pure AST analysis
- Syntax error handling

**Detection Method**:
- Keyword matching in names (strategy, indicator, risk, etc.)
- Class/function signature analysis
- Docstring extraction

### 8. Normalizer Module (`src/moltbot_scout/normalizer/`)

**Purpose**: Convert raw analysis data into standardized formats.

**Output Formats**:
- **JSON Specification**: Machine-readable structured data
- **Markdown Documentation**: Human-readable reports

**Normalization**:
- Standardized schema (version 1.0)
- Metadata organization
- Summary statistics
- Component-level details

**Spec Structure**:
```
metadata/
├── spec_version
├── generated_at
└── repository/

trustworthiness/
├── overall_score
├── level
├── components/
└── metrics/

security/
├── scanned
├── total_issues
└── issues/

code_analysis/
├── files_parsed
├── strategies[]
├── indicators[]
├── risk_management[]
└── summary/
```

### 9. Indexer Module (`src/moltbot_scout/indexer/`)

**Purpose**: Organize and catalog analyzed repositories.

**Features**:
- Master index (JSON)
- Repository entries with metadata
- Statistics tracking
- Filtering capabilities
- Index report generation

**Index Structure**:
```json
{
  "version": "1.0",
  "created_at": "...",
  "updated_at": "...",
  "repositories": [...],
  "stats": {
    "total_repositories": 0,
    "total_strategies": 0,
    "total_indicators": 0,
    "total_security_issues": 0
  }
}
```

## Data Flow

### Discovery Pipeline

```
1. User runs `moltbot-scout discover`
   ↓
2. Load configuration (config.yaml or defaults)
   ↓
3. Initialize all components
   ↓
4. FOR EACH search query:
     ↓
   5. Query GitHub API
     ↓
   6. Extract repository metadata
     ↓
   7. Score repository
     ↓
   8. IF score >= min_score:
        ↓
      9. Clone repository safely
        ↓
     10. Scan for security issues
        ↓
     11. Parse code with AST
        ↓
     12. Normalize to JSON/MD
        ↓
     13. Save artifacts
        ↓
     14. Add to index
        ↓
     15. Cleanup clone (if enabled)
   ↓
16. Generate index report
   ↓
17. Display summary
```

## Design Principles

### 1. Safety First
- No code execution at any stage
- Static analysis only
- Git hooks disabled
- Shallow clones
- Sandboxed operations

### 2. Modularity
- Each component has single responsibility
- Clear interfaces between modules
- Independently testable
- Easy to extend

### 3. Configuration-Driven
- All parameters configurable
- Sensible defaults
- Environment variable support
- YAML-based config

### 4. Transparency
- Detailed logging
- Comprehensive output
- Source tracking (file:line)
- Audit trail

### 5. Usability
- CLI for common tasks
- Programmatic API
- Clear documentation
- Example scripts

## Extension Points

### Adding New Search Providers
Create new discovery module implementing:
- `discover(queries) -> List[Dict]`
- Repository info extraction

### Custom Scoring Algorithms
Extend `RepoScorer`:
- Override `score_repository()`
- Add new component scores
- Adjust weights dynamically

### Additional Security Checks
Extend `SecurityScanner`:
- Add patterns to config
- Implement custom scanners
- Plugin architecture possible

### New Code Analyzers
Extend `StrategyParser`:
- Additional AST visitors
- Language-specific parsers
- Custom extraction logic

### Output Formats
Extend `SpecNormalizer`:
- Additional output formats (XML, CSV, etc.)
- Custom report templates
- Integration formats

## Technology Stack

- **Language**: Python 3.8+
- **CLI**: Click
- **GitHub API**: PyGithub
- **Git Operations**: GitPython
- **Configuration**: PyYAML
- **AST Parsing**: Python stdlib `ast`
- **Regex**: Python stdlib `re`

## File Structure

```
Crustaceous_Assimilator/
├── README.md                    # Main documentation
├── USAGE_GUIDE.md              # Usage examples
├── ARCHITECTURE.md             # This file
├── LICENSE                     # MIT License
├── setup.py                    # Package setup
├── requirements.txt            # Dependencies
├── config.yaml                 # Default config
├── example.py                  # Example usage
├── test_functionality.py       # Comprehensive tests
└── src/
    └── moltbot_scout/
        ├── __init__.py         # Package init
        ├── cli.py              # CLI interface
        ├── config.py           # Configuration
        ├── discovery/          # GitHub discovery
        │   └── __init__.py
        ├── scoring/            # Trustworthiness scoring
        │   └── __init__.py
        ├── cloner/             # Safe cloning
        │   └── __init__.py
        ├── security/           # Security scanning
        │   └── __init__.py
        ├── parser/             # AST parsing
        │   └── __init__.py
        ├── normalizer/         # Spec generation
        │   └── __init__.py
        └── indexer/            # Artifact indexing
            └── __init__.py
```

## Security Considerations

### Threat Model

**Threats Mitigated**:
- Malicious code execution during clone
- Hook-based attacks
- Import-time side effects
- Large repository DoS

**Implementation**:
- No code execution
- Hook disabling
- Shallow clones
- File size limits
- Timeout protection

### Static Analysis Only

All analysis is performed via:
- AST parsing (Python `ast` module)
- Regex pattern matching
- File metadata inspection

No dynamic analysis or code execution.

## Performance Considerations

### Rate Limiting
- GitHub API: 5000/hour (authenticated), 60/hour (anonymous)
- Built-in delay between requests
- Configurable via timeouts

### Resource Management
- Shallow clones minimize disk usage
- File size limits prevent memory issues
- Cleanup removes temporary data
- Parallel-safe design

### Scalability
- Process repositories sequentially
- Configurable result limits
- Incremental indexing
- Resumable operations (via index)

## Future Enhancements

Potential improvements:
- Multi-language support (JavaScript, Go, etc.)
- Machine learning for strategy classification
- Dependency vulnerability scanning
- Backtesting framework integration
- Web UI
- Database backend
- Distributed processing
- Docker containerization

## License

MIT License - See LICENSE file for details
