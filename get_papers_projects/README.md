# Get Papers

A Python tool to fetch PubMed research papers with at least one author affiliated with a pharmaceutical or biotech company.

## Code Organization
- `get_papers/api.py`: Contains the `PaperFetcher` class handling API calls and data processing.
- `get_papers/cli.py`: Command-line interface using the API module.
- `pyproject.toml`: Poetry configuration for dependencies and script execution.

## Installation
1. Ensure you have [Poetry](https://python-poetry.org/) installed.
2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/get-papers-project.git
   cd get-papers-project