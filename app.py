
import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='StatVista | Analisis Statistika', page_icon='📊', layout='wide')
st.markdown("""<style>
.stApp {background:linear-gradient(145deg,#e0f7ff 0%,#c9ecff 48%,#edfaff 100%);color:#24304b}
.block-container {padding-top:1.6rem;max-width:1200px}
h1,h2,h3 {color:#124c78!important;letter-spacing:-.5px}
h1 {font-size:clamp(2.1rem,5vw,3.5rem)!important}
[data-testid="stSidebar"] {background:linear-gradient(170deg,#d7f3ff,#bce6ff,#e7f8ff)}
[data-testid="stMetric"] {background:linear-gradient(135deg,#ffffff,#e2f5ff 65%,#cbeaff);border:2px solid #a5dcfa;border-radius:22px;padding:20px;box-shadow:0 10px 28px #298aca20}
[data-testid="stMetricLabel"] {color:#176b9d}
[data-testid="stMetricValue"] {color:#087bb5}
[data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {background:#ffffffcc;border-radius:20px;padding:8px;box-shadow:0 8px 24px #2488b01c}
.stButton>button, .stDownloadButton>button {border-radius:14px!important;background:linear-gradient(90deg,#168bd2,#25b8db)!important;color:white!important;border:0!important;font-weight:700!important}
.stSelectbox>div, .stMultiSelect>div {border-radius:14px}
hr {border-color:#a5dcfa}
@media(max-width:600px){.block-container{padding:1rem .8rem} [data-testid="stMetric"]{padding:12px}}
</style>""",unsafe_allow_html=True)

st.title('StatVista')
st.caption('Dashboard Interaktif • Statistika Deskriptif | UTS Matematika 1B')
st.info('✨ Unggah Excel/CSV, pilih variabel, eksplorasi grafik, dan unduh hasil analisis dengan mudah!')

@st.cache_data
def load_data(file_bytes, name):
    b=io.BytesIO(file_bytes)
    if name.lower().endswith('.csv'):
        try:return pd.read_csv(b)
        except UnicodeDecodeError:
            b.seek(0);return pd.read_csv(b,encoding='latin1')
    return pd.read_excel(b)

with st.sidebar:
    st.header('⚙️ Pengaturan Analisis')
    upload=st.file_uploader('Unggah dataset',type=['xlsx','xls','csv'])
    st.caption('Format: .xlsx, .xls, .csv')
    st.divider()
    st.subheader('Panduan singkat')
    st.write('1. Unggah file atau gunakan data contoh.\n\n2. Pilih variabel numerik.\n\n3. Pilih ukuran statistik.\n\n4. Lihat grafik dan unduh hasil.')
    st.info('Varians dan simpangan baku menggunakan rumus **sampel (ddof=1)**. Kuartil memakai interpolasi linear.')

if upload is not None:
    try:df=load_data(upload.getvalue(),upload.name)
    except Exception as e:
        st.error(f'File gagal dibaca: {e}');st.stop()
    label=upload.name
else:
    df=pd.DataFrame({'Usia':[18,19,20,19,21,18,20,22,19,21,20,18], 'Tinggi Badan (cm)':[160,168,172,165,174,158,170,176,166,173,169,162], 'Berat Badan (kg)':[51,60,68,56,72,49,65,77,58,70,63,53], 'Nilai Ujian':[78,85,90,82,94,74,88,96,80,92,86,76], 'Kelas':['1B']*12})
    label='Data contoh (otomatis)'
    st.info('💡 Belum ada file diunggah. Dashboard menggunakan **data contoh** agar fitur dapat langsung dicoba.')

st.subheader('📁 Dataset')
a,b,c=st.columns(3)
a.metric('Jumlah baris',f'{len(df):,}')
b.metric('Jumlah kolom',len(df.columns))
c.metric('Total nilai kosong',int(df.isna().sum().sum()))
st.caption(f'Sumber: {label}')
with st.expander('Lihat tabel dataset',expanded=True):
    st.dataframe(df,use_container_width=True,hide_index=True)

numeric=df.select_dtypes(include='number').columns.tolist()
if not numeric:
    st.warning('Dataset tidak memiliki kolom numerik. Gunakan file yang berisi angka.');st.stop()
st.subheader('🔎 Konfigurasi Analisis')
variables=st.multiselect('Pilih satu atau beberapa variabel numerik',numeric,default=numeric[:min(3,len(numeric))])
options=['N','Minimum','Maksimum','Mean','Median','Modus','Varians','Standar Deviasi','Q1','Q2','Q3']
metrics=st.multiselect('Pilih ukuran statistika',options,default=options)
if not variables or not metrics:
    st.warning('Pilih minimal satu variabel dan satu ukuran statistik.');st.stop()

def mode_str(s):
    m=s.mode(dropna=True)
    if m.empty:return np.nan
    return ', '.join(f'{v:g}' if isinstance(v,(int,float,np.integer,np.floating)) else str(v) for v in m.iloc[:5]) + (' …' if len(m)>5 else '')

