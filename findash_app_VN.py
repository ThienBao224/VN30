# ===========================================================
# File: findash_app_VN.py
# Đề tài: Financial Dashboard cho dữ liệu VN-INDEX 30
# Nhóm: (Tên nhóm)
# Ngày: (Cập nhật)
# ===========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# ===========================================================
# 1️⃣ Tải dữ liệu VN30 tự động (chung cho toàn bộ ứng dụng)
# ===========================================================

@st.cache_data(ttl=3600)
def load_vn30_data():
    vn30_tickers = [
        "FPT.VN", "HPG.VN", "MWG.VN", "VNM.VN", "VCB.VN", "SSI.VN",
        "TCB.VN", "MBB.VN", "CTG.VN", "GAS.VN", "VHM.VN", "BVH.VN",
        "VIC.VN", "PLX.VN", "STB.VN", "SAB.VN", "NVL.VN", "VPB.VN"
    ]
    data_list = []
    for tk in vn30_tickers:
        try:
            df = yf.download(tk, period="1y", progress=False)

# Làm phẳng cột nếu là MultiIndex
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if not df.empty:
                df = df.reset_index()
                df["Ticker"] = tk.replace(".VN", "")
                data_list.append(df)

        except Exception as e:
            print(f"Lỗi tải {tk}: {e}")
    if data_list:
        return pd.concat(data_list)
    else:
        return pd.DataFrame()

# ===========================================================
# 2️⃣ Cấu trúc giao diện sidebar
# ===========================================================

st.sidebar.title("VN30 Financial Dashboard")
st.sidebar.write("Ứng dụng phân tích dữ liệu tài chính nhóm VN30")

st.sidebar.info("🔄 Đang tải dữ liệu VN30 ...")
data = load_vn30_data()

# ===============================
# ✅ Kiểm tra dữ liệu VN30 đã tải
# ===============================
if data.empty:
    st.error("❌ Không tải được dữ liệu. Kiểm tra kết nối mạng hoặc mã cổ phiếu.")
    st.stop()
else:
    num_tickers = data["Ticker"].nunique()
    num_rows = len(data)
    st.sidebar.success(f"✅ Tải thành công {num_tickers} mã cổ phiếu ({num_rows:,} dòng dữ liệu).")

tickers = sorted(data["Ticker"].unique())
ticker = st.sidebar.selectbox("Chọn mã cổ phiếu", tickers)

# ===========================================================
# 3️⃣ Khai báo các tab của ứng dụng
# ===========================================================

tab = st.sidebar.radio(
    "Chọn phần hiển thị:",
    ["Summary", "Chart", "Statistics", "Monte Carlo Simulation", "Portfolio Trend"]
)

# ===========================================================
# 4️⃣ TAB 1 - SUMMARY (Nguyễn Thị Hồng Thắm)
# ===========================================================

