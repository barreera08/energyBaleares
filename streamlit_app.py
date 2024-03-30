import streamlit as st
from scraper import EnergyDataScraper
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


class EnergyDataApp:
    """
    Clase para analizar y visualizar datos de producción energética.
    """

    def __init__(self):
        """
        Inicializa el DataFrame que almacenará los datos recopilados.
        """
        self.dataframe = pd.DataFrame()

    def fetch_data_for_period(self, start_date, end_date):
        """
        Obtiene datos de la producción energética para un rango de fechas.

        Parameters:
        - start_date: La fecha de inicio del período (datetime).
        - end_date: La fecha de fin del período (datetime).
        """
        delta = end_date - start_date
        for i in range(delta.days + 1):
            day = start_date + timedelta(days=i)
            scraper = EnergyDataScraper(day.year, day.month, day.day)
            scraper.scrape()
            daily_data = scraper.get_dataframe()
            if daily_data is not None and not daily_data.empty:
                self.dataframe = pd.concat([self.dataframe, daily_data], ignore_index=True)

    def display_interface(self):
        """
        Configura la interfaz de usuario de Streamlit y controla la interacción del usuario.
        """
        self.load_css()
        st.title('Análisis de la Producción Energética en Baleares')

        # Inicializa el DataFrame en la sesión si aún no existe
        if 'dataframe' not in st.session_state or 'filtered_data' not in st.session_state:
            st.session_state['dataframe'] = self.dataframe.copy()
            st.session_state['filtered_data'] = self.dataframe.copy()

        # Agregar un expander para mostrar instrucciones o información adicional
        with st.expander("Instrucciones de Uso e Información Adicional"):
            st.write("""
                Bienvenido a la aplicación de análisis de producción energética en Baleares. Esta herramienta te permite visualizar la producción de energía por tipo y fecha. Utiliza los controles de entrada para seleccionar el rango de fechas de interés.

                **Instrucciones:**
                - Selecciona la fecha de inicio y fin en la barra lateral para cargar los datos.
                - Haz clic en 'Cargar Datos' para visualizar la información.
                - Explora las diferentes visualizaciones para obtener insights sobre la producción energética.
            """)

        # Selección de rango de fechas y carga de datos
        start_date = st.sidebar.date_input('Fecha de inicio', value=datetime.now() - timedelta(days=7))
        end_date = st.sidebar.date_input('Fecha de fin', value=datetime.now())

        if st.sidebar.button('Cargar Datos'):
            self.fetch_data_for_period(start_date, end_date)
            # Actualiza tanto el dataframe original como el filtrado en el estado de la sesión
            st.session_state['dataframe'] = self.dataframe.copy()
            st.session_state['filtered_data'] = self.dataframe.copy()

        # Verificación y selección de tipo de energía basado en el dataframe actual en sesión
        if not st.session_state['dataframe'].empty:
            unique_types = st.session_state['dataframe']['Tipo'].unique().tolist()
            selected_type = st.sidebar.selectbox('Seleccione el tipo de energía', ['Todos'] + unique_types, key='selectbox_tipo')

            if selected_type and selected_type != 'Todos':
                st.session_state['filtered_data'] = st.session_state['dataframe'][st.session_state['dataframe']['Tipo'] == selected_type].copy()
            else:
                st.session_state['filtered_data'] = st.session_state['dataframe'].copy()

        # Visualización de datos y gráficos basados en los datos filtrados en sesión
        if not st.session_state['filtered_data'].empty:
            st.header('Datos de Producción Energética')
            st.dataframe(st.session_state['filtered_data'])
            self.display_charts(st.session_state['filtered_data'])

    def display_charts(self, data):
        """
        Carga los gráficos de la producción energética.
        """
        if not data.empty:
            self.plot_daily_total_production(data)
            self.plot_production_by_energy_type(data)
            self.plot_daily_production_stacked_bar(data)
            self.plot_total_production_area(data)
            self.plot_heatmap(data)

    # Los siguientes métodos definen los gráficos específicos mostrados por la aplicación.

    def plot_daily_total_production(self, data):
        """
        Visualiza la producción total de energía diaria a lo largo del tiempo seleccionado.
        """
        # Gráfico de la producción total diaria usando Matplotlib
        st.header('Producción Total Diaria de Energía')
        data['Fecha'] = pd.to_datetime(data['Fecha'])
        daily_totals = data.groupby('Fecha')['Día'].sum()
        plt.figure(figsize=(10, 6))
        daily_totals.plot(kind='line', marker='o', linestyle='-')
        plt.xlabel('Fecha')
        plt.ylabel('Producción Total (MWh)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)

    def plot_production_by_energy_type(self, data):
        """
        Visualiza la comparación de la producción total por tipo de energía.
        """
        # Gráfico de barras de la producción por tipo de energía usando Seaborn
        st.header('Comparación de la Producción por Tipo de Energía')
        production_by_type = data.groupby('Tipo')['Día'].sum().sort_values(ascending=False)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=production_by_type.values, y=production_by_type.index, palette='viridis')
        plt.xlabel('Producción Total (MWh)')
        plt.ylabel('Tipo de Energía')
        plt.tight_layout()
        st.pyplot(plt)

    def plot_daily_production_stacked_bar(self, data):
        """
        Muestra un gráfico de barras de la producción diaria por tipo de energía.
        """
        st.header("Producción Diaria por Tipo de Energía (Barras Apiladas)")
        pivot_df = data.pivot_table(values='Día', index='Fecha', columns='Tipo', aggfunc='sum').fillna(0)
        st.bar_chart(pivot_df)

    def plot_total_production_area(self, data):
        """
        Muestra un gráfico de área de la variación de la producción total de energía.
        """
        st.header("Variación de la Producción Total de Energía (Área)")
        total_daily = data.groupby('Fecha')['Día'].sum().reset_index()
        total_daily.set_index('Fecha', inplace=True)
        st.area_chart(total_daily)

    def plot_heatmap(self, data):
        """
        Muestra un mapa de calor de la producción total de energía por tipo y día.
        """
        if not data.empty:
            st.header('Mapa de Calor de la Producción de Energía por Tipo y Fecha')

            # Preparar los datos
            heatmap_data = data.pivot_table(values='Día', index='Fecha', columns='Tipo', aggfunc=np.sum)

            # Generar y mostrar el mapa de calor
            plt.figure(figsize=(12, 8))
            sns.heatmap(heatmap_data, cmap='viridis', annot=True, fmt=".0f")
            plt.title('Producción de Energía (MWh)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)

    def load_css(self):
        css = """
        <style>
            .stButton>button {
                color: white;
                background-color: #4CAF50;
                border-radius: 20px;
                border: 1px solid green;
            }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)


if __name__ == "__main__":
    app = EnergyDataApp()
    app.display_interface()
