from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import sqlite3, socket, routeros_api
from werkzeug.security import generate_password_hash, check_password_hash
# importing the libraries.
#flask : web framework
#render template enables us to load the HTML files
#request: grabs data sent from web forms
#session tracks what user is logged in 
#jsonify - sends the live cpu data

# sql3lite connects to the database file
#socket checks if the router is reachable
#routeros_PI is the mikrotiks tool for recieving data

#werkzeug scrambles passwords into code for security

app = Flask(__name__) #initiates the flask application __name__ tells the script how it is being used
app.secret_key = 'netneuronix_key'#secret key to ensure the session can not be faked 

# rtr creds
MIKROTIK_RTR_IP = "192.168.88.1" # saves the routers address into a variable for reference
RTR_USRNAME = "admin" #routers username
RTR_PW = "admin" #routers password

#these are used for the API connection as they are the routers credentials

def find_router_specs(): #begins a function that starts whenever the routers stats like cpu usage are being called
    stats = {"model": "MikroTik", "cpu": "0", "router_mac": "Unknown", "version": "N/A"} # creates a list of facts that we want from the router
    if not rtr_status_check(): return stats #checks if the router is online first if not create a blank list
    try: #try to do these steps if it fails dont crash the website
        connection = routeros_api.RouterOsApiPool(MIKROTIK_RTR_IP, username=RTR_USRNAME, password=RTR_PW, plaintext_login=True) #initiates a connection to the router using the predefined credentials
        api = connection.get_api() #opens the communication line so we can begin talking to the router
        resource = api.get_resource('/system/resource').get() # asks the router for its cpu load which is internal system information
        if resource:# if the router can senbd a reply
            stats["model"] = resource[0].get('board-name', 'MikroTik Device') # look at the resources and save it
            stats["cpu"] = resource[0].get('cpu-load', '0')
            stats["version"] = resource[0].get('version', 'N/A')



        interfaces = api.get_resource('/interface').get() #ask the router for all of its physical interfaces
        if interfaces: #if it sent back the list of interfaces
            stats["router_mac"] = interfaces[0].get('mac-address', 'Unknown') #take the data
        connection.disconnect() # disconnect
    except: pass #ignore any errors and move on 
    return stats #return the completed list of router stats

def find_client_information(PI_IP="192.168.88.252"): # start a function which that looks for the raspberry pi ip address
    info = {"mac": "Unknown", "hostname": "Searching..."} # servers as a blank list 
    if not rtr_status_check(): return info #checks if the router is online or not 
    try: #attempt these next steps
        connection = routeros_api.RouterOsApiPool(MIKROTIK_RTR_IP, username=RTR_USRNAME, password=RTR_PW, plaintext_login=True) #establish a connection with the router using the predefined variables 
        api = connection.get_api() #open the connection line 



        leases = api.get_resource('/ip/dhcp-server/lease').get(address=PI_IP)#look at the list of ips and get the target ip specified 
        if leases: #if the router found the ip address
            info["mac"] = leases[0].get('mac-address', 'N/A') #take the first address matched and save it
            info["hostname"] = leases[0].get('host-name', 'RaspberryPi-Node') #save the hostname and call it raspberry pi
        connection.disconnect() #end the connection with the router
    except: pass
    return info # return all of the info gathered 

def databse_create(): # makes a function which creates the database
    conn = sqlite3.connect('netneuronix.db') # open a file if it doesnt exist
    CRSR = conn.cursor() # creates a cursor which can be used  to select objects within the database
    CRSR.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')#tell the database if you dont have a folder called users make one with these parameters
    CRSR.execute('CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY, client_name TEXT, bandwidth INTEGER, queue_name TEXT, status TEXT)')#do the same but for the bandwidth requests instead 
    CRSR.execute("SELECT count(*) FROM users")#how many users are currently in the folder 
    if CRSR.fetchone()[0] == 0:# if the answer is zero it means the database is empty and brand new 
        CRSR.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', generate_password_hash('admin'), 'ADMIN')) #create an admin role with these credentials and put it into the users database table
        CRSR.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('client', generate_password_hash('client'), 'CLIENT'))#do the same for clients 
        conn.commit()#commit these new changes to the dtabase
    conn.close()#close changes