def tab_summary():
    # --- Tiêu đề chính căn giữa ---
    st.markdown(
        """
        <h1 style='text-align: center; color: #1a73e8;'>
            📊 Tab “Summary” – Tổng quan từng mã cổ phiếu VN30
        </h1>
        """,
        unsafe_allow_html=True
    )

    

    # --- 1️⃣ Lọc dữ liệu theo mã được chọn ---
    df_ticker = data[data["Ticker"] == ticker].copy()
    df_ticker = df_ticker.sort_values("Date")

    if df_ticker.empty:
        st.warning("⚠️ Không có dữ liệu cho mã cổ phiếu này.")
        return

    # --- Tiêu đề phụ thông báo mã đang hiển thị ---
    st.markdown(
        f"""
        <h3 style='text-align: center; color: #34a853;'>
            🔍 Đang hiển thị dữ liệu cổ phiếu: <b>{ticker}</b>
        </h3>
        """,
        unsafe_allow_html=True
    )

    # --- 2️⃣ Tính toán các chỉ số tổng quan ---
    df_ticker["Return"] = df_ticker["Close"].pct_change()
    latest_close = df_ticker["Close"].iloc[-1]                     # Giá đóng cửa gần nhất
    mean_30d = df_ticker["Close"].tail(30).mean()                  # Trung bình 30 ngày gần nhất
    std_return = df_ticker["Return"].std()                         # Độ lệch chuẩn lợi nhuận

    # --- 3️⃣ Hiển thị các chỉ tiêu cơ bản ---
    st.subheader("📈 Các chỉ tiêu cơ bản")
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Giá đóng cửa mới nhất", f"{latest_close:,.2f} VND")
    col2.metric("📆 Trung bình 30 ngày gần nhất", f"{mean_30d:,.2f} VND")
    col3.metric("📉 Độ lệch chuẩn lợi nhuận (σ)", f"{std_return:.2%}")

    st.markdown("""
    <div style="text-align: justify;">
    Các chỉ tiêu trên là <b>thước đo định lượng</b> quan trọng:
    <ul>
        <li>💰 <b>Giá đóng cửa mới nhất</b>: phản ánh giá trị hiện hành trên thị trường.</li>
        <li>📆 <b>Giá trung bình 30 ngày</b>: thể hiện xu hướng ngắn hạn.</li>
        <li>📉 <b>Độ lệch chuẩn lợi nhuận (σ)</b>: biểu thị mức độ biến động và rủi ro của cổ phiếu.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- 4️⃣ Biểu đồ giá cổ phiếu ---
    st.subheader(f"📊 Diễn biến giá cổ phiếu {ticker} trong 1 năm gần đây")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_ticker["Date"],
        y=df_ticker["Close"],
        mode="lines",
        name="Giá đóng cửa",
        line=dict(color="#0077b6", width=2),
        fill="tozeroy",
        fillcolor="rgba(0, 119, 182, 0.25)"
    ))

    # Bộ chọn thời gian
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all", label="MAX")
            ])
        ),
        rangeslider=dict(visible=False),
        type="date"
    )

    # Tùy chỉnh giao diện
    fig.update_layout(
        title=f"Biểu đồ biến động giá cổ phiếu {ticker}",
        xaxis_title="Thời gian",
        yaxis_title="Giá đóng cửa (VND)",
        template="plotly_white",
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=60, b=30)
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})

    # --- 5️⃣ Bảng dữ liệu 100 ngày gần nhất ---
    st.subheader("📋 Bảng dữ liệu 100 ngày gần nhất")
    df_recent = df_ticker.tail(100)[["Date", "Open", "High", "Low", "Close", "Volume"]]
    st.dataframe(
        df_recent.style.format({
            "Open": "{:,.2f}",
            "High": "{:,.2f}",
            "Low": "{:,.2f}",
            "Close": "{:,.2f}",
            "Volume": "{:,.0f}"
        }),
        use_container_width=True,
        height=350
    )

    

    

# ===========================================================
# 5️⃣ TAB 2 - CHART (Phan Văn Thảo)
# ===========================================================

def tab_chart():
    st.title("📈 Phân tích biểu đồ giá và chỉ báo kỹ thuật")
    df_ticker = data[data["Ticker"] == ticker]

    # Tính SMA (đường trung bình động)
    df_ticker["SMA_20"] = df_ticker["Close"].rolling(window=20).mean()
    df_ticker["SMA_50"] = df_ticker["Close"].rolling(window=50).mean()

    # Biểu đồ giá + SMA
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_ticker["Date"], y=df_ticker["Close"], mode="lines", name="Close"))
    fig.add_trace(go.Scatter(x=df_ticker["Date"], y=df_ticker["SMA_20"], mode="lines", name="SMA 20"))
    fig.add_trace(go.Scatter(x=df_ticker["Date"], y=df_ticker["SMA_50"], mode="lines", name="SMA 50"))
    fig.update_layout(title=f"Đường giá và trung bình động của {ticker}")
    st.plotly_chart(fig, use_container_width=True)

# ===========================================================
# 6️⃣ TAB 3 - STATISTICS (Nguyễn Hoàng Thiên Bảo)
# ===========================================================
def tab_statistics():
    # --- Tiêu đề tab ---
    st.markdown("""
        <h1 style='text-align: center; color: #1a73e8;'>
            📉 Tab “Statistics” – Phân tích thống kê & rủi ro cổ phiếu
        </h1>
    """, unsafe_allow_html=True)

    # --- Lọc dữ liệu theo mã cổ phiếu được chọn ---
    df_ticker = data[data["Ticker"] == ticker].copy()
    if df_ticker.empty:
        st.warning("⚠️ Không có dữ liệu cho mã cổ phiếu này.")
        return

    # --- Tính tỷ suất lợi nhuận hàng ngày ---
    df_ticker["Lợi_nhuận"] = df_ticker["Close"].pct_change()
    df_ticker.dropna(inplace=True)

    # --- Thêm cột Tháng & Quý (1 lần duy nhất) ---
    df_ticker["Tháng"] = df_ticker["Date"].dt.to_period("M")
    df_ticker["Quý"] = df_ticker["Date"].dt.to_period("Q")

    # --- Bảng mô tả thống kê cơ bản ---
    st.subheader("📋 Bảng mô tả thống kê cơ bản")
    stats_df = df_ticker["Lợi_nhuận"].describe().to_frame()
    stats_df.loc["Độ lệch (Skew)"] = df_ticker["Lợi_nhuận"].skew()
    stats_df.loc["Độ nhọn (Kurtosis)"] = df_ticker["Lợi_nhuận"].kurt()
    sharpe_ratio = df_ticker["Lợi_nhuận"].mean() / df_ticker["Lợi_nhuận"].std()
    stats_df.loc["Chỉ số Sharpe (Lợi nhuận theo rủi ro)"] = sharpe_ratio

    # Hiển thị bảng
    st.dataframe(
        stats_df.style.format("{:.4f}").set_table_styles(
            [{'selector': 'th', 'props': [('text-align', 'left')]}]
        ),
        use_container_width=True,
        height=400
    )

    # --- Boxplot lợi nhuận ---
    fig_box = px.box(
        df_ticker, y="Lợi_nhuận",
        color_discrete_sequence=["#ff6361"],
        title=f"Boxplot lợi nhuận cổ phiếu {ticker}",
        labels={"Lợi_nhuận": "Tỷ suất lợi nhuận hàng ngày"}
    )
    fig_box.update_layout(template="plotly_white")
    st.plotly_chart(fig_box, use_container_width=True)

    # --- Giải thích ý nghĩa ---
    st.markdown("""
    <div style="text-align: justify;">
    <b>💡 Nhận xét:</b>
    <ul>
        <li><b>Mean</b>: Lợi nhuận trung bình mỗi ngày (cao là tốt).</li>
        <li><b>Std</b>: Độ biến động lợi nhuận (cao là rủi ro cao).</li>
        <li><b>Min / Max</b>: Biên độ dao động cực trị.</li>
        <li><b>Skew</b>: Độ lệch phân phối (âm = dễ giảm mạnh, dương = dễ tăng mạnh).</li>
        <li><b>Kurtosis</b>: Độ nhọn, thể hiện mức độ xuất hiện của biến động cực đoan.</li>
        <li><b>Sharpe Ratio</b>: Đo hiệu quả lợi nhuận so với rủi ro (càng lớn càng tốt).</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- Histogram lợi nhuận ---
    st.subheader("📊 Phân phối tỷ suất lợi nhuận (Rủi ro biến động)")
    fig_hist = px.histogram(
        df_ticker, x="Lợi_nhuận", nbins=40,
        color_discrete_sequence=["#1a73e8"],
        title=f"Phân phối lợi nhuận cổ phiếu {ticker}",
        labels={"Lợi_nhuận": "Tỷ suất lợi nhuận hàng ngày", "count": "Số ngày"}
    )
    fig_hist.update_layout(template="plotly_white")
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("""
    <div style="text-align: justify;">
    <b>📘 Giải thích:</b>
    <ul>
        <li>Biểu đồ histogram cho thấy mức độ thường xuyên của các mức lợi nhuận.</li>
        <li>Phần lớn cột nằm bên phải 0 ⇒ cổ phiếu thường sinh lãi.</li>
        <li>Biểu đồ boxplot giúp phát hiện ngày biến động cực mạnh (outliers).</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- Lợi nhuận trung bình theo Tháng & Quý ---
    st.subheader("📅 Lợi nhuận trung bình theo Tháng và Quý")

    # Theo Tháng
    monthly_ret = df_ticker.groupby("Tháng")["Lợi_nhuận"].mean().reset_index()
    monthly_ret["Tháng"] = monthly_ret["Tháng"].astype(str)
    fig_month = px.bar(
        monthly_ret, x="Tháng", y="Lợi_nhuận",
        title="Lợi nhuận trung bình theo Tháng",
        text_auto=".2%", color_discrete_sequence=["#003f5c"],
        labels={"Tháng": "Tháng (YYYY-MM)", "Lợi_nhuận": "Tỷ suất lợi nhuận trung bình"}
    )
    fig_month.update_layout(xaxis=dict(tickangle=-45, automargin=True), yaxis=dict(automargin=True), template="plotly_white")
    fig_month.update_traces(textposition='outside', cliponaxis=False)
    st.plotly_chart(fig_month, use_container_width=True)

    # Theo Quý
    quarterly_ret = df_ticker.groupby("Quý")["Lợi_nhuận"].mean().reset_index()
    quarterly_ret["Quý"] = quarterly_ret["Quý"].astype(str)
    fig_quarter = px.bar(
        quarterly_ret, x="Quý", y="Lợi_nhuận",
        title="Lợi nhuận trung bình theo Quý",
        text_auto=".2%", color_discrete_sequence=["#58508d"],
        labels={"Quý": "Quý (YYYYQ)", "Lợi_nhuận": "Tỷ suất lợi nhuận trung bình"}
    )
    fig_quarter.update_layout(xaxis_tickangle=0, template="plotly_white")
    st.plotly_chart(fig_quarter, use_container_width=True)

    st.markdown("""
    <div style="text-align: justify;">
    <b>📙 Nhận xét:</b>
    <ul>
        <li>Các biểu đồ trên cho thấy xu hướng lợi nhuận thay đổi theo thời gian.</li>
        <li>Tháng hoặc quý có giá trị dương cao ⇒ giai đoạn cổ phiếu hoạt động tốt.</li>
        <li>Phù hợp để đánh giá mùa vụ và hiệu suất trung hạn.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- Sharpe Ratio theo Tháng và Quý (dạng %) ---
    st.subheader("📈 Sharpe Ratio theo Tháng và Quý")

    # Theo Tháng
    monthly_stats = df_ticker.groupby("Tháng")["Lợi_nhuận"].agg(['mean', 'std']).reset_index()
    monthly_stats["Sharpe"] = (monthly_stats["mean"] / monthly_stats["std"]) * 100
    monthly_stats["Tháng"] = monthly_stats["Tháng"].astype(str)
    fig_sharpe_month = px.bar(
        monthly_stats,
        x="Tháng",
        y="Sharpe",
        text=monthly_stats["Sharpe"].map("{:.2f}%".format),
        color_discrete_sequence=["#ff7f0e"],
        title=f"Sharpe Ratio theo Tháng của {ticker}",
        labels={"Sharpe": "Sharpe Ratio (%)", "Tháng": "Tháng (YYYY-MM)"}
    )
    fig_sharpe_month.update_layout(xaxis=dict(tickangle=-45, automargin=True), yaxis=dict(automargin=True), template="plotly_white")
    fig_sharpe_month.update_traces(textposition='outside', cliponaxis=False)
    st.plotly_chart(fig_sharpe_month, use_container_width=True)

    # Theo Quý
    quarterly_stats = df_ticker.groupby("Quý")["Lợi_nhuận"].agg(['mean', 'std']).reset_index()
    quarterly_stats["Sharpe"] = (quarterly_stats["mean"] / quarterly_stats["std"]) * 100
    quarterly_stats["Quý"] = quarterly_stats["Quý"].astype(str)
    fig_sharpe_quarter = px.bar(
        quarterly_stats,
        x="Quý",
        y="Sharpe",
        text=quarterly_stats["Sharpe"].map("{:.2f}%".format),
        color_discrete_sequence=["#ffa600"],
        title=f"Sharpe Ratio theo Quý của {ticker}",
        labels={"Sharpe": "Sharpe Ratio (%)", "Quý": "Quý (YYYYQ)"}
    )
    fig_sharpe_quarter.update_layout(xaxis=dict(tickangle=0, automargin=True), yaxis=dict(automargin=True), template="plotly_white")
    fig_sharpe_quarter.update_traces(textposition='outside', cliponaxis=False)
    st.plotly_chart(fig_sharpe_quarter, use_container_width=True)

    # Giải thích Sharpe Ratio
    st.markdown("""
    <div style="text-align: justify;">
    <b>💡 Lợi nhuận theo rủi ro:</b>  
    Chỉ số <b>Sharpe Ratio</b> đo hiệu quả sinh lời của cổ phiếu so với mức rủi ro.  

    - Giá trị cao → cổ phiếu mang lại lợi nhuận tốt trên mỗi đơn vị rủi ro.  
    - Giá trị thấp → lợi nhuận không xứng đáng với mức rủi ro phải chịu.  
    - Hiển thị ở dạng % giúp dễ so sánh và trực quan hơn.
    </div>
    """, unsafe_allow_html=True)


# ===========================================================
# 7️⃣ TAB 4 - MONTE CARLO SIMULATION (Phan Văn Thảo)
# ===========================================================

def tab_montecarlo():
    st.title("🎲 Mô phỏng Monte Carlo")
    df_ticker = data[data["Ticker"] == ticker]
    df_ticker["Return"] = df_ticker["Close"].pct_change().dropna()
    daily_vol = df_ticker["Return"].std()
    last_price = df_ticker["Close"].iloc[-1]

    n_sim = st.slider("Số lần mô phỏng", 200, 1000, 500)
    t_horizon = st.slider("Số ngày dự báo", 30, 180, 60)

    np.random.seed(42)
    simulation_df = pd.DataFrame()

    for i in range(n_sim):
        price_series = [last_price]
        for j in range(t_horizon):
            price_series.append(price_series[-1] * (1 + np.random.normal(0, daily_vol)))
        simulation_df[i] = price_series

    st.line_chart(simulation_df)
# ===========================================================
# 8️⃣ TAB 5 - PORTFOLIO TREND (Nguyễn Hoàng Thiên Bảo)
# ===========================================================

def tab_portfolio():
    st.markdown("""
        <h1 style='text-align: center; color: #1a73e8;'>
            📊 So sánh xu hướng
        </h1>
    """, unsafe_allow_html=True)

    # --- Chọn cổ phiếu để so sánh ---
    selected = st.multiselect(
        "📌 Chọn cổ phiếu để so sánh xu hướng", 
        tickers, 
        default=["FPT", "VNM", "VCB", "HPG", "SSI", "MWG"]
    )

    if not selected:
        st.warning("⚠️ Vui lòng chọn ít nhất một mã cổ phiếu.")
        return

    df_port = data[data["Ticker"].isin(selected)].copy()
    df_port = df_port.sort_values(["Ticker", "Date"])

    # --- Biểu đồ 1: Biến động giá chuẩn hóa (%) ---
    df_port["Norm_Close"] = df_port.groupby("Ticker")["Close"].transform(lambda x: x / x.iloc[0] * 100)
    df_port["Tooltip_Norm"] = df_port.apply(
        lambda row: f"{row['Ticker']}<br>Ngày: {row['Date'].strftime('%Y-%m-%d')}<br>Giá: {row['Close']:,.0f} VND<br>Tỷ lệ: {row['Norm_Close']:.2f}%", axis=1
    )

    st.subheader("📈 Biểu đồ Biến động giá chuẩn hóa (%)")
    fig1 = px.line(
        df_port,
        x="Date",
        y="Norm_Close",
        color="Ticker",
        labels={"Date": "Thời gian", "Norm_Close": "Biến động giá (%)", "Close": "Giá (VND)"},
        hover_data={
            "Ticker": True,
            "Date": True,
            "Close": ":,.0f",
            "Norm_Close": ":.2f"
        }
    )
    fig1.update_layout(template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)


    st.markdown("""
    <div style="text-align: justify;">
    <b>Dựa vào biểu đồ ta thấy:</b>
    <ul>
        <li>Giá được chuẩn hóa để ngày đầu tiên = 100%.</li>
        <li>Đường tăng thể hiện cổ phiếu tăng nhanh hơn mức trung bình.</li>
        <li>Đường giảm thể hiện cổ phiếu giảm so với ngày đầu.</li>
        <li>Dễ so sánh hiệu suất nhiều cổ phiếu cùng lúc.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- Biểu đồ 2: Giá thực tế (VND) ---
    df_port["Tooltip_Value"] = df_port.apply(
        lambda row: f"{row['Ticker']}<br>Ngày: {row['Date'].strftime('%Y-%m-%d')}<br>Giá: {row['Close']:,.0f} VND", axis=1
    )

    st.subheader("📈 Biểu đồ Giá thực tế (VND)")
    fig2 = px.line(
        df_port,
        x="Date",
        y="Close",
        color="Ticker",
        labels={"Date": "Thời gian", "Close": "Giá (VND)"},
        hover_data={
            "Ticker": True,
            "Date": True,
            "Close": ":,.0f"
        }
    )
    fig2.update_layout(template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div style="text-align: justify;">
    <b>Dựa vào biểu đồ ta thấy:</b>
    <ul>
        <li>Hiển thị giá thực tế của các cổ phiếu.</li>
        <li>Giúp quan sát mức giá tuyệt đối theo VND.</li>
        <li>Phù hợp để so sánh giá hiện tại giữa các cổ phiếu cùng thời điểm.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ===========================================================
# 9️⃣ Chạy ứng dụng chính
# ===========================================================

if tab == "Summary":
    tab_summary()
elif tab == "Chart":
    tab_chart()
elif tab == "Statistics":
    tab_statistics()
elif tab == "Monte Carlo Simulation":
    tab_montecarlo()
elif tab == "Portfolio Trend":
    tab_portfolio()

