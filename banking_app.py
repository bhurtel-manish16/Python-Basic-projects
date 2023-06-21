#Welcome to login system
import mysql.connector as msc
from cryptography.fernet import Fernet as fnet
from datetime import datetime
import random
import pyqrcode
from fpdf import FPDF

"""
For this project please install xampp ( https://www.apachefriends.org/ ) for the database.
Along with this, install libraries mysql, pycode, cryptography and pdf using pip
"""
mydb = msc.connect(
	host = "localhost",
	user = "root",
	password = "",
	database = "userdata"
	)

con = mydb.cursor()


#Database created
con.execute("CREATE DATABASE userdata")

#Creating table
con.execute("CREATE TABLE login_data(Name VARCHAR(250), Email VARCHAR(250), Password VARCHAR(250))")

def get_user_choice():
	print("-----------------------------------------")
	print("\t Welcome to Bhurtel bank")
	print("-----------------------------------------")
	print("Press 1 to create account: ")
	print("Press 2 to login into system: ")
	choice = int(input("Do you want to login or create your account"))
	if choice == 1:
		create_user()
	elif choice == 2:
		login_user()

def create_user():
	print("-----------------------------------------")
	print("\t New account opening")
	print("-----------------------------------------")
	#Getting data and encryptinh it
	name = input("Enter your name: ")
	email = input("Enter your email: ")
	password = bytes(input("Enter password: "), 'utf-8')
	key = (fnet.generate_key())
	crypter = fnet(key)
	pw = crypter.encrypt(password)
	
	#Inserting data to databse
	insert_key = "INSERT INTO pass_key (Pwkey) VALUES(%s)"
	dta = (key,)
	con.execute(insert_key,dta)
	mydb.commit()

	sql_data = "INSERT INTO login_data (Name, Email, Password) VALUES(%s, %s, %s)"
	data = (name,email,pw,)
	con.execute(sql_data,data)
	mydb.commit()

	add_new_costumer()

	choice = input("Do you want to login? y/n")
	if choice.upper == "Y":
		login_user()
	else:
		exit()

def login_user():
	print("-----------------------------------------")
	print("\t Login to proceed")
	print("-----------------------------------------")
	try:
		name = input("Enter your name: ")
		password = input("Enter password: ")

		#Getting user_id and passwordr
		sl_cal = ("SELECT * FROM login_data WHERE Name = %s")
		val = (name,)
		con.execute(sl_cal,val)
		for x in con:
			x = x
		id_num = int(x[3])
		pwd = bytes(x[2], 'utf-8')

		#Extracting id
		sql_key = ("SELECT Pwkey FROM pass_key WHERE id = %s")
		val_id = (id_num, )
		con.execute(sql_key,val_id)
		for x in con:
			x = x
		key = bytes(x[0], 'utf-8')

		#decrypt password and verifyying 
		crypter = fnet(key)
		dec = crypter.decrypt(pwd)
		if (str(dec, 'utf-8') == password):
			show_details(name,id_num)
		else:
			print("Wrong password\nmn")
			print("\n")
			print("Do you want to change your password? (Y/N)")
			reser_pass = input()
			if reser_pass.upper() == "Y":
				reset_pass(id_num)
			get_user_choice()
	except (UnboundLocalError):
		print("\nYou don't have an account with the name "+name)
		user_choice = input("Would you like to open new accounr? (Y/N)")
		if user_choice.upper() == "Y":
			create_user()


def reset_pass(id_num):
	sl_cal = ("SELECT Name FROM login_data WHERE id = %s")
	send_query = (id_num, )
	con.execute(sl_cal,send_query)
	for user_name in con:
		user_name = user_name
	print("Hello "+user_name[0])
	check_user = input("Is thsi you? ")
	if check_user.upper() == "Y":
		password = bytes(input("Enter new password: "), 'utf-8')
		key = (fnet.generate_key())
		crypter = fnet(key)
		pw = crypter.encrypt(password)
		#reset password in loogin_data table
		reset_querry = ("UPDATE login_data SET Password = %s WHERE id = %s")
		reset_data = (pw,id_num,)
		con.execute(reset_querry,reset_data)
		mydb.commit()

		#reset keys in pass_keys table
		reset_querry = ("UPDATE pass_key SET Pwkey = %s WHERE id = %s")
		reset_data = (key, id_num)
		con.execute(reset_querry, reset_data, )
		mydb.commit()

		print("Password changed successfully")
	else:
		login_user()


