import psycopg2
import tempfile,csv,json,os,io
from contextlib import contextmanager
import pandas as pd
from flask import Response, stream_with_context,Blueprint,render_template,redirect,url_for, request, session,make_response,send_file
from io import StringIO
from cachelib import SimpleCache
extracted_data_cache = {}
app = Blueprint('app',__name__)

hostname='localhost'
database='dump'
username='postgres'
pwd='password'
port_id=5432

practice_areas = [
    "Administrative Law",
    "Alternative Dispute Resolution",
    "Animal Law",
    "Antitrust Litigation",
    "Appellate",
    "Aviation and Aerospace",
    "Banking",
    "Bankruptcy",
    "Business Litigation",
    "Business/Corporate",
    "Cannabis Law",
    "Civil Litigation",
    "Civil Rights",
    "Class Action/Mass Torts",
    "Closely Held Business",
    "Communications",
    "Constitutional Law",
    "Construction Litigation",
    "Consumer Law",
    "Creditor Debtor Rights",
    "Criminal Defense",
    "Criminal Defense: DUI/DWI",
    "Criminal Defense: White Collar",
    "E-Discovery",
    "Elder Law",
    "Eminent Domain",
    "Employee Benefits",
    "Employment & Labor",
    "Employment Litigation",
    "Energy & Natural Resources",
    "Entertainment & Sports",
    "Environmental",
    "Environmental Litigation",
    "Estate & Trust Litigation",
    "Estate Planning & Probate",
    "Family Law",
    "Food and Drugs",
    "Franchise/Dealership",
    "Gaming",
    "General Litigation",
    "Government Contracts",
    "Government Finance",
    "Government Relations",
    "Health Care",
    "Immigration",
    "Insurance Coverage",
    "Intellectual Property",
    "Intellectual Property Litigation",
    "International",
    "Land Use/Zoning",
    "Legal Aid/Pro Bono",
    "Legislative & Governmental Affairs",
    "Lobbying",
    "Media and Advertising",
    "Mergers & Acquisitions",
    "Military/Veterans Law",
    "Native American Law",
    "Nonprofit Organizations",
    "Personal Injury - General",
    "Personal Injury - Medical Malpractice",
    "Personal Injury - Products",
    "Professional Liability",
    "Real Estate",
    "Schools & Education",
    "Securities & Corporate Finance",
    "Securities Litigation",
    "Social Security Disability",
    "State, Local & Municipal",
    "Surety",
    "Tax",
    "Technology Transactions",
    "Transportation/Maritime",
    "Utilities",
    "Workers' Compensation"
]

actice_areas=sorted(practice_areas)
def alnumspace(practice_areas):
    ii=practice_areas
    x=""
    for j in range(0,len(ii)):
        if ii[j]==" " or ii[j].isalnum():
            x+=ii[j]
    practice_areas=x
    return practice_areas


def to_capital(x):
    xx=[]
    y=""
    for i in range(0,len(x)):
        if x[i]==" ":
            xx.append(i)
    for i in xx:
        y=x[:i+1]+x[i+1].capitalize()+x[i+2:]
    return y
        
def display_state(data):
    # cur.execute(f'''SELECT state FROM dump WHERE practice_areas @> ARRAY['{to_capital(data.capitalize())}'] or practice_areas @> ARRAY['{data.capitalize()}']''')
    conn=psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)
    cur = conn.cursor()
    conn.autocommit= True
    cur.execute(f'''SELECT state FROM dump WHERE practice_areas @> ARRAY['{(data)}']''')
    all_states=(cur.fetchall())
    cur.close()
    conn.close()
    return all_states

def display_city(data,extracted_data):
    conn=psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)
    cur = conn.cursor()
    conn.autocommit= True
    cur.execute(f'''SELECT city FROM dump WHERE ((practice_areas @> ARRAY['{(extracted_data[0]['practice_areas'])}']) and (state @> ARRAY['{to_capital((extracted_data[0]['state']).capitalize())}'] or state @> ARRAY['{(extracted_data[0]['state']).capitalize()}']))''')
    # cur.execute(f'''SELECT state FROM dump''')
    all_city=(cur.fetchall())
    cur.close()
    conn.close()
    return all_city

def display_firms(data,extracted_data):
    conn=psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)
    cur = conn.cursor()
    conn.autocommit= True
    cur.execute(f'''SELECT * FROM dump WHERE (practice_areas @> ARRAY['{(extracted_data[0]['practice_areas'])}']) and (state @> ARRAY['{to_capital(extracted_data[0]['state'].capitalize())}'] or state @> ARRAY['{extracted_data[0]['state'].capitalize()}']) AND ((city @> ARRAY['{to_capital(data.capitalize())}'] or city @> ARRAY['{data}'] or city @>  ARRAY['{to_capital(data.capitalize())}']))''')
    # cur.execute(f'''SELECT state FROM dump''')
    all_firms=(cur.fetchall())
    cur.execute(f'''SELECT * FROM dump WHERE (practice_areas @> ARRAY['{(extracted_data[0]['practice_areas'])}']) and (state @> ARRAY['{to_capital(extracted_data[0]['state'].capitalize())}'] or state @> ARRAY['{extracted_data[0]['state'].capitalize()}'])''')
    all_firms_ofstates=(cur.fetchall())
    cur.execute(f'''SELECT * FROM dump WHERE (practice_areas @> ARRAY['{(extracted_data[0]['practice_areas'])}']) and (state @> ARRAY['{to_capital(data.capitalize())}'] or state @> ARRAY['{data.capitalize()}']) AND (state @> ARRAY['{to_capital(extracted_data[0]['state'].capitalize())}'] or state @> ARRAY['{extracted_data[0]['state']}'])''')
    yy=cur.fetchall()
    cur.close()
    conn.close()
    
    return all_firms,all_firms_ofstates

