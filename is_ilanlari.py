from selenium import webdriver
from bs4 import BeautifulSoup
import sqlite3
import time

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import os


EMAIL = ""
PASSWORD = ""


def mainPage():
    links = []
    id_s = []
    
    browser = webdriver.Chrome(os.getcwd() + "\\chromedriver.exe")
    browser.get("https://www.kariyer.net/is-ilanlari/#&kw=siber%20güvenlik")
                
    browser.refresh()
    
    
    soup = BeautifulSoup(browser.page_source, "html.parser")
    
    for result in soup.find_all("a", class_ = "link position", href=True):
        id_s.append(int(result['data-id']))
        links.append(( result['href'], int(result['data-id']) )) #tuple list
    
    
    return browser, id_s, links


def initial_DB(id_s):
    with sqlite3.connect("jobs.sqlite") as vt:
        im = vt.cursor()
        im.execute("""CREATE TABLE IF NOT EXISTS all_id (id_s INT)""")
        
        for each in id_s:
            im.execute("""INSERT INTO all_id VALUES (?)""", [each])
            vt.commit()

    

def jobsControl(browser, id_s):
    id_db = []
    new_jobs_id = []
    
    # Check all id
    with sqlite3.connect("jobs.sqlite") as vt:
        im = vt.cursor()    
        im.execute("""SELECT * FROM all_id""")

        for each in im:
            id_db.append(each[0])
        
    
    for each in id_s:
        if each not in id_db:
            new_jobs_id.append(each)
    
    
    # Insert new id
    with sqlite3.connect("jobs.sqlite") as vt:
        im = vt.cursor()
            
        for each in new_jobs_id:
            im.execute("""INSERT INTO all_id VALUES (?)""", [each])
            vt.commit()
    
    
    return new_jobs_id
                

def getJobs(browser, links, id_s, new_jobs_id):
    jobResults = []
    href = ""
    
    for each in new_jobs_id:
   
        for i in links:
            if each == i[1]:
                href = i[0]
        
        browser.get("https://www.kariyer.net" + href)
        soup = BeautifulSoup(browser.page_source, "html.parser")
        
        jobTitle = soup.find("a", class_ = "link position").text
        jobCompany = soup.find("a", class_ = "link company").text
        jobCity = soup.find("span", class_ = "city").text
        jobBody = soup.find("div", class_ = "genel-nitelikler").text
        
        jobResults.append("{} \n{} \n{} \n{} \n\n{}".format(jobTitle, jobCompany, jobCity, 
                          jobBody, "https://www.kariyer.net" + href))
    
        time.sleep(3)
    
    i = 0
    for each in jobResults:  # düzenleme
        jobResults[i] = each.replace("·\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0", "\n ·")
        
        
    return jobResults
        


def getEmails():
    emails = []
    
    with sqlite3.connect("jobs.sqlite") as vt:
        im = vt.cursor()
        im.execute("""SELECT * FROM users""")
        
        for each in im:
            emails.append(each[0]) #tuple'ın içinde geldiği için 0'ı aldık.
    
    
    return emails
 

def sendMail(body, To):
    message = MIMEMultipart()
    
    message['From'] = EMAIL 
    message['To'] = To
    message['Subject'] = "IUCYBER | Yeni İş İlanı"
    
    body_text = MIMEText(body, 'plain')
    
    message.attach(body_text)
    
    #Gmail serverlerine bağlanma işlemi.
    try:
        mail = smtplib.SMTP("smtp.gmail.com",587)  

        mail.ehlo()

        mail.starttls()    

        mail.login(EMAIL, PASSWORD)

        mail.sendmail(message["From"],message["To"],message.as_string())

        print("Mail Başarılı bir şekilde gönderildi.")

        mail.close()
    
    #Eğer mesaj gönderirken hata ile karşılaşırsak except çalışır.
    except:
        sys.stderr.write("Bir hata oluştu. Tekrar deneyin...")
        sys.stderr.flush()
    
    
    


browser, id_s, links = mainPage()
#initial_DB(id_s)  # If the program is run first time, this func is run.


new_jobs_id = jobsControl(browser, id_s)

if(len(new_jobs_id) != 0):
    jobResults = getJobs(browser, links, id_s, new_jobs_id)
    
    emails = getEmails()
    
    for each in jobResults:
        for account in emails:
            sendMail(each, account)














