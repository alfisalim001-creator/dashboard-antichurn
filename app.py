import streamlit as pd
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="Executive Dashboard Anti-Churn 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk Executive Dark Mode & Clean UI
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetric"] label {
        color: #8b949e !important;
        font-weight: 600;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #58a6ff !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOAD DATA DARI GOOGLE SHEETS
# ==========================================
@st.cache_data(ttl=600)
def load_data():
    try:
        # Menggunakan koneksi native Streamlit gsheets
        conn = st.connection("gsheets", type="gsheets")
        
        # Baca worksheet pencapaian_revenue
        df_rev = conn.read(worksheet="pencapaian_revenue", ttl=5)
        if df_rev is None or df_rev.empty:
            df_rev = pd.DataFrame(columns=['TanggalBayar', 'SBU', 'KP', 'Type', 'Revenue_Standalone', 'Transaksi_Standalone', 'Revenue_Akumulasi', 'Transaksi_Akumulasi'])

        # Baca worksheet tren_followup (opsional)
        try:
            df_fol = conn.read(worksheet="tren_followup", ttl=5)
        except Exception:
            df_fol = pd.DataFrame()

        return df_rev, df_fol
    except Exception as e:
        st.error(f"❌ Gagal memuat data dari Google Sheets. Pastikan koneksi gsheets sudah diatur di secrets. Detail: {e}")
        st.stop()

df_revenue, df_followup = load_data()

# Validasi & Konversi Format Tanggal dan Angka
if not df_revenue.empty:
    df_revenue['TanggalBayar'] = pd.to_datetime(df_revenue['TanggalBayar'], errors='coerce')
    df_revenue['Revenue_Standalone'] = pd.to_numeric(df_revenue['Revenue_Standalone'], errors='coerce').fillna(0)
    df_revenue['Transaksi_Standalone'] = pd.to_numeric(df_revenue['Transaksi_Standalone'], errors='coerce').fillna(0)
    df_revenue['Revenue_Akumulasi'] = pd.to_numeric(df_revenue['Revenue_Akumulasi'], errors='coerce').fillna(0)
    df_revenue['Transaksi_Akumulasi'] = pd.to_numeric(df_revenue['Transaksi_Akumulasi'], errors='coerce').fillna(0)

# ==========================================
# 3. SIDEBAR: GLOBAL FILTER PANEL
# ==========================================
st.sidebar.markdown("## 🎛️ Filter Panel")
st.sidebar.markdown("---")

if not df_revenue.empty:
    all_sbu = sorted(df_revenue['SBU'].dropna().unique().tolist())
    selected_sbu = st.sidebar.multiselect("Pilih SBU / Regional", options=all_sbu, default=all_sbu)
    
    filtered_df_kp = df_revenue[df_revenue['SBU'].isin(selected_sbu)]
    all_kp = sorted(filtered_df_kp['KP'].dropna().unique().tolist())
    selected_kp = st.sidebar.multiselect("Pilih Kantor Perwakilan (KP)", options=all_kp, default=all_kp)

    all_type = sorted(df_revenue['Type'].dropna().unique().tolist())
    selected_type = st.sidebar.multiselect("Pilih Jenis Program (Type)", options=all_type, default=all_type)

    valid_dates = df_revenue['TanggalBayar'].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
    else:
        min_date = datetime.today().date()
        max_date = datetime.today().date()
    
    date_range = st.sidebar.date_input(
        "Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    df_filtered = df_revenue[
        df_revenue['SBU'].isin(selected_sbu) &
        df_revenue['KP'].isin(selected_kp) &
        df_revenue['Type'].isin(selected_type)
    ]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_filtered[
            (df_filtered['TanggalBayar'].dt.date >= start_date) &
            (df_filtered['TanggalBayar'].dt.date <= end_date)
        ]
else:
    df_filtered = pd.DataFrame()
    st.sidebar.warning("Data Revenue belum tersedia.")

# ==========================================
# 4. MAIN CONTENT & TABS UI/UX
# ==========================================
st.title("⚡ Executive Dashboard Anti-Churn & Revenue")
st.markdown("Monitoring performa operasional, pencapaian harian (*stand-alone*), dan pertumbuhan kumulatif (*akumulasi*) regional ICONNET.")
st.markdown("---")

if df_filtered.empty:
    st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang Anda pilih.")
