import streamlit as st
import joblib
import pandas as pd
import os

# Load model and metadata with caching for performance
@st.cache_resource
def load_model_and_metadata():
    base_path = os.path.dirname(__file__)
    model = joblib.load(os.path.join(base_path, 'bengaluru_price_model.pkl'))
    locations = joblib.load(os.path.join(base_path, 'locations.pkl'))
    area_types = joblib.load(os.path.join(base_path, 'area_types.pkl'))
    return model, locations, area_types
    
model, locations, area_types = load_model_and_metadata()

st.title('🏠 Bangalore House Price Predictor')
st.markdown('Enter the details below to estimate the house price.')

# Use sidebar for inputs to declutter main page
with st.sidebar:
    total_sqft = st.number_input(
        'Enter the size of the house (sq.ft.):', 
        min_value=100.0, max_value=10000.0, value=1000.0,
        step=50.0
    )
    bath = st.selectbox('Number of Bathrooms', list(range(1, 11)), index=1)
    bhk = st.selectbox('Number of BHK', list(range(1, 11)), index=1)
    balcony = st.selectbox('Number of Balconies', list(range(0, 5)), index=1)
    location = st.selectbox('Location', sorted(locations))
    area_type = st.selectbox('Area Type', sorted(area_types))

# Button triggers prediction
if st.button('Predict Price'):
    input_df = pd.DataFrame({
        'total_sqft': [total_sqft],
        'bath': [bath],
        'bhk': [bhk],
        'balcony': [balcony],
        'area_type': [area_type],
        'location': [location]
    })
    
    if location not in locations:
        st.warning("⚠️ This location wasn't in the training data, so prediction may be less accurate.")

    st.subheader('Your Input:')
    st.write(input_df)

    try:
        with st.spinner('Calculating...'):
            price = model.predict(input_df)[0]
        
        if price >= 100:
            crore = price / 100
            st.success(f"💰 Estimated Price: ₹ {price:,.2f} Lakhs (≈ ₹ {crore:.2f} Crores)")
        else:
            st.success(f"💰 Estimated Price: ₹ {price:,.2f} Lakhs")

    except Exception as e:
        st.error(f'Prediction failed: {e}')

st.markdown("---")
st.markdown("Made with ❤️ by [Ritabrata Dutta](https://www.linkedin.com/in/ritabrata-dutta-0a0077320/) | [GitHub](https://github.com/RitabrataDutta01)")
