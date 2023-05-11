#%% Revenue Estimation App


#imports
import streamlit as st
import time
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.io as pio
from fpdf import FPDF
import matplotlib.pyplot as plt 

#testing
import random


# set the page icon and title
# may not be useful in the iframe
st.set_page_config(page_title='Revenue Model',  layout='wide', page_icon='https://noctrixhealth.com/wp-content/uploads/2021/05/cropped-SiteIcon-32x32.jpg')


# remove the orange/red line on top
# also hides the hamburger menu
hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
        footer {visibility: hidden;} 
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)




## Global variables for Model



Set_Initial_Number_Of_Clinics                       = 2
Set_Number_Of_New_Clinics_Annual_Growth             = 10
Set_Patients_Per_Clinic_Per_Month                   = 2
Set_New_Patients_In_Existing_Clinic_Annual_Growth   = 10
Set_Patient_Attrition_Rate_Per_Month                = 20
Set_Percent_Patients_On_Medicare                    = 40
Set_Rental_Period_Refill_TOMA_CMS                   = 13
Set_Rental_Period_Refill_TOMA_PP                    = 6
Set_Rental_Period_Refill_CCG                        = 3
Set_Rental_Period_Refill_CDI                        = 1
Set_CMS_TOMA_CMS                                    = 7500
Set_CMS_CCG                                         = 200
Set_CMS_CDI                                         = 30
Set_Private_Payer_Premium_Over_Medicare             = 40


def form_callback():
    print("==Pricing Assumptions==")
    
import streamlit as st



# main page

# setting up the 3 columns for the Optimism, Periodicity and Printer sections

def resetDefault():
    del st.session_state['firstRunDone']

col1, col2, col3 = st.columns(3)

with col1:
    choice = st.radio(
     "Choose Preset",
     ('Optimistic', 'Conservative', 'Realistic'), index=0, disabled=False, on_change=resetDefault)
    
    Month_size                          =     st.slider("Number of Months to forecast",
                                                                min_value = 12,
                                                                max_value = 60,
                                                                value = 36, disabled=False)

with col2:
    Periodicity = st.radio(
     "Periodicity:",
     ('Yearly', 'Quarterly', 'Monthly'), index=2)
    
    Decimal_places                          =     st.slider("Number of Decimal Places",
                                                                min_value = 0,
                                                                max_value = 8,
                                                                value = 0 )

if choice == "Conservative":
    Set_Initial_Number_Of_Clinics                       = 1
    Set_Number_Of_New_Clinics_Annual_Growth            = 5
    Set_Patients_Per_Clinic_Per_Month                   = 2
    Set_New_Patients_In_Existing_Clinic_Annual_Growth   = 5
    Set_Patient_Attrition_Rate_Per_Month                = 15
    Set_Percent_Patients_On_Medicare                    = 60
    Set_Rental_Period_Refill_TOMA_CMS                   = 13
    Set_Rental_Period_Refill_TOMA_PP                    = 9
    Set_Rental_Period_Refill_CCG                        = 3
    Set_Rental_Period_Refill_CDI                        = 3
    Set_CMS_TOMA_CMS                                    = 300 * 2
    Set_CMS_CCG                                         = 150 * 2
    Set_CMS_CDI                                         = 21 * 2
    Set_Private_Payer_Premium_Over_Medicare             = 15 


if choice == "Realistic":
    Set_Initial_Number_Of_Clinics                       = 2
    Set_Number_Of_New_Clinics_Annual_Growth            = 10
    Set_Patients_Per_Clinic_Per_Month                   = 2 # was 4, set to match new excel model
    Set_New_Patients_In_Existing_Clinic_Annual_Growth   = 10
    Set_Patient_Attrition_Rate_Per_Month                = 10
    Set_Percent_Patients_On_Medicare                    = 40
    Set_Rental_Period_Refill_TOMA_CMS                   = 13
    Set_Rental_Period_Refill_TOMA_PP                    = 6
    Set_Rental_Period_Refill_CCG                        = 3
    Set_Rental_Period_Refill_CDI                        = 1   #was set to 3
    Set_CMS_TOMA_CMS                                    = 450* 2
    Set_CMS_CCG                                         = 250* 2
    Set_CMS_CDI                                         = 42* 2
    Set_Private_Payer_Premium_Over_Medicare             = 40
    
    
if choice == "Optimistic":
    Set_Initial_Number_Of_Clinics                       = 10
    Set_Number_Of_New_Clinics_Annual_Growth             = 40
    Set_Patients_Per_Clinic_Per_Month                   = 4
    Set_New_Patients_In_Existing_Clinic_Annual_Growth   = 10
    Set_Patient_Attrition_Rate_Per_Month                = 10
    Set_Percent_Patients_On_Medicare                    = 30
    Set_Rental_Period_Refill_TOMA_CMS                   = 13
    Set_Rental_Period_Refill_TOMA_PP                    = 13
    Set_Rental_Period_Refill_CCG                        = 3
    Set_Rental_Period_Refill_CDI                        = 1
    Set_CMS_TOMA_CMS                                    = 7500
    Set_CMS_CCG                                         = 200
    Set_CMS_CDI                                         = 45
    Set_Private_Payer_Premium_Over_Medicare             = 0
    
