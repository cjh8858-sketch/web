# CLAUDE.md - Web Version

This file provides guidance to Claude Code (claude.ai/code) when working with the web version of the Handwritten Digit Recognition application.

## Project Overview

The **Web Version** is a browser-based application that allows users to draw handwritten digits and receive instant AI recognition results. It uses Flask as the backend API server and modern HTML5 Canvas for the drawing interface.

## Architecture

### Backend (Flask)
- **Framework**: Flask web server
- **Model**: TensorFlow/Keras neural network (same as desktop version)
- **Model Management**: Lazy-loads model on first request, caches in memory
- **API Endpoints**: RESTful design for digit recognition

### Frontend (HTML5)
- **Canvas API**: Native drawing with mouse and touch support
- **Styling**: Modern CSS with gradient backgrounds and smooth animations
- **Interactivity**: Real-time canvas feedback with loading states

### Communication
- Canvas image → Base64 encoding → Flask API → Model prediction → JSON response

## Directory Structure

```
web/
├── app.py                          # Flask application server
├── requirements.txt                # Python dependencies
├── templates/
│   └── index.html                  # Main HTML page
├── static/
│   ├── css/
│   │   └── style.css               # Styling (gradients, animations, responsive)
│   └── js/
│       └── canvas.js               # Canvas drawing & API interaction
├── mnist_model.keras               # Trained model (generated on first run)
└── CLAUDE.md                       # This file
```

## Running the Application

### Setup
1. Install dependencies:
```
cd web
pip install -r requirements.txt
```

2. Run the Flask server:
```
python app.py
```

3. Open browser and navigate to:
```
http://127.0.0.1:5000
```

### First Launch
First run trains the MNIST model (~1-2 minutes). Model is saved to `mnist_model.keras` for instant subsequent launches.

## API Endpoints

### GET `/`
Returns the main HTML page.

### GET `/api/health`
Health check endpoint. Returns:
```json
{
  "status": "ok",
  "message": "Server is running"
}
```

### POST `/api/recognize`
Recognizes a digit from canvas image.

**Request:**
```json
{
  "canvas": "data:image/png;base64,..."
}
```

**Response (Success):**
```json
{
  "digit": 7,
  "confidence": 97.45,
  "success": true
}
```

**Response (Error):**
```json
{
  "error": "error message",
  "success": false
}
```

## Frontend Components

### Canvas Interaction
- `canvas.js` handles:
  - Mouse drawing with click-drag tracking
  - Touch support for mobile/tablets
  - Real-time stroke rendering
  - Canvas reset functionality

### Result Display
- Animated result card shows predicted digit and confidence
- Loading spinner during server processing
- Error messages for failed recognitions

### Responsive Design
- Works on desktop, tablet, and mobile
- Canvas scales with viewport
- Touch-friendly button sizing

## Modifying the Application

### Improving Model Accuracy
1. Edit `app.py`, function `get_or_create_model()`
2. Increase `epochs` (currently 5, try 10-20)
3. Adjust network layers or neurons in the Sequential model
4. Delete `mnist_model.keras` to retrain

### Customizing UI
- **Canvas size**: Edit `width="280" height="280"` in `templates/index.html`
- **Colors**: Modify CSS variables in `static/css/style.css` (`:root { ... }`)
- **Stroke width/style**: Edit `ctx.lineWidth = 5` and `ctx.strokeStyle = 'black'` in `static/js/canvas.js`

### Deploying to Production
1. Set `debug=False` in `app.py`: `app.run(debug=False, ...)`
2. Use a production WSGI server (e.g., Gunicorn):
```
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
3. Set environment variables for Flask:
```
set FLASK_ENV=production
set FLASK_DEBUG=0
```

### Adding Authentication
Wrap endpoints with login_required decorator:
```python
from flask_login import login_required

@app.route('/api/recognize', methods=['POST'])
@login_required
def api_recognize():
    # ... existing code
```

### Database Integration
Store recognition history:
```python
# Add SQLAlchemy model
class Recognition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    digit = db.Column(db.Integer)
    confidence = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# In api_recognize():
result = Recognition(digit=predicted_digit, confidence=confidence)
db.session.add(result)
db.session.commit()
```

## Common Tasks

### Test the API with curl
```
curl -X POST http://127.0.0.1:5000/api/recognize \
  -H "Content-Type: application/json" \
  -d '{"canvas":"data:image/png;base64,..."}'
```

### Enable CORS (if needed)
```python
from flask_cors import CORS
CORS(app)
```

### Debug Model Predictions
Add in `app.py`, `recognize_digit()` function:
```python
# After model prediction
print("Raw predictions:", prediction[0])
print("All digits:", {i: float(prediction[0][i]) for i in range(10)})
```

### Performance Optimization
- Model caching: Currently cached in global `model` variable (already implemented)
- Image resizing: Done server-side to keep model consistent
- Batch predictions: Modify `recognize_digit()` to handle multiple images

## Notes

- Model loading is lazy (on first request), not at app startup
- Canvas uses base64 encoding for image transmission (~5-10KB per image)
- Touch events are supported for tablet/mobile drawing
- Confidence scores are softmax probabilities (rarely 100%)
- MNIST training uses CPU only; GPU not available on native Windows
- Flask development server is single-threaded; use Gunicorn for production