def show_details(name,id_num):
	now = datetime.now()
	date = now.strftime("%d/%m/%Y")
	print("\t\t\t\t---------------------")
	print("\t\t\t\tWelcome back ",name)
	print("\t\t\t\t    ",date)
	print("\t\t\t\t---------------------\n")

	fetch_data = "SELECT current_balance, interest_rate, interest_balance, acc_num FROM acc_details WHERE id = %s"
	id_val = (id_num, )
	con.execute(fetch_data,id_val)
	for i in con:
		i = i
	print("\t\t Account Number:   ",i[3])
	print('\t\t Current Balance:  ',"NPR",i[0])
	print("\t\t Interest Rate:    ",i[1])
	print("\t\t Interest Balance: ","NPR",i[2])
	print("\n")
	more_trac = input("Perform operation? (Y/N)")
	if more_trac.upper() == "Y":
		print("Press 1 to withdraw fund: ")
		print("Press 2 to deposit fund: ")
		print("Press 3 to view statement: ")
		print("Press 4 to share your details in qr code: ")
		print("Press 5 to close your account: ")
		
		transcation = int(input())
		if transcation == 1:
			withdraw(i[0], id_num)
		elif transcation == 2:
			deposit(i[0], id_num)
		elif transcation == 3:
			view_statement(i[3])
		elif transcation == 4:
			share_acc(name, i[3])
		elif transcation == 5:
			pass
			delete_acc(name, id_num,i[3])
		else:
			print("Invalid choice, please enter valid (w/d)")

def add_new_costumer():
	acc_num = "1104"
	gen_random = str(random.randint(100000000,900000000000))
	for i in gen_random:
		if len(acc_num) < 12:
			acc_num += i
	print(acc_num)
	
	add_acc = "INSERT INTO acc_details (current_balance, interest_rate, interest_balance, acc_num) VALUES(%s,%s,%s,%s)"
	acc_data = ("100","10%","1.2",acc_num)
	con.execute(add_acc, acc_data)
	mydb.commit()


def withdraw(amt,id_num):
	amount = int(input("Enter the fund you want to widthdraw: "))
	if amount > int(amt):
		print("Insufficient balance")
	else:
		new_balance = (int(amt) - amount)
		update = "UPDATE acc_details SET current_balance = %s WHERE id = %s"
		amt = (new_balance,id_num,  )
		con.execute(update,amt)
		mydb.commit()

		amount = "-"+str(amount)
		acc_num = trial(id_num)
		now = datetime.now()
		date = now.strftime("%d/%m/%Y")
		time = now.strftime("%H:%M:%S")
		statement_sql = "INSERT INTO statement (Transaction_amount, Transaction_date, Transaction_time, account_number) VALUES(%s,%s,%s,%s)"
		statement_data = (amount,date,time,acc_num,)
		con.execute(statement_sql,statement_data)
		mydb.commit()
		print("widthdrawn successfully!")

def deposit(amt,id_num):
	amount = int(input("Enter the fund to deposit: "))
	new_balance = (int(amt) + amount)
	update = "UPDATE acc_details SET current_balance = %s WHERE id = %s"
	amt = (new_balance,id_num,  )
	con.execute(update,amt)
	mydb.commit()
	print("Deposited successfully!")

	deposit_amount = "+"+str(amount)
	acc_num = trial(id_num)
	now = datetime.now()
	date = now.strftime("%d/%M/%Y")
	time = now.strftime("%H/%M/%S")
	statement_sql = "INSERT INTO statement (Transaction_amount, Transaction_date, Transaction_time, account_number) VALUES(%s,%s,%s,%s)"
	statement_data = (deposit_amount,date,time,acc_num,)
	con.execute(statement_sql,statement_data)
	mydb.commit()

def trial(id_num):
	insert_sql = ("SELECT acc_num FROM acc_details WHERE id = %s")
	id_val = (id_num, )
	con.execute(insert_sql,id_val)
	for i in con:
		return i[0]