# Default Support model values, can be implemented into optimising options 

Set_Existing_Hours_Per_Week                             = 8
Set_New_Hours_Per_Week                                  = 30
Set_Max_Hours_Per_Week                                  = 36
    
# the sliding out section used to set parameters to the model


# %%
# These functions are needed to be used in callbacks to keep the paried
# inputs in sync.

#kit loops
def update_slider_kit():
    st.session_state.slider_kit = st.session_state.text_kit

def update_text_kit():
    st.session_state.text_kit = st.session_state.slider_kit

# CCG function loops to keep the two inputs linked
def update_slider_CCG():
    st.session_state.slider_CCG = st.session_state.text_CCG

def update_text_CCG():
    st.session_state.text_CCG = st.session_state.slider_CCG
    
# CDI function loops 

def update_slider_CDI():
    st.session_state.slider_CDI = st.session_state.text_CDI

def update_text_CDI():
    st.session_state.text_CDI = st.session_state.slider_CDI
    
### set default values
if "firstRunDone" not in st.session_state:
    st.session_state.slider_kit = st.session_state.text_kit = Set_CMS_TOMA_CMS
    st.session_state.slider_CCG = st.session_state.text_CCG = Set_CMS_CCG
    st.session_state.slider_CDI = st.session_state.text_CDI = Set_CMS_CDI
    st.session_state.firstRunDone = True


#%% Sidebar setup
    
