# Quick Start Guide - Web Application

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install flask flask-cors
   ```

2. **Start the web server**:
   ```bash
   python run_web.py
   ```

3. **Open your browser**:
   Navigate to: **http://localhost:5000**

That's it! The web application is now running.

## 📋 Prerequisites

- Python 3.8+
- Trained ML models (run `python train_all_countries.py` if needed)
- Flask and Flask-CORS installed

## 🎨 Features

- **Modern Dark Mode UI**: Minimalist design with smooth animations
- **Real-time Predictions**: Get instant predictions for deals, valuations, and shark preferences
- **Multi-Country Support**: India, US, and Australia
- **Responsive Design**: Works on desktop and mobile devices

## 🔧 Troubleshooting

**Port 5000 already in use?**
- Change the port in `api.py`: `app.run(..., port=5001)`

**Models not found?**
- Run: `python train_all_countries.py`

**API connection errors?**
- Make sure Flask server is running
- Check browser console for CORS errors

## 📁 File Structure

```
├── api.py              # Flask backend
├── run_web.py          # Startup script
├── templates/          # HTML templates
│   └── index.html
├── static/             # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
```

Enjoy using the Shark Tank Intelligence Platform! 🦈

