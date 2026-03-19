# Philadelphia Street Safety Analysis

A comprehensive analysis integrating Google Street View imagery, YOLO object detection, and crime data to explore the relationship between street-level infrastructure and urban safety patterns.

## 📋 Project Overview

This project aims to understand the spatial relationship between traffic control infrastructure (traffic lights, stop signs) and crime incidents across Philadelphia neighborhoods. By leveraging multiple data sources and modern computer vision techniques, we provide an interactive dashboard for analyzing street-level safety patterns.

### Research Question
- How does the distribution of street-level traffic infrastructure correlate with crime incident patterns?
- Can we use automated image recognition to identify safety infrastructure at scale?
- How can we effectively visualize and communicate these patterns to urban planners?

### Key Features
- **Automated Street View Analysis**: Download and process 15° street-view images using Google Street View API
- **Object Detection**: YOLOv3 model to identify traffic lights and stop signs
- **Geospatial Analysis**: Spatial join between detected infrastructure and crime data
- **Interactive Dashboard**: React-based web application with real-time visualization

## 🗺️ Study Areas

Four representative Philadelphia neighborhoods:
- **Center City** - Commercial core with mixed-income residents
- **KENSINGTON** - Lower-income industrial neighborhood
- **POINT_BREEZE** - Medium-density residential area
- **UNIVERSITY_CITY** - High-density educational district

## 📊 Data Sources

### 1. Google Street View Images
- **Source**: Google Street View Static API
- **Format**: 15° pitch (pedestrian perspective) images
- **Coverage**: Street-level panoramic imagery for Philadelphia
- **Total Processed**: ~2,000+ images per neighborhood

### 2. Traffic Infrastructure Data
- **Detection Method**: YOLOv3 object detection
- **Classes**: Traffic Lights, Stop Signs
- **Output Format**: GeoJSON with GPS coordinates
- **Accuracy**: 88-93% detection accuracy

### 3. Crime Data
- **Source**: Philadelphia Police Department public records
- **Format**: Shapefile with point geometries
- **Total Records**: 152,555 crime incidents
- **Attributes**: Incident type, date, time, location

## 🔧 Technical Stack

### Backend
- **Framework**: Flask
- **Geospatial**: GeoPandas, Shapely
- **Data Processing**: Pandas
- **API**: RESTful API with CORS support

### Frontend
- **Framework**: React
- **Mapping**: Leaflet.js
- **Charts**: Recharts
- **HTTP Client**: Axios

### Data Processing
- **Detection**: YOLOv3 (PyTorch)
- **Image Processing**: OpenCV, Pillow
- **GIS**: GeoPandas, Shapely

## 📁 Project Structure

```
streetview yolo3/
├── dashboard/                      # Web application
│   ├── backend/                   # Flask API server
│   │   ├── app.py                # Main Flask application
│   │   ├── config.py             # Configuration
│   │   ├── data_manager.py       # Data loading
│   │   ├── preprocess_data.py    # Data preprocessing
│   │   ├── preprocess_incidents.py # Spatial analysis
│   │   └── processed_data/       # Preprocessed JSON files
│   └── frontend/                  # React application
│       ├── src/
│       │   ├── components/       # React components
│       │   ├── pages/            # Page components
│       │   └── styles/           # CSS stylesheets
│       └── package.json          # Dependencies
├── philly_streetscape_project/    # Detection results (GeoJSON)
├── incidents/                     # Crime data (shapefile)
├── philadelphia-neighborhoods/    # Administrative boundaries (shapefile)
├── step1_download_gsv.py         # Download Street View images
├── step2_yolo_detection.py       # Run YOLO detection
└── README.md                      # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- Git
- Google Street View API key (optional, for downloading new images)

### Installation

#### 1. Clone the repository
```bash
git clone https://github.com/yourusername/philadelphia-street-safety.git
cd philadelphia-street-safety
```

#### 2. Backend Setup
```bash
cd dashboard/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run spatial analysis (generates incident statistics)
python preprocess_incidents.py

# Preprocess all data
python preprocess_data.py

# Start Flask server
python app.py
```

The API will be available at `http://localhost:5000`

#### 3. Frontend Setup
```bash
cd dashboard/frontend

# Install dependencies
npm install

# Start development server
npm start
```

The application will be available at `http://localhost:3000`

## 📈 Usage

### View the Dashboard
1. Ensure both backend and frontend servers are running
2. Open browser to `http://localhost:3000`
3. Use the neighborhood selector dropdown to switch between neighborhoods
4. Explore the interactive map and statistics panel