with st.sidebar: #.form(key='my_form'):
    # logo in sidebar
    #st.markdown("<div style="text-align: center;">
    #            <img src="https://noctrixhealth.com/wp-content/uploads/2020/10/NoctrixLogo@2x.png" alt="logo" width=200/></div>

    #""", unsafe_allow_html=True)
    

    
    st.subheader('Model Parameters')
    #top_submit_button = st.form_submit_button(label='🖩 Calculate', on_click=form_callback)

    

    

    with st.expander("🏥 Number of Clinic Parameters"):
        Initial_Number_Of_Clinics                       =     st.slider("Initial Number Of Clinics [#]",
                                                                min_value = 0,
                                                                max_value = 5,
                                                                value = Set_Initial_Number_Of_Clinics)
    
        Number_Of_New_Clinics__Annual_Growth            =     st.slider("Number Of New Clinics Annual Growth",
                                                                min_value = 0,
                                                                max_value = 100,
                                                                value = Set_Number_Of_New_Clinics_Annual_Growth,
                                                                format="%i%%")*.01
               
        Patients_Per_Clinic_Per_Month                   =     st.slider("Patients Per Clinic Per Month [#]",
                                                                min_value = 0,
                                                                max_value = 10,
                                                                value = Set_Patients_Per_Clinic_Per_Month)
        
        
        
    with st.expander("👤Number of Patients Parameters"):                             
        New_Patients_In_Existing_Clinic_Annual_Growth   =     st.slider("New Patients In Existing Clinic Annual Growth",
                                                                min_value = 0,
                                                                max_value = 25,
                                                                value = Set_New_Patients_In_Existing_Clinic_Annual_Growth,
                                                                format="%i%%")*.01
        
        Patient_Attrition_Rate_Per_Month                =     st.slider("Patient Attrition Rate Per Month",
                                                                min_value = 0,
                                                                max_value = 25,
                                                                value = Set_Patient_Attrition_Rate_Per_Month,
                                                                format="%i%%")*.01
        
        
        Percent_Patients_On_Medicare                    =     st.slider("Percent Patients On Medicare",
                                                                min_value = 0,
                                                                max_value = 100,
                                                                value = Set_Percent_Patients_On_Medicare,
                                                                format="%i%%")*.01
    with st.expander("📈 Center Productivity Parameters"):                             
        Patients_per_month_per_prescriber               =     st.slider("Patients / month / prescriber",
                                                                min_value = 0,
                                                                max_value = 25,
                                                                value = 4)
        
        Number_of_prescribers_added_per_month           =     st.slider("Number of prescribers added per month",
                                                                min_value = 0,
                                                                max_value = 25,
                                                                value = 1)
        
        Center_max_patients_per_month                   =     st.slider("Center max patients per month",
                                                                min_value = 0,
                                                                max_value = 70,
                                                                value = 30)
        
        
        Number_of_prescribers_needed_to_max             =     st.slider("Number of prescribers needed to max",
                                                                min_value = 0,
                                                                max_value = 15,
                                                                value = 8)
            

    
    #Number per kit
    Number_Per_Kit_TOMA_CMS                        =     1
    
    
    Number_Per_Kit_TOMA_PP                         =     1
    
    Number_Per_Kit_CCG                             =     1
    
    Number_Per_Kit_CDI                             =     1
    
    
    
    # Rental period / Refill frequency (months)
    with st.expander("📅 Rental / Refill Period"):
        Rental_Period_Refill_TOMA_CMS                 =     st.slider("Rental Period for TOnic Motor ACtivator when Medicare [months]",
                                                                min_value = 0,
                                                                max_value = 24,
                                                                value = Set_Rental_Period_Refill_TOMA_CMS, disabled=True)
                                                      
        Rental_Period_Refill_TOMA_PP                  =     st.slider("Rental Period for TOnic Motor ACtivator when Private [months]",
                                                                min_value = 0,
                                                                max_value = 13,
                                                                value = Set_Rental_Period_Refill_TOMA_PP)
        
        Rental_Period_Refill_CCG                      =     st.slider("Refill Period for Compressive Conduction Garment [months]",
                                                                min_value = 0,
                                                                max_value = 12,
                                                                value = Set_Rental_Period_Refill_CCG, disabled=False)       
        
        Rental_Period_Refill_CDI                      =     st.slider("Refill Period for Charge Dispersing Interface [months]",
                                                                min_value = 0,
                                                                max_value = 12,
                                                                value = Set_Rental_Period_Refill_CDI, disabled=True) 
        
    
        
        
    with st.expander("💵 ASP Assumptions"):    
    #Total CMS Reimbursement per unit
        
       CMS_TOMA_CMS_TEXT                            =     st.number_input('New Kit ASP',                                                                          
                                                                          key = "text_kit",
                                                                          on_change = update_slider_kit,
                                                                          step=1,
                                                                          format="%i"
                                                                          )

       
       CMS_TOMA_CMS                                 =     st.slider("New Kit ASP",
                                                                min_value = 200,
                                                                max_value = 12000,                                                             
                                                                format="$%i",
                                                                key="slider_kit",
                                                                value  = Set_CMS_TOMA_CMS,
                                                                on_change=update_text_kit,
                                                                label_visibility="collapsed")
       
       st.markdown("""---""")
       
       CMS_CCG_TEXT                                 =     st.number_input('Garment refill (CCG) ASP', 
                                                                          value = Set_CMS_CCG, 
                                                                          key = "text_CCG",
                                                                          on_change = update_slider_CCG
                                                                          )
        
        
       CMS_CCG                                      =     st.slider("Garment refill (CCG) ASP",
                                                            min_value = 0,
                                                            max_value = 3000,
                                                            format="$%i",
                                                            key = "slider_CCG",
                                                            value=Set_CMS_CCG,
                                                            on_change = update_text_CCG,
                                                            label_visibility="collapsed")
       
       st.markdown("""---""")
       
       CMS_CDI_TEXT                                 =     st.number_input('Monthly electrode refill (CDI) ASP', 
                                                                          value = Set_CMS_CDI, 
                                                                          key = "text_CDI",                                                                          
                                                                          on_change = update_slider_CDI
                                                                          )
        
       CMS_CDI                                       =     st.slider("Monthly electrode refill (CDI) ASP",
                                                                min_value = 15,
                                                                max_value = 1100,
                                                                format="$%i",
                                                                key = "slider_CDI",
                                                                value = Set_CMS_CDI,
                                                                on_change=update_text_CDI,
                                                                label_visibility="collapsed")
        
       Private_Payer_Premium_Over_Medicare           =    0
       # medicare not a factor currently
        
       # Private_Payer_Premium_Over_Medicare           =     st.slider("Private Payer Premium Over Medicare",
       #                                                         min_value = 0,
       #                                                         max_value = 100,
       #                                                         value = Set_Private_Payer_Premium_Over_Medicare,
       #                                                         format="%i%%")*.01
      
        
        


    with st.expander("👩‍⚕️ Clinical Support Staffing"):   
        Number_of_Patients_per_Tech                     =     st.slider("Number of New Patients per Month per Remote Tech",
                                                                min_value = 10,
                                                                max_value = 50,
                                                                value = 25)
        
        # Number_of_Patients_per_Specialist               =     st.slider("Number of Patients per Field Clinical Specialist",
        #                                                         min_value = 80,
        #                                                         max_value = 300,
        #                                                         value = 200)
        
        Cost_per_Calibration_Session                    =     st.slider("Cost of a Calibration Session",
                                                                min_value = 100,
                                                                max_value = 300,
                                                                value = 200)
        
        Cost_per_New_site                               =     st.slider("Cost of a New Site",
                                                                min_value = 2000,
                                                                max_value = 4000,
                                                                value = 3000) 
        
        
        
        
    with st.expander("🪙 Cost of goods sold (COGS)"):    

        NTX_TOMAC_COGS_Y1                      =     st.slider("NTX100 TOMAC Kit COGS Year 1",
                                                                min_value = 250,
                                                                max_value = 2000,
                                                                value = 1000)
        
        NTX_TOMAC_COGS_AF1                      =     st.slider("NTX100 TOMAC Kit COGS After Year 1",
                                                                min_value = 250,
                                                                max_value = 2000,
                                                                value = 500)
        
        CDI_COGS_Y1                      =     st.slider("Monthly CDI COGS Year 1",
                                                                min_value = 5,
                                                                max_value = 50,
                                                                value = 30)
        
        CDI_COGS_AF1                      =     st.slider("Monthly CDI COGS After Year 1",
                                                                min_value = 5,
                                                                max_value = 50,
                                                                value = 25)
        
        CCG_COGS_Y1                      =     st.slider("Pair of CCG COGS Year 1",
                                                                min_value = 5,
                                                                max_value = 50,
                                                                value = 25)
        
        CCG_COGS_AF1                      =     st.slider("Pair of CCG COGS After Year 1",
                                                                min_value = 5,
                                                                max_value = 50,
                                                                value = 18)
    
        CAC_COGS_Y1                      =     st.slider("Fully loaded CAC Year 1",
                                                                min_value = 500,
                                                                max_value = 2000,
                                                                value = 1500)
        
        CAC_COGS_AF1                      =     st.slider("Fully loaded CAC After Year 1",
                                                                min_value = 500,
                                                                max_value = 2000,
                                                                value = 750)
        

        
    


    