rows=[]
for col in variables:
    s=pd.to_numeric(df[col],errors='coerce').dropna()
    row={'Variabel':col,'N':len(s),'Minimum':s.min() if len(s) else np.nan,'Maksimum':s.max() if len(s) else np.nan,'Mean':s.mean() if len(s) else np.nan,'Median':s.median() if len(s) else np.nan,'Modus':mode_str(s),'Varians':s.var(ddof=1) if len(s)>1 else np.nan,'Standar Deviasi':s.std(ddof=1) if len(s)>1 else np.nan,'Q1':s.quantile(.25) if len(s) else np.nan,'Q2':s.quantile(.5) if len(s) else np.nan,'Q3':s.quantile(.75) if len(s) else np.nan}
    rows.append(row)
result=pd.DataFrame(rows)[['Variabel']+metrics]
st.subheader('📋 Ringkasan Statistika Deskriptif')
st.dataframe(result.style.format({k:'{:,.2f}' for k in metrics if k not in ['N','Modus']},na_rep='—'),use_container_width=True,hide_index=True)
st.caption('N = banyak data valid (tidak kosong). Modus dapat memiliki lebih dari satu nilai. Varians/standar deviasi tidak tersedia bila N < 2.')

st.subheader('📈 Visualisasi Data')
col1,col2=st.columns([1,1])
with col1:
    chosen=st.selectbox('Variabel untuk grafik',variables)
with col2:
    chart=st.selectbox('Jenis grafik',['Histogram','Boxplot','Diagram batang frekuensi','Diagram lingkaran frekuensi'])
color=st.color_picker('🎨 Pilih warna grafik','#A855F7')
series=pd.to_numeric(df[chosen],errors='coerce').dropna()
if series.empty:
    st.warning('Tidak ada nilai valid untuk digambarkan.')
else:
    if chart=='Histogram':
        bins=st.slider('Jumlah kelompok (bins)',3,30,10)
        fig=px.histogram(x=series,nbins=bins,labels={'x':chosen,'y':'Frekuensi'},title=f'Distribusi {chosen}',color_discrete_sequence=[color])
        fig.update_layout(yaxis_title='Frekuensi')
    elif chart=='Boxplot':
        fig=px.box(y=series,labels={'y':chosen},title=f'Boxplot {chosen}',color_discrete_sequence=[color],points='outliers')
    else:
        freq=series.value_counts().sort_index().reset_index()
        freq.columns=['Nilai','Frekuensi']
        if len(freq)>30:st.info('Banyak nilai unik; grafik menampilkan 30 nilai dengan frekuensi tertinggi.');freq=freq.nlargest(30,'Frekuensi')
        freq['Nilai']=freq['Nilai'].astype(str)
        if chart=='Diagram batang frekuensi':fig=px.bar(freq,x='Nilai',y='Frekuensi',title=f'Frekuensi {chosen}',color_discrete_sequence=[color])
        else:fig=px.pie(freq,names='Nilai',values='Frekuensi',title=f'Proporsi Nilai {chosen}',color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(template='plotly_white',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',margin=dict(l=15,r=15,t=55,b=15))
    st.plotly_chart(fig,use_container_width=True)

st.subheader('📊 Tabel Distribusi Frekuensi')
valid=series
if len(valid):
    grouping=st.radio('Pengelompokan',['Nilai unik','Interval kelas'],horizontal=True)
    if grouping=='Nilai unik':
        frequency=valid.value_counts().sort_index().rename_axis('Nilai').reset_index(name='Frekuensi')
    else:
        classes=st.slider('Jumlah kelas',2,20,6)
        if valid.nunique()==1:frequency=pd.DataFrame({'Interval':[str(valid.iloc[0])],'Frekuensi':[len(valid)]})
        else:
            counts,edges=np.histogram(valid,bins=classes)
            frequency=pd.DataFrame({'Interval':[f'{edges[i]:.2f} – {edges[i+1]:.2f}' for i in range(len(counts))],'Frekuensi':counts})
    frequency['Persentase (%)']=(frequency['Frekuensi']/len(valid)*100).round(2)
    frequency['Frekuensi Kumulatif']=frequency['Frekuensi'].cumsum()
    st.dataframe(frequency,use_container_width=True,hide_index=True)

st.subheader('💡 Interpretasi Otomatis')
for col in variables:
    s=pd.to_numeric(df[col],errors='coerce').dropna()
    if len(s):
        st.write(f'**{col}:** Dari **{len(s)}** data valid, nilai berkisar antara **{s.min():.2f}** dan **{s.max():.2f}**. Rata-rata **{s.mean():.2f}**, median **{s.median():.2f}**. Terdapat **{len(df)-len(s)}** data kosong/tidak numerik.')

st.subheader('⬇️ Unduh Hasil')
left,right=st.columns(2)
left.download_button('Unduh ringkasan CSV',result.to_csv(index=False).encode('utf-8-sig'),file_name='ringkasan_statistika.csv',mime='text/csv',use_container_width=True)
buf=io.BytesIO()
with pd.ExcelWriter(buf,engine='openpyxl') as writer:
    result.to_excel(writer,index=False,sheet_name='Ringkasan')
    df.to_excel(writer,index=False,sheet_name='Dataset')
    if len(valid):frequency.to_excel(writer,index=False,sheet_name='Frekuensi')
right.download_button('Unduh laporan Excel',buf.getvalue(),file_name='laporan_statistika.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
st.caption('StatVista • Dibuat dengan Python, Streamlit, Pandas, NumPy, dan Plotly')
