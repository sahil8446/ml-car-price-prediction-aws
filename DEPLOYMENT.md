# 🚗 Car Price Predictor - Deployment Guide

## Deploy to Streamlit Cloud

### Prerequisites
- GitHub account
- Git installed on your machine
- Streamlit Cloud account (streamlit.io)

### Steps to Deploy

#### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Car price predictor app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

#### 2. Deploy on Streamlit Cloud
1. Go to [Streamlit Cloud](https://share.streamlit.io)
2. Click "New app"
3. Select your repository: `YOUR_USERNAME/YOUR_REPO`
4. Branch: `main`
5. Main file path: `streamlit_apps/model_app.py`
6. Click "Deploy"

### Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_apps/model_app.py
```

The app will open at `http://localhost:8501`

### Project Structure
```
new_app/
├── models/
│   └── xgb_car_price_model.pkl    # Trained XGBoost model
├── streamlit_apps/
│   └── model_app.py                # Main Streamlit app
├── data/
│   └── cars24-car-price-cleaned-new.csv
├── scripts/
│   ├── train_model.py
│   └── predict.py
├── notebooks/
├── requirements.txt
├── .streamlit/
│   └── config.toml
└── .gitignore
```

### Configuration
The `.streamlit/config.toml` file contains theme and deployment settings. Customize as needed:
- Colors and fonts
- Toolbar visibility
- Error detail levels

### Notes
- The model is cached using `@st.cache_resource` for fast predictions
- Relative paths work for both local development and cloud deployment
- Make sure `requirements.txt` is up to date before deploying

---
Built with ❤️ using Streamlit and XGBoost