#%% Calculations



# Calculated fields
#-------------------------------

CMS_TOMA_PP               = CMS_TOMA_CMS * (1+ Private_Payer_Premium_Over_Medicare) 

#Total CMS Reimbursement
Total_TOMA_CMS            = CMS_TOMA_CMS * Number_Per_Kit_TOMA_CMS
Total_TOMA_PP             =  CMS_TOMA_PP * Number_Per_Kit_TOMA_PP
Total_CCG                 =      CMS_CCG * Number_Per_Kit_CCG
Total_CDI                 =      CMS_CDI * Number_Per_Kit_CDI

#-------------------------------
#Private Payer
Private_TOMA                = Total_TOMA_CMS * (1+ Private_Payer_Premium_Over_Medicare) 
# no Private and blended for CMS_TOMA_PP row.  This was included for rental periods
Private_CCG                 =      Total_CCG * (1+ Private_Payer_Premium_Over_Medicare)
Private_CDI                 =      Total_CDI * (1+ Private_Payer_Premium_Over_Medicare)

#-------------------------------
#Blended Reimbursement
Percent_Private = 1 - Percent_Patients_On_Medicare

Blended_TOMA                =  (Percent_Patients_On_Medicare * Total_TOMA_CMS) + (Percent_Private * Private_TOMA)
# no Private and blended for CMS_TOMA_PP row.  This was included for rental periods
Blended_CCG                 =  (Percent_Patients_On_Medicare * Total_CCG) + (Percent_Private * Private_CCG)
Blended_CDI                 =  (Percent_Patients_On_Medicare * Total_CDI) + (Percent_Private * Private_CDI)



numMonths = Month_size + 1 # add one to the actual number you want


Month                             = np.arange(numMonths)
New_Clinics                       = np.zeros(numMonths)
Total_prescribing_clinics         = np.zeros(numMonths)
New_patients_by_month             = np.zeros(numMonths)
Hours_required                    = np.zeros(numMonths)
Staff_required                    = np.zeros(numMonths)
Calibration_costs                 = np.zeros(numMonths)
Patient_Setup_Costs               = np.zeros(numMonths)
Follow_up_Costs                   = np.zeros(numMonths)
NTX100_TOMAC_Kit_COGS             = np.zeros(numMonths)
CDI_COGS                          = np.zeros(numMonths)
CCG_COGS                          = np.zeros(numMonths)
New_patients_per_month_per_clinic = np.zeros(numMonths)

# Month one inital condition
New_Clinics[1]                      = Initial_Number_Of_Clinics
Total_prescribing_clinics[1]        = Initial_Number_Of_Clinics
New_patients_by_month[1]            = Initial_Number_Of_Clinics * Patients_Per_Clinic_Per_Month
Calibration_costs[1]                = New_patients_by_month[1] * Cost_per_Calibration_Session
New_patients_per_month_per_clinic[1]= Patients_Per_Clinic_Per_Month  

# one time calculation for monthly growth factor

Monthly_Growth = 1 + (New_Patients_In_Existing_Clinic_Annual_Growth / 12)

Number_Of_New_Clinics_Monthly_Growth = Number_Of_New_Clinics__Annual_Growth / 12

# Loop for remaining months
for i in range(2,numMonths):
  pre = i-1   # previous month
  New_Clinics[i]                       = (Total_prescribing_clinics[pre] * Number_Of_New_Clinics_Monthly_Growth) #np.ceil(Total_prescribing_clinics[pre] * Number_Of_New_Clinics_Monthly_Growth)
  Total_prescribing_clinics[i]         = Total_prescribing_clinics[pre] + New_Clinics[i] 
  # had np.ceil in this step
  New_patients_per_month_per_clinic[i] = New_patients_per_month_per_clinic[pre] * Monthly_Growth
  #New_patients_by_month[i]             = (Total_prescribing_clinics[pre] * (Monthly_Growth ** Month[pre]) * Patients_Per_Clinic_Per_Month + New_Clinics[i] * Patients_Per_Clinic_Per_Month)
  New_patients_by_month[i]             = Total_prescribing_clinics[i] * New_patients_per_month_per_clinic[i]

