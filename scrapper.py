import bs4 as bs
import requests
import json


#amazon blocks the request if the user agent is not set to a browser 
#because it thinks it is a bot which is not allowed to scrape the website
#so we set the user agent to a browser to bypass this restriction
custom_headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0'
} 

#reading the json file that contains the links of the categories
urls = json.loads(open('links.json').read())
urls = urls['links']

#function to pull data from the page of specific category
#url: the url of the category
#custom_headers: the headers to bypass the restriction of scraping the website
#page_number: the number of the page to scrape from the specific category
def PullProductURLsFromSpecificCategory(input_url:str, custom_headers: str, page_number: int,file_name:str, writeToFile=False):

    #looping through the categories to get the links of the products
    #NOT DONE YET
    ProductURL_List = []
    ProductCounter = 0
    for x in range(1, page_number + 1):
        #pulling data from the page
        cont = requests.get(input_url, headers=custom_headers)
        cont.encoding = 'utf-8'
        content = cont.content

        #parsing the content of the page with beautifulsoup
        soup = bs.BeautifulSoup(content, 'lxml')

        #finding the divs that contain the products on the page of specific category by class name
        box = soup.find_all('div', class_='puis-card-container s-card-container s-overflow-hidden aok-relative puis-expand-height puis-include-content-margin puis puis-v1102xfiy6gme925w67f1x0fa3d s-latency-cf-section puis-card-border')

        #looping through the divs to get the links of the products by class name
        for i in box:
            productLink = i.find('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')['href']
            
            #checking if the link is a product link or not
            if productLink[0:5] == '/sspa':
                continue
            ProductURL_List.append(productLink)
            ProductCounter += 1
            print(f'{ProductCounter} URL appended to the list.')

        
        #pass to the next page
        input_url = input_url.replace(f'page={x}', 'page='+str(x + 1))
    for x in ProductURL_List:
        print(x)
        print('-----------------------------------')
    print(f'Length of Specific List {len(ProductURL_List)}')

    #writing the links of the products to a file
    if writeToFile:
        with open(file_name, 'w') as file:
            json.dump(ProductURL_List, file)
    return ProductURL_List

def PullDataFromSpecificProductsReviews(productID: str, custom_headers: dict) -> list:

    #there is a link that redirects to all the reviews of the product so we get the link of that page
    #we use url to get the productID and then we use the productID to get the link of the reviews

    #getting the number of reviews
    pageNumber = 1
    AllReviews = []
    while True:
        #access the page of the reviews
        reviewLink = f'https://www.amazon.com.tr/product-reviews/{productID}/?pageNumber={pageNumber}'
        reviewPage = requests.get(reviewLink, headers=custom_headers)
        reviewPage.encoding = 'utf-8'
        reviewContent = reviewPage.content
        soupReviewPage = bs.BeautifulSoup(reviewContent, 'lxml')
        #if there are no reviews on the page, break the loop
        if len(soupReviewPage.find_all('div', class_='a-section celwidget')) == 0:
            break
        #Türkiye: 0 yorum ve 0 müşteri puanı var
        if "0 yorum ve 0 müşteri puanı var" in soupReviewPage.text:
            break

        #3 features of the review: review text, review rating, review title

        #id should containd customer_review-XXXXXXXXXX
        #ReviewsEachPage = soupReviewPage.find_all('div', class_='a-section celwidget')
        ReviewsEachPage = soupReviewPage.find_all('div', class_='a-section celwidget', id=lambda x: x and x.startswith('customer_review-'))  
        for review in ReviewsEachPage:
            reviewText = review.find('span', class_='a-size-base review-text review-text-content').text
            reviewRating = review.find('span', class_='a-icon-alt').text
            reviewTitle = review.find('a', class_='a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold')
            if reviewTitle:
                reviewTitle = reviewTitle.text
            else:
                reviewTitle = 'No Title'
            AllReviews.append({'Review': reviewText, 'Rating': reviewRating, 'Title': reviewTitle})
        pageNumber += 1
    return AllReviews
    
    ####reviewNumber = int(reviewNumberString.split(' ')[-2])
    #getting the number of reviews of the product to loop through the pages of the reviews (no need)
    ####reviewNumberString = soupReviewPage.find('div', class_='a-row a-spacing-base a-size-base').text
    ####reviewNumberString = reviewNumberString.strip()
    #output: XXX toplam puan, XXX yorumlu
    
    ####reviewPage = requests.get('https://amazon.com.tr' + reviewLink + '&pageNumber=' + str(page), headers=custom_headers)
    
    #writing the reviews to a file
    ####with open(f'{productID}.json', 'w') as file:
    ####    json.dump(AllReviews, file)
    
    ####for page in range(1, reviewNumber // 10 + 1):
    ####    #getting the reviews of the product
    ####    reviewPage = requests.get('https://amazon.com.tr' + reviewLink + '&pageNumber=' + str(page), headers=custom_headers)
    ####    reviewContent = reviewPage.content
    ####    soupReviewPage = bs.BeautifulSoup(reviewContent, 'lxml')
    ####for category in urls:
    ####   PullDataFromSpecificPage(category['url'] , custom_headers, category['maxNumberOfPages'], f"{category['name']}.json")

