import streamlit as st
import pickle
import pandas as pd
import requests

movies_list = pickle.load(open('movie_new_dict.pkl','rb'))
movies = pd.DataFrame(movies_list)
movies_list_names=movies["title"].values
st.title("Movie Recommendation System")
option=st.selectbox("Search movies",movies_list_names)

similarity=pickle.load(open('similarity_vec.pkl','rb'))

def recommend(text):
    movie_index=movies[movies["title"].str.lower()==text.lower()].index[0]
    distance=sorted(list(enumerate(similarity[movie_index])),reverse=True,key=lambda x:x[1])[1:6]
    recommended=[]
    recom_movie_poster = []
    for i,k in distance:
        recommended.append(movies.iloc[i,1])
        recom_movie_poster.append(fetch_movie_poster(movies.iloc[i,0]))

    return recommended, recom_movie_poster


def fetch_movie_poster(movie_id):
    response=requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=0ff537d323525617ee3b8916dbf95770')
    data=response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

if st.button("Recommend"):
    recommendations,movie_poster=recommend(option)
    #for i in recommendations:
     #st.write(i)
    #for i in movie_poster:
     #st.image(i, caption='Your Image', use_column_width=True)
      #print(i)
       #create 5 columns
    col1,col2,col3,col4,col5 = st.columns(5)
    with col1:
         st.text(recommendations[0])
         st.image(movie_poster[0])
    with col2:
         st.text(recommendations[1])
         st.image(movie_poster[1])
    with col3:
         st.text(recommendations[2])
         st.image(movie_poster[2])
    with col4:
        st.text(recommendations[3])
        st.image(movie_poster[3])
    with col5:
        st.text(recommendations[4])
        st.image(movie_poster[4])