One_patient_amortization = np.zeros((numMonths,numMonths))
One_patient_amortization[1] =  New_patients_by_month
Attrition_Rate = 1 - Patient_Attrition_Rate_Per_Month

for row in range(2,numMonths):
  for col in range(row,numMonths):
    One_patient_amortization[row][col] = np.ceil(One_patient_amortization[row-1][col-1] * Attrition_Rate) # had np.ceil

Total_patients = One_patient_amortization.sum(axis=0)


# ==================================================================  #
# updated formula for new prescibers used to match Excel model for a 12 month model
# ==================================================================  #
if False:
    Salesperson_Rate = 6 # New Salesperson every 6 months
    Number_of_Sales_Reps = np.ceil(Month/Salesperson_Rate)
    Prescribers_Open_per_month_per_sales_rep = 2
    
    New_Clinics = Number_of_Sales_Reps * Prescribers_Open_per_month_per_sales_rep
    
    Total_prescribing_clinics = np.cumsum(New_Clinics)
    New_patients_by_month = Total_prescribing_clinics * Patients_Per_Clinic_Per_Month
    Total_patients = np.cumsum(New_patients_by_month)
    # factor attrition
    Total_patients = Total_patients * (1-Patient_Attrition_Rate_Per_Month)
    New_patients_by_month = np.diff(Total_patients)
    New_patients_by_month = np.insert(New_patients_by_month,0,Total_patients[0])
#### experimental Sheet 3 complete



# ==================================================================  #
# updated formula for Center productivity model
# ==================================================================  #
Center_productivity = col3.checkbox("Center Productivity Calculations", value=True, help="When disabled, uses previous model based on growth and attritrion.")
if Center_productivity:
 Center_productivity_matrix = np.zeros((numMonths,numMonths))
 
 #setup empty arrays to loop over
 New_prescribers_added = np.zeros(numMonths)
 Total_prescribers     = np.zeros(numMonths)
 New_patients          = np.zeros(numMonths)
 
 for month in range(1,numMonths):
     New_prescribers_added[month] = Number_of_prescribers_added_per_month if month <= Number_of_prescribers_needed_to_max else 0
     Total_prescribers[month] = np.sum(New_prescribers_added)
     New_patients[month] = Total_prescribers[month] * Patients_per_month_per_prescriber
     
     
 
 
 Center_productivity_matrix[1] =  New_patients
 

 for row in range(2,numMonths):
   for col in range(row,numMonths):
     Center_productivity_matrix[row][col] = Center_productivity_matrix[row-1][col-1] 
     
 New_patients_by_month = np.dot(New_Clinics,Center_productivity_matrix)  
 
 One_patient_amortization = np.zeros((numMonths,numMonths))
 One_patient_amortization[1] =  New_patients_by_month
 Attrition_Rate = 1 - Patient_Attrition_Rate_Per_Month

 for row in range(2,numMonths):
   for col in range(row,numMonths):
     One_patient_amortization[row][col] = np.ceil(One_patient_amortization[row-1][col-1] * Attrition_Rate) # had np.ceil

 Total_patients = One_patient_amortization.sum(axis=0)
   


#Number_of_Field_Clinical_Specialists = np.ceil(Total_patients / Number_of_Patients_per_Specialist)
Number_of_Remote_techs = np.ceil(New_patients_by_month / Number_of_Patients_per_Tech )


Calibration_costs        = New_patients_by_month * Cost_per_Calibration_Session

New_site_costs           = New_Clinics * Cost_per_New_site 



#  ===

TOMA_CMS                   = np.zeros(numMonths)
TOMA_PP                    = np.zeros(numMonths)
CCG                        = np.zeros(numMonths)  
CDI                        = np.zeros(numMonths)

# For TOMA, check if within rental period before calculating
for month in Month[1:]:
  if month <= Rental_Period_Refill_TOMA_CMS:
    TOMA_CMS[month] = (Number_Per_Kit_TOMA_CMS * CMS_TOMA_CMS) / Rental_Period_Refill_TOMA_CMS
    #else 0 as prefilled

  if month <= Rental_Period_Refill_TOMA_PP:
    TOMA_PP[month] = (Number_Per_Kit_TOMA_PP * CMS_TOMA_PP)  / Rental_Period_Refill_TOMA_PP 
  # The CCG and CDI paid on refill months
  pre = month - 1
  # take the modulus and if its zero (not non-zero) then fill the value
  if not (pre % Rental_Period_Refill_CCG): 
      CCG[month] = CMS_CCG
      
  if not (pre % Rental_Period_Refill_CDI):
      CDI[month] = CMS_CDI
    
# if after rental period, leave as 0

# cast to all values the same result for CCG and CDI
#CCG[:] = Blended_CCG / Rental_Period_Refill_CCG
#CDI[:] = Blended_CDI / Rental_Period_Refill_CDI

Total = (TOMA_CMS * Percent_Patients_On_Medicare) + (TOMA_PP * Percent_Private) + CCG + CDI