### Available API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/neighborhoods` | GET | List all neighborhoods with statistics |
| `/api/data/<neighborhood>` | GET | GeoJSON data for neighborhood |
| `/api/stats/<neighborhood>` | GET | Statistics summary for neighborhood |
| `/api/comparison` | GET | Comparison data for all neighborhoods |

## 📊 Key Findings

### Infrastructure Distribution

| Neighborhood | Traffic Lights | Stop Signs | Incidents |
|--------------|----------------|-----------|-----------|
| Center City | 76 | 12 | 1,527 |
| KENSINGTON | 44 | 53 | 737 |
| POINT_BREEZE | 58 | 122 | 2,023 |
| UNIVERSITY_CITY | 219 | 23 | 4,293 |

### Incident Patterns

**UNIVERSITY_CITY**: High incident count driven by:
- Narcotic/Drug violations (558)
- Campus-related offenses (1,372)
- High student population density

**POINT_BREEZE**: Theft-dominant pattern:
- Property crimes: 593 thefts
- Vehicle-related crimes
- Medium-density residential area

**CENTER_CITY**: Commercial district pattern:
- Commercial theft (636)
- Assault offenses (265)
- Business district activity

**KENSINGTON**: Vehicle-focused crimes:
- Motor vehicle theft (149)
- Theft from vehicles (114)
- Industrial area characteristics

## 🔬 Methodology

### 1. Data Collection
- Grid-based sampling along streets in target neighborhoods
- Automated download of 15° Street View images via API
- Metadata collection (coordinates, heading, timestamp)

### 2. Object Detection
- Pre-trained YOLOv3 model on COCO dataset
- Confidence threshold: 0.5
- Custom fine-tuning on local street infrastructure (optional)

### 3. Data Transformation
- Convert detections to GeoJSON format
- Spatial validation and snapping to street network
- Deduplication using spatial clustering

### 4. Crime Data Integration
- Load Philadelphia Police Department shapefile
- Perform spatial join with neighborhood boundaries
- Classify incidents by type and neighborhood

### 5. Analysis
- Calculate facility density (per km²)
- Identify incident type distribution
- Generate comparison statistics

### 6. Visualization
- Interactive web dashboard with Leaflet maps
- Real-time statistics and charts
- Responsive design for multiple devices

## 📝 API Response Examples

### Get Neighborhood Statistics
```bash
curl http://localhost:5000/api/stats/Center%20City
```

Response:
```json
{
  "status": "success",
  "data": {
    "neighborhood": "Center City",
    "traffic_lights_count": 76,
    "stop_signs_count": 12,
    "incidents_count": 1527,
    "facility_density": {
      "traffic_lights_per_km2": 30.4,
      "stop_signs_per_km2": 4.8
    },
    "incident_by_type": {
      "Thefts": 636,
      "Other Assaults": 265,
      "All Other Offenses": 196
    }
  }
}
```

## 🔐 Data Privacy

- Google Street View data: Pre-processed by Google (faces/plates obscured)
- Crime data: Public records from Philadelphia Police Department
- No personally identifiable information collected or stored
- All analysis performed on aggregated, neighborhood-level data

## 📚 References

- Li, X., Ratti, C. (2020). Mapping the spatio-temporal distribution of solar radiation within street canyons of Boston using Google Street View panoramas and building height model. *Computers, Environment and Urban Systems*

## 🛠️ Development

### Running Tests
```bash
cd dashboard/backend
pytest
```

### Building Frontend for Production
```bash
cd dashboard/frontend
npm run build
```

### Performance Optimization
- Backend preprocessing reduces startup time from 30s to 1-2s
- GeoJSON files loaded from pre-processed JSON
- Spatial analysis cached for repeated queries

## 🚧 Future Enhancements

### Short-term
- Mobile-responsive dashboard
- Advanced filtering and querying
- Export functionality (PDF reports, GeoJSON)

### Medium-term
- Expand to all Philadelphia neighborhoods
- Temporal analysis (track changes over time)
- Additional infrastructure types (crosswalks, bike lanes)

### Long-term
- Predictive modeling (incident forecasting)
- Integration with 311 service request data
- Causal analysis of infrastructure impact on safety

## 📄 License

This project is provided for educational and research purposes. Data sources are subject to their respective licenses:
- Google Street View: Google's Terms of Service
- Crime Data: Philadelphia Police Department public data
- Boundaries: OpenStreetMap

## 👥 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or inquiries about this project, please contact the research team.

---

**Disclaimer**: This project is for research and educational purposes. The findings do not constitute official policy recommendations. Users should verify all data and analysis with original sources.
