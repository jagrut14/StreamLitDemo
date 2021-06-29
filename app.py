# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 18:47:50 2020

@author: jagru
"""
import streamlit as st
import pandas as pd
import numpy as np
import base64
from io import BytesIO

from PIL import Image

# Set title of our Front web app
image = Image.open('image.png')
st.image(image, use_column_width=True)

st.title('Nilkamal NSS-Excel Automation')



#load Data
file=st.file_uploader("Upload your CSV Data file",type=['txt','csv'])

if file is not None:
    st.success("File upload success")
    
    data=pd.read_csv(file,skiprows=[0,1,2,3,4,5,6,7,8,9,10,12])
    st.dataframe(data.head())


    #renaming columns
    data.columns=['Load_1_kn', 'Dial1mm', 'Dial2mm','Dial3mm','Time_Sec']
    data['index.no']=data.index

    #Rounding of the first column
    data['Load_1_kn']=round(data['Load_1_kn'],2)


    #Take user input for lower and upper bound
    lower_b=float(st.number_input("Enter your LOWER BOUND value"))
    #lower_b = float(input("Enter your LOWER BOUND value: "))

    upper_b=float(st.number_input("Enter your UPPER BOUND value"))
    #upper_b = float(input("Enter your UPPER BOUND value: "))

    split_size=int(st.number_input("Enter number of splits you want: "))
    #split_size=int(input("Enter number of splits you want: "))


    if st.checkbox("Select, if this is you first test"):
        test_1=1
    else:
        test_1=0

    st.warning("Always update this box")
    #test_1=st.checkbox("Select if this is a first test")
    #test_1=int(input("Enter 1 if this is a first test: "))



    #Funtion to split the range into equal no of parts
    def split_into_parts(split_size):
        return np.linspace(lower_b, upper_b, split_size+1)[1:]

    split_values=split_into_parts(split_size)
    if test_1==1:
        split_values=np.insert(split_values,0,data.iloc[0,0])
    else:
        split_values=np.insert(split_values,0,lower_b)


    #rounding the split_values
    for i in range(len(split_values)):
        split_values[i]=round(split_values[i],2)

    #Subset Data according to the range to reslove the conflict of multiple matches
    def bound1(upper_b):
        #prodata1=data[data['Load_1_kn']==lower_b]
        ind1=0
        prodata2=data[data['Load_1_kn']==upper_b]
        ind2=prodata2.index[0]
        data_t=data.iloc[ind1:ind2+1,:]
        return data_t


    def bound(lower_b,upper_b):
        prodata1=data[data['Load_1_kn']==lower_b]
        ind1=prodata1.index[0]
        prodata2=data[data['Load_1_kn']==upper_b]
        ind2=prodata2.index[0]
        data_t=data.iloc[ind1:ind2+1,:]
        return data_t

    if test_1==1:

        data_test=bound1(upper_b)
    else:
        data_test=bound(lower_b,upper_b)



    #Find the exact split values in out data_test or its lowerneighbour

    def find_neighbours(value):

        exactmatch=data_test[data_test['Load_1_kn']==value]
        if exactmatch is None:
            lowerneighbour_ind = data_test[data_test['Load_1_kn']<value].Load_1_kn.idxmax()
            #upperneighbour_ind = data_t1[data_t1['Load_1_kn']>value].Load_1_kn.idxmin()
            return [lowerneighbour_ind]

        else:
            return exactmatch.index


    #St0ring all the exact match or nearest neighbour values into a list
    index=find_neighbours(split_values[0])
    ind_f=index[0]
    d=data_test[data_test['index.no']==ind_f]
    for i in range(1,len(split_values)):
        index=find_neighbours(split_values[i])
        ind_f=index[0]
        d=d.append(data_test[data_test['index.no']==ind_f])

    #Apending the first 0 load value row
    temp_t2=data_test.tail(1)
    x=temp_t2.iloc[0,-1]+1
    data_t2=data.iloc[x+20:,:]
    top10=data_t2.iloc[0:35,:]
    wanted=top10[top10.Load_1_kn == top10.Load_1_kn.min()]

    d=d.append(wanted.iloc[0,:])

    #Apending the respective lower bound load value row
    def find_neighbours2(value):



        exactmatch=data_t2[data_t2['Load_1_kn']==value]
        if exactmatch is None:


            lowerneighbour_ind = data_t2[data_t2['Load_1_kn']<value].Load_1_kn.idxmax()
            #upperneighbour_ind = data_t1[data_t1['Load_1_kn']>value].Load_1_kn.idxmin()
            return [lowerneighbour_ind]

        else:
            return exactmatch.index
    index2=find_neighbours2(upper_b)
    ind_f2=index2[0]
    d=d.append(data_t2[data_t2['index.no']==ind_f2])

       #d['index.no']+=14
       #d.index=d['index.no']
       #d = d.iloc[:, :-1]

    #finald=pd.Series(lis)
    d['index.no']+=14
    d.index=d['index.no']
    d = d.iloc[:, :]

    #d.to_excel(filename+'.xlsx', engine='xlsxwriter')
    st.write(d)
    #t.success("Completed, Please check you local drive from where you uploaded the file")

    def to_excel(d):
        output = BytesIO()

        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        d.to_excel(writer, index=False, sheet_name='Sheet1', float_format="%.2f")
        writer.save()
        processed_data = output.getvalue()
        return processed_data


    def get_table_download_link(d):
        """Generates a link allowing the data in a given panda dataframe to be downloaded
        in:  dataframe
        out: href string
        """
        val = to_excel(d)
        b64 = base64.b64encode(val)  # val looks like b'...'
        return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="Your_File.xlsx">Download Excel file</a>'  # decode b'abc' => abc


    st.markdown(get_table_download_link(d), unsafe_allow_html=True)
