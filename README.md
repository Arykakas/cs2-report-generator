# CS2 Report

CS2 Report is a Streamlit application that analyzes Counter-Strike 2 demo files and generates detailed player performance reports with interactive visualizations.

## Features

- **Interactive Bullet Heatmaps**: Visualize where players hit their targets
- **Weapon Categorization**: Group hits by weapon type for better analysis
- **Detailed Statistics**: Comprehensive player performance metrics
- **500MB Demo File Support**: Handle large demo files efficiently

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

You can run the application in two ways:

#### Method 1: Using Batch File (Recommended)
1. Place your `.dem` demo file in the project directory
2. Run `run_streamlit_app.bat` 
3. The application will automatically launch in your browser

#### Method 2: Direct Streamlit Command
```bash
streamlit run app.py
```

### Generating Reports

1. Upload a `.dem` demo file using the file uploader
2. Enter the player's Steam ID
3. Click "Generate Report" to create the analysis
4. View interactive visualizations including bullet heatmaps and weapon statistics

## Project Structure

```
cs2-report/
├── app.py                 # Main Streamlit application
├── report.py              # Core reporting logic
├── run_streamlit_app.bat  # Batch file to run the Streamlit app
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── cs2_report/            # Main package directory
    ├── __init__.py
    ├── analysis/
    │   └── hits.py        # Hit analysis and visualization logic
    ├── rendering/
    │   └── html.py        # HTML generation for visualizations
    └── constants.py       # Application constants
```

## Development

### Creating New Features

To work on new features:
1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Commit and push to your branch
4. Create a pull request

### Bullet Hole Visualization

The bullet hole visualization has been updated with:
- Reduced bullet hole size by 50% (from 28 to 11 pixels)
- Maintained all visual enhancements (colors, opacity, white border effects)
- Fixed JavaScript syntax errors that were preventing report generation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.