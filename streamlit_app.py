import streamlit as st
from scraper import EnergyDataScraper
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns


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
        st.title('Análisis de la Producción Energética en Baleares')

        # Selección de rango de fechas
        start_date = st.date_input('Fecha de inicio', value=datetime.now() - timedelta(days=7))
        end_date = st.date_input('Fecha de fin', value=datetime.now())

        # Cargar datos según el rango seleccionado
        if st.button('Cargar Datos'):
            self.fetch_data_for_period(start_date, end_date)
            st.write(f"Datos cargados desde {start_date} hasta {end_date}")

        # Visualización de datos y gráficos si hay datos disponibles
        if not self.dataframe.empty:
            st.header('Datos de Producción Energética')
            st.dataframe(self.dataframe)
            self.display_charts()

    def display_charts(self):
        """
        Carga los gráficos de la producción energética.
        """
        if not self.dataframe.empty:
            self.plot_daily_total_production()
            self.plot_production_by_energy_type()
            self.plot_daily_production_stacked_bar()
            self.plot_total_production_area()

    # Los siguientes métodos definen los gráficos específicos mostrados por la aplicación.

    def plot_daily_total_production(self):
        """
        Visualiza la producción total de energía diaria a lo largo del tiempo seleccionado.
        """
        # Gráfico de la producción total diaria usando Matplotlib
        st.header('Producción Total Diaria de Energía')
        self.dataframe['Fecha'] = pd.to_datetime(self.dataframe['Fecha'])
        daily_totals = self.dataframe.groupby('Fecha')['Día'].sum()
        plt.figure(figsize=(10, 6))
        daily_totals.plot(kind='line', marker='o', linestyle='-')
        plt.xlabel('Fecha')
        plt.ylabel('Producción Total (MWh)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)

    def plot_production_by_energy_type(self):
        """
        Visualiza la comparación de la producción total por tipo de energía.
        """
        # Gráfico de barras de la producción por tipo de energía usando Seaborn
        st.header('Comparación de la Producción por Tipo de Energía')
        production_by_type = self.dataframe.groupby('Tipo')['Día'].sum().sort_values(ascending=False)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=production_by_type.values, y=production_by_type.index, palette='viridis')
        plt.xlabel('Producción Total (MWh)')
        plt.ylabel('Tipo de Energía')
        plt.tight_layout()
        st.pyplot(plt)

    def plot_daily_production_stacked_bar(self):
        """
        Muestra un gráfico de barras de la producción diaria por tipo de energía.
        """
        st.header("Producción Diaria por Tipo de Energía (Barras Apiladas)")
        pivot_df = self.dataframe.pivot_table(values='Día', index='Fecha', columns='Tipo', aggfunc='sum').fillna(0)
        st.bar_chart(pivot_df)

    def plot_total_production_area(self):
        """
        Muestra un gráfico de área de la variación de la producción total de energía.
        """
        st.header("Variación de la Producción Total de Energía (Área)")
        total_daily = self.dataframe.groupby('Fecha')['Día'].sum().reset_index()
        total_daily.set_index('Fecha', inplace=True)
        st.area_chart(total_daily)


if __name__ == "__main__":
    app = EnergyDataApp()
    app.display_interface()
