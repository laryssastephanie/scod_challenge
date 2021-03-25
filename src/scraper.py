import requests
import json
from bs4 import BeautifulSoup

from Contact import Contact
from Debit import Debit

def find_contact():
    for line in div_contato.splitlines():
        if line.find('E-mail') > 0:
            email = extract_contact_line(line)
        elif line.find('Telefones:') > 0:
            phone = extract_contact_line(line)
        elif line.find('Endereço:') > 0:
            adress = extract_contact_line(line)
        elif line.find('Cidade:') > 0:
            city = extract_contact_line(line)
    return Contact(email, phone, adress, city)

def extract_contact_line(line):
    return line[line.find(':') + 1 : len(line)].strip()

def get_amount_page_detail(page_details):
    soupDetail = BeautifulSoup(page_details.text, 'lxml')
    detail_table = soupDetail.find('table', attrs={'class':'table'})
    detail_table_rows = detail_table.find_all('tr')
    for rowDetail in detail_table_rows:
        colsDetail = rowDetail.find_all('td')
        colsDetail = [ele.text.strip() for ele in colsDetail]
        if len(colsDetail) == 4:
            return colsDetail[3]
    return '0'


def get_click_detail(col):
    if col.find('form'):
        form = col.find('form')
        action_form = form.get('action')
        ano_parcela = form.find('input', {'name': 'ano_parcela'}).get('value')
        token = form.find('input', {'name': '_token'}).get('value')
        data =  {"ano_parcela": ano_parcela, "_token": token}
        page_details = (session.post(url_scod + action_form, data))
        return get_amount_page_detail(page_details)
    return '0'

url_scod = "https://scodbrasil.com"
url_scod_teste = "https://scodbrasil.com/teste"

with requests.Session() as session:
    page = session.get(url_scod_teste)

    soup = BeautifulSoup(page.text, 'lxml')

    div_contato = soup.find('div', class_='col-md-3').text

    debit_table = soup.find('table', attrs={'class':'table'})
    debit_table_rows = debit_table.find_all('tr')

    debits = []

    for row in debit_table_rows:
        cols = row.find_all('td')
        if cols:
            debits.append(Debit(get_click_detail(cols[0]),  cols[1].text, cols[2].text, cols[3].text))

with open('Contato.json', 'w', encoding='utf-8') as f:
    json.dump(find_contact().__dict__, f, ensure_ascii=False, indent=4)

with open('Debitos.json', 'w', encoding='utf-8') as f:
    json.dump([ob.__dict__ for ob in debits], f, ensure_ascii=False, indent=4)    

jsonContactStr = json.dumps(find_contact().__dict__)
jsonDebitsStr = json.dumps([ob.__dict__ for ob in debits])

print(jsonContactStr)
print(jsonDebitsStr)