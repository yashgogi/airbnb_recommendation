import streamlit as st
import pandas as pd
import re
from glob import glob
from PIL import Image
import requests
from io import BytesIO
from price_inference import get_prediction

def load_recommendations():
    '''
    Load Recommendation file to dataframe
    '''
    # read existing user recommendation file
    path = glob('./results/recommend/*.csv')
    df = pd.concat([pd.read_csv(p) for p in path])
    return df

def load_listing():
    '''
    Load listing table to dataframe
    '''
     # listing detail file
    listing = pd.read_csv('./data/raw_data/listings.csv')
    return listing

def merge_listing(recom, listing):
    '''
    Merge recommendation table with listing details
    Params:
        recom: dataframe - Recommendation data
        listing: dataframe - Listing data 
    Returns:
        df: dataframe
    '''
    # merge two dataframe
    df = pd.merge(recom, listing[['id','name','picture_url']], 
                   left_on=['listing_id'], right_on=['id'], 
                   how='left') 
    return df

def get_img(url):
    '''
    Load image using pillow and resize it
    Params:
        url: str - File name
    Returns:
        img: image 
    '''
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((224,224))
    except:
        img = Image.open('./data/default_image.jpeg')
        img = img.resize((224,224))
    return img
    
def write_2_webpage(img_url, l_name, l_id, n=5):
    '''
    Writing listing details to webpage 
    Params:
        img_url: list - image urls
        l_name: list - name of listings 
        l_id: list - id of listings
        n: int - no of listings     
    '''
    # Create a grid of columns
    st.write('Listing Ids')
    id_cols = st.columns(n)
    # Insert an image from a URL
    img = st.columns(n)
    st.write('Name of Listing')
    cols = st.columns(n)
    

    for i in range(n):
        cols[i].write(l_name[i])
        img[i].image(get_img(img_url[i]), use_column_width=True)
        id_cols[i].write(l_id[i])


def recommend_listing(df, listing, sent, n=5):
    '''
    For existing users get listing ids recommended 
    by ALS model
    '''
    l_name = df[df['reviewer_id']==sent]['name'].values.tolist()
    l_id = df[df['reviewer_id']==sent]['listing_id'].values.tolist()
    img_url = df[df['reviewer_id']==sent]['picture_url'].values.tolist()
            
    st.write('## Top picks for you:')
    write_2_webpage(img_url, l_name, l_id, n=5)
    
    create_popular_listings(listing)
    

def create_popular_listings(df, pop=[220676, 1936861,\
                                     708802, 1584362,\
                                        72811]):
    '''
    For new users create listing recommendation
    based on popular listings
    '''
    filt = df[df['id'].isin(pop)]
    l_id = filt['id'].unique().tolist()
    l_name = filt['name'].unique().tolist()
    img_url = filt['picture_url'].unique().tolist()

    st.write('## Popular listings:')

    n = len(pop)
    write_2_webpage(img_url, l_name, l_id, n=5)


def new_user(df, sent):
    '''
    For new user create lay out with options to choose
    '''
    # Define a house type
    home_type = ["Entire Home/apt", "Private Room", "Shared Room"]
    ht = st.radio("Property Type:", home_type)
    ht1 = 1 if ht=='Entire Home/apt' else 0

    # No of bedrooms
    # Create a slider input for a range between 0 and 5
    bed = st.slider("Number of Bedrooms:", 1, 6, 2)
    # bathrooms
    # Create a slider input for a range between 0 and 5
    bath = st.slider("Number of Baths:", 1, 6, 2)

    # no of carts
    carts = st.slider("Number of Carts:", 1, 16, 2)
    # no of pax
    pax = st.slider("Number of pax:",1,16,carts)    
    # no of night stays
    nyts = st.text_input("Number of Nights:",'1')  

    user_inputs = {'room_type':ht1, \
                   'bedrooms': bed,\
                   'beds': carts, \
                   'bathrooms': bath,\
                   'minimum_nights': nyts,\
                   'accommodates': pax}
    
    pred = get_prediction(user_inputs)[0]
    st.markdown(f"### **Listing Estimated Price: <span style='color: green'>{pred:.2f}**",\
                 unsafe_allow_html=True)       

    create_popular_listings(df)
    
    

if __name__ == '__main__':
    # load recommendations created from als model
    recom = load_recommendations()
    # load listings
    listing = load_listing()
    # merge recom with listing
    df = merge_listing(recom, listing)
    # user id list with recommendation
    reviewers = df['reviewer_id'].values.tolist()

    # set web page layout
    st.set_page_config(page_title='House Recommendation', \
                       page_icon='random', \
                       layout= 'wide', \
                       initial_sidebar_state="expanded")
    
    # Get user input
    sentence = st.text_input('Input your Userid:')
    
    # Check if user input is not empty
    if sentence:
        sent = re.sub("[^0-9]", "", sentence)
        sent = int(sent)
        # recommend if user id exists
        if sent in reviewers:
            recommend_listing(df, listing, sent)
        else:
            new_user(listing, sent)           

    else:
        st.write('Please enter a valid Userid')
