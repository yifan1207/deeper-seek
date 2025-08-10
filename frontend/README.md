# Satellite Embeddings Similarity Search

An interactive web application for exploring satellite imagery similarity using Google Earth Engine's AI embeddings. Click anywhere on the map to find similar patterns across the globe.

![Demo Screenshot](https://via.placeholder.com/800x400/667eea/ffffff?text=Satellite+Embeddings+Similarity+Search)

## Features

- 🌍 **Interactive Global Map**: Explore satellite imagery with Google Maps integration
- 🔍 **AI-Powered Similarity Search**: Find similar patterns using Earth Engine embeddings
- 🎨 **Multiple Color Palettes**: Choose from Viridis, Plasma, and Inferno color schemes
- 📅 **Temporal Analysis**: Select different years for analysis
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- 🔗 **Shareable URLs**: Bookmark and share specific locations and settings

## Prerequisites

Before running this application, you'll need:

1. **Google Earth Engine Account**: Sign up at [earthengine.google.com](https://earthengine.google.com)
2. **Google Maps API Key**: Get one from [Google Cloud Console](https://console.cloud.google.com)
3. **Modern Web Browser**: Chrome, Firefox, Safari, or Edge

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/satellite-embeddings-similarity-search.git
cd satellite-embeddings-similarity-search
```

### 2. Configure API Keys

Edit `index.html` and replace `YOUR_GOOGLE_MAPS_API_KEY` with your actual Google Maps API key:

```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_ACTUAL_API_KEY"></script>
```

### 3. Start the Development Server

```bash
# Using Python (recommended)
python3 -m http.server 8000

# Or using Node.js
npm start
```

### 4. Open in Browser

Navigate to `http://localhost:8000` in your web browser.

## Usage

### Basic Operation

1. **Load the Application**: The map will load with satellite imagery
2. **Select a Point**: Click anywhere on the map to choose a reference point
3. **Wait for Processing**: The system calculates similarity across the globe
4. **Explore Results**: Similar areas are highlighted in bright colors
5. **Adjust Settings**: Use the control panel to change year or color palette

### Understanding the Visualization

- **Bright Colors**: High similarity to the selected point
- **Dark Colors**: Low similarity to the selected point
- **Color Scale**: Use the legend to interpret similarity values

### Controls

- **Year Selector**: Choose different years for analysis (2022-2024)
- **Color Palette**: Switch between Viridis, Plasma, and Inferno schemes
- **Zoom/Pan**: Standard map navigation controls

## Technical Details

### Architecture

- **Frontend**: Vanilla JavaScript with ES6+ features
- **Mapping**: Google Maps API with Earth Engine integration
- **Styling**: CSS3 with responsive design
- **Data**: Google Earth Engine satellite embeddings

### Key Components

- `index.html`: Main HTML structure
- `styles.css`: Responsive styling and animations
- `app.js`: Core application logic and Earth Engine integration
- `frontend.js`: Original Earth Engine code (reference)

### Earth Engine Integration

The application uses Google Earth Engine's satellite embeddings to:
- Load satellite imagery collections
- Calculate similarity in embedding space
- Generate visualizations
- Handle cloud filtering and data processing

## Deployment

### Static Hosting (Recommended)

This is a static web application that can be deployed to any static hosting service:

#### GitHub Pages

1. Push your code to a GitHub repository
2. Enable GitHub Pages in repository settings
3. Set source to main branch
4. Your site will be available at `https://username.github.io/repository-name`

#### Netlify

1. Connect your GitHub repository to Netlify
2. Set build command to: `echo "Static site"`
3. Set publish directory to: `.`
4. Deploy automatically on push

#### Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Follow the prompts

### Environment Variables

For production deployment, consider using environment variables for API keys:

```javascript
// In app.js
const MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY || 'your-api-key';
```

## Development

### Project Structure

```
satellite-embeddings-similarity-search/
├── index.html          # Main HTML file
├── styles.css          # CSS styles
├── app.js              # Main JavaScript application
├── frontend.js         # Original Earth Engine code
├── package.json        # Node.js configuration
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

### Development Commands

```bash
# Start development server
npm run dev

# Format code
npm run format

# Lint code
npm run lint

# Build for production
npm run build
```

### Customization

#### Adding New Color Palettes

Edit the `palettes` object in `app.js`:

```javascript
this.palettes = {
    viridis: ['000004', '2C105C', '711F81', ...],
    plasma: ['0D0887', '46039F', '7201A8', ...],
    inferno: ['000004', '1B0C41', '4A0C6B', ...],
    // Add your custom palette here
    custom: ['your', 'hex', 'colors', 'here']
};
```

#### Modifying Earth Engine Logic

The core Earth Engine functionality is in the `calculateSimilarity()` method in `app.js`. Modify this to integrate with your specific Earth Engine scripts.

## Troubleshooting

### Common Issues

1. **Map Not Loading**
   - Check your Google Maps API key
   - Ensure billing is enabled for the Maps API
   - Check browser console for errors

2. **Earth Engine Not Working**
   - Verify your Earth Engine account is active
   - Check network connectivity
   - Review browser console for API errors

3. **Performance Issues**
   - Reduce map zoom level
   - Wait for initial loading to complete
   - Check your internet connection

### Debug Mode

Enable debug mode by opening browser console and running:

```javascript
window.app.debug = true;
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Earth Engine team for the satellite embeddings
- Google Maps Platform for mapping services
- Sentinel-2 mission for satellite imagery
- Open source community for tools and libraries

## Support

For support and questions:
- Open an issue on GitHub
- Check the [Earth Engine documentation](https://developers.google.com/earth-engine)
- Review the [Google Maps documentation](https://developers.google.com/maps)

---

**Note**: This application requires active Google Earth Engine and Maps API access. Ensure you have proper authentication and billing set up before deployment.