else:
    tab_summary, tab_followup, tab_standalone, tab_accumulated = st.tabs([
        "📊 Executive Summary", 
        "📞 Follow-up & Operasional", 
        "💰 Pencapaian Stand-Alone", 
        "📈 Pencapaian Akumulasi"
    ])

    with tab_summary:
        st.subheader("📌 Ringkasan Performa Utama")
        
        total_rev_sa = df_filtered['Revenue_Standalone'].sum()
        total_trx_sa = df_filtered['Transaksi_Standalone'].sum()
        max_date_filtered = df_filtered['TanggalBayar'].max()
        df_latest_acc = df_filtered[df_filtered['TanggalBayar'] == max_date_filtered]
        total_rev_acc = df_latest_acc['Revenue_Akumulasi'].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue Stand-Alone", f"Rp {total_rev_sa:,.0f}".replace(",", "."))
        col2.metric(f"Total Akumulasi Revenue (per {max_date_filtered.strftime('%d-%m-%Y')})", f"Rp {total_rev_acc:,.0f}".replace(",", "."))
        col3.metric("Total Transaksi Periode Ini", f"{total_trx_sa:,.0f} Trx".replace(",", "."))

        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 📈 Tren Harian Revenue (Stand-Alone)")
            df_trend = df_filtered.groupby('TanggalBayar')['Revenue_Standalone'].sum().reset_index()
            fig_trend = px.line(df_trend, x='TanggalBayar', y='Revenue_Standalone', template='plotly_dark', markers=True, color_discrete_sequence=['#58a6ff'])
            fig_trend.update_layout(xaxis_title="Tanggal", yaxis_title="Revenue (Rp)", margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)

        with c2:
            st.markdown("#### 🏢 Kontribusi Revenue per SBU")
            df_sbu = df_filtered.groupby('SBU')['Revenue_Standalone'].sum().reset_index()
            fig_sbu = px.bar(df_sbu, x='SBU', y='Revenue_Standalone', template='plotly_dark', color='SBU', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_sbu.update_layout(xaxis_title="SBU", yaxis_title="Total Revenue (Rp)", showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_sbu, use_container_width=True)

    with tab_followup:
        st.subheader("📞 Modul Analisis Follow-up & Tagihan")
        if not df_followup.empty:
            st.dataframe(df_followup, use_container_width=True)
        else:
            st.info("💡 Modul follow-up siap diintegrasikan dengan data dari tab `tren_followup` Google Sheets Anda.")

    with tab_standalone:
        st.subheader("💰 Analisis Fluktuasi Harian (Stand-Alone)")
        st.markdown("Menampilkan data transaksi dan nominal pencapaian murni per hari.")

        df_table_sa = df_filtered.groupby(['TanggalBayar', 'SBU', 'KP', 'Type'])[['Revenue_Standalone', 'Transaksi_Standalone']].sum().reset_index()
        df_table_sa['TanggalBayar'] = df_table_sa['TanggalBayar'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            df_table_sa.style.format({
                'Revenue_Standalone': 'Rp {:,.0f}',
                'Transaksi_Standalone': '{:,.0f}'
            }),
            use_container_width=True,
            height=400
        )

    with tab_accumulated:
        st.subheader("📈 Trajektori Pertumbuhan Kumulatif (Akumulasi)")
        st.markdown("Grafik laju pertumbuhan berjalan (*running total*) untuk mengukur pencapaian target jangka panjang.")

        df_acc_trend = df_filtered.groupby('TanggalBayar')[['Revenue_Akumulasi', 'Transaksi_Akumulasi']].max().reset_index()
        
        fig_acc = px.area(
            df_acc_trend, 
            x='TanggalBayar', 
            y='Revenue_Akumulasi', 
            template='plotly_dark',
            color_discrete_sequence=['#238636']
        )
        fig_acc.update_layout(
            xaxis_title="Tanggal", 
            yaxis_title="Akumulasi Revenue (Rp)", 
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_acc, use_container_width=True)

        st.markdown("#### 📋 Detail Tabel Akumulasi per Wilayah")
        df_table_acc = df_filtered.groupby(['TanggalBayar', 'SBU', 'KP', 'Type'])[['Revenue_Akumulasi', 'Transaksi_Akumulasi']].max().reset_index()
        df_table_acc['TanggalBayar'] = df_table_acc['TanggalBayar'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            df_table_acc.style.format({
                'Revenue_Akumulasi': 'Rp {:,.0f}',
                'Transaksi_Akumulasi': '{:,.0f}'
            }),
            use_container_width=True,
            height=400
        )