Devices = (TOMA_CMS * Percent_Patients_On_Medicare) + (TOMA_PP * Percent_Private)

Monthly_Revenue = np.dot(Total[1:], np.delete(One_patient_amortization, 0, 0))
Monthly_Revenue[0] = 1
Revenue_New_Patients = Total[1] * One_patient_amortization[1]
Revenue_Existing_Patients = Monthly_Revenue - Revenue_New_Patients
Revenue_Devices = np.dot(Devices, One_patient_amortization)
Revenue_Consumables = Monthly_Revenue - Revenue_Devices
Device_Percentage = Revenue_Devices / Monthly_Revenue
Consumables_Percentage = 1 - Device_Percentage

# i indicates inventory, variables above are revenue



iTOMA                  = np.zeros(numMonths) # each new patient requires TOMA
iCCG                   = np.zeros(numMonths)
iCDI                   = np.zeros(numMonths)

for month in Month:
    iTOMA[month] = ((New_patients_by_month[month] * Number_Per_Kit_TOMA_CMS) +  # each new patient needs a kit
                     New_Clinics[month])                                        # each new clinic needs a kit (calibration) (not modeled in reimbursement)
    
    # to determine the number of CCG, inspect the number of patients x months ago (x months = refill period)
    
    # need to clip to zero to prevent negative months
    CCG_Refill_Month = np.clip(month-Rental_Period_Refill_CCG, a_min=0, a_max=None)    
    
    iCCG[month]  = (iTOMA[month] +                                              # each new TOMA will need a CCG kit
                   (Total_patients[CCG_Refill_Month] * Number_Per_Kit_CCG))     # The patients we had x months ago are due for a refill
    
    # need to clip to zero to prevent negative months
    CDI_Refill_Month = np.clip(month-Rental_Period_Refill_CDI, a_min=0, a_max=None)    
    
    iCDI[month]  = (iTOMA[month] +                                              # each new TOMA will need a CCG kit
                   (Total_patients[CDI_Refill_Month] * Number_Per_Kit_CDI))     # The patients we had y months ago are due for a refill

#adjust the calculation for inventory using dot product

iCCG = np.dot((CCG>0),One_patient_amortization)
iCDI = np.dot((CDI>0),One_patient_amortization)

# c indicates cost

cTOMA                  = np.zeros(numMonths) 
cCCG                   = np.zeros(numMonths)
cCDI                   = np.zeros(numMonths) 
CAC                    = np.zeros(numMonths) 

for month in Month:
    cTOMA[month] = iTOMA[month] * (NTX_TOMAC_COGS_Y1           if month <= 12 else NTX_TOMAC_COGS_AF1 )
    cCCG[month]  = iCCG[month] * (CCG_COGS_Y1                  if month <= 12 else CCG_COGS_AF1 )
    cCDI[month]  = iCDI[month] * (CDI_COGS_Y1                  if month <= 12 else CDI_COGS_AF1)
    CAC[month]   = New_patients_by_month[month] * (CAC_COGS_Y1 if month <=12 else CAC_COGS_AF1)

            


Quarter = np.ceil(Month /3)

Year = np.ceil(Month / 12)

df = pd.DataFrame({
    'Month':Month,
    'Quarter':Quarter,
    'Year':Year,
    'New Clinics':np.round(New_Clinics, Decimal_places) ,
    'Total prescribing clinics':np.round(Total_prescribing_clinics, Decimal_places),
    'New patients':np.round(New_patients_by_month, Decimal_places),
    'Total patients':np.round(Total_patients, Decimal_places),
    'Monthly_Revenue': np.round(Monthly_Revenue, Decimal_places),
    'Revenue New Patients':np.round(Revenue_New_Patients, Decimal_places),
    'Revenue Existing Patients':np.round(Revenue_Existing_Patients, Decimal_places),
    'Revenue Devices':np.round(Revenue_Devices, Decimal_places),
    'Revenue Consumables':np.round(Revenue_Consumables, Decimal_places),
    'Device Percentage':np.round(Device_Percentage, Decimal_places),
    'Consumables Percentage':np.round(Consumables_Percentage, Decimal_places),
    'Staff required':np.round(Staff_required, Decimal_places),
    'TOMAC Inventory':np.round(iTOMA, Decimal_places),
    'CCG Inventory':np.round(iCCG, Decimal_places),
    'CDI Inventory':np.round(iCDI, Decimal_places),
    'Calibration costs':Calibration_costs,
    'Patient Setup Costs':Patient_Setup_Costs,
    'Follow up Costs':Follow_up_Costs,
    #'Number of Field Clinical Specialists':Number_of_Field_Clinical_Specialists,
    'Number of Remote techs':Number_of_Remote_techs,
    'New site costs':New_site_costs,
    'CAC':CAC,
    'Cost of TOMAC':np.round(cTOMA, Decimal_places),
    'Cost of CCG':np.round(cCCG, Decimal_places),
    'Cost of CDI':np.round(cCDI, Decimal_places)})

