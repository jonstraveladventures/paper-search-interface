# Paper Search Interface

A comprehensive web interface for searching through 200,000+ academic papers from major AI/ML conferences. This tool allows researchers to easily filter and search papers by title, authors, countries, venues, and publication years.

This data originally comes from https://github.com/papercopilot/paperlists

This repo was built using Cursor.

## Features

- **206,459 papers** from major AI/ML conferences (1987-2025)
- **Interactive search** by title and author names
- **Geographic filtering** by countries and continents
- **Venue filtering** by conference and research subfield
- **Year range selection** (1987-2025)
- **Comprehensive paper information** with status indicators
- **Color-coded status indicators** (accepted, rejected, withdrawn)
- **Bulk selection options** for countries and venues

## Conferences Included

### Artificial Intelligence
- NIPS/NeurIPS, ICLR, ICML, AAAI, IJCAI, AISTATS, CoRL, ACML

### Computational Linguistics
- ACL, EMNLP, NAACL, COLING, ARR, COLM

### Computer Vision
- CVPR, ICCV, WACV

### Computer Graphics
- SIGGRAPH, SIGGRAPH Asia

### Data Mining
- KDD

### Databases & Information Systems
- WWW

### Multimedia
- ACMMM

### Robotics
- ICRA, IROS, RSS

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jonstraveladventures/paper-search-interface.git
   cd paper-search-interface
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Generate the data files:**
```bash
   python tools/combine_papers.py
```

5. **Run the application:**
```bash
   python run.py
   ```

6. **Open your browser:**
   Navigate to `http://localhost:5001`

## Usage

### Basic Search
- **Title Search**: Enter keywords to search paper titles
- **Author Search**: Search for specific authors
- **Year Range**: Use the sliders to filter by publication year

### Advanced Filtering

#### Countries
- Click on continent headers to expand/collapse
- Use "Select All [Continent]" buttons for bulk selection
- Use "Select All African Countries" for African research focus
- Individual country checkboxes for precise filtering

#### Venues
- Venues are organized by research subfield
- Use "Select All [Subfield]" buttons for entire research areas
- Individual venue checkboxes for specific conferences

#### Paper Information
- **Status indicators** show paper acceptance status:
  - 🟢 Green: Accepted papers
  - 🔴 Red: Rejected papers
  - 🟡 Yellow: Withdrawn papers
  - ⚫ Gray: Unknown status

## Data Sources

The dataset includes papers from major AI/ML conferences spanning 1987-2025. Each paper entry contains:
- Title and authors
- Conference and year
- Research subfield classification
- Author institutions and countries
- Paper status and track
- Citation count

### Original Data Attribution
The original paper data was sourced from [Paper Copilot](https://papercopilot.com), a comprehensive research toolbox that collects and visualizes academic paper data from major AI/ML conferences. Paper Copilot provides data from OpenReview, official conference sites, and community sources, making it an invaluable resource for the research community.

## Project Structure

```
paper-search-interface/
├── tools/
│   ├── web_interface.py          # Flask web application
│   ├── combine_papers.py         # Data processing script
│   ├── templates/
│   │   └── index.html           # Web interface template
│   └── requirements.txt         # Python dependencies
├── all_papers.csv               # Combined dataset (generated locally)
├── african_papers.csv           # African papers subset (generated locally)
├── [name]_papers.csv            # Papers by specific author (generated locally)
├── unique_countries.txt         # List of all countries (generated locally)
├── african_countries.txt        # African countries list (generated locally)
├── mathematica_data.txt         # Data for Mathematica visualization (generated locally)
└── README.md                    # This file
```

## API Endpoints

- `GET /` - Main interface
- `GET /search` - Search API with query parameters:
  - `title` - Title search keywords
  - `author` - Author search keywords
  - `countries[]` - Array of selected countries
  - `venues[]` - Array of selected venues
  - `year_min` - Minimum year
  - `year_max` - Maximum year

## Development

### Adding New Data
1. Place new JSON files in appropriate conference folders
2. Run `python tools/combine_papers.py` to regenerate the CSV
3. Restart the web interface

### Data Generation
The repository includes scripts to generate various data files:
- `python tools/combine_papers.py` - Creates the main CSV file
- `python tools/extract_countries.py` - Extracts unique countries
- `python tools/filter_african_papers.py` - Creates African papers subset
- `python tools/find_name_papers.py [name]` - Finds papers by specific author name
- `python tools/generate_mathematica_data.py` - Creates Mathematica data

### Customizing the Interface
- Modify `tools/templates/index.html` for UI changes
- Update `tools/web_interface.py` for backend logic
- Add new subfields in the `get_subfield()` function

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Original Data**: Sourced from [Paper Copilot](https://papercopilot.com), a comprehensive research toolbox that collects and visualizes academic paper data from major AI/ML conferences
- **Data Sources**: OpenReview, official conference sites, and community sources
- **Technology**: Built with Flask, Pandas, and modern web technologies
- **Community**: Special thanks to the research community for making this data available

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

