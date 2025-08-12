
#  HealthKart Influencer Campaign ROI Dashboard

##  Project Overview

HealthKart runs influencer campaigns across multiple platforms (Instagram, YouTube, Twitter, etc.) to promote products under brands like **MuscleBlaze**, **HKVitals**, and **Gritzo**. Influencers are paid per post or per order.

This dashboard provides actionable insights into **campaign performance, influencer ROI, and payout tracking** to help optimize marketing spend.

##  Objectives

Track influencer and post performance  
Measure **ROI & Incremental ROAS (Return on Ad Spend)**  
Identify **top-performing influencers** & **low-ROI campaigns**  
Provide **payout tracking** & **brand/product-wise filtering**  
Export insights as **CSV** and **PDF reports**

##  Data Modeling

The dashboard uses 4 datasets (CSV files):

1. **influencers.csv**     
   ID, name, category, gender, follower_count, platform   

2. **posts.csv**  
   influencer_id, platform, date, URL, caption, reach, likes, comments

3. **tracking_data.csv**  
   source, campaign, influencer_id, user_id, product, date, orders, revenue

4. **payouts.csv**  
   influencer_id, basis (post/order), rate, orders, total_payout, date


##  Features

###  1. Data Upload & Filters
- Upload all 4 CSV files via Streamlit sidebar. 
- Filters: **Platform, Gender, Category, Brand/Source**.
- ## And then close the sidebar for better appearance of Dashboard

### 2. Campaign Performance
- **Total Revenue, Spend, ROAS, Incremental ROAS** .
- **ROAS Trend Over Time** .

### 3. Influencer & Post Insights
- **Top Influencers by ROAS** (table view).
- **Bottom Influencers (Poor ROAS)**.
- **Best Personas** (category/gender with highest ROI).
- **Post Performance** (reach, likes, comments).

### 4. Payout Tracking
- Total payouts by influencer.

### 5. Export & Reporting
- **CSV Download** of filtered data.
- **PDF Insights Summary** (auto-generated with top influencers & key metrics).

## Setup & Installation

### 1. Clone or Download

clone the repository


### 2. Install Dependencies

pip install -r requirements.txt

### 3. Run Dashboard

streamlit run dashboard.py


### 4. Upload CSVs
Upload the four required CSVs from the sidebar.

## Insights Example

Sample insights from generated PDF:
- **Total Revenue:** Rs.501,798  
- **Total Spend:** Rs.2,412,867  
- **Overall ROAS:** 0.21  
- **Incremental ROAS vs Baseline:** -0.79  
- **Top Influencers:**
  1. Cheryl Bradley – ROAS: 9.38
  2. Walter Pratt – ROAS: 8.96

## Assumptions

1. Payouts are calculated per influencer .  
2. Dates in payouts are aligned with campaign tracking periods.  
3. Baseline ROAS = **1.0** .

# Author

### Ananya Kapoor
For queries, contact: **kapoorananya2003@gmail.com**
