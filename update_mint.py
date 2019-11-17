from fuzzywuzzy import process
import requests

cookies = { ... } ###CHANGEME

headers = {
    'Host': 'mint.intuit.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://mint.intuit.com/transaction.event',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'ADRUM': 'isAjax:true',
    'Connection': 'keep-alive',
}

data = {
    ########CHANGE THIS########
    ####You need to capture a request to /updateTransaction.xevent and populate this with the data.  The code below assumes that data is a dictionary where each param is a key-value pairing.  Requests such as data["merchant"] need to work.
}

categories = {  #These categories obtained by a request to https://mint.intuit.com/app/getJsonData.xevent?task=categories&rnd=1574015986589
'Auto Insurance': '1405',
'Auto Payment': '1404',
'Gas & Fuel': '1401',
'Parking': '1402',
'Public Transportation': '1406',
'Service & Parts': '1403',
'Home Phone': '1302',
'Internet': '1303',
'Mobile Phone': '1304',
'Television': '1301',
'Utilities': '1306',
'Web Hosting': '1491838',
'Advertising': '1701',
'Legal': '1705',
'Office Supplies': '1702',
'Printing': '1703',
'Shipping': '1704',
'Books & Supplies': '1003',
'Student Loan': '1002',
'Tuition': '1001',
'Amusement': '102',
'Arts': '101',
'Movies & DVDs': '104',
'Music': '103',
'Newspapers & Magazines': '105',
'ATM Fee': '1605',
'Bank Fee': '1606',
'Finance Charge': '1604',
'Late Fee': '1602',
'Service Fee': '1601',
'Trade Commissions': '1607',
'Financial Advisor': '1105',
'Life Insurance': '1102',
'Alcohol & Bars': '708',
'Coffee Shops': '704',
'Fast Food': '706',
'Groceries': '701',
'Restaurants': '707',
'Charity': '802',
'Gift': '801',
'Dentist': '501',
'Doctor': '502',
'Eyecare': '503',
'Gym': '507',
'Health Insurance': '506',
'Pharmacy': '505',
'Sports': '508',
'Furnishings': '1201',
'Home Improvement': '1203',
'Home Insurance': '1206',
'Home Services': '1204',
'Home Supplies': '1208',
'Lawn & Garden': '1202',
'Mortgage & Rent': '1207',
'Bonus': '3004',
'Drill Paycheck': '1491841',
'Interest Income': '3005',
'Paycheck': '3001',
'Reimbursement': '3006',
'Rental Income': '3007',
'Returned Purchase': '3003',
'Allowance': '610',
'Baby Supplies': '611',
'Babysitter & Daycare': '602',
'Child Support': '603',
'Kids Activities': '609',
'Toys': '606',
'Loan Fees and Charges': '6005',
'Loan Insurance': '6002',
'Loan Interest': '6004',
'Loan Payment': '6001',
'Loan Principal': '6003',
'Hair': '403',
'Laundry': '406',
'Spa & Massage': '404',
'Pet Food & Supplies': '901',
'Pet Grooming': '902',
'Veterinary': '903',
'Books': '202',
'Clothing': '201',
'Electronics & Software': '204',
'Hobbies': '206',
'Sporting Goods': '207',
'Federal Tax': '1901',
'Local Tax': '1903',
'Property Tax': '1905',
'Sales Tax': '1904',
'State Tax': '1902',
'Credit Card Payment': '2101',
'Transfer for Cash Spending': '2102',
'Air Travel': '1501',
'Hotel': '1502',
'Rental Car & Taxi': '1503',
'Vacation': '1504',
'Cash & ATM': '2001',
'Check': '2002'
}

category_keys = categories.keys() #Save the keys so we can reference with fuzzywuzzy

#here is a chunk of my bank transactions (modified for privacy, obviously).  This was originally a csv file, however I changed all the comma deliminations to \ (I dont remember why, sorry)
#of this data that my bank exported, all I really care about is the date, merchant, category, and amount
'''
posted\\8/16/2019\\WF HOME MTG      AUTO PAY   ***********1234\Mortgages\-997.92
posted\\8/16/2019\\WF Insurance     AUTOPAY    ***********1234\Insurance\-61.53
posted\\8/16/2019\\VA ABC STORE 063         FAYETTEVILLE       NC\Groceries\-44.49
posted\\8/16/2019\\GIANT FOOD INC   FAIRFAX     VA\Groceries\-26.48
posted\\8/16/2019\\BUFFALO WILD WINGS  FAIRFAX     VA\Restaurants/Dining\-19.08
posted\\8/16/2019\\GIANT FOOD INC  FAIRFAX     VA\Groceries\-14.77
posted\\8/16/2019\\PANERA BREAD\Restaurants/Dining\-8.64
'''
filepath = 'C:\\Users\\Username\\Downloads\\bank_transaction_data.csv' #This is the file of bank transaction data.  My code assumes it is formated like the above
count = 0
with open(filepath) as fp:
    line = fp.readline()
    cnt = 1
    while line:
        #print line
        date = line.split("\\")[2] #NOTE This assumes your bank file is formatted as I have above.  Change if otherwise!!
        merchant = line.split("\\")[4]
        category = line.split("\\")[5]
        amount = line.split("\\")[6]
        #print date
        #print merchant
        #print category
        #print amount
        data["date"] = date
        data["merchant"] = merchant
        data["category"] = category
        data["amount"] = amount
        if "-" in amount: #mint tracks "deposits/withdraws" via the mtIsExpense value.  Remove the negative and change mtIsExpense to true
            amount = amount.strip("-")
            data["mtIsExpense"] = True
        else:
            data["mtIsExpense"] = False
        #This is from https://www.datacamp.com/community/tutorials/fuzzy-string-python
        highest = process.extractOne(data["category"], category_keys) #I am comparing the current bank category against the list of Mint categories
        if highest[1] > 70: #percentage of certanty.  If there is a > 70% certainty between the bank's category description and mint's category description, then change the category to mint's category description
            #print data["category"] + " -> " + str(highest)
            data["category"] = highest[0]
            data["catId"] = categories[highest[0]] #update the category ID with the appropriate value, so the category actually changes in mint
            count = count + 1 #tracking for debug reasons.  
        
        response = requests.post('https://mint.intuit.com/updateTransaction.xevent', headers=headers, cookies=cookies, data=data)
        print "Inserting " + line + "-----> " + str(response)
        line = fp.readline()
        cnt += 1