@app.route('/')
def index():
    return render_template("practice_areas.html",datas=practice_areas)

@app.route('/practice_areas', methods=['POST'])
def practice_area_select():
    return render_template("practice_areas.html",datas=practice_areas)

@app.route('/state', methods=['POST'])
def state():
    dic = {
        "practice_areas":"",
        "state":"",
        "city":"",
    }
    extracted_data=[]
    session_id = request.cookies.get('session_id')
    extracted_data.append(dic)
    extracted_data_cache[session_id] = extracted_data
    def state_match(data):
        matching_states=[]
        state_list=display_state(data)
        for i in state_list:
            for j in i:
                for k in j:
                    if k!="Statename cannot be scraped":
                        matching_states.append(k)
        return matching_states
    
    input_areas=request.form.get('input_areas')
    if input_areas!=None:
        if len(input_areas)!=0:
            matching_states=state_match(input_areas)
            session_id = session.get('session_id')
            extracted_data = extracted_data_cache.get(session_id, [])
            extracted_data[0]["practice_areas"]=input_areas
            session_id = request.cookies.get('session_id')
            extracted_data_cache[session_id] = extracted_data
            return render_template('practice_areas.html', state_list=sorted(list(set(matching_states))))
   
    get_areas=request.form['input_submit']
    if len(get_areas)!=0:
        matching_states=state_match(get_areas)
        session_id = session.get('session_id')
        extracted_data = extracted_data_cache.get(session_id, [])
        extracted_data[0]["practice_areas"]=get_areas 
        session_id = request.cookies.get('session_id')
        extracted_data_cache[session_id] = extracted_data
        return render_template('practice_areas.html', state_list=sorted(list(set(matching_states))))
    
    return "Please enter a valid Practice areas"

@app.route('/city', methods=['POST'])
def city():
    def city_match(data,extracted_data):
        session_id = session.get('session_id')
        extracted_data = extracted_data_cache.get(session_id, [])
        matching_city=[]
        city_list=display_city(data,extracted_data)
        for i in city_list:
            for j in i:
                for k in j:
                    if k!="Statename cannot be scraped":
                        matching_city.append(k)
        return matching_city
    
    get_states=request.form['input_state']
    session_id = session.get('session_id')
    extracted_data = extracted_data_cache.get(session_id, [])
    extracted_data[0]["state"]=get_states 
    session_id = request.cookies.get('session_id')
    extracted_data_cache[session_id] = extracted_data
    matching_city=city_match(get_states,extracted_data)
    return render_template('practice_areas.html', city_list=sorted(list(set(matching_city))))
    
@app.route('/law_firms', methods=['POST'])
def law_firms():
    def firms_match(data,extracted_data):
        session_id = session.get('session_id')
        extracted_data = extracted_data_cache.get(session_id, [])
        matching_firms=[]
        matching_firms_ofstates=[]
        firms_list,firms_list_ofstates=display_firms(data,extracted_data)
        for i in firms_list:
            dicc = {
                "url":i[1],
                "practice_areas":"",
                "law_firm_name":i[2],
                "address":i[3],
                "state":i[4],
                "city":i[5],
                "phone_numbers":i[6]
            }
            if dicc not in matching_firms:
                matching_firms.append(dicc)
        for i in firms_list_ofstates:
            diccc = {
                "url":i[1],
                "practice_areas":"",
                "law_firm_name":i[2],
                "address":i[3],
                "state":i[4],
                "city":i[5],
                "phone_numbers":i[6]
            }
            if (diccc not in matching_firms_ofstates):
                matching_firms_ofstates.append(diccc)
        return matching_firms,matching_firms_ofstates
    
    get_city=request.form['input_city']
    session_id = session.get('session_id')
    extracted_data = extracted_data_cache.get(session_id, [])
    extracted_data[0]["city"]=get_city
    session_id = request.cookies.get('session_id')
    extracted_data_cache[session_id] = extracted_data
    matching_city,matching_states=firms_match(get_city,extracted_data)
    matching_states_filtered=[]
    for i in matching_states:
        if i not in matching_city:
            matching_states_filtered.append(i)
    if len(matching_states_filtered)==0:
        firms_list_ofstates_status=False
    else:
        firms_list_ofstates_status=True
    print(extracted_data)
    return render_template('practice_areas.html', firms_list=(list((matching_city))),firms_list_ofstates=(list(matching_states_filtered)),extracted_data=extracted_data[0],firms_list_ofstates_status=firms_list_ofstates_status)
    