def open_database():# starts the function and opens the database
    conn = sqlite3.connect('netneuronix.db')# opens the database file
    conn.row_factory = sqlite3.Row #return data with labels like id username and admin 
    return conn #return this information

def rtr_status_check(ip=MIKROTIK_RTR_IP):# uses the routers ip as information and create a function to check availability
    try:# try these 
        s = socket.create_connection((ip, 8728), timeout=1) #tries to connect to the routers api waits a second and then decides whether its online or not
        s.close()
        return True #if online returns true
    except: return False #anything else is considered false

#routes for web pages

@app.route('/') #defines the main home of the html webpage 
def index(): #names the function of the home page
    if 'user' in session: return redirect(url_for('dashboard'))#if the user is recorded as being logged in and if they are send them to their respective dashboard
    return render_template('index.html')#return the home page if they arnt logged in 

@app.route('/login', methods=['POST']) #this site handles post requests is waiting for the user to click submit
def login(): # login function
    db = open_database()# fetches the database
    user = db.execute('SELECT * FROM users WHERE username = ?', (request.form['username'],)).fetchone() #go into the database and find the users folder and the person who has the username that was just typed in
    if user and check_password_hash(user['password'], request.form['password']):# if the user was found and it matches the password they typed in
        session['user'] = user['username']#site remembers their username 
        session['role'] = user['role']#site remembers their role 
        return redirect(url_for('dashboard'))#sends their respective dashboard to the now verified user
    flash("Invalid login!", "danger")#if the password was wrong flash invalid login banner
    return redirect(url_for('index'))#return the url for the login page again

@app.route('/dashboard')# follow this code when someone reaches the dashboard address
def dashboard():#function for dashboard
    if 'user' not in session: return redirect(url_for('index'))#if there is no name saved in memory back to login page
    db = open_database()# get database
    if session['role'] == 'ADMIN':# if the credentials matches the admin role
        all_reqs = db.execute('SELECT * FROM requests').fetchall()#if they are admin ask the database for all bandwidth plans 
        device_data = find_client_information()#run that function to find the mac address and hostname
        router_data = find_router_specs()#grab the mikrotiks statistics
        return render_template('isp.html', requests=all_reqs, health="Online" if rtr_status_check() else "OFFLINE", device=device_data, router=router_data)#send the admin to the isp.html page with the requested data so it can be displayed
    else:#if not an admin they are client
        my_plans = db.execute('SELECT * FROM requests WHERE client_name = ?', (session['user'],)).fetchall()# ask the database for the information that belongs to the client as they cant be anyone else
        return render_template('client.html', plans=my_plans)# return the client html page to the user

@app.route('/api/status')# this is background script for the cpu usage
def api_status():
    stats = find_router_specs()# get the router stats
    online = rtr_status_check()# check if its online
    return jsonify({"cpu": stats["cpu"], "health": "Online" if online else "OFFLINE"})# returns the routers data

@app.route('/add_new', methods=['POST']) # add a new bandwidth plan 
def add_new():# define the function for it 
    db = open_database() # open database
    db.execute('INSERT INTO requests (client_name, bandwidth, queue_name, status) VALUES (?, ?, ?, ?)',# create a new role in the requests folder. logs the username speed label and puts it as inactive
               (session['user'], request.form['bandwidth'], request.form['queue_name'], 'Inactive'))
    db.commit() # commit to the database
    return redirect(url_for('dashboard')) # refereshes the respective dashboard page 


@app.route('/rename/<int:id>', methods=['POST'])#background process for renaming the bandwidth plans 
def rename_plan(id):
    new_name = request.form['new_name']#this grabs the new name 
    db = open_database()#grabs the database
    # checks the client name to see if they actually exist within the datbase for security reasons 
    db.execute('UPDATE requests SET queue_name = ? WHERE id = ? AND client_name = ?', 
               (new_name, id, session['user']))# go to the requests folder find that specific plan and change its name 
    db.commit()#commit the new changes
    flash("Plan renamed successfully!", "success")#output communication banner for succesfully application
    return redirect(url_for('dashboard'))#referes the page again so the client can see the changes made

