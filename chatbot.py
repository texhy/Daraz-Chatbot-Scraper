import nltk
import pandas as pd
from sqlalchemy import create_engine
import re
import mysql.connector
pd.set_option('mode.chained_assignment', None)


my_dictionary = dict()
my_dictionary['Brand Name'] = 'Xiaomi Redmi Note 12'
my_dictionary['Words'] = ['storage','under', 'less than', 'more than', 'greater', 'between', 'best']

#I am designing my chat bot like this 
# if it finds a particular keyword such as storage this would mean that it need to find storage
# another thing would be to find the digits in the query and then convert them into an integer
#this function would always return a pandas data frame

#converting SQL to CSV

def sql_to_csv():
    engine = create_engine('mysql://root:123456@localhost/pai_project')
    table_name = 'not_merged_data'
    df_from_mysql = pd.read_sql_table(table_name, con=engine)
    return df_from_mysql

df = sql_to_csv()
def convert_to_int(value):
    if value == 'No Reviews':
        return 0
    else:
        return float(value)
    
    
def changeReviews(df):
    df['Reviews Score'] = df['Reviews Score'].apply(convert_to_int)
    return df


def manipulate(query):
    tokens = nltk.word_tokenize(query)
    
    if 'between' in query.lower() and 'reviews' in query.lower() and 'price' in query.lower() and 'review' in query.lower():
        return get_price_reviews()     
    
    if 'show' in query.lower():
        return getAllPhones()
    
    #works with find: 
    for word in tokens:
        if word.lower() == 'storage' or word == 'GB':
            return getStorage(query)
        elif word.lower() == 'under' or word.lower() == 'less'or word.lower() == 'below':
            return getMin(query)
        elif word.lower() == 'greater' or word.lower() == 'more' or word == 'above':
            return getMax(query)
        elif word.lower() == 'between':
            return getBetwn(query)
        elif word.lower() == 'best':
            return getBest(query)
        
        elif word.lower() == 'lowest':
            if 'lowest' in query.lower() and 'rating' in query.lower():
                return lowestRating() 
            else:
                return getLowestPrice()
        
        elif word.lower() == 'highest':
            if 'highest' in query.lower() and 'rating' in query.lower():
                return lowestRating() 
            else:
                return getHeighestPrice()

def extractDigits(input_string):
    match = re.findall(r'\d+', input_string)
    return list(map(int, match))

def getStorage(query):
    '''
    return storage wise
    ''' 
    storage = extractDigits(query)[0]
    # df = sql_to_csv()
    filtered_df = df[df['Storage Capacity'] == storage].drop_duplicates(subset=['Product Name'])
    filtered_df = changeReviews(filtered_df).sort_values(by='Reviews Score', ascending=False)
    filteredDict = dict()
    filteredDict['Product Name'] = filtered_df['Product Name']
    filteredDict['Images Links'] = filtered_df['Images Links']
    filteredDict['Pricing'] = filtered_df['Pricing']
    filteredDict['Reviews Score'] = filtered_df['Reviews Score']
    filteredDict['Daraz Links'] = filtered_df['Daraz Links']    
    
    return filteredDict
    
def get_price_reviews(query):
 
    df = sql_to_csv()
    input_string = "Find me phones with price between 50000 and 90000 with review score above 3.0"

    # Extract all numerics using regex
    numerics = re.findall(r'\b\d+\.*\d*\b', input_string)
    float_numerics = [float(num) for num in numerics]

    min_price = float_numerics[0]
    max_price = float_numerics[1]
    review = float_numerics[2]
    
    if 'above' in query.lower():
        df = changeReviews(df)
        result = df[(df['Pricing'] > min_price) & (df['Pricing'] < max_price) & (df['Reviews Score'] > review)].sort_values(By = 'Reviews Score')
        return result
        
        
        return result
    elif 'lower' in query.lower():
        df = changeReviews(df)
        result = df[(df['Pricing'] > min_price) & (df['Pricing'] < max_price) & (df['Reviews Score'] < review)].sort_values(By = 'Reviews Score')
        return result
    
    
def getMin(query): 
    '''
    return above below or less than
    ''' 
    price = extractDigits(query)[0]
    df = sql_to_csv()
    print('inside getmin')
    filtered_df = df[df['Pricing'] < price].drop_duplicates(subset=['Product Name'])
    print("DF getmin: ", filtered_df)
    filtered_df = changeReviews(filtered_df).sort_values(by='Pricing', ascending=False)
    
    filteredDict = dict()
    filteredDict['Product Name'] = filtered_df['Product Name']
    filteredDict['Images Links'] = filtered_df['Images Links']
    filteredDict['Daraz Links'] = filtered_df['Daraz Links']    
    filteredDict['Pricing'] = filtered_df['Pricing']
    filteredDict['Reviews Score'] = filtered_df['Reviews Score']
    return filteredDict
    
