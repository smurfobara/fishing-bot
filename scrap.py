import requests
from bs4 import BeautifulSoup


def clearDictionary(dict):
    for key, value in dict.items():
        # Убираем лишние пробелы и символы новой строки
        cleaned_value = ' '.join(value.split())
        dict[key] = cleaned_value
    return dict




def getAutorsList():
    #try:
        temporaryAutors = []
        temporaryLinks = []
        it = 1
        response = requests.get(f'https://our.fishing/fishermans/?page={it}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            numbers = soup.find_all('a', class_='pager-number')
            pages = [int(number.text.strip()) for number in numbers]

            for page in pages:
                print(f'Парсинг страницы {page}')
                response = requests.get(f'https://our.fishing/fishermans/?page={page}')
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    autorsPage = soup.find_all('div', class_='card-profile pt-10')

                    for autorPage in autorsPage:
                        autor = autorPage.find('h5').text.strip()
                        temporaryAutors.append(autor)
                        link = autorPage.find('a').get('href')
                        full_link = f'https://our.fishing{link}'
                        temporaryLinks.append(full_link)

            cleaned_autors = [' '.join(item.split()).strip() for item in temporaryAutors]
            cleaned_links = [' '.join(item.split()).strip() for item in temporaryLinks]
            autors = {
                "names" : cleaned_autors,
                "links" : cleaned_links
            }
            return autors
        else:
            print(f'site is not available! SC={str(response.status_code)}')
    #except Exception as ex:
     #   print(print(F'CRITICAL ERROR! {ex}'))

def findLastTrophy():
    response = requests.get('https://our.fishing')
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        trophy_obj = soup.find_all('div', class_='row mt-70')
        trophy_obj = trophy_obj[1]
        trophy_href = trophy_obj.find('div', class_='card-grid-5').find('a')
        trophy_href = trophy_href.get('href')
        trophy_href = f'https://our.fishing/{trophy_href}'
        trophy_obj = trophy_obj.find('div', class_='content-bottom')
        trophy_name = trophy_obj.find('h3').text
        trophy_weight = trophy_obj.find('span', class_='color-white mr-25').text
        trophy_height = trophy_obj.find('span', class_='color-white').text
        #trophy_autor = trophy_obj.find('div', class_='author d-flex align-items-center mr-20 mt-20').text
        response = requests.get(trophy_href)
        soup = BeautifulSoup(response.content, 'html.parser')
        autor_href = soup.find('ul', class_='breadcrumbs mt-40')
        autor_href = autor_href.find_all('li')
        autor_href = autor_href[1]
        autor_href = autor_href.find('a')
        autor_href = autor_href.get('href')
        trophy = {
            'name' : trophy_name,
            'weight' : trophy_weight,
            'height' : trophy_height,
            #'autor' : trophy_autor,
            'href' : trophy_href,
            'autor_href' : autor_href
        }

        print(trophy["name"])
        print(trophy["weight"])
        print(trophy["height"])
        print(trophy["href"])
        return clearDictionary(trophy)






def checkNewArticle():
   # try:
        response = requests.get('https://our.fishing')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_card = soup.find_all('div', class_='card-block-info')
            article_card = article_card[8]
            article_name_obj = article_card.find('h5').find('a')
            article_name = article_name_obj.text
            article_href = article_name_obj.get('href')
            article_autor = article_card.find('span', class_='font-sm font-bold color-brand-1 op-70').text
            article_href = f'https://our.fishing/{article_href}'
            response = requests.get(article_href)
            soup = BeautifulSoup(response.content, 'html.parser')
            article_autor_link = soup.find('div', class_='author d-flex align-items-center mr-30')
            article_autor_link = article_autor_link.find('a')
            article_autor_link = article_autor_link.get('href')
            article_autor_link = f'https://our.fishing/{article_autor_link}'


            article = {
                'name' : article_name,
                'autor' : article_autor,
                'href' : article_href,
                'autor_href' : article_autor_link
            }
            print(article["name"])
            print(article["autor"])
            print(article["href"])
            print(article["autor_href"])
            return clearDictionary(article)





        else:
            print(f'site is not available! SC={str(response.status_code)}')
   # except Exception as ex:
   #     print(F'CRITICAL ERROR! {ex}')


