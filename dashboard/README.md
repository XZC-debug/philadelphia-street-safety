# Philadelphia Street Safety Analysis Dashboard

A full-stack web application for analyzing traffic facilities (traffic lights, stop signs) and their relationship with crime incidents in Philadelphia neighborhoods.

## Quick Start (5 minutes)

### Prerequisites
- Python 3.7+
- Node.js 14+
- npm or yarn

### Setup

**1. Start the Backend**

```bash
cd dashboard/backend
pip install -r requirements.txt
python app.py
```

Backend will run on `http://localhost:5000`

**2. Start the Frontend (in a new terminal)**

```bash
cd dashboard/frontend
npm install
npm start
```

Frontend will open at `http://localhost:3000`

---

## Project Structure

```
dashboard/
├── backend/                    # Flask API Server
│   ├── app.py                 # Main Flask app
│   ├── config.py              # Configuration
│   ├── data_manager.py        # Data loading & processing
│   ├── requirements.txt        # Python dependencies
│   ├── data/                  # GeoJSON & CSV data
│   └── README.md
│
└── frontend/                  # React Dashboard
    ├── src/
    │   ├── components/        # React components
    │   ├── pages/            # Page layouts
    │   ├── styles/           # CSS styles
    │   ├── utils/            # API utilities
    │   └── App.jsx
    ├── public/
    │   └── index.html
    ├── package.json
    └── README.md
```

---

## Key Features

### Backend (Flask)
- ✅ RESTful API for spatial data
- ✅ Automatic data loading from GeoJSON & CSV
- ✅ 6 core API endpoints
- ✅ CORS enabled for frontend integration
- ✅ Error handling & logging

### Frontend (React)
- ✅ Interactive map (Mapbox GL JS)
- ✅ Real-time neighborhood selection
- ✅ Statistics dashboard
- ✅ Neighborhood comparison charts
- ✅ Responsive design (mobile-friendly)

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Server health check |
| `/api/neighborhoods` | GET | List all 4 neighborhoods with stats |
| `/api/data/<neighborhood>` | GET | Get traffic lights & stop signs GeoJSON |
| `/api/incidents/<neighborhood>` | GET | Get crime incidents (with time filtering) |
| `/api/stats/<neighborhood>` | GET | Get statistics (density, incident types, hourly) |
| `/api/comparison` | GET | Compare all neighborhoods |

### Example Requests

```bash
# Get all neighborhoods
curl http://localhost:5000/api/neighborhoods

# Get Center City data
curl http://localhost:5000/api/data/Center%20City

# Get incidents filtered by time
curl "http://localhost:5000/api/incidents/Center%20City?hour_from=18&hour_to=23"
```

---

## Data Overview

**Loaded Data:**
- 152,555 crime incidents
- 4 neighborhoods with traffic facilities:
  - Center City: 76 traffic lights, 12 stop signs
  - Kensington: 44 traffic lights, 53 stop signs
  - Point Breeze: 58 traffic lights, 122 stop signs
  - University City: 219 traffic lights, 23 stop signs

**Data Sources:**
- Google Street View (YOLO Detection)
- Philadelphia Police Department (Crime Incidents)

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Mapbox GL JS, Recharts |
| **Backend** | Flask, GeoPandas, Pandas |
| **Database** | GeoJSON + CSV (no database required) |
| **Styling** | CSS Grid, Flexbox, Responsive Design |
| **API** | RESTful with CORS |

---

## Configuration

### Backend Configuration (`backend/config.py`)
```python
NEIGHBORHOODS = ['Center City', 'KENSINGTON', 'POINT_BREEZE', 'UNIVERSITY_CITY']
CORS_ORIGINS = ["*"]  # Development
DEBUG = True
```

### Frontend Configuration (`frontend/.env`)
```
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_MAPBOX_TOKEN=your_token_here  # Optional
```

---

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.7+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check port 5000 is not in use
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows
```

### Frontend won't connect to backend
- Ensure backend is running on port 5000
- Check CORS configuration
- Clear browser cache and restart dev server
- Check browser console for CORS errors

### Data not loading
- Verify `../philly_streetscape_project/` directory exists
- Verify `../incidents/incidents.csv` exists
- Check backend console for file path errors
- Ensure GeoJSON files are valid

---

## Development

### Backend Development
```bash
cd backend
export FLASK_ENV=development
python app.py
```

### Frontend Development
```bash
cd frontend
npm start
```

### Adding New Features

1. **Add a new API endpoint** in `backend/app.py`:
```python
@app.route('/api/new-endpoint', methods=['GET'])
def new_endpoint():
    return jsonify({'status': 'success', 'data': {...}})
```

2. **Call from frontend** in `frontend/src/utils/api.js`:
```javascript
newEndpoint: () => api.get('/new-endpoint'),
```

3. **Use in components**:
```javascript
const response = await apiService.newEndpoint();
```

---

## Deployment

### Deploy Backend (Heroku)
```bash
cd backend
heroku create your-app-name
git push heroku main
```

### Deploy Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

---

## Future Enhancements

- [ ] PostGIS database integration for large datasets
- [ ] Real-time data updates
- [ ] Advanced spatial analysis (buffering, clustering)
- [ ] Time-series analysis
- [ ] Machine learning predictions
- [ ] Mobile app (React Native)
- [ ] Multi-city support

---

## Team & Attribution

- **Data Collection**: Google Street View + YOLO Detection
- **Data Source**: Philadelphia Police Department
- **Development**: Full-stack web application

---

## License

MIT

---

## Support

For issues or questions:
1. Check the backend/README.md for API documentation
2. Check the frontend/README.md for frontend details
3. Review the troubleshooting section above
4. Check browser console and backend logs for errors

