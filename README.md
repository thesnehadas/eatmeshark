# 🌍 Global Shark Tank Intelligence Platform

A production-ready, multi-country machine learning platform that provides comprehensive predictions for Shark Tank pitches across **India**, **US**, and **Australia**.

## 🎯 Overview

This platform provides four ML-powered features that work across all supported countries:

1. **Deal Outcome Predictor** - Binary classification to predict if a startup will receive a deal
2. **Startup Valuation Estimator** - Regression to estimate startup valuation
3. **Shark Preference Analyzer** - Multi-label classification to predict which sharks will invest
4. **Similar Companies Finder** - Find similar startups based on business description using TF-IDF similarity

## 🏗️ Architecture

### Key Design Principles

1. **Canonical Schema**: All countries use the same internal schema (`industry`, `ask_amount`, etc.)
2. **Country Adapters**: Dataset-specific adapters map raw columns → canonical schema
3. **Country-Specific Models**: Separate models trained per country
4. **Dynamic Configuration**: YAML configs define country-specific settings (sharks, columns, etc.)

### Project Structure

```
shark-tank-deal-predictor/
├── data/
│   ├── Shark Tank India.csv
│   ├── Shark Tank US.csv
│   └── Shark Tank Australia.csv
├── src/
│   ├── config/
│   │   ├── india.yaml          # India configuration
│   │   ├── us.yaml             # US configuration
│   │   └── australia.yaml      # Australia configuration
│   ├── data_adapters/
│   │   ├── base.py             # Base adapter class
│   │   ├── india.py            # India-specific adapter
│   │   ├── us.py               # US-specific adapter
│   │   └── australia.py        # Australia-specific adapter
│   ├── canonical_preprocess.py  # Canonical preprocessing
│   ├── train_deal.py           # Train deal models
│   ├── train_valuation.py      # Train valuation models
│   ├── train_sharks.py         # Train shark models
│   └── inference.py           # Unified inference interface
├── models/
│   ├── india/
│   │   ├── deal_model.joblib
│   │   ├── valuation_model.joblib
│   │   └── shark_models.joblib
│   ├── us/
│   │   └── ...
│   └── australia/
│       └── ...
├── app.py                      # Streamlit application
├── train_all_countries.py     # Master training script
└── requirements.txt
```

## 📋 Canonical Schema

All models use this internal schema (regardless of country):

- `industry` - Industry category
- `ask_amount` - Amount requested
- `ask_equity` - Equity percentage offered
- `valuation_requested` - Requested valuation
- `monthly_sales` - Monthly sales/revenue (if available)
- `{shark}_present` - Binary flags for each shark (country-specific)
- `{shark}_investment_amount` - Investment amount per shark
- `{shark}_investment_equity` - Investment equity per shark

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Data

Place your datasets in the `data/` folder:
- `data/Shark Tank India.csv`
- `data/Shark Tank US.csv`
- `data/Shark Tank Australia.csv`

### 3. Train Models

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

### 4. Run Application

```bash
streamlit run app.py
```

## 🎨 Using the Application

1. **Select Country**: Choose India, US, or Australia from the sidebar
2. **Enter Details**: Fill in startup information (industry, ask amount, equity, etc.)
3. **Select Sharks**: Check which sharks are present (country-specific)
4. **Get Predictions**: Use the four tabs to get:
   - Deal probability
   - Valuation estimate
   - Shark investment probabilities
   - Similar companies based on description

## 🔧 Configuration Files

Each country has a YAML configuration file that defines:

```yaml
country: India
dataset_path: data/Shark Tank India.csv

column_mapping:
  industry: "Industry"
  ask_amount: "Original Ask Amount"
  # ... more mappings

sharks:
  - name: "Namita"
    present_column: "Namita Present"
    investment_amount: "Namita Investment Amount"
    # ... more shark configs

model_paths:
  deal: "models/india/deal_model.joblib"
  valuation: "models/india/valuation_model.joblib"
  sharks: "models/india/shark_models.joblib"
```

## 📊 Model Training

### Deal Predictor
- **Task**: Binary classification
- **Target**: `deal = 1` if investment received, else `0`
- **Models**: Logistic Regression, Random Forest, Gradient Boosting
- **Metric**: ROC-AUC (best model selected)

### Valuation Estimator
- **Task**: Regression
- **Target**: Deal valuation (log-transformed)
- **Models**: Linear Regression, Random Forest, Gradient Boosting
- **Metric**: RMSE (best model selected)

### Shark Analyzer
- **Task**: Multi-label classification
- **Target**: Binary flag per shark
- **Models**: Random Forest (one per shark)
- **Metric**: Precision, ROC-AUC per shark

### Similar Companies Finder
- **Task**: Text similarity search
- **Method**: TF-IDF vectorization + Cosine similarity
- **Input**: Business description text
- **Output**: Top N similar companies with similarity scores

## 🌐 Adding New Countries

1. **Create config file**: `src/config/{country}.yaml`
2. **Create adapter**: `src/data_adapters/{country}.py`
3. **Add dataset**: Place CSV in `data/` folder
4. **Train models**: Use training scripts with `--country {Country}`

## ✨ Platform Features

- ✅ **Multi-country support** - India, US, Australia (easily extensible)
- ✅ **Dynamic UI** - Adapts to selected country (industries, currency, sharks)
- ✅ **Currency-aware** - Lakhs for India, USD for US/Australia
- ✅ **Country-specific models** - Separate models per country
- ✅ **Canonical schema** - Consistent features across all countries
- ✅ **Production-ready** - Clean, modular, scalable code

## 📝 Notes

- All models use the same canonical feature set
- Country-specific differences are handled by adapters
- Models are trained separately per country (no mixing)
- The app dynamically adapts to selected country

## 🔍 Key Features

- ✅ Multi-country support
- ✅ Canonical schema with adapters
- ✅ Country-specific shark handling
- ✅ Dynamic UI based on country selection
- ✅ Production-ready code structure
- ✅ Scalable to more countries

---

**Built with ❤️ for Global Shark Tank Intelligence**

