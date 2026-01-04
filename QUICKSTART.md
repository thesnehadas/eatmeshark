# Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Prepare Data

Place your datasets in the `data/` folder:
- `data/Shark Tank India.csv`
- `data/Shark Tank US.csv`
- `data/Shark Tank Australia.csv`

## Step 3: Train Models

**Train all countries:**
```bash
python train_all_countries.py
```

**Train specific country:**
```bash
# Deal model
python src/train_deal.py --country India

# Valuation model
python src/train_valuation.py --country India

# Shark models
python src/train_sharks.py --country India

# Similarity model
python src/train_similarity.py --country India
```

## Step 4: Run Application

```bash
streamlit run app.py
```

## Using the App

1. **Select Country**: Choose from dropdown in sidebar
2. **Enter Details**: Fill in startup information
3. **Select Sharks**: Check which sharks are present (country-specific)
4. **Get Predictions**: Use tabs to get:
   - Deal probability
   - Valuation estimate
   - Shark investment probabilities
   - Similar companies (based on business description)

## Troubleshooting

### Config file not found
- Ensure YAML files exist in `src/config/`
- Check country name matches exactly (India, US, Australia)

### Dataset not found
- Check `dataset_path` in config file
- Ensure CSV file exists at specified path

### Model not found
- Train models first using training scripts
- Check model paths in config file

---

**Ready to use!** 🚀

