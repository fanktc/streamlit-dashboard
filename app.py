import streamlit as st
import pandas as pd
import plotly.express as px

#Page configuration
st.set_page_config(
    page_title="Salaries Dashboard in Data Area",
    page_icon="📊",
    layout="wide"
)

#Data load
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

#Side filter bar
st.sidebar.header("🔍 Filters")

available_years = sorted(df['ano'].unique())
selected_years = st.sidebar.multiselect("Year", available_years, default=available_years)

available_seniority = sorted(df['senioridade'].unique())
selected_seniority = st.sidebar.multiselect("Seniority", available_seniority, default=available_seniority)

available_contracts = sorted(df['contrato'].unique())
selected_contracts = st.sidebar.multiselect("Contract type", available_contracts, default=available_contracts)

available_sizes = sorted(df["tamanho_empresa"].unique())
selected_sizes = st.sidebar.multiselect("Company Size", available_sizes, default=available_sizes)

#creating filtered DF based on selected options
df_filter = df[
    (df['ano'].isin(selected_years)) &
    (df['senioridade'].isin(selected_seniority)) &
    (df['contrato'].isin(selected_contracts)) &
    (df['tamanho_empresa'].isin(selected_sizes))
]

#Main content
st.title("🎲 Salary analysis in Data Area Dashboard")
st.markdown("Explore salary data in Data area from previous years. Use left filters to refine your search.")

#KPIs
st.subheader("General metrics (Annual Salary in USD)")

if not df_filter.empty:
    avg_salary = df_filter['usd'].mean()
    max_salary = df_filter['usd'].max()
    total_records = df_filter.shape[0]
    more_frequent_role = df_filter["cargo"].mode()[0]
else:
    avg_salary, max_salary, total_records, more_frequent_role = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Salary", f"${avg_salary:,.0f}")
col2.metric("Maximum Salary", f"${max_salary:,.0f}")
col3.metric("Total Record Count", f"{total_records:,}")
col4.metric("More frequent role", more_frequent_role)

st.markdown("---")

# --- Visual Analysis With Plotly ---
st.subheader("Charts")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filter.empty:
        top_roles = df_filter.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        roles_chart = px.bar(
            top_roles,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 roles by average salary",
            labels={'usd': 'Average annual salary (USD)', 'cargo': ''}
        )
        roles_chart.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(roles_chart, use_container_width=True)
    else:
        st.warning("No data to show in the chart.")

with col_graf2:
    if not df_filter.empty:
        hist_chart = px.histogram(
            df_filter,
            x='usd',
            nbins=30,
            title="Annual salary distribution",
            labels={'usd': 'Salary range (USD)', 'count': ''}
        )
        hist_chart.update_layout(title_x=0.1)
        st.plotly_chart(hist_chart, use_container_width=True)
    else:
        st.warning("No data to show in the chart.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filter.empty:
        remote_count = df_filter['remoto'].value_counts().reset_index()
        remote_count.columns = ['tipo_trabalho', 'quantidade']
        remote_chart = px.pie(
            remote_count,
            names='tipo_trabalho',
            values='quantidade',
            title='Types of work proportion',
            hole=0.5
        )
        remote_chart.update_traces(textinfo='percent+label')
        remote_chart.update_layout(title_x=0.1)
        st.plotly_chart(remote_chart, use_container_width=True)
    else:
        st.warning("No data to show in the chart.")

with col_graf4:
    if not df_filter.empty:
        df_ds = df_filter[df_filter['cargo'] == 'Data Scientist']
        avg_ds_country = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        countries_chart = px.choropleth(avg_ds_country,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        countries_chart.update_layout(title_x=0.1)
        st.plotly_chart(countries_chart, use_container_width=True)
    else:
        st.warning("No data to show in the chart.")

# --- Detailed Data Table ---
st.subheader("Detailed Data")
st.dataframe(df_filter)
