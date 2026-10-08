import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px 
import base64

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #062F2F 0%,
        #073C3A 45%,
        #021F20 100%
    );
}



/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #062F2F 0%,
        #031F20 100%
    );
}

/* Sidebar content */
[data-testid="stSidebar"] > div:first-child {
    padding-top: 25px 20px ;
}

/* Main Title */
h1 {
    font-size: 42px !important;
    font-weight: 800;
}

/* KPI Cards */
[data-testid="stMetric"] {
    background: linear-gradient(
        135deg,
        #FFFFFF 0%,
        #F0FFFC 100%
    );
    border: 1px solid #47B9A6;
    border-radius: 15px;
    padding: 18px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

[data-testid="stMetricLabel"] {
    color: #000000 !important;
    font-weight: 900;
}

[data-testid="stMetricValue"] {
    color: #073C3A !important;
    font-weight: 800;
}
/* Chart containers */
.stPlotlyChart {
    background-color: white;
    border-radius: 15px;
    padding: 10px;
}
/* Plotly Axis Text */
.stPlotlyChart text {
    fill: #000000 !important;
}

/* Section Headings */
h2, h3 {
    color: #FFFFFF !important;
    font-weight: 700;
}

/* Dashboard Spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
} 

/* FINAL SIDEBAR POSITION */

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0px !important;
    padding-left: 12px !important;
    padding-right: 12px !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    margin-top: 0px !important;
    padding-top: 0px !important;
    margin-bottom: 12px !important;
    font-size: 28px !important;
    line-height: 1.2 !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.4rem !important;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Indian Food Delivery Analysis",
    page_icon="🍔",
    layout="wide"
)

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():

    df = pd.read_csv("Indian_Food_Delivery_.csv")

    # Convert column names to lowercase
    df.columns = df.columns.str.lower()

    # Clean text columns
    text_cols = [
        "city",
        "payment_method",
        "food_category",
        "customer_name",
        "order_status",
        "customer_gender"
    ]

    for col in text_cols:
        df[col] = df[col].astype(str).str.strip().str.title()
        df[col] = df[col].replace({
            "Nan": np.nan,
            "None": np.nan
        })

    # Fill categorical missing values using mode
    categorical_cols = [
        "customer_name",
        "city",
        "food_category",
        "payment_method"
    ]

    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Fill numerical missing values using median
    numerical_cols = [
        "customer_rating",
        "customer_age"
    ]

    for col in numerical_cols:
        df[col] = df[col].fillna(df[col].median())

    # Remove duplicate records
    df = df.drop_duplicates()

    # Convert date
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )
    # Extract Year and Month from Order Date
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["month_name"] = df["order_date"].dt.strftime("%b")

    # Fix unrealistic customer age
    df.loc[
        df["customer_age"] > 100,
        "customer_age"
    ] = np.nan

    df["customer_age"] = df["customer_age"].fillna(
        df["customer_age"].median()
    )

    # Delivery time difference
    df["delivery_time_difference"] = (
        df["actual_delivery_min"]
        - df["estimated_delivery_min"]
    )

    # Customer age groups
    df["age_group"] = pd.cut(
        df["customer_age"],
        bins=[0, 25, 35, 45, 55, 100],
        labels=[
            "18-25",
            "26-35",
            "36-45",
            "46-55",
            "56+"
        ]
    )

    return df


# Load cleaned data
df = load_data()
# -----------------------------
# Common Chart Style
# -----------------------------

def apply_chart_style(fig):
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            color="#000000",
            family="Arial"
        ),
        xaxis=dict(
            title_font=dict(
                color="#000000",
                size=14
            ),
            tickfont=dict(
                color="#000000",
                size=12
            )
        ),
        yaxis=dict(
            title_font=dict(
                color="#000000",
                size=14
            ),
            tickfont=dict(
                color="#000000",
                size=12
            )
        ),
        legend=dict(
            font=dict(color="#000000")
        )
    )
# -----------------------------
# Sidebar Filters
# -----------------------------

st.sidebar.title("🔎 Dashboard Filters")