st.write("")
st.write("")

#%% == creaate the quarterly and yearly DataFrames

df['Revenue'] = df['Monthly_Revenue']

qdf    = df.groupby('Quarter').sum()
qdfMax = df.groupby('Quarter').max()  # for patient count

qdf['Quarter'] = qdf.index
qdfMax['Quarter'] = qdfMax.index
   

qdf['Revenue'] = qdf['Monthly_Revenue']

ydf    = df.groupby('Year').sum()
ydfMax = df.groupby('Year').max()  # for patient count

ydf['Year'] = ydf.index
ydfMax['Year'] = ydfMax.index
   

ydf['Revenue'] = ydf['Monthly_Revenue']

#totals need to be based on max
qdf['Total patients'] = qdfMax['Total patients']
ydf['Total patients'] = ydfMax['Total patients']

qdf['Total prescribing clinics'] = qdfMax['Total prescribing clinics']
ydf['Total prescribing clinics'] = ydfMax['Total prescribing clinics']


#%% Main plots - barplot function

def barPlot(yArray, Title, Units, maximize=False):
    
    # default is cumulative, in some cases(percentage) the maximum value is more approraite
    if Periodicity ==  'Monthly':
        DataFrame = df[1:]
    if Periodicity ==  'Quarterly' and not maximize:
        DataFrame = qdf[1:]
    if Periodicity ==  'Quarterly' and maximize:
        DataFrame = qdfMax[1:]
    if Periodicity ==  'Yearly' and not maximize:
        DataFrame = ydf[1:]
    if Periodicity ==  'Yearly' and maximize:
        DataFrame = ydfMax[1:]
        
    fig = px.bar(
        data_frame = DataFrame,
        x = Periodicity[:-2],
        y = yArray,
        opacity = 0.5,
        color_discrete_sequence=['deepskyblue','MediumSlateBlue','DarkTurquoise'],
        orientation = "v",
        barmode = 'group',
        title=Title,
        labels={'x': Periodicity[:-2], 'value':Units},
    )

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    
    fig.update_layout(hovermode='x unified', 
                      hoverlabel=dict(
                            font_size=20
                        ),
                      xaxis=dict(tickmode='linear',dtick=1))
    
    st.plotly_chart(fig, use_container_width=True)   


#%% Main Layout

#barPlot (yArray,                                  Title,                 Units,              maximize=False)
#New Clinics
barPlot(["New Clinics","Total prescribing clinics"], "Number of Clinics", 'Number of Clinics', maximize=False)
#New Patients
barPlot(['New patients','Total patients'],"Number of Patients","Number of Patients")
#Revenue
barPlot(["Revenue"],f"{Periodicity} Revenue","Dollars USD $")
#New Vs Existing
barPlot(["Revenue New Patients","Revenue Existing Patients"],'Existing vs New Patient Revenue','Dollars USD $')
#Device vs Consumables
barPlot(["Revenue Devices","Revenue Consumables"],'Devices vs Consumables Revenue','Dollars USD $')
#Seperator
with st.expander("Costs, Inventory and Staff"):
    # Inventory
    barPlot(['TOMAC Inventory','CCG Inventory','CDI Inventory'],'Inventory','Units')
    # Inventory costs
    barPlot(['Cost of CCG','Cost of CDI','Cost of TOMAC'],'Inventory Costs','Dollars USD $')
    # Costs
    barPlot(['Calibration costs','New site costs','CAC'],'Costs','Dollars USD $')
    barPlot(['Number of Remote techs'],'Number of Staff','Count')


#barPlot (yArray,                                  Title,                 Units,              maximize=False)

    
#%%  Drop down calculation table/dataframes

with st.expander("Calculations"):
    st.write('Monthly')
    #df2 = df.T.style.format("{:.2}")
    df.T
    st.write('Quarterly')
    #qdf2 = qdf.T.style.format("{:.2}")
    qdf.T
    st.write('Annually')
    #qdf2 = qdf.T.style.format("{:.2}")
    ydf.T
    
with st.expander("Amortization Matrix"):
    One_patient_amortization
    
