from flask import Flask, render_template, request, redirect, url_for, session
import time
import chatbot
import random
import pandas as pd 
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysearchform'


@app.route('/', methods = ['GET','POST'])
def homepage():
    if request.method == 'POST':
        query = request.form['query']
        session['query'] = query
        session['click_count'] = session.get('click_count', 0)
        return redirect(url_for('loader', query_given = query))
    return render_template('homepage.html')

@app.route('/loader/<query_given>')
def loader(query_given):
    return render_template('loader.html',query_show = query_given)


@app.route('/results')
def result():
    temp = dict()
    show_query = session.get('query', 'No Query')
    main_dict = chatbot.manipulate(show_query)
    main_df = pd.DataFrame(main_dict)
    temp['Product Name'] = main_df['Product Name']
    temp['Pricing'] = main_df['Pricing']
    temp['Reviews Score'] = main_df['Reviews Score']
    
    darazLinks = list(main_df['Daraz Links'])[:5] #this is the correct code this will work well
    names = list(main_df['Product Name'])[:5]
    price_lst = list(main_df['Pricing'])[:5]
    
    df = pd.DataFrame(temp)
    
    headers = [
        'Product Name', 'Pricing', 'Reviews Score'
    ]
    
    data = df.to_dict(orient='records')
    
    if (main_df.shape[0]) == 1 or (main_df.shape[0]) == 2:
        #this will get the 5 images only if there is only one product
        images = chatbot.getImages()[:5]
        names, darazLinks, price_lst= chatbot.getTop5()
    else:
        images = chatbot.getImages()[:5]
        random.shuffle(images)
        
    session['click_count'] += 1
    
    total_listings, avg_price, avg_rating, avg_review = chatbot.getStats()
    current_datetime = datetime.now()
    formatted_time = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    
    #to use the images i need to get the images also 
    return render_template('results.html', headers=headers,
                           data=data, query = show_query, 
                           clicks = session['click_count'], 
                           Dlink = darazLinks, image_links = images,
                           names = names, price = price_lst,
                           total_listings=total_listings, avg_price=68372.16,
                           avg_rating=2.412, avg_review=19.96, curr_time = formatted_time)
if __name__ == '__main__':
    app.run(debug = True)