# Philadelphia Streetscape Dashboard - Frontend

React-based interactive dashboard for visualizing traffic facilities and incident data.

## Quick Start

### 1️⃣ Install Dependencies

```bash
cd dashboard/frontend
npm install
```

### 2️⃣ Start Development Server

```bash
npm start
```

The dashboard will open at `http://localhost:3000`

**Requirements:**
- Backend API must be running on `http://localhost:5000`

---

## Features

- **Interactive Map**: Display traffic lights, stop signs, and incident locations
- **Neighborhood Selection**: Switch between 4 neighborhoods (Center City, Kensington, Point Breeze, University City)
- **Real-time Statistics**: Display facility counts and incident statistics
- **Comparison Charts**: Compare key metrics across neighborhoods
- **Responsive Design**: Works on desktop, tablet, and mobile devices

---

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Map.jsx              # Mapbox integration
│   │   ├── StatsPanel.jsx       # Statistics display
│   │   └── ComparisonChart.jsx  # Neighborhood comparison
│   ├── pages/
│   │   └── Dashboard.jsx        # Main dashboard layout
│   ├── styles/
│   │   ├── Dashboard.css        # Dashboard styles
│   │   ├── Map.css
│   │   ├── StatsPanel.css
│   │   └── ComparisonChart.css
│   ├── utils/
│   │   └── api.js              # API service calls
│   ├── App.jsx
│   ├── App.css
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

---

## Dependencies

- **React 18**: UI library
- **Mapbox GL JS**: Interactive maps
- **Recharts**: Data visualization charts
- **Axios**: HTTP client for API calls

---

## API Integration

The frontend communicates with the backend API:

```
http://localhost:5000/api/
├── /neighborhoods           → Get all neighborhoods
├── /data/<neighborhood>     → Get geo data
├── /incidents/<neighborhood> → Get incident data
├── /stats/<neighborhood>    → Get statistics
└── /comparison              → Get all neighborhoods comparison
```

---

## Configuration

### Mapbox Token (Optional)

To use Mapbox instead of OSM, add your token in `src/components/Map.jsx`:

```javascript
const MAPBOX_TOKEN = 'your_token_here';
```

Get a free token from [mapbox.com](https://mapbox.com)

---

## Development

### Available Scripts

```bash
npm start      # Start development server
npm build      # Build for production
npm test       # Run tests
npm eject      # Eject configuration (⚠️ cannot be undone)
```

### Environment Variables

Create `.env` file for custom configuration:

```
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_MAPBOX_TOKEN=your_token
```

---

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

---

## Troubleshooting

### Backend not connecting
- Ensure backend is running: `python app.py`
- Check backend API is on `http://localhost:5000`
- Check CORS configuration in `backend/config.py`

### Map not displaying
- Try OSM fallback (current implementation)
- Add Mapbox token if using Mapbox layer
- Check browser console for errors

### Styling issues
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

---

## Build for Production

```bash
npm run build
```

Output will be in the `build/` directory, ready for deployment.

---

## Deployment Options

- **Vercel**: Fastest, automatic deployments
- **Netlify**: Static hosting, serverless functions
- **GitHub Pages**: Free, but requires build modifications
- **Traditional Server**: nginx, Apache, etc.

---

## Future Enhancements

- [ ] Time-based filtering (hour/date range)
- [ ] Heat map layer for incidents
- [ ] Detailed popup information on click
- [ ] Export data as CSV/GeoJSON
- [ ] Dark mode theme
- [ ] Advanced spatial analysis filters
- [ ] Incident type filtering

