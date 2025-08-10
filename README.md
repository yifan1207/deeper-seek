# Deeper Seek

A geospatial similarity search tool that uses Google Earth Engine satellite imagery embeddings to find visually similar locations on Earth.

## Features

- Interactive map interface for location selection
- Satellite imagery similarity search using Google Earth Engine
- Real-time heatmap visualization of similarity scores
- Responsive web interface with query capabilities

## Setup

### Prerequisites

- Python 3.11+
- Google Earth Engine account and authentication
- Modern web browser

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yifan1207/deeper-seek.git
cd deeper-seek
```

2. Install Python dependencies:
```bash
pip install -e .
```

3. Set up Google Earth Engine authentication:
```bash
earthengine authenticate
```

## Usage

The main interface is available in the `frontend_old/geoguessr.html` file. Open it in a web browser to start exploring geospatial similarity search.

### Query Interface

- Click on any location on the map to generate a similarity heatmap
- Use the query box to describe locations you're looking for
- View satellite imagery thumbnails of selected locations

## Project Structure

- `frontend_old/` - Web interface and visualization tools
- `training/` - Machine learning training scripts (in development)
- `pyproject.toml` - Python project configuration

## Contributing

This project is in active development. Feel free to open issues or submit pull requests.

## License

See LICENSE file for details.
