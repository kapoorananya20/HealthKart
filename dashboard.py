import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime
from fpdf import FPDF
import tempfile
import plotly.express as px

# Streamlit config

st.set_page_config(page_title="HealthKart ROI Dashboard", layout="wide")
st.title("📊 HealthKart Influencer Campaign ROI Dashboard")

# File upload
st.sidebar.header("📁 Upload Data")

def load_csv(label):
    uploaded_file = st.sidebar.file_uploader(f"Upload {label} CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()  
        return df
    return None

influencers = load_csv("influencers")
posts = load_csv("posts")
tracking = load_csv("tracking")
payouts = load_csv("payouts")

if not all([influencers is not None, posts is not None, tracking is not None, payouts is not None]):
    st.warning("Please upload all 4 required CSV files.")
    st.stop()

# Coloumn validate
required_tracking_cols = {'revenue', 'date', 'influencer_id'}
if not required_tracking_cols.issubset(tracking.columns):
    st.error(f" Tracking CSV missing columns: {required_tracking_cols - set(tracking.columns)}")
    st.stop()

if 'date' not in payouts.columns:
    payouts['date'] = pd.NaT  

tracking['date'] = pd.to_datetime(tracking['date'], errors='coerce')
payouts['date'] = pd.to_datetime(payouts['date'], errors='coerce')

# Sidebar filter
st.sidebar.header("🔍 Filters")

merged_df = tracking.merge(
    influencers[['id', 'gender', 'category', 'platform']],
    left_on='influencer_id',
    right_on='id',
    how='left'
)

platforms = st.sidebar.multiselect("Platform", options=merged_df['platform'].dropna().unique(), default=merged_df['platform'].dropna().unique())
genders = st.sidebar.multiselect("Gender", options=merged_df['gender'].dropna().unique(), default=merged_df['gender'].dropna().unique())
categories = st.sidebar.multiselect("Category", options=merged_df['category'].dropna().unique(), default=merged_df['category'].dropna().unique())
brands = st.sidebar.multiselect("Brand / Source", options=merged_df['source'].dropna().unique(), default=merged_df['source'].dropna().unique())

filtered_df = merged_df[
    (merged_df['platform'].isin(platforms)) &
    (merged_df['gender'].isin(genders)) &
    (merged_df['category'].isin(categories)) &
    (merged_df['source'].isin(brands))
]

# Campaign Summary
st.subheader("📈 Campaign Summary")

total_revenue = filtered_df['revenue'].sum()
total_spend = payouts['total_payout'].sum()
roas = total_revenue / total_spend if total_spend > 0 else 0
baseline_roas = 1.0
incremental_roas = roas - baseline_roas

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"Rs.{total_revenue:,.0f}")
col2.metric("Total Spend", f"Rs.{total_spend:,.0f}")
col3.metric("ROAS", f"{roas:.2f}")
col4.metric("Incremental ROAS vs Baseline", f"{incremental_roas:.2f}")

# ROAS Over Time
st.subheader("📊 ROAS Over Time ")

start_date = st.date_input("Start Date", value=tracking['date'].min())
end_date = st.date_input("End Date", value=tracking['date'].max())

filtered_tracking = tracking[(tracking['date'] >= pd.to_datetime(start_date)) & (tracking['date'] <= pd.to_datetime(end_date))]
filtered_payouts = payouts[(payouts['date'] >= pd.to_datetime(start_date)) & (payouts['date'] <= pd.to_datetime(end_date))]

daily_rev = filtered_tracking.groupby('date')['revenue'].sum()
daily_spend = filtered_payouts.groupby('date')['total_payout'].sum()
roas_over_time = (daily_rev / daily_spend).fillna(0).reset_index()
roas_over_time.columns = ['Date', 'ROAS']

fig = px.line(
    roas_over_time,
    x="Date",
    y="ROAS",
    markers=True,
    title="ROAS Trend Over Time",
)
fig.update_traces(line_color="green")
fig.update_layout(xaxis_title="Date", yaxis_title="ROAS", template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# Post performance
st.subheader("📸 Post Performance (Top 10 by Reach)")
top_posts = posts.sort_values('reach', ascending=False).head(10)
fig_posts = px.bar(
    top_posts,
    x="reach",
    y="url",
    orientation="h",
    color="reach",
    title="Top Posts by Reach",
    color_continuous_scale="Blues"
)
st.plotly_chart(fig_posts, use_container_width=True)

# Best persons and poor ros
st.subheader("🏆 Best Personas (Avg ROAS by Gender & Category)")
persona_df = filtered_df.groupby(['gender', 'category'])['revenue'].sum() / total_spend
st.dataframe(persona_df.reset_index().sort_values('revenue', ascending=False))

st.subheader("⚠️ Bottom Influencers (Lowest ROAS)")
bottom_df = filtered_df.groupby('influencer_id')[['revenue']].sum()
bottom_df['payout'] = payouts.groupby('influencer_id')['total_payout'].sum()
bottom_df['roas'] = bottom_df['revenue'] / bottom_df['payout']
bottom_df = bottom_df.sort_values('roas', ascending=True).head(5)
st.dataframe(bottom_df)

# Top influences
st.subheader("🏆 Top Influencers by ROAS ")
payouts_grouped = payouts.groupby('influencer_id')['total_payout'].sum().reset_index()
top_df = filtered_df.groupby('influencer_id')[['revenue']].sum().reset_index()
top_df = top_df.merge(payouts_grouped, on='influencer_id', how='left')
top_df['roas'] = top_df['revenue'] / top_df['total_payout']
top_df = top_df.merge(influencers[['id', 'name']], left_on='influencer_id', right_on='id', how='left')
top_df = top_df.sort_values('roas', ascending=False).head(10)

fig_top = px.bar(
    top_df,
    x="roas",
    y="name",
    orientation="h",
    color="roas",
    title="Top 10 Influencers by ROAS",
    color_continuous_scale="Greens"
)
st.plotly_chart(fig_top, use_container_width=True)

# Export filtered data
st.subheader("📤 Export Filtered Data")
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(filtered_df)
st.download_button("Download CSV", csv, "filtered_data.csv", "text/csv")

# PDF insights
st.subheader("📝 Insights Summary (PDF)")

def generate_insights_pdf():
    pdf = FPDF()
    pdf.add_page()
   
    pdf.add_font("Nirmala", "", "C:/Windows/Fonts/Nirmala.ttf", uni=True)
    pdf.set_font("Nirmala", size=12)


    pdf.cell(200, 10, txt="HealthKart Influencer Campaign Insights Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Revenue: ₹{total_revenue:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"Total Spend: ₹{total_spend:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"Overall ROAS: {roas:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Incremental ROAS vs Baseline (1.0): {incremental_roas:.2f}", ln=True)
    pdf.ln(5)

    top_names = top_df['name'].tolist()
    top_roas = top_df['roas'].round(2).tolist()
    pdf.cell(200, 10, txt="Top 5 Influencers by ROAS:", ln=True)
    for i in range(min(5, len(top_names))):
        pdf.cell(200, 10, txt=f"{i+1}. {top_names[i]} - ROAS: {top_roas[i]}", ln=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        return tmp.name

if st.button("📄 Generate Insights PDF"):
    pdf_file = generate_insights_pdf()
    with open(pdf_file, "rb") as f:
        st.download_button("Download Insights PDF", f, file_name="HealthKart_Insights.pdf", mime="application/pdf")