# %% Save PDF
with col3:
     PDFgen = st.button("⚙️ Generate PDF", disabled=True)
     
     if PDFgen:
        with st.spinner('Generating PDF...'):
            pdf = FPDF(orientation="P", unit="mm", format="Letter")
            pdf.add_page()
            pdf.set_font("helvetica", "B", 16)
            pdf.image("Logo.png",x=10,y=10,w=40)

            pdf.cell(190, 40, "Revenue Estimation Report", ln=1, align='C')

            pdf.cell(40,5,"Input Parameters to Model",ln=1)

            pdf.set_font("helvetica", "", 14)

            pdf.ln(1)

            rh = 7 # row height

            pdf.cell(150,rh,"Initial Number Of Clinics",border=1)
            pdf.cell(40,rh,str(Initial_Number_Of_Clinics),border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"Number Of New Clinics Monthly Growth",border=1)
            pdf.cell(40,rh,str(Number_Of_New_Clinics_Monthly_Growth*100)+'%',border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"Patients Per Clinic Per Month",border=1)
            pdf.cell(40,rh,str(Patients_Per_Clinic_Per_Month),border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"New Patients In Existing Clinic Annual Growth",border=1)
            pdf.cell(40,rh,str(New_Patients_In_Existing_Clinic_Annual_Growth*100)+'%',border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"Patient Attrition Rate Per Month",border=1)
            pdf.cell(40,rh,str(Patient_Attrition_Rate_Per_Month*100)+'%',border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"Percent Patients On Medicare",border=1)
            pdf.cell(40,rh,str(Percent_Patients_On_Medicare*100)+'%',border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"Rental Period Refill TOMA CMS",border=1)
            pdf.cell(40,rh,str(Rental_Period_Refill_TOMA_CMS)+' months',border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"Rental Period Refill TOMA PP",border=1)
            pdf.cell(40,rh,str(Rental_Period_Refill_TOMA_PP)+' months',border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"Rental Period Refill CCG",border=1)
            pdf.cell(40,rh,str(Rental_Period_Refill_CCG)+' months',border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"Rental Period Refill CDI ",border=1)
            pdf.cell(40,rh,str(Rental_Period_Refill_CDI)+' months',border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"CMS TOMA CMS ",border=1)
            pdf.cell(40,rh,'$'+str(CMS_TOMA_CMS),border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"CMS CCG",border=1)
            pdf.cell(40,rh,'$'+str(CMS_CCG),border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"CMS CDI",border=1)
            pdf.cell(40,rh,'$'+str(CMS_CDI),border=1)
            pdf.ln(rh)
            pdf.cell(150,rh,"Private Payer Premium Over Medicare",border=1)
            pdf.cell(40,rh,str(Private_Payer_Premium_Over_Medicare*100)+'%',border=1)
            pdf.ln(rh)


            #  next page begins plots

            pdf.add_page()


            X = qdf['Quarter'].astype(int)
            Y = qdf['Monthly_Revenue']

            X_axis = np.arange(len(X))

            plt.figure(dpi=250)  
            plt.bar(X_axis - 0.2, Y, 0.4, label = 'Revenue',color='MediumSlateBlue', alpha=0.7)

              
            plt.xticks(X_axis, X)
            plt.xlabel("Quarter")
            plt.ylabel("Dollars USD")
            plt.title("Revenue")
            plt.legend()
            plt.savefig('plot.png')
            pdf.image("plot.png",x=10,y=10,w=180)



            Y = qdf['Revenue_New_Patients']
            Z = qdf['Revenue_Existing_Patients']



            plt.figure(dpi=250)    
            plt.bar(X_axis - 0.2, Y, 0.4, label = 'Revenue New Patients',color='deepskyblue', alpha=0.7)
            plt.bar(X_axis + 0.2, Z, 0.4, label = 'Revenue Existing Patients',color='MediumSlateBlue', alpha=0.7)
              
            plt.xticks(X_axis, X)
            plt.xlabel("Quarter")
            plt.ylabel("Dollars USD")
            plt.title("Revenue From New vs Existing Patients")
            plt.legend()
            plt.savefig('plot2.png')
            pdf.image("plot2.png",x=10,y=140,w=180)



            # next page   =============

            pdf.add_page()

            Y = qdfMax['New_Clinics']
            Z = qdfMax['Total_prescribing_clinics']

            plt.figure(dpi=250)    
            plt.bar(X_axis - 0.2, Y, 0.4, label = 'New Clinics',color='deepskyblue', alpha=0.7)
            plt.bar(X_axis + 0.2, Z, 0.4, label = 'Total prescribing clinics',color='MediumSlateBlue', alpha=0.7)
              
            plt.xticks(X_axis, X)
            plt.xlabel("Quarter")
            plt.ylabel("Clinics")
            plt.title("New vs Total Prescibing Clinics")
            plt.legend()
            plt.savefig('plot3.png')
            pdf.image("plot3.png",x=10,y=10,w=180)



            Y = qdfMax['New_patients_by_month']
            Z = qdfMax['Total_patients']



            plt.figure(dpi=250)    
            plt.bar(X_axis - 0.2, Y, 0.4, label = 'New patients by month',color='deepskyblue', alpha=0.7)
            plt.bar(X_axis + 0.2, Z, 0.4, label = 'Total patients',color='MediumSlateBlue', alpha=0.7)
              
            plt.xticks(X_axis, X)
            plt.xlabel("Quarter")
            plt.ylabel("Patients")
            plt.title("New Patient vs Total Patients")
            plt.legend()
            plt.savefig('plot4.png')
            pdf.image("plot4.png",x=10,y=140,w=180)
            pdf.output("Report1.pdf")

            with open("Report1.pdf", "rb") as pdf_file:
                PDFbyte = pdf_file.read()
                
        st.success('📃 PDF Created!') 
        
        st.download_button(
            "⬇️ Download PDF",
            data=PDFbyte,
            file_name="Revenue Estimation.pdf",
            mime="application/octet-stream",
        )