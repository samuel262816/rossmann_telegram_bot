import pandas as pd
import json
import requests
import os
from flask import Flask, requests, Response

# constants
token = '5800603609:AAGuchfYsRi1urWgomSgGGb5s1hO2XPcjfU'

# # info about bot
# https://api.telegram.org/bot5800603609:AAGuchfYsRi1urWgomSgGGb5s1hO2XPcjfU/getMe

# # get Updates
# https://api.telegram.org/bot5800603609:AAGuchfYsRi1urWgomSgGGb5s1hO2XPcjfU/getUpdates

# # send Message
# https://api.telegram.org/bot5800603609:AAGuchfYsRi1urWgomSgGGb5s1hO2XPcjfU/sendMessage?chat_id=884913866&text=Ola Samuel, belezinha!


def send_message( chat_id, text ):
    url = f'https://api.telegram.org/bot{token}/'
    url = url + 'sendMessage?chat_id={chat_id}'
    
    r = requests.post( url, json={'text': text} )
    print( f'Status Code {r.status_code}' )
    return None


def load_datadet( store_id ):
    # Loading test dataset
    df10 = pd.read_csv( 'test.csv')
    df_store_raw = pd.read_csv( 'store.csv' )

    # merge test dataset + store
    df_test = pd.merge( df10, df_store_raw, how= 'left', on= 'Store')

    # Choose store for prediction
    df_test = df_test[ df_test['Store'] == store_id ]
    
    if not df_test.empty:
        # remove closed days
        df_test = df_test[ df_test['Open'] != 0 ]
        df_test = df_test[ ~df_test['Open'].isnull() ]
        df_test = df_test.drop( 'Id', axis=1 )

        # convert dataframe to json
        data = json.dumps( df_test.to_dict( orient = 'recors'))
    
    else:
        data = 'error'
        
    return data



def predict( data ):
    # API Call
    url = 'https://webapp-rossmann.onrender.com/predict'
    header= {'Content-type': 'application/json'}
    data= data

    r = requests.post( url, data= data, headers= header)
    print( 'Status Code {}'.format( r.status_code ) )

    # convert into dataframe
    df = pd.DataFrame( r.json(), columns= r.json()[0].keys() )
    return d1



def parse_message( message ):
    chat_id = message['message']['chat']['id']
    store_id = message['message']['text']

    store_id = store_id.replace( '/', '')
    
    try:
        store_id = int( store_id )
    
    except ValueError:
        store_id = 'error'
        
    return chat_id, store_id


# API Initialize
app = Flask( __name__ )

@app.route('/', methods= ['GET', 'POST'] )
def index():
    if requests.method == 'POST':
        message = requests.get_json()
        
        chat_id, store_id = parse_message( message )
        
        if store_id != 'error':
            # loadind data
            data = load_datadet( store_id )
            
            if data != 'error':
                # prediction
                d1 = predict( data )

                # calculation
                df2 = df[['store', 'prediction']].groupby('store').sum().reset_index()
                
                # send message
                msg =  ( f'Store number { df2["store"].values[0] } will sell R${ df2["prediction"].values[0] :,.2f} in the next 6 weeks') 

            else:
                send_message( chat_id, 'Store not available!')
                return Response( 'OK', status = 200)
                  
        else:    
            send_message( chat_id, 'Store-Id is not a number')
            return Response( 'OK', status = 200)
        
    else:
        return '<h1> Rossmann Telegram BOT </h1>'


if __name__ == '__main__':
    port = os.environ.get( 'PORT', 5000)
    app.run( host= '0.0.0.0', port= port, debug= True )