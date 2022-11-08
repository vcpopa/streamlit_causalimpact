from cProfile import label
import pandas as pd
import numpy as np
from datetime import datetime
# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
# Causal impact
from causalimpact import CausalImpact
import numpy as np
import streamlit as st
from PIL import Image
import sys
import re
from datetime import datetime
import os
import io
import traceback
sys.tracebacklimit = 0
st.set_option('deprecation.showPyplotGlobalUse', False)

class Impact():
    def __init__(self,df,date_col,control,response,treatment_start):
        self.df=df
        self.date_col=date_col
        self.control=control
        self.response=response
        self.treatment_start=str(treatment_start)
        self.treatment_start=datetime.strptime(self.treatment_start, '%Y-%m-%d')


    def causal_impact(self):
        self.df[self.date_col]=pd.to_datetime(self.df[self.date_col])

        self.df[self.control]=self.df[self.control].astype(float)

        self.df[self.response]=self.df[self.response].astype(float)


        self.treatment_start_index=self.df.index[self.df[self.date_col]==self.treatment_start]

        self.start_date_index=int(self.df.index[self.df[self.date_col]==self.df[self.date_col].min()][0])

        self.end_date_index=int(self.df.index[self.df[self.date_col]==self.df[self.date_col].max()][0])
  

        if len(self.treatment_start_index)>1:
            raise ValueError(f"{self.treatment_start} occurs multiple times in the dataset, please aggregate your data")
        elif len(self.treatment_start_index)==0:
            raise ValueError(f"{self.treatment_start} is not present in the dataset, specify a different value")

        else:
            self.treatment_start_index=self.treatment_start_index[0]



        ts_fig=plt.figure()
        st.header("TIME SERIES PLOT")
        sns.set(rc={'figure.figsize':(12,8)})
        sns.lineplot(x=self.df[self.date_col], y=self.df[self.control],label='CONTROL')
        sns.lineplot(x=self.df[self.date_col], y=self.df[self.response],label='RESPONSE')
        plt.axvline(x= self.df[self.date_col].iloc[self.treatment_start_index],color='r')
        
        
        # Set pre-period

        
        pre_period = [pd.to_datetime(date) for date in  [self.df[self.date_col].min(),self.df[self.date_col].iloc[self.treatment_start_index-1]]]

        post_period = [pd.to_datetime(date) for date in [self.df[self.date_col].iloc[self.treatment_start_index],self.df[self.date_col].max()]]

        self.df.set_index(self.date_col,inplace=True)


    # Causal impact model
        impact = CausalImpact(data=self.df, pre_period=pre_period, post_period=post_period)
        return ts_fig,impact


if __name__=="__main__":
    st.title('CAUSAL IMPACT ANALYSIS')
    image_main = Image.open(os.path.join(os.getcwd(),"logo.png")).resize((800, 200))
    image_side=Image.open(os.path.join(os.getcwd(),"logo2.png"))

    st.image(image_main)
    st.sidebar.image(image_side)
    file  = st.sidebar.file_uploader('Upload data', type = 'csv')


    if file is not None:
        df=pd.read_csv(file)

        df2=df.copy()
        cols_menu_opts=df.columns
        mask = df2.astype(str).apply(lambda x : x.str.match('(\d{2,4}(-|\/|\\|\.| )\d{2}(-|\/|\\|\.| )\d{2,4})+').any())
        date_column_options=df2.loc[:,mask].columns
        date_col= st.sidebar.selectbox("Select date column", date_column_options)
        df[date_col]=pd.to_datetime(df[date_col])
        control= st.sidebar.selectbox("Select control column", cols_menu_opts)
        response= st.sidebar.selectbox("Select response column", cols_menu_opts)
        treatment_start=st.sidebar.date_input(label="Enter your intervention start date",value=None,min_value=df[date_col].min(),max_value=None)

        if st.sidebar.button("RUN"):
            imp=Impact(df=df,date_col=date_col,control=control,response=response,treatment_start=treatment_start)
            
            ts_fig,impact=imp.causal_impact()
            
            st.pyplot(ts_fig)
            impact.run()
            st.header("IMPACT PLOTS")
            st.pyplot(impact.plot())

            st.header("SUMMARY REPORT")
#             impact_summary=impact_summary.replace("\n","<br>")
#             impact_summary=impact_summary.replace("{Causal Impact}","")
#             impact_summary=impact_summary.replace("For more details run the command: print(impact.summary('report'))","")
            st.write(str(impact.summary()))

            st.header("FULL REPORT")
#             report=report.replace("{CausalImpact}","")
            st.write(str(impact.summary(output='report')))



       