st.markdown("""
<style>

/* Sidebar Filter Panel */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #062F2F 0%,
        #031F20 100%
    );
}

/* Filter area */
[data-testid="stSidebar"] > div:first-child {
    padding: 25px 20px;
}

/* Dropdowns */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #071B1D;
    border: 1px solid #2FAF9F;
    border-radius: 10px;
}

/* Filter labels */
[data-testid="stSidebar"] label {
    color: white !important;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# City Filter
city_options = ["All"] + sorted(
    df["city"].dropna().unique().tolist()
)

selected_city = st.sidebar.selectbox(
    "🏙️ Select City",
    city_options
)


# Food Category Filter
food_options = ["All"] + sorted(
    df["food_category"].dropna().unique().tolist()
)

selected_food = st.sidebar.selectbox(
    "🍕 Select Food Category",
    food_options
)


# Payment Method Filter
payment_options = ["All"] + sorted(
    df["payment_method"].dropna().unique().tolist()
)

selected_payment = st.sidebar.selectbox(
    "💳 Select Payment Method",
    payment_options
)


# Order Status Filter
status_options = ["All"] + sorted(
    df["order_status"].dropna().unique().tolist()
)

selected_status = st.sidebar.selectbox(
    "📦 Select Order Status",
    status_options
)

st.sidebar.image(
    "food scooter image.png",
    width=320
)

# -----------------------------
# Apply Filters
# -----------------------------

filtered_df = df.copy()


if selected_city != "All":
    filtered_df = filtered_df[
        filtered_df["city"] == selected_city
    ]


if selected_food != "All":
    filtered_df = filtered_df[
        filtered_df["food_category"] == selected_food
    ]


if selected_payment != "All":
    filtered_df = filtered_df[
        filtered_df["payment_method"] == selected_payment
    ]


if selected_status != "All":
    filtered_df = filtered_df[
        filtered_df["order_status"] == selected_status
    ]

# -----------------------------
# Top Right Food Image
# -----------------------------

with open("food_top_right.png", "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode()

st.markdown(
    f"""
    <style>
    .top-food-image {{
        position: absolute;
        top: 0px;
        right: 0px;
        width: 300px;
        z-index: 1;
        pointer-events: none;
    }}
    

    </style>

    <img class="top-food-image"
         src="data:image/png;base64,{img_base64}">
    """,
    unsafe_allow_html=True
)
# -----------------------------
# Title
# -----------------------------

st.title("🍔 Indian Food Delivery Analysis")

st.write(
    "Exploring Customer Behavior, Order Patterns "
    "and Delivery Performance"
)


# -----------------------------
# KPI Cards
# -----------------------------

st.success("Dataset loaded and cleaned successfully! ✅")

st.subheader("📌 Key Performance Indicators")

total_orders = len(filtered_df)

total_sales = filtered_df["order_amount"].sum()

average_order_value = filtered_df["order_amount"].mean()

average_rating = filtered_df["customer_rating"].mean()


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "📦 Total Orders",
        f"{total_orders:,}"
    )


with col2:
    st.metric(
        "💰 Total Sales",
        f"₹{total_sales:,.0f}"
    )


with col3:
    st.metric(
        "🛒 Average Order Value",
        f"₹{average_order_value:,.2f}"
    )


with col4:
    st.metric(
        "⭐ Average Rating",
        f"{average_rating:.2f}"
    )

# -----------------------------
# Analysis Selection
# -----------------------------

st.subheader("📊 Analysis")

# Initialize analysis state
if "analysis" not in st.session_state:
    st.session_state.analysis = "univariate"

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(
        "📊 Univariate Analysis",
        use_container_width=True
    ):
        st.session_state.analysis = "univariate"

with col2:
    if st.button(
        "📈 Bivariate Analysis",
        use_container_width=True
    ):
        st.session_state.analysis = "bivariate"

with col3:
    if st.button(
        "🔗 Multivariate Analysis",
        use_container_width=True
    ):
        st.session_state.analysis = "multivariate"
# =========================================================
# EDA ANALYSIS CHARTS
# =========================================================

# -----------------------------
# UNIVARIATE ANALYSIS
# -----------------------------

if st.session_state["analysis"] == "univariate":

    st.markdown("### 📊 Univariate Analysis")

    # --------------------------------
    # 1. Order Amount - Histogram
    # --------------------------------

    st.subheader("💰 Distribution of Order Amount")

    fig = px.histogram(
        filtered_df,
        x="order_amount",
        nbins=30,
        labels={
            "order_amount": "Order Amount",
            "count": "Frequency"
        }
    )

    fig.update_traces(marker_color="#47B9A6")

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            title_font=dict(color="#333333"),
            tickfont=dict(color="#333333")
        ),
        yaxis=dict(
            title_font=dict(color="#333333"),
            tickfont=dict(color="#333333")
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="uni_hist_order_amount"
    )


    # --------------------------------
    # 2. Order Amount - KDE
    # --------------------------------

    st.subheader("📈 KDE Plot of Order Amount")

    fig = px.density_contour(
        filtered_df,
        x="order_amount"
    )

    fig.update_traces(
        line_color="#47B9A6"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            title="Order Amount",
            title_font=dict(color="#333333"),
            tickfont=dict(color="#333333")
        ),
        yaxis=dict(
            title="Density",
            title_font=dict(color="#333333"),
            tickfont=dict(color="#333333")
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="uni_kde_order_amount"
    )


    # --------------------------------
    # 3. Customer Rating - Histogram
    # --------------------------------

    st.subheader("⭐ Customer Rating Distribution")

    fig = px.histogram(
        filtered_df,
        x="customer_rating",
        nbins=10
    )

    fig.update_traces(marker_color="#47B9A6")

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            title="Customer Rating",
            title_font=dict(color="#333333"),
            tickfont=dict(color="#333333")
        ),
        yaxis=dict(
            title="Number of Orders",
            title_font=dict(color="#333333"),
            tickfont=dict(color="#333333")
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="uni_hist_rating"
    )


       # --------------------------------
    # 4. Food Category - Box Plot
    # --------------------------------

    st.subheader("🍕 Order Amount Distribution by Food Category")

    fig = px.box(
        filtered_df,
        x="food_category",
        y="order_amount",
        labels={
            "food_category": "Food Category",
            "order_amount": "Order Amount"
        }
    )

    fig.update_traces(
        marker_color="#47B9A6"
    )

    fig.update_layout(
        title="Order Amount Distribution by Food Category",
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            title_font=dict(color="#333333"),
            tickfont=dict(color="#333333")
        ),
        yaxis=dict(
            title_font=dict(color="#333333"),
            tickfont=dict(color="#333333")
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="uni_box_food_category"
    )


    # --------------------------------
    # 5. Payment Method - Bar Chart
    # --------------------------------

    st.subheader("💳 Distribution of Payment Methods")

    payment_data = (
        filtered_df["payment_method"]
        .value_counts()
        .sort_values(ascending=True)
    )

    fig = px.bar(
        x=payment_data.values,
        y=payment_data.index,
        orientation="h",
        labels={
            "x": "Number of Orders",
            "y": "Payment Method"
        }
    )

    fig.update_traces(marker_color="#47B9A6")

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="uni_bar_payment"
    )

    # --------------------------------
    # 6. Restaurant Popularity - Dot Plot
    # --------------------------------

    st.subheader("🍽️ Top 10 Most Popular Restaurants")

    restaurant_orders = (
        filtered_df
        .groupby("restaurant_name")["order_id"]
        .count()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    fig = px.scatter(
        x=restaurant_orders.values,
        y=restaurant_orders.index,
        labels={
            "x": "Number of Orders",
            "y": "Restaurant Name"
        }
    )

    fig.update_traces(
        marker=dict(
            size=14,
            color="#47B9A6"
        )
    )

    fig.update_layout(
        title="Top 10 Most Popular Restaurants by Order Count",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="uni_restaurant_popularity"
    )
# =========================================================
# BIVARIATE ANALYSIS
# =========================================================

elif st.session_state["analysis"] == "bivariate":

    st.markdown("### 📈 Bivariate Analysis")

        # --------------------------------
    # 1. Food Category vs Order Amount - Box Plot
    # --------------------------------

    st.subheader("🍕 Food Category vs Order Amount")

    fig = px.box(
        filtered_df,
        x="food_category",
        y="order_amount",
        labels={
            "food_category": "Food Category",
            "order_amount": "Order Amount"
        }
    )

    fig.update_traces(
        marker_color="#47B9A6"
    )

    fig.update_layout(
        title="Order Amount Distribution by Food Category",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="bi_food_amount_box"
    ) 


    # --------------------------------
    # 2. City vs Order Amount
    # --------------------------------

    st.subheader("🏙️ City vs Average Order Amount")

    city_data = (
        filtered_df
        .groupby("city")["order_amount"]
        .mean()
        .sort_values(ascending=True)
    )

    fig = px.bar(
        x=city_data.values,
        y=city_data.index,
        orientation="h",
        labels={
            "x": "Average Order Amount",
            "y": "City"
        }
    )

    fig.update_traces(marker_color="#47B9A6")

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="bi_city_amount"
    )


    # --------------------------------
    # 3. Discount vs Order Amount
    # --------------------------------

    st.subheader("🏷️ Discount Percentage vs Order Amount")

    fig = px.scatter(
        filtered_df,
        x="discount_percent",
        y="order_amount",
        labels={
            "discount_percent": "Discount Percentage",
            "order_amount": "Order Amount"
        }
    )

    fig.update_traces(
        marker_color="#47B9A6"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="bi_discount_amount"
    )


    # --------------------------------
    # 4. Delivery Distance vs Actual Time
    # --------------------------------

    st.subheader("🚚 Delivery Distance vs Actual Delivery Time")

    fig = px.scatter(
        filtered_df,
        x="delivery_distance_km",
        y="actual_delivery_min",
        labels={
            "delivery_distance_km": "Delivery Distance (km)",
            "actual_delivery_min": "Actual Delivery Time (minutes)"
        }
    )

    fig.update_traces(
        marker_color="#47B9A6"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="bi_distance_time"
    )


    # --------------------------------
    # 5. Customer Age vs Order Amount
    # --------------------------------

    st.subheader("👤 Customer Age vs Order Amount")

    fig = px.scatter(
        filtered_df,
        x="customer_age",
        y="order_amount",
        labels={
            "customer_age": "Customer Age",
            "order_amount": "Order Amount"
        }
    )

    fig.update_traces(
        marker_color="#47B9A6"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="bi_age_amount"
    )


    # --------------------------------
    # 6. Rating vs Order Amount - Boxplot
    # --------------------------------

    st.subheader("⭐ Customer Rating vs Order Amount")

    fig = px.box(
        filtered_df,
        x="customer_rating",
        y="order_amount",
        labels={
            "customer_rating": "Customer Rating",
            "order_amount": "Order Amount"
        }
    )

    fig.update_traces(
        marker_color="#47B9A6"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="bi_rating_amount_box"
    )

        # --------------------------------
    # 7. Monthly Revenue Trend by Year
    # --------------------------------

    st.subheader("📅 Monthly Revenue Trend by Year")

    monthly_revenue = (
        filtered_df
        .groupby(
            ["year", "month", "month_name"]
        )["order_amount"]
        .sum()
        .reset_index()
        .sort_values(["year", "month"])
    )

    fig = px.line(
        monthly_revenue,
        x="month_name",
        y="order_amount",
        color="year",
        markers=True,
        labels={
            "month_name": "Month",
            "order_amount": "Total Order Amount",
            "year": "Year"
        }
    )

    fig.update_layout(
        title="Monthly Revenue Trend by Year",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(
        l=60,
        r=120,
        t=60,
        b=60
    )

    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="bi_monthly_revenue"
    )
# =========================================================
# MULTIVARIATE ANALYSIS
# =========================================================

elif st.session_state["analysis"] == "multivariate":

    st.markdown("### 🔗 Multivariate Analysis")

    # --------------------------------
    # 1. Distance + Time + Status
    # --------------------------------

    st.subheader(
        "🚚 Delivery Distance vs Actual Delivery Time by Order Status"
    )

    fig = px.scatter(
        filtered_df,
        x="delivery_distance_km",
        y="actual_delivery_min",
        color="order_status",
        labels={
            "delivery_distance_km": "Delivery Distance (km)",
            "actual_delivery_min": "Actual Delivery Time (minutes)",
            "order_status": "Order Status"
        }
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="multi_distance_time_status"
    )


    # --------------------------------
    # 2. Food Category + Gender + Amount
    # --------------------------------

    st.subheader(
        "🍕 Average Order Amount by Food Category and Gender"
    )

    food_gender = (
        filtered_df
        .groupby(
            ["food_category", "customer_gender"]
        )["order_amount"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        food_gender,
        x="food_category",
        y="order_amount",
        color="customer_gender",
        barmode="group",
        labels={
            "food_category": "Food Category",
            "order_amount": "Average Order Amount",
            "customer_gender": "Customer Gender"
        }
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="multi_food_gender_amount"
    )


    # --------------------------------
    # 3. City + Food Category + Amount
    # --------------------------------

    st.subheader(
        "🏙️ Average Order Amount by City and Food Category"
    )

    city_food = filtered_df.pivot_table(
        values="order_amount",
        index="city",
        columns="food_category",
        aggfunc="mean"
    )

    fig = px.imshow(
        city_food,
        aspect="auto",
        labels={
            "x": "Food Category",
            "y": "City",
            "color": "Average Order Amount"
        }
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="multi_city_food_amount"
    )


    # --------------------------------
    # 4. Food Category + Status + Amount
    # --------------------------------

    st.subheader(
        "🍕 Order Amount by Food Category and Order Status"
    )

    fig = px.box(
        filtered_df,
        x="food_category",
        y="order_amount",
        color="order_status",
        labels={
            "food_category": "Food Category",
            "order_amount": "Order Amount",
            "order_status": "Order Status"
        }
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="multi_food_status_box"
    )


    # --------------------------------
    # 5. Age Group + Gender + Amount
    # --------------------------------

    st.subheader(
        "👥 Average Order Amount by Age Group and Gender"
    )

    age_gender = (
        filtered_df
        .groupby(
            ["age_group", "customer_gender"]
        )["order_amount"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        age_gender,
        x="age_group",
        y="order_amount",
        color="customer_gender",
        barmode="group",
        labels={
            "age_group": "Age Group",
            "order_amount": "Average Order Amount",
            "customer_gender": "Customer Gender"
        }
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="multi_age_gender_amount"
    )
# -----------------------------
# Preview
# -----------------------------

st.subheader("💡 Key Business Insights")

st.markdown("""
<div style="
    background: linear-gradient(135deg, #FFFFFF 0%, #F0FFFC 100%);
    padding: 22px;
    border-radius: 15px;
    border-left: 6px solid #47B9A6;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin-top: 10px;
">

<h4 style="color:#073C3A; margin-bottom:15px;">
📊 Business Insights
</h4>

<p style="color:#333333; font-size:15px;">
📌 <b>Sales Analysis:</b> Food category-wise and city-wise sales help identify major sales segments.
</p>

<p style="color:#333333; font-size:15px;">
📌 <b>Customer Behaviour:</b> Payment methods and order status provide insights into customer ordering patterns.
</p>

<p style="color:#333333; font-size:15px;">
📌 <b>Delivery Performance:</b> Estimated and actual delivery times help understand delivery delays.
</p>

<p style="color:#333333; font-size:15px;">
📌 <b>Customer Analysis:</b> Age group, gender and customer ratings help understand customer characteristics.
</p>

<p style="color:#333333; font-size:15px;">
📌 <b>Discount Analysis:</b> Discount percentage can be compared with order amount to understand their relationship.
</p>

<p style="color:#333333; font-size:15px;">
📌 <b>Order Value:</b> Average order amount can be compared across different food categories and cities.
</p>

</div>
""", unsafe_allow_html=True)