def getMax(query):
    '''
    return above  or more than
    ''' 
    price = extractDigits(query)[0]
    df = sql_to_csv()
    filtered_df = df[df['Pricing'] > price].drop_duplicates(subset=['Product Name'])
    filtered_df = changeReviews(filtered_df).sort_values(by='Pricing', ascending=False)
    
    filteredDict = dict()
    filteredDict['Product Name'] = filtered_df['Product Name']
    filteredDict['Images Links'] = filtered_df['Images Links']
    filteredDict['Daraz Links'] = filtered_df['Daraz Links']    
    filteredDict['Pricing'] = filtered_df['Pricing']
    filteredDict['Reviews Score'] = filtered_df['Reviews Score']
    return filteredDict
    
def getBetwn(query):
    '''
    returns the prices in between
    ''' 
    price_lower = extractDigits(query)[0]
    price_heigher = extractDigits(query)[1]
    df = sql_to_csv()
    filtered_df = df[(df['Pricing'] > price_lower) & (df['Pricing'] < price_heigher)].drop_duplicates(subset=['Product Name']).sort_values(by='Reviews Score', ascending=True)
    filtered_df = changeReviews(filtered_df).sort_values(by='Pricing', ascending=False)
    filteredDict = dict()
    filteredDict['Product Name'] = filtered_df['Product Name']
    filteredDict['Images Links'] = filtered_df['Images Links']
    filteredDict['Daraz Links'] = filtered_df['Daraz Links']    
    filteredDict['Pricing'] = filtered_df['Pricing']
    filteredDict['Reviews Score'] = filtered_df['Reviews Score']
    return filteredDict
    
#this will return the best one item dict .head()
def getBest(query):
    """gives us the best items but what i have to do is that i need 
    to return only 1 filtered dict item so that i get the heighest and best item
    
    Keyword arguments:
    argument -- query
    Return: 2 items in a dictionary
    """
    
    #if the query goes like show me the best items under 10,000
    def getBestLowest():
        price = extractDigits(query)[0]
        df = sql_to_csv()
        
        filtered_df = df[df['Pricing'] < price].sort_values(by=['Pricing'], ascending=True).drop_duplicates(subset=['Product Name'])
        filtered_df = changeReviews(filtered_df).sort_values(by=['Reviews Score'], ascending=False)[:2]
        
        filteredDict = dict()
        filteredDict['Product Name'] = filtered_df['Product Name']
        filteredDict['Images Links'] = filtered_df['Images Links']
        filteredDict['Daraz Links'] = filtered_df['Daraz Links']    
        filteredDict['Pricing'] = filtered_df['Pricing']
        filteredDict['Reviews Score'] = filtered_df['Reviews Score']
        filteredDict['Seller Rating'] = filtered_df['Seller Rating']
        return filteredDict #product A and Product B
    
    def getBestHighest():
        price = extractDigits(query)[0]
        df = sql_to_csv()

        filtered_df = df[df['Pricing'] > price].sort_values(by=['Pricing'], ascending=False).drop_duplicates(subset=['Product Name'])
        filtered_df = changeReviews(filtered_df).sort_values(by=['Reviews Score'], ascending=False)[:2]
        
        filteredDict = dict()
        filteredDict['Product Name'] = filtered_df['Product Name']
        filteredDict['Images Links'] = filtered_df['Images Links']
        filteredDict['Daraz Links'] = filtered_df['Daraz Links']    
        filteredDict['Pricing'] = filtered_df['Pricing']
        filteredDict['Reviews Score'] = filtered_df['Reviews Score']
        filteredDict['Seller Rating'] = filtered_df['Seller Rating']
        return filteredDict 
    
    if "under" in query.lower():
        return getBestLowest()
    else:
        return getBestHighest()
    
# manipulate('find me phones above rs 50000')
# print(extractDigits('Find me mobiles under rs30000 and rs90000')) working finee as fuxk
def getImages():
    """this will get the images links of the relevent mobiles
    if image is in the format of data///// then we would have to convert 
    if it still does not work then we can replace it with an average local photo
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """
    
    images = [
        'https://static-01.daraz.pk/p/e337d7382e3dc0ca8c82bb04259ceb1f.jpg_300x0q75.webp',
              'https://static-01.daraz.pk/p/cad65545dfc2ba35abee523e14b29b53.png_300x0q75.webp',
              'https://static-01.daraz.pk/p/67d0213e9891004b6449185e99ca7b93.jpg_300x0q75.webp',
              'https://static-01.daraz.pk/p/5fe0d6e8edfcff6ae2ce86bfd17fe74c.png_300x0q75.webp',
              'https://static-01.daraz.pk/p/b675906934c892d749281ed784d408b7.jpg_300x0q75.webp',
              'https://static-01.daraz.pk/p/f0a57dd905298873b9bdff83f2f325a6.jpg_300x0q75.webp',
              'https://static-01.daraz.pk/p/f7b67ccd38ed819861e0d416665a18ac.png_300x0q75.webp',
              'https://static-01.daraz.pk/p/b24ca371e0f38f239958f623f95f0bcb.jpg_300x0q75.webp',
              'https://static-01.daraz.pk/p/b24ca371e0f38f239958f623f95f0bcb.jpg_300x0q75.webp',
              'https://static-01.daraz.pk/p/7d1c4a52380973fe14de57dcdf6d7dc2.jpg_300x0q75.webp'
              ]
    
    return images
    

