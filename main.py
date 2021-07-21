import base64
import datetime
import pandas as pd
from PIL import Image
import requests
import streamlit as st

st.set_page_config(page_title='table_scrapper')

logo = Image.open('logo.png')
st.image(logo)

language = st.radio(
    'Language/Język:',
    ('English', 'Polski'))

if language == 'Polski':
    agreement_text = '''
        **Kontynuując używanie tego narzędzia zgadzasz się nie pobierać z jego pomocą materiałów chronionych prawem
        autorskim!**
        
        Narzędzie ma spore ograniczenia i nie będzie działało m. in. na stronach wymagających zalogowania.
    '''
    input_label = 'Wklej adres strony internetowej i naciśniej Enter'
    fetching_label = 'Wyszukiwanie strony i tabel...'
    schema_error_text = 'Niepoprawny adres url'
    url_error_text = '''
        Nie odnalezniono podanej strony internetowej lub strona odmówiła dostępu. Sprawdź poprawność linku i spróbuj
        ponownie.
    '''
    no_tables_error_text = 'Nie znaleziono żadnych tabel.'
    table_label = 'Tabela '
else:
    agreement_text = '''
        **By using this tool you agree to download only data not protected by the copyright!**

        Tool's capabilities are limited, e.g. it won't work on websites that require logging in.
    '''
    input_label = 'Paste the webpage address and press Enter'
    fetching_label = 'Searching for the page and tables...'
    schema_error_text = 'Invalid url'
    url_error_text = 'Page not found or access denied. Please check the url and try again.'
    no_tables_error_text = 'No tables found.'
    table_label = 'Table '

st.write(agreement_text)

url = st.text_input(input_label)
tables = None

if url:
    with st.spinner(fetching_label):
        try:
            tables = pd.read_html(url)
        except ValueError:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    st.error(no_tables_error_text)
                else:
                    st.error(url_error_text)
            except requests.exceptions.MissingSchema:
                st.error(schema_error_text)
            except requests.exceptions.InvalidSchema:
                st.error(schema_error_text)
            except requests.exceptions.InvalidURL:
                st.error(schema_error_text)
            except:
                st.error(url_error_text)
        except:
            st.error(url_error_text)

    # https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806/2
    def get_table_download_link(df, text_language, number):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        file_name = str('scrapper_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + '_' + str(number) + '.csv')
        if text_language == 'Polski':
            href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">Pobierz jako plik csv</a>'
        else:
            href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">Download as csv file</a>'
        return href

    if tables is not None:
        for i, table in enumerate(tables):
            st.write(str(table_label + str(i + 1)))
            st.write(table)
            st.markdown(get_table_download_link(table, language, i+1), unsafe_allow_html=True)