@app.route('/increase/<int:id>')
def increase_speed(id): # function for increasing an already existing speed plan 
    db = open_database()
    req = db.execute('SELECT * FROM requests WHERE id = ?', (id,)).fetchone()#find that specific plan within the database
    new_speed = int(req['bandwidth']) + 25#adds 25 to Mbps to the identified plan
    db.execute('UPDATE requests SET bandwidth = ?, status = "Pending" WHERE id = ?', (new_speed, id))#saves the new speed and chages the status to pending for verification via the admin page 
    db.commit()# commit new changes
    return redirect(url_for('dashboard'))

@app.route('/decrease/<int:id>')#same instance for increasing the plan but we take away 25 Mbps
def decrease_speed(id):
    db = open_database()
    req = db.execute('SELECT * FROM requests WHERE id = ?', (id,)).fetchone()
    new_speed = max(5, int(req['bandwidth']) - 25)
    db.execute('UPDATE requests SET bandwidth = ?, status = "Pending" WHERE id = ?', (new_speed, id))
    db.commit()
    return redirect(url_for('dashboard'))

@app.route('/switch/<int:id>')#listens for when a user wants to change their plan to an already existing one 
def switch_to(id):
    db = open_database()
    db.execute('UPDATE requests SET status = "Pending" WHERE id = ?', (id,))#marks it as pending for the admin
    db.commit()
    return redirect(url_for('dashboard'))#refreshes dashboard

@app.route('/approve/<int:id>')#approve policy for the admin page 
def approve(id):
    if not rtr_status_check():# if the router is not online
        flash("Router offline!", "danger")#display offline message
        return redirect(url_for('dashboard'))
    db = open_database()
    req = db.execute('SELECT * FROM requests WHERE id = ?', (id,)).fetchone()# gets the speed and name of the plan that the admin approved
    try:#begins a connection with the mikrotik 
        connection = routeros_api.RouterOsApiPool(MIKROTIK_RTR_IP, username=RTR_USRNAME, password=RTR_PW, plaintext_login=True)#initialises a connection
        api = connection.get_api()
        list_queues = api.get_resource('/queue/simple')#goes to the simple queues page in the router where they are kept
        existing = list_queues.get(target="192.168.88.252/32")# are there any queues active on the target
        for q in existing: list_queues.remove(id=q['id'])# for loop every old limit delete it we want the latest one approved active
        list_queues.add(name=req['queue_name'], target="192.168.88.252", max_limit=f"{req['bandwidth']}M/{req['bandwidth']}M")# creates the new bandwidth speed limit sets the namd and tells the router to limit the pi
        connection.disconnect()#end connection
        db.execute('UPDATE requests SET status = "Inactive" WHERE client_name = ?', (req['client_name'],))#mark all other plans as inactive
        db.execute('UPDATE requests SET status = "Active" WHERE id = ?', (id,))# change this specific plan to active
        db.commit()#commit the new status
        flash("Policy Successfully Deployed!", "success")#successful banner message 
    except Exception as e:#if anything went wrong show the error message on screen
        flash(f"Router Error: {str(e)}", "danger")# flash the error
    return redirect(url_for('dashboard'))#return to the respective dashboard

@app.route('/delete/<int:id>')# serves as the remove plan button.
def delete(id):
    db = open_database()
    db.execute('DELETE FROM requests WHERE id = ?', (id,))# grabs the identified id and deltes it from the database
    db.commit()#commit the new changes and status
    return redirect(url_for('dashboard'))#refresh page

@app.route('/logout')# logs the user out 
def logout():
    session.clear()
    return redirect(url_for('index'))#return to home page

if __name__ == '__main__':#if the running file is equal to main host the program
    databse_create()# runs the database and app
    app.run(debug=True, host='127.0.0.1', port=5000)# this begins self hosting the flask login page 