def getLowestPrice():
    '''''
    In this function we will get a product with just one dictionary item according to price.
    '''
    df = sql_to_csv()
    filtered_df = df.sort_values(by='Pricing', ascending=True).drop_duplicates(subset=['Product Name'])
    filtered_df = changeReviews(filtered_df)[:1]
    filteredDict = dict()
    filteredDict['Product Name'] = filtered_df['Product Name']
    filteredDict['Images Links'] = filtered_df['Images Links']
    filteredDict['Daraz Links'] = filtered_df['Daraz Links']    
    filteredDict['Pricing'] = filtered_df['Pricing']
    filteredDict['Reviews Score'] = filtered_df['Reviews Score']
    filteredDict['Seller Rating'] = filtered_df['Seller Rating']
    return filteredDict 
    
def getHeighestPrice():
    '''''
    In this function we will get a product with just one dictionary item according to price.
    '''
    df = sql_to_csv()
    filtered_df = df.sort_values(by='Pricing', ascending=False).drop_duplicates(subset=['Product Name'])
    filtered_df = changeReviews(filtered_df)[:1]
    filteredDict = dict()
    filteredDict['Product Name'] = filtered_df['Product Name']
    filteredDict['Images Links'] = filtered_df['Images Links']
    filteredDict['Daraz Links'] = filtered_df['Daraz Links']    
    filteredDict['Pricing'] = filtered_df['Pricing']
    filteredDict['Reviews Score'] = filtered_df['Reviews Score']
    filteredDict['Seller Rating'] = filtered_df['Seller Rating']
    return filteredDict 
    


def highestRating():
    """
    this function will return based on sorting of the rating of reviews 
    """
    df = sql_to_csv()
    filtered_df = df.drop_duplicates(subset=['Product Name'])
    filtered_df = changeReviews(filtered_df).sort_values(by='Reviews Score', ascending=False)[:1]
    filteredDict = dict()
    filteredDict['Product Name'] = filtered_df['Product Name']
    filteredDict['Images Links'] = filtered_df['Images Links']
    filteredDict['Daraz Links'] = filtered_df['Daraz Links']    
    filteredDict['Pricing'] = filtered_df['Pricing']
    filteredDict['Reviews Score'] = filtered_df['Reviews Score']
    filteredDict['Seller Rating'] = filtered_df['Seller Rating']
    return filteredDict 

def lowestRating():
    df = sql_to_csv()
    filtered_df = df.drop_duplicates(subset=['Product Name'])
    filtered_df = changeReviews(filtered_df).sort_values(by='Reviews Score', ascending=True)[:1]
    filteredDict = dict()
    filteredDict['Product Name'] = filtered_df['Product Name']
    filteredDict['Images Links'] = filtered_df['Images Links']
    filteredDict['Daraz Links'] = filtered_df['Daraz Links']    
    filteredDict['Pricing'] = filtered_df['Pricing']
    filteredDict['Reviews Score'] = filtered_df['Reviews Score']
    filteredDict['Seller Rating'] = filtered_df['Seller Rating']
    return filteredDict 



def getAllPhones():
    df = sql_to_csv()
    filtered_df = df.drop_duplicates(subset=['Product Name'])
    filtered_df = changeReviews(filtered_df).sort_values(by='Pricing', ascending=False)
    filteredDict = dict()
    filteredDict['Product Name'] = filtered_df['Product Name']
    filteredDict['Images Links'] = filtered_df['Images Links']
    filteredDict['Pricing'] = filtered_df['Pricing']
    filteredDict['Reviews Score'] = filtered_df['Reviews Score']
    filteredDict['Daraz Links'] = filtered_df['Daraz Links']    
    
    return filteredDict
    
    
    
def getTop5():
    df = sql_to_csv()
    filtered_df = df.drop_duplicates(subset=['Product Name'])
    filtered_df = changeReviews(filtered_df).sort_values(by='Reviews Score', ascending=False)[:5]
    names = list(filtered_df['Product Name'])
    daraz_links = list(filtered_df['Daraz Links'])    
    pricing = list(filtered_df['Pricing'])
    return names, daraz_links, pricing
    
def getStats():
    filtered_df = df.drop_duplicates(subset=['Product Name'])
    filtered_df = filtered_df.sort_values(by='Reviews Score', ascending=False)
    final_df = changeReviews(filtered_df)
    total_listings = len(final_df)
    
    avg_price = final_df['Pricing'].mean()
    avg_rating = final_df['Reviews Score'].mean()
    avg_review_count = final_df['Total Reviews'].mean()
    
    print(avg_price)
    print(avg_rating)
    print(avg_review_count)
    
    return total_listings, avg_price, avg_rating, avg_review_count
