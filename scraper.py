import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


class EnergyDataScraper:
    """
    Clase para obtener datos de la producción energética diaria de la página web de REE (Red Eléctrica Española).

    Atributos:
        date (datetime): Fecha para la cual se obtendrán los datos.
        df_expandido (DataFrame): DataFrame para almacenar los datos extraidos y procesados.
    """

    BASE_URL = "https://www.ree.es/es/balance-diario/baleares"

    def __init__(self, year, month, day):
        """
        Inicializa el objeto EnergyDataScraper con una fecha específica.

        Args:
            year (int): Año de los datos.
            month (int): Mes de los datos.
            day (int): Día de los datos.
        """
        self.date = datetime(year, month, day)
        self.df_expandido = pd.DataFrame()

    def build_url(self):
        """
        Construye la URL para obtener los datos basándose en la fecha inicializada.

        Returns:
            str: URL construida para la fecha especifica.
        """
        return f"{self.BASE_URL}/{self.date.year}/{self.date.month:02d}/{self.date.day:02d}"

    def fetch_data(self):
        """
        Realiza una petición HTTP a la URL construida y obtiene la respuesta HTML.

        Returns:
            BeautifulSoup: Objeto BeautifulSoup que contiene el contenido HTML.
        """
        response = requests.get(self.build_url())
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        else:
            print(f"Error al realizar la petición: {response.status_code}")
            return None

    def parse_data(self, soup):
        """
        Extrae los datos relevantes del HTML y los prepara para ser procesados.

        Args:
            soup (BeautifulSoup): Objeto BeautifulSoup que contiene el contenido HTML.

        Returns:
            data: Lista que contiene los datos extraídos.
        """
        if soup is not None:
            rows = soup.find_all('tr', class_='datos')
            data = []
            for row in rows:
                cells = row.find_all('th') + row.find_all('td')
                tipo_energia = cells[0].get_text().strip()
                valores = [cell.get_text().strip().replace(',', '.').replace(' ', '') for cell in cells[1:]]
                data.append([self.date.strftime('%Y-%m-%d'), tipo_energia] + valores)
            return data
        else:
            return []

    def expand_data(self, data):
        """
        Convierte los datos extraídos en un DataFrame de Pandas y realiza transformaciones de datos necesarias.

        Args:
            data (list): Lista que contiene los datos extraídos.
        """
        if data:
            columnas_datos = ['Fecha', 'Tipo', 'Día', 'Mes', '%∆ Mes', 'Año', '%∆ Año', 'Año móvil', '%∆ Móvil']
            self.df_expandido = pd.DataFrame(data, columns=columnas_datos)
            # Convierte las columnas de datos a numérico, excepto 'Fecha' y 'Tipo'
            for col in columnas_datos[2:]:
                self.df_expandido[col] = pd.to_numeric(self.df_expandido[col], errors='coerce')

    def scrape(self):
        """
        Ejecuta el proceso de scrapping: obtiene datos, los parsea y los expande en un DataFrame.
        """
        soup = self.fetch_data()
        data = self.parse_data(soup)
        self.expand_data(data)

    def get_dataframe(self):
        """
        Obtiene el DataFrame que contiene los datos y procesados.

        Returns:
            DataFrame: DataFrame que contiene los datos y procesados.
        """
        return self.df_expandido


if __name__ == "__main__":
    scraper = EnergyDataScraper(2024, 2, 29)
    scraper.scrape()
    df = scraper.get_dataframe()
    print(df)