def view_statement(id_num):
	try:
		get_statement = "SELECT * FROM statement where account_number = %s"
		statement_val = (id_num, )
		con.execute(get_statement,statement_val)
		val = []
		for j in con:
			val.append(j) 

		#design
		print("\t\t\t-----------------------------")
		print("\t\t\t\tAccount Number")
		print("\t\t\t\t"+val[0][3])
		print("\t\t\t-----------------------------")
		print("\n")
		print("\t\tAmount\t\tTnasaction date\t\tTransaction time")
		print("\t\t---------------------------------------------------------")

		remaing_amount = 0
		#diisplaying transaction history
		for i in range(len(val)):
			for j in range(0,1):
				print("\t\t"+val[i][0]+"\t\t"+val[i][1]+"\t\t"+val[i][2])
				# print('\t'+val[i][1])
				# print("\t"+val[i][2])
				remaing_amount += int(val[i][0])
				print("\n")
				# print(val[i])
		print("------------------------")
		print("Remaning fund"+"\t"+str(remaing_amount))
		print("------------------------")

		now = datetime.now()
		date = now.strftime("%d/%M/%Y")
		time = now.strftime("%H/%M/%S")
		current_date = ""
		current_time = ""
		for dt in date:
			dt = dt.replace("/","_")
			current_date += dt
		for tm in time:
			tm = tm.replace("/","_")
			current_time += tm

		download_statement = input("Do you want to downlaod statement? ")
		if download_statement.upper() == "Y":	
			with open(val[0][3]+"_"+current_date+"_"+current_time+".txt","w") as s:
				s.write("\t\t\t-----------------------\n")
				s.write("\t\t\t\tAccount Number\n")
				s.write("\t\t\t\t"+val[0][3])
				s.write("\n\t\t\t----------------------\n\n")
				s.write("\t\tAmount   Tnasaction date   Transaction time")
				s.write("\n\t\t--------------------------------------------------\n")
				for i in range(len(val)):
					for j in range(0,1):
						s.write("\t\t"+val[i][0]+"\t\t\t"+val[i][1]+"\t\t\t"+val[i][2])
						s.write("\n")
				s.write("------------------------\n")
				s.write("Remaning fund"+"   "+str(remaing_amount))
				s.write("\n------------------------")
			get_pdf = input("Do you want pdf file? ")
			if get_pdf.upper() == "Y":
				create_pdf(val[0][3],current_date,current_time)


	except IndexError:
		print("Cannot find statement")

def create_pdf(acc_num,current_date,current_time):
	pdf = FPDF()  
  
	# Add a page
	pdf.add_page()
	  
	# set style and size of font
	# that you want in the pdf
	pdf.set_font("Arial", size = 15)

	 
	# open the text file in read mode
	f = open(acc_num+"_"+current_date+"_"+current_time+".txt", "r")
	 
	# insert the texts in pdf
	for x in f:
	    pdf.cell(200, 10, txt = x, ln = 1, align = 'L')
	  
	# save the pdf with name .pdf
	pdf.output("mygfg.pdf")  

def share_acc(name, acc_num):
	data = str(name)+" "+str(acc_num)
	print(data)
	qr = pyqrcode.create(data)
	qr.png("share.png", scale=8)

def delete_acc(name, id_num,acc_num):
	user_choice = input("Are you sure you want to close you account? ")
	if user_choice.upper() == "Y":
		delete_query = ("DELETE FROM acc_details WHERE id = %s")
		delete_data = (id_num,)
		con.execute(delete_query,delete_data)
		mydb.commit()

		delete_query = ("DELETE FROM login_data WHERE Name = %s")
		delete_data = (name,)
		con.execute(delete_query,delete_data)
		mydb.commit()

		delete_query = ("DELETE FROM pass_key WHERE id = %s")
		delete_data = (id_num,)
		con.execute(delete_query,delete_data)
		mydb.commit()

		delete_query = ("DELETE FROM statement WHERE account_number = %s")
		delete_data = (acc_num,)
		con.execute(delete_query,delete_data)
		mydb.commit()

		print("successfully")

get_user_choice()