def PullDataFromSpecificProduct(url: str, custom_headers: str, writeToFile=False) -> list:
    #pulling data from the page
    print("Fetching the data of the product...")
    cont = requests.get('https://amazon.com.tr'+url, headers=custom_headers)
    #encoding the content of the page for turkich characters
    cont.encoding = 'utf-8'
    content = cont.content

    #parsing the content of the page with beautifulsoup
    soup = bs.BeautifulSoup(content, 'lxml')
    
    productURL = url
    productTitle = soup.find('span', class_='a-size-large product-title-word-break').text
    productPrice = soup.find('span', class_='a-price-whole').text
    productRating = soup.find('span', class_='a-icon-alt').text
    productReviewNumber = soup.find('span', class_='a-size-base').text
    productID = url.split('/')[-2]
    print(f"All data of the product {productID} is fetched.")
    print("Fetching the reviews of the product...")
    ProductReviews = PullDataFromSpecificProductsReviews(productID, custom_headers)
    print(f"All reviews of the product {productID} are fetched.")


    #writing the product data to a file
    if writeToFile:
        with open(f'{productID}.json', 'w') as file:
            json.dump({'Product Title': productTitle, 'Product Price': productPrice, 'Product Rating': productRating, 'Product Review Number': productReviewNumber, 'Product Reviews': ProductReviews}, file)

    return {'Product Title': productTitle, 'Product Price': productPrice, 'Product Rating': productRating, 'Product Review Number': productReviewNumber, 'Product Reviews': ProductReviews}

def PullAllProductsFromSpecificCategory(category_url: str, custom_headers: dict, page_number: int,category_name: str, writeToFile=False):
    print(f"Fetching the data of the category {category_name}... ")
    AllProductURLs = PullProductURLsFromSpecificCategory(category_url, custom_headers, page_number,writeToFile)
    AllProducts = []
    ProductCounter = 0
    for ProductURL in AllProductURLs:
        AllProducts.append(PullDataFromSpecificProduct(ProductURL, custom_headers, writeToFile))
        ProductCounter += 1
        print(f'{ProductCounter} product fetched from this category.')
    if writeToFile:
        with open(f'{category_url.split('/')[-1]}.json', 'w') as file:
            json.dump(AllProducts, file)
    return AllProducts

for category in urls:
    Products = PullAllProductsFromSpecificCategory(category['url'], custom_headers, category['maxNumberOfPages'], category_name=category['name'], writeToFile=False)
    #write the data of the products to a file
    with open(f'{category["name"]}.json', 'w') as file:
        json.dump(Products, file)
