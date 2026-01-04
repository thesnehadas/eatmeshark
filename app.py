"""
Global Shark Tank Intelligence Platform
Multi-country ML-powered predictions for Shark Tank pitches.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import load_config, get_available_countries
from src.inference import predict_all
from src.data_adapters import get_adapter

# Page configuration
st.set_page_config(
    page_title="Global Shark Tank Intelligence",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🌍 Global Shark Tank Intelligence Platform")
st.markdown("""
Comprehensive ML-powered predictions for Shark Tank pitches across multiple countries.
Get insights on deal probability, valuation estimates, and shark preferences.
""")

# Get available countries
available_countries = get_available_countries()

# Sidebar
with st.sidebar:
    st.header("🌍 Country Selection")
    
    # Country selector
    selected_country = st.selectbox(
        "Select Country",
        available_countries,
        index=0 if 'India' in available_countries else 0
    )
    
    st.markdown("---")
    st.header("📊 Model Status")
    
    # Check model availability for selected country
    try:
        config = load_config(selected_country)
        adapter = get_adapter(selected_country)
        adapter.set_config(config)
        
        deal_available = os.path.exists(config['model_paths']['deal'])
        valuation_available = os.path.exists(config['model_paths']['valuation'])
        shark_available = os.path.exists(config['model_paths']['sharks'])
        similarity_available = os.path.exists(config['model_paths'].get('similarity', f"models/{selected_country.lower()}/similarity_model.joblib"))
        
        if deal_available:
            st.success("✅ Deal Predictor")
        else:
            st.error("❌ Deal Predictor")
            st.caption(f"Run: `python src/train_deal.py --country {selected_country}`")
        
        if valuation_available:
            st.success("✅ Valuation Estimator")
        else:
            st.warning("⚠️ Valuation Estimator")
            st.caption(f"Run: `python src/train_valuation.py --country {selected_country}`")
        
        if shark_available:
            st.success("✅ Shark Analyzer")
        else:
            st.warning("⚠️ Shark Analyzer")
            st.caption(f"Run: `python src/train_sharks.py --country {selected_country}`")
        
        if similarity_available:
            st.success("✅ Similar Companies")
        else:
            st.warning("⚠️ Similar Companies")
            st.caption(f"Run: `python src/train_similarity.py --country {selected_country}`")
        
        # Show sharks for this country
        st.markdown("---")
        st.header(f"🦈 Sharks ({selected_country})")
        shark_names = [shark['name'] for shark in config['sharks']]
        for shark in shark_names:
            st.write(f"• {shark}")
        
    except Exception as e:
        st.error(f"Error loading config: {str(e)}")
        st.stop()
    
    st.markdown("---")
    st.header("ℹ️ About")
    st.markdown(f"""
    **Selected Country**: {selected_country}
    
    This app provides four ML-powered features:
    
    1. **Deal Predictor**: Will you get a deal?
    2. **Valuation Estimator**: What's your startup worth?
    3. **Shark Analyzer**: Which sharks will invest?
    4. **Similar Companies**: Find similar startups from Shark Tank
    
    All predictions are based on **Shark Tank {selected_country}** historical data.
    """)

# Main content
st.header(f"📝 Enter Startup Details (Shark Tank {selected_country})")

# Get adapter for input form
adapter = get_adapter(selected_country)
adapter.set_config(config)
shark_names = [shark['name'] for shark in config['sharks']]

col1, col2 = st.columns(2)

# Get industries from the selected country's dataset
try:
    df_sample = adapter.load_data(config['dataset_path'])
    available_industries = sorted([str(ind) for ind in df_sample['Industry'].unique() if pd.notna(ind)])
    if not available_industries:
        available_industries = ['Food and Beverage', 'Technology', 'Healthcare', 'Other']
except:
    available_industries = ['Food and Beverage', 'Technology', 'Healthcare', 'Other']

# Determine currency unit based on country
currency_unit = "Lakhs" if selected_country == "India" else "USD"
currency_symbol = "₹" if selected_country == "India" else "$"

with col1:
    # Industry selection (dynamic based on country)
    industry = st.selectbox("Industry *", available_industries)
    
    ask_amount = st.number_input(f"Ask Amount (in {currency_unit}) *", min_value=0.0, value=50.0 if selected_country == "India" else 50000.0, step=1.0, format="%.2f")
    
    ask_equity = st.number_input("Ask Equity (%) *", min_value=0.0, max_value=100.0, value=5.0, step=0.1, format="%.2f")

with col2:
    valuation_requested = st.number_input(f"Valuation Requested (in {currency_unit}) *", min_value=0.0, value=1000.0 if selected_country == "India" else 1000000.0, step=10.0, format="%.2f")
    
    # Monthly sales - only show if available for this country
    if config['column_mapping'].get('monthly_sales'):
        monthly_sales = st.number_input(f"Monthly Sales (in {currency_unit}) *", min_value=0.0, value=8.0 if selected_country == "India" else 8000.0, step=0.1, format="%.2f")
    else:
        monthly_sales = 0.0  # Not available for US/Australia
        st.info(f"💡 Monthly Sales not available for {selected_country} dataset")
    
    st.subheader("Sharks Present")
    shark_present = {}
    for shark in shark_names:
        shark_present[shark] = st.checkbox(f"{shark} Present", value=True, key=f"{shark}_present")

# Business Description (optional)
business_description = st.text_area(
    "Business Description (optional)",
    height=80,
    placeholder="Describe your business/product..."
)

# Prepare canonical input data
input_data = {
    'industry': industry,
    'ask_amount': float(ask_amount),
    'ask_equity': float(ask_equity),
    'valuation_requested': float(valuation_requested),
    'monthly_sales': float(monthly_sales),
    'business_description': business_description if business_description else '',
}

# Add shark present columns
for shark in shark_names:
    shark_lower = shark.lower()
    input_data[f'{shark_lower}_present'] = 1 if shark_present.get(shark, False) else 0

# Tabs for different features
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Deal Predictor", "💰 Valuation Estimator", "🦈 Shark Analyzer", "🔍 Similar Companies"])

# Tab 1: Deal Predictor
with tab1:
    st.header(f"🎯 Deal Probability Prediction ({selected_country})")
    
    if not deal_available:
        st.error(f"⚠️ Deal prediction model not found for {selected_country}!")
        st.info(f"Please train the model first:\n```bash\npython src/train_deal.py --country {selected_country}\n```")
    else:
        if st.button("🔮 Predict Deal Probability", type="primary", use_container_width=True, key="deal_btn"):
            try:
                predictions = predict_all(selected_country, input_data)
                
                if predictions['deal']['available']:
                    probability = predictions['deal']['probability']
                    prediction = predictions['deal']['prediction']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Deal Probability", f"{probability * 100:.2f}%")
                    
                    with col2:
                        if prediction == 1:
                            st.metric("Prediction", "✅ **DEAL**", delta="Likely to get a deal")
                        else:
                            st.metric("Prediction", "❌ **NO DEAL**", delta="Unlikely to get a deal")
                    
                    st.progress(probability)
                    
                    st.info(f"💡 **Based on Shark Tank {selected_country} data**")
                    
                    # Interpretation
                    st.subheader("💡 Interpretation")
                    if probability >= 0.7:
                        st.success("**High Probability**: Strong chance of getting a deal!")
                    elif probability >= 0.5:
                        st.info("**Moderate Probability**: Decent chance, room for improvement.")
                    elif probability >= 0.3:
                        st.warning("**Low-Moderate Probability**: Consider refining your pitch.")
                    else:
                        st.error("**Low Probability**: May face challenges. Adjust ask amount, equity, or valuation.")
                else:
                    st.error("Deal prediction not available")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.exception(e)

# Tab 2: Valuation Estimator
with tab2:
    st.header(f"💰 Startup Valuation Estimator ({selected_country})")
    
    if not valuation_available:
        st.error(f"⚠️ Valuation model not found for {selected_country}!")
        st.info(f"Please train the model first:\n```bash\npython src/train_valuation.py --country {selected_country}\n```")
    else:
        if st.button("💰 Estimate Valuation", type="primary", use_container_width=True, key="val_btn"):
            try:
                predictions = predict_all(selected_country, input_data)
                
                if predictions['valuation']['available']:
                    valuation = predictions['valuation']['valuation']
                    conf_range = predictions['valuation']['confidence_range']
                    
                    st.metric("Estimated Valuation", f"{currency_symbol}{valuation:,.2f} {currency_unit}")
                    
                    st.subheader("📊 Valuation Range")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Lower Bound", f"{currency_symbol}{conf_range[0]:,.2f} {currency_unit}")
                    with col2:
                        st.metric("Upper Bound", f"{currency_symbol}{conf_range[1]:,.2f} {currency_unit}")
                    
                    # Comparison
                    if input_data['valuation_requested'] > 0:
                        ratio = valuation / input_data['valuation_requested']
                        st.subheader("📈 Valuation Analysis")
                        if ratio >= 1.0:
                            st.success(f"✅ Estimated valuation ({currency_symbol}{valuation:,.2f} {currency_unit}) is **{ratio:.2f}x** your requested valuation")
                        elif ratio >= 0.7:
                            st.info(f"⚠️ Estimated valuation ({currency_symbol}{valuation:,.2f} {currency_unit}) is **{ratio:.2f}x** your requested valuation")
                        else:
                            st.warning(f"❌ Estimated valuation ({currency_symbol}{valuation:,.2f} {currency_unit}) is **{ratio:.2f}x** your requested valuation. Consider adjusting.")
                    
                    st.info(f"💡 **Based on Shark Tank {selected_country} data**")
                else:
                    st.error("Valuation prediction not available")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.exception(e)

# Tab 3: Shark Analyzer
with tab3:
    st.header(f"🦈 Shark Preference Analyzer ({selected_country})")
    
    if not shark_available:
        st.error(f"⚠️ Shark preference models not found for {selected_country}!")
        st.info(f"Please train the models first:\n```bash\npython src/train_sharks.py --country {selected_country}\n```")
    else:
        if st.button("🦈 Analyze Shark Preferences", type="primary", use_container_width=True, key="shark_btn"):
            try:
                predictions = predict_all(selected_country, input_data)
                
                # Check deal prediction first - if no deal, no shark would invest
                deal_prediction = predictions.get('deal', {}).get('prediction', None)
                deal_probability = predictions.get('deal', {}).get('probability', None)
                deal_available = predictions.get('deal', {}).get('available', False)
                
                # If deal prediction is available and indicates NO DEAL, show message
                if deal_available and (deal_prediction == 0 or (deal_probability is not None and deal_probability < 0.3)):
                    # No deal predicted - show appropriate message
                    st.warning("⚠️ **No Deal Predicted**")
                    prob_text = f" (probability: {deal_probability*100:.1f}%)" if deal_probability is not None else ""
                    st.info(f"""
                    **Since the deal prediction indicates **NO DEAL**{prob_text}, 
                    no sharks would invest in this pitch.**
                    
                    To see which sharks might invest, you need to first improve your pitch parameters 
                    (ask amount, equity, valuation, monthly sales) to increase the likelihood of getting a deal.
                    """)
                    st.info(f"💡 **Based on Shark Tank {selected_country} data**")
                elif predictions['sharks']['available']:
                    shark_probs = predictions['sharks']['probabilities']
                    ranked_sharks = predictions['sharks']['ranked']
                    insights = predictions['sharks']['insights']
                    
                    st.subheader("📊 Investment Probabilities by Shark")
                    
                    # Display in columns
                    cols = st.columns(min(3, len(ranked_sharks)))
                    for idx, (shark, prob) in enumerate(ranked_sharks):
                        col_idx = idx % 3
                        with cols[col_idx]:
                            if prob >= 0.6:
                                delta_color = "normal"
                                delta = "High"
                            elif prob >= 0.4:
                                delta_color = "normal"
                                delta = "Moderate"
                            else:
                                delta_color = "inverse"
                                delta = "Low"
                            
                            st.metric(
                                label=f"{shark}",
                                value=f"{prob * 100:.1f}%",
                                delta=delta,
                                delta_color=delta_color
                            )
                            st.progress(prob)
                    
                    # Best match
                    if ranked_sharks:
                        best_shark, best_prob = ranked_sharks[0]
                        if best_prob > 0.3:
                            st.success(f"💡 **Best Match**: {best_shark} has the highest probability ({best_prob * 100:.1f}%) of investing!")
                    
                    # Insights
                    if insights:
                        st.subheader("🔍 Shark Investment Insights")
                        for insight in insights:
                            st.write(insight)
                    
                    st.info(f"💡 **Based on Shark Tank {selected_country} data**")
                else:
                    st.error("Shark predictions not available")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.exception(e)

# Tab 4: Similar Companies
with tab4:
    st.header(f"🔍 Find Similar Companies ({selected_country})")
    
    # Check if similarity model exists
    similarity_available = os.path.exists(config['model_paths'].get('similarity', f"models/{selected_country.lower()}/similarity_model.joblib"))
    
    if not similarity_available:
        st.error(f"⚠️ Similarity model not found for {selected_country}!")
        st.info(f"Please train the model first:\n```bash\npython src/train_similarity.py --country {selected_country}\n```")
    else:
        st.markdown("""
        Enter your business description above to find similar companies that have appeared on Shark Tank.
        The system will match based on business description using TF-IDF similarity.
        """)
        
        if business_description and business_description.strip():
            if st.button("🔍 Find Similar Companies", type="primary", use_container_width=True, key="similar_btn"):
                try:
                    predictions = predict_all(selected_country, input_data)
                    
                    if predictions.get('similar_companies', {}).get('available'):
                        similar_companies = predictions['similar_companies']['companies']
                        
                        if similar_companies:
                            st.subheader(f"📊 Top {len(similar_companies)} Similar Companies")
                            st.info(f"💡 **Based on Shark Tank {selected_country} data**")
                            
                            for i, company in enumerate(similar_companies, 1):
                                with st.expander(f"#{i} {company['company_name']} (Similarity: {company['similarity_score']*100:.1f}%)"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.write(f"**Industry:** {company.get('industry', 'Unknown')}")
                                        if company.get('ask_amount', 0) > 0:
                                            st.write(f"**Ask Amount:** {currency_symbol}{company['ask_amount']:,.2f} {currency_unit}")
                                        if company.get('ask_equity', 0) > 0:
                                            st.write(f"**Ask Equity:** {company['ask_equity']:.1f}%")
                                    
                                    with col2:
                                        st.write(f"**Similarity Score:** {company['similarity_score']*100:.1f}%")
                                        st.progress(company['similarity_score'])
                                    
                                    if company.get('description'):
                                        st.write("**Description:**")
                                        st.write(company['description'])
                        else:
                            st.warning("No similar companies found. Try providing a more detailed business description.")
                    else:
                        error_msg = predictions.get('similar_companies', {}).get('error', 'Unknown error')
                        message = predictions.get('similar_companies', {}).get('message', '')
                        if message:
                            st.info(message)
                        else:
                            st.error(f"Similar companies not available: {error_msg}")
                            
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.exception(e)
        else:
            st.info("💡 Enter a business description above to find similar companies.")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: gray;'>
    <p>Built with ❤️ using Machine Learning | Global Shark Tank Intelligence Platform</p>
    <p>Predictions based on <strong>Shark Tank {selected_country}</strong> historical data</p>
</div>
""", unsafe_allow_html=True)
