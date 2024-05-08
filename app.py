from flask import Flask, render_template, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
import time
from PyPDF2 import PdfReader
import google.generativeai as genai

app = Flask(__name__)
genai.configure()


def configure_api_key(api_key):
  if not api_key:
    raise ValueError("Please provide your Gemini API key. Do not embed it in code!")
  genai.configure(api_key=api_key)

# Replace with your actual Gemini API key (not within the code)
your_gemini_api_key = "AIzaSyC3aNlBGGmJqasAgBDEWXNe4aZgj4KyDCA"  # Keep this secret

try:
  # Configure the API using the function (avoid embedding key directly)
  configure_api_key(your_gemini_api_key)
except ValueError as e:
  print(f"Error: {e}")
  exit(1)

model = genai.GenerativeModel('gemini-1.0-pro')



@app.route('/')
def index():
    return render_template('index.html')
@app.route('/resume')
def resume():
    return render_template('resume.html')
@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        
        file = request.files['file']
        
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        
        # If the file is a PDF
        if file and file.filename.endswith('.pdf'):
            pdf_content = read_pdf(file)
            pdf_content = model.generate_content("This is my resume: \n"+ pdf_content +"\n Guess what job I am looking for (The response should be direct without any explanation or detail).")
            pdf_content = pdf_content.text
            
            about_me = model.generate_content('This is my resume: \n'+pdf_content+'/n give me a summary about me according to the details mentioned in my resume (like the skills, education etc.). Also make sure to not add any heading or title like short description, additionally dont mention about the experince because some resume doesnt reflect according to the experience. I just need the response to be direct.')
            about_me = about_me.text
            
            advice = model.generate_content('This is my resume: \n'+pdf_content+'/n Give me career advice to be the best in my career. Also make sure to not add any heading or title like short description, additionally dont mention about the experince because some resume doesnt reflect according to the experience. I just need the response to be direct.')
            advice = advice.text
            advice = advice.replace('**', 'TEMP_PLACEHOLDER')
            advice = advice.replace('*', '\n')
            advice = advice.replace('TEMP_PLACEHOLDER', '')
            
            job = pdf_content
            location = request.form['location']
            exp = request.form['exp']
            worktype = request.form['worktype']
            experience = request.form['experience']
            cont = request.form['cont']
            
        
            linkedin_links = []
            indeed_links = []
            foundit_links = []
            naukri_links = []
            glassdoor_links = []
            shine_links = []
            TIMES_links = []
        
            cache_key = f"{job}_{location}_{exp}_{worktype}_{experience}_{cont}"
            if cache_key in cache and is_cache_valid(cache_key, cache[cache_key]['timestamp']):
    
                return render_template('result.html', **cache[cache_key])
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            
            #LINKEDIN
            driver.get('https://www.linkedin.com/jobs/search/?f_AL=true&f_E='+exp+'&f_WT='+worktype+'&keywords='+job+'&location='+location+'&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true&sortBy=R')
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            try:
                ul_element = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[2]/ul')
                a_tags = ul_element.find_elements(By.TAG_NAME, 'a')
                for a_tag in a_tags:
                    href = a_tag.get_attribute('href')
                    if href is not None and href.startswith('https://in.linkedin.com/jobs/view/'):
                        linkedin_links.append(href)
                driver.quit()
            except NoSuchElementException:
                pass
            
            #INDEED
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            if cont == 'India':
                if worktype == '1':    
                    if exp == '2' or exp == '3':
                        driver.get('https://in.indeed.com/jobs?q='+job+'&l=india&sc=0kf%3Ajt%28new_grad%29%3B&vjk=d6c8d73fdf09d1c2')
                    elif exp == '4':
                        driver.get('https://in.indeed.com/jobs?q=MID_LEVEL+'+job+'&l=india&from=searchOnDesktopSerp&vjk=73ad0b80bd34783f')
                    else:
                        driver.get('https://in.indeed.com/jobs?q=SENIOR_LEVEL+'+job+'&l=india&from=searchOnDesktopSerp&vjk=cf3aaad012121320')
                elif worktype == '2':
                    if exp == '2' or exp == '3':
                        driver.get('https://in.indeed.com/jobs?q='+job+'&l=india&sc=0kf%3Aattr%28DSQF7%29jt%28new_grad%29%3B&vjk=d6c8d73fdf09d1c2')
                    elif exp == '4':
                        driver.get('https://in.indeed.com/jobs?q=MID_LEVEL+'+job+'&l=india&sc=0kf%3Aattr%28DSQF7%29%3B&vjk=73ad0b80bd34783f')
                    else:
                        driver.get('https://in.indeed.com/jobs?q=SENIOR_LEVEL+'+job+'&l=india&sc=0kf%3Aattr%28DSQF7%29%3B&vjk=cf3aaad012121320')
                else:
                    if exp == '2' or exp == '3':
                        driver.get('https://in.indeed.com/jobs?q=Entry+Level+'+job+'&l=india&sc=0kf%3Aattr%28PAXZC%29%3B&vjk=6af2d42b35f771d1')
                    elif exp == '4':
                        driver.get('https://in.indeed.com/jobs?q=MID+Level+'+job+'&l=india&sc=0kf%3Aattr%28PAXZC%29%3B&vjk=6af2d42b35f771d1')
                    else:
                        driver.get('https://in.indeed.com/jobs?q=SENIOR+Level+'+job+'&l=india&sc=0kf%3Aattr%28PAXZC%29%3B&vjk=6af2d42b35f771d1')
            
            else:
                if worktype == '1':    
                    if exp == '2' or exp == '3':
                        driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aexplvl%28ENTRY_LEVEL%29%3B&vjk=d594e92e41587b3d')
                    elif exp == '4':
                        driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aexplvl%28MID_LEVEL%29%3B&vjk=80d8f8205c53b671')
                    else:
                        driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aexplvl%28SENIOR_LEVEL%29%3B&vjk=2023c13cd2477e44')
                elif worktype == '2':
                    if exp == '2' or exp == '3':
                        driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aattr%28DSQF7%29explvl%28ENTRY_LEVEL%29%3B&vjk=9eac3c1dd4df9074')
                    elif exp == '4':
                        driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aattr%28DSQF7%29explvl%28MID_LEVEL%29%3B&vjk=80d8f8205c53b671')
                    else:
                        driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aattr%28DSQF7%29explvl%28SENIOR_LEVEL%29%3B&vjk=72345ca4b4a0a23f')
                else:
                    if exp == '2' or exp == '3':
                        driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aattr%28PAXZC%29explvl%28ENTRY_LEVEL%29%3B&vjk=d27890f0e3805994')
                    elif exp == '4':
                        driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aattr%28PAXZC%29explvl%28MID_LEVEL%29%3B&vjk=2187dd820a19aebf')
                    else:
                        driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aattr%28PAXZC%29explvl%28SENIOR_LEVEL%29%3B&vjk=72345ca4b4a0a23f')
            
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            # Find all 'a' tags dynamically
            li_index = 1
            while True:
                try:
                    a_tag = driver.find_element(By.XPATH, f'/html/body/main/div/div[2]/div/div[5]/div/div[1]/div[5]/div/ul/li[{li_index}]/div/div/div/div/div/table/tbody/tr/td[1]/div[1]/h2/a')
                    indeed_links.append(a_tag.get_attribute('href'))
                    li_index += 1
                except NoSuchElementException:
                    break
    
        # Close the driver
            driver.quit()
            
            # FOUND IT
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            if cont == 'India':
                driver.get('https://www.foundit.in/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) 
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
                for job_element in job_elements:
                    job_title = job_element.text
                    if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS', 'ROLES']:
                        foundit_links.append('https://www.foundit.in/srp/results?query=' + job_title + '&locations=' + location + '&experienceRanges=' + experience + '%7E' + experience + '&experience=' + experience)
    
                # Close the driver
                driver.quit()
            elif cont == 'Gulf':
                driver.get('https://www.founditgulf.com/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) 
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
                for job_element in job_elements:
                    job_title = job_element.text
                    if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                        foundit_links.append('https://www.founditgulf.com/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
    
                # Close the driver
                driver.quit()
            elif cont == 'HongKong':
                driver.get('https://www.foundit.hk/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) 
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
                for job_element in job_elements:
                    job_title = job_element.text
                    if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                        foundit_links.append('https://www.foundit.hk/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
    
                # Close the driver
                driver.quit()
            elif cont == 'Singapore':
                driver.get('https://www.foundit.sg/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) 
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
                for job_element in job_elements:
                    job_title = job_element.text
                    if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                        foundit_links.append('https://www.foundit.sg/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
    
                # Close the driver
                driver.quit()
            elif cont == 'Philippines':
                driver.get('https://www.foundit.com.ph/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) 
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
                for job_element in job_elements:
                    job_title = job_element.text
                    if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                        foundit_links.append('https://www.foundit.com.ph/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
    
                # Close the driver
                driver.quit()
            elif cont == 'Thailand':
                driver.get('https://www.monster.co.th/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) 
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
                for job_element in job_elements:
                    job_title = job_element.text
                    if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                        foundit_links.append('https://www.monster.co.th/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)

                # Close the driver
                driver.quit()
            elif cont == 'Malaysia':
                driver.get('https://www.foundit.my/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) 
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
                for job_element in job_elements:
                    job_title = job_element.text
                    if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                        foundit_links.append('https://www.foundit.my/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
                # Close the driver
                driver.quit()
            elif cont == 'Indonesia':
                driver.get('https://www.foundit.id/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) 
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
                for job_element in job_elements:
                    job_title = job_element.text
                    if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                        foundit_links.append('https://www.foundit.id/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
    
                # Close the driver
                driver.quit()
            elif cont == 'Vietnam':
                driver.get('https://www.monster.com.vn/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) 
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
                for job_element in job_elements:
                    job_title = job_element.text
                    if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                        foundit_links.append('https://www.monster.com.vn/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
    
                # Close the driver
                driver.quit()
            else:
                pass
       
            # NAUKRI
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            if cont == 'India':
                if worktype == '1':
                    driver.get('https://www.naukri.com/'+job+'-jobs-in-'+location+'?k='+job+'&l='+location+'&experience='+experience+'&wfhType=0')
                elif worktype == '2':
                    driver.get('https://www.naukri.com/'+job+'-jobs-in-'+location+'?k='+job+'&l='+location+'&experience='+experience+'&wfhType=2')
                else:
                    driver.get('https://www.naukri.com/'+job+'-jobs-in-'+location+'?k='+job+'&l='+location+'&experience='+experience+'&wfhType=3')
                
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) 
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
    
                # Find all <a> tags within the parent div and its descendants
                a_tags = driver.find_elements(By.XPATH, './/a')    
                # Extract href attributes from the <a> tags and store them in href_links
                for a_tag in a_tags:
                    href = a_tag.get_attribute('href')
                    if href is not None and href.startswith('https://www.naukri.com/job-listings-'):
                        naukri_links.append(href)
                        
                
                driver.quit()
            else:
                pass
            
            # Glass Door
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            if worktype == '1':    
                if exp == '2' or exp == '3':
                    driver.get('https://www.glassdoor.co.in/Job/'+location+'-'+job+'-jobs-SRCH_IL.0,6_IS4942_KO7,13.htm?seniorityType=entrylevel')
                elif exp == '4':
                    driver.get('https://www.glassdoor.co.in/Job/'+location+'-'+job+'-jobs-SRCH_IL.0,6_IS4942_KO7,13.htm?seniorityType=midseniorlevel')
                else:
                    pass
            else:
                if exp == '2' or exp == '3':
                    driver.get('https://www.glassdoor.co.in/Job/'+location+'-'+job+'-jobs-SRCH_IL.0,6_IS4942_KO7,13.htm?seniorityType=entrylevel&remoteWorkType=1')
                elif exp == '4':
                    driver.get('https://www.glassdoor.co.in/Job/'+location+'-'+job+'-jobs-SRCH_IL.0,6_IS4942_KO7,13.htm?seniorityType=midseniorlevel&remoteWorkType=1')
                else:
                    pass
                
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            a_tags = driver.find_elements(By.XPATH, './/a')    
            # Extract href attributes from the <a> tags and store them in href_links
            for a_tag in a_tags:
                href = a_tag.get_attribute('href')
                if href is not None and href.startswith('https://www.glassdoor.co.in/job-listing/'):
                    glassdoor_links.append(href)
    
            # Close the driver
            driver.quit()
    
            #SHINE
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            if cont == 'India':
                if worktype == '1':
                    if exp == '2':
                        driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=1')
                    elif exp == '3':
                        driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=2')
                    elif exp == '4':
                        driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=4')
                    else:
                        driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=5')
                    
                else:
                    if exp == '2':
                        driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=1&emp_type=4')
                    elif exp == '3':
                        driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=2&emp_type=4')
                    elif exp == '4':
                        driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=4&emp_type=4')
                    else:
                        driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=5&emp_type=4')
                
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) 
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
    
                # Find all 'a' tags dynamically
                li_index = 1
                while True:
                    try:
                        a_tag = driver.find_element(By.XPATH, f'//*[@id="1"]/div[{li_index}]/div[1]/div[1]/meta[1]')
                        shine_links.append(a_tag.get_attribute('content'))
                        li_index += 1
                    except NoSuchElementException:
                        break
                        
                
                driver.quit()
            else:
                pass
            
            #TIMES
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            if exp == '2':
                driver.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords='+job+'&txtLocation='+location+'&cboWorkExp1=0')
            elif exp == '3':
                driver.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords='+job+'&txtLocation='+location+'&cboWorkExp1=1')
            elif exp == '4':
                driver.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords='+job+'&txtLocation='+location+'&cboWorkExp1=3')
            elif exp == '5':
                driver.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords='+job+'&txtLocation='+location+'&cboWorkExp1=4')
            else:
                driver.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords='+job+'&txtLocation='+location+'&cboWorkExp1=5')
            
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            a_tags = driver.find_elements(By.XPATH, './/a')    
            # Extract href attributes from the <a> tags and store them in href_links
            for a_tag in a_tags:
                href = a_tag.get_attribute('href')
                if href is not None and href.startswith('https://www.timesjobs.com/job-detail/'):
                    TIMES_links.append(href)
        
        
            driver.quit()
        
            foundit_links = set(foundit_links)
            TIMES_links = set(TIMES_links)
            shine_links = set(shine_links)
            glassdoor_links = set(glassdoor_links)
            naukri_links = set(naukri_links)
            indeed_links = set(indeed_links)
            linkedin_links = set(linkedin_links)
            return render_template('result.html', advice=advice, content=pdf_content, about_me="Based on the data provided in your resume: "+about_me, linkedin_links=linkedin_links, indeed_links=indeed_links, naukri_links=naukri_links, glassdoor_links=glassdoor_links, shine_links=shine_links, TIMES_links=TIMES_links, foundit_links=foundit_links)
        
        # If the file is not a PDF
        else:
            return render_template('index.html', error='Please upload a PDF file')
@app.route('/re')
def re():
    return render_template('redirect.html')

def read_pdf(file):
    pdf_content = ''
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
        pdf_content += page.extract_text()
    return pdf_content

cache1 = {}
MAX_CACHE_AGE_SECONDS1 = 300
def is_cache_valid1(timestamp):
    current_time = time.time()
    return (current_time - timestamp) < MAX_CACHE_AGE_SECONDS1
@app.route('/redirect/<path:link>')
def redirect_to_link(link):
    if link in cache1 and is_cache_valid1(cache1[link]['timestamp']):
        cached_data = cache1[link]['data']
        return render_template('redirect.html', **cached_data)
    
    #TimesJob
    if link.startswith('https://www.timesjobs.com/job-detail/'):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(link)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
        JOBHEADING = driver.find_element(By.XPATH, '//*[@id="job-detail-main-container"]/div[1]/div[2]/h1').text
        INDUSTRYNAME = driver.find_element(By.XPATH, '//*[@id="job-detail-main-container"]/div[1]/div[2]/h2').text
        EXPHEAD = driver.find_element(By.XPATH, '//*[@id="job-detail-main-container"]/div[1]/div[2]/ul[1]/li[1]')
        EXPHEAD = EXPHEAD.text.strip()
        EXPHEAD = EXPHEAD.split()[1:]
        EXPHEAD = ' '.join(EXPHEAD)
        LOCHEAD = driver.find_element(By.XPATH, '//*[@id="job-detail-main-container"]/div[1]/div[2]/ul[1]/li[3]')
        LOCHEAD = LOCHEAD.text.strip()
        LOCHEAD = LOCHEAD.split()[1:]
        LOCHEAD = ' '.join(LOCHEAD)
        LOCHEAD = LOCHEAD.replace('/','')
        try:
            APPLICANTS = driver.find_element(By.XPATH, '//*[@id="jobInsightApplyCount"]/strong').text
            if APPLICANTS == '':
                APPLICANTS = '0'
        except NoSuchElementException:
            APPLICANTS = '0'
        description_element = driver.find_element(By.XPATH, '//div[@class="jd-desc job-description-main"]')
        description = description_element.text.strip()
        description = description.split()[2:]
        description1 = ' '.join(description)
        
        # Prompt for text generation
        response = model.generate_content("Following is a job description, simplify it, so that I can understand about the job more accurately in simple words: "+ description1 + "\n Also make sure to not add any heading or title like short description, I just need the response to be direct.")
        description = response.text
        
        skill_tags = driver.find_elements(By.XPATH, '//span[@class="jd-skill-tag"]')
        skills_list = [tag.text.strip() for tag in skill_tags]
        skills_list = ' /'.join(skills_list)
        
        cover = model.generate_content("Following is the job description and key skills required for the job, prepare a cover letter for this job with the informations provided: \nDescription "+ description1 + "\nSkills Required:"+skills_list+"Also make sure to not add any heading or title like cover letter or here is the cover letter etc, I just need the response to be direct. Additionally instead of giving experinece details yourself, leave spaces that I can fill like, [EXPERIENCE] or [NAME] etc.")
        cover = cover.text
        
        inter_tips = model.generate_content("Following is the job description and key skills required for the job, prepare a list of interview tips for this job with the informations provided: \nDescription "+ description1 + "\nSkills Required:"+skills_list+"Also make sure to not add any heading or title like interview tips or here is the interview tips etc, I just need the response to be direct.")
        inter_tips = inter_tips.text
        
        about_com1 = 'NILL' 
        about_com2 = 'NILL' 
        about_com3 = 'NILL' 
        about_com4 = 'NILL' 
        about_com5 = 'NILL' 
        try:
            about_com1 = driver.find_element(By.XPATH, '//*[@id="applyFlowHideDetails_4"]/ul[1]/li/span').text #COMPANY NAME
        except NoSuchElementException:
            about_com1 = 'NILL'
        try:
            about_com2 = driver.find_element(By.XPATH, '//*[@id="applyFlowHideDetails_4"]/ul[2]/li[1]/span/a').text #COMPANY URL
        except NoSuchElementException:
            about_com2 = 'NILL'
        try:
            about_com3 = driver.find_element(By.XPATH, '//*[@id="applyFlowHideDetails_4"]/ul[2]/li[2]/span').text #ABOUT COMPANY 
        except NoSuchElementException:
            about_com3 = 'NILL'
        try:
            about_com4 = driver.find_element(By.XPATH, '//*[@id="applyFlowHideDetails_4"]/ul[2]/li[3]/span').text #TURNOVER
        except NoSuchElementException:
            about_com4 = 'NILL'
        try:
            about_com5 = driver.find_element(By.XPATH, '//*[@id="applyFlowHideDetails_4"]/ul[2]/li[4]/span').text #Employee Count
        except NoSuchElementException:
            about_com5 = 'NILL'
            
        about_com = model.generate_content("Following are the company details, prepare a description on the company with the following information: \n Company Name- "+ about_com1 + "\nCompany URL- "+about_com2+"\nAbout Company- "+about_com3+"\nCompany Turnover- "+about_com4+"\nEmployee Count- "+about_com5+"Also make sure to not add any heading or title like About company or here is the details on company etc, I just need the response to be direct.")
        about_com = about_com.text
        driver.quit()
        
    elif link.startswith('https://in.linkedin.com/jobs'):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(link)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
        JOBHEADING = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/section[1]/div/div[1]/h3').text
        try:
            INDUSTRYNAME = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/section[1]/div/div[1]/div/a').text
        except NoSuchElementException:
            INDUSTRYNAME = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/section[2]/div/div[2]/div/h4/div[1]/span[1]').text
        try:
            EXPHEAD = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/div/section[1]/div/ul/li[1]/span').text
        except NoSuchElementException:
            EXPHEAD = 'No data!'
        LOCHEAD = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/section[1]/div/div[1]/div/span').text
        try:
            APPLICANTS = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/section[2]/div/div[1]/div/h4/div[2]/span[2]').text
            if APPLICANTS == '':
                APPLICANTS = '0'
        except NoSuchElementException:
            APPLICANTS = '0'
        description1 = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/div/section/div/div/section/div').text
        
        # Prompt for text generation
        try:
            response = model.generate_content("Following is a job description, simplify it, so that I can understand about the job more accurately in simple words: "+ description1 + "\n Also make sure to not add any heading or title like short description, I just need the response to be direct.")
        except:
            response = model.generate_content("Following is a job description, simplify it, so that I can understand about the job more accurately in simple words: "+ description1 + "\n Also make sure to not add any heading or title like short description, I just need the response to be direct.")
        description = response.text
        
        skills_list = model.generate_content("Following is a job description, provide me the key skills mentioned in the content that a job applier should have. The key skills should be provided with a seperation using comma (,): "+ description1 + "\n Also make sure to not add any heading or title like key skills or skills etc, I just need the response to be direct.")
        
        cover = model.generate_content("Following is the job description and key skills required for the job, prepare a cover letter for this job with the informations provided: "+ description1 + "Also make sure to not add any heading or title like cover letter or here is the cover letter etc, I just need the response to be direct. Additionally instead of giving experinece details yourself, leave spaces that I can fill like, [EXPERIENCE] or [NAME] etc.")
        skills_list = skills_list.text
        
        cover = cover.text
        
        inter_tips = model.generate_content("Following is the job description and key skills required for the job, prepare a list of interview tips for this job with the informations provided: "+ description1 + "Also make sure to not add any heading or title like interview tips or here is the interview tips etc, I just need the response to be direct.")
        inter_tips = inter_tips.text
        
        about_com1 = 'NILL' 
        try:
            about_com1 = INDUSTRYNAME #COMPANY NAME
        except NoSuchElementException:
            about_com1 = 'NILL'
            
        about_com = model.generate_content("Following are the company details, prepare a description on the company with the following information: \n Company Name- "+ about_com1 + "\nCompany Job Description- "+description1+"Also make sure to not add any heading or title like About company or here is the details on company etc, I just need the response to be direct.")
        about_com = about_com.text
        driver.quit()
        
    elif 'indeed' in link:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(link)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
        JOBHEADING = driver.find_element(By.XPATH, '//*[@id="viewJobSSRRoot"]/div[2]/div[3]/div/div/div[1]/div[2]/div[1]/div[1]/h1/span').text
        INDUSTRYNAME = driver.find_element(By.XPATH, '//*[@id="viewJobSSRRoot"]/div[2]/div[3]/div/div/div[1]/div[2]/div[1]/div[2]/div/div/div/div[1]/div/span/a').text
        EXPHEAD = driver.find_element(By.XPATH, '//*[@id="jobDescriptionText"]/p[3]')
        EXPHEAD = EXPHEAD.text.strip()
        EXPHEAD = EXPHEAD.split()[3:]
        EXPHEAD = ' '.join(EXPHEAD)
        LOCHEAD = driver.find_element(By.XPATH, '//*[@id="viewJobSSRRoot"]/div[2]/div[3]/div/div/div[1]/div[2]/div[1]/div[2]/div/div/div/div[2]/div').text
        APPLICANTS = 'No data!'
        description1 = driver.find_element(By.XPATH, '//*[@id="jobDescriptionText"]').text
        
        # Prompt for text generation
        response = model.generate_content("Following is a job description, simplify it, so that I can understand about the job more accurately in simple words: "+ description1 + "\n Also make sure to not add any heading or title like short description, I just need the response to be direct.")
        description = response.text
        
        skills_list = model.generate_content("Following is a job description, provide me the key skills mentioned in the content that a job applier should have. The key skills should be provided with a seperation using comma (,): "+ description1 + "\n Also make sure to not add any heading or title like key skills or skills etc, I just need the response to be direct.")
        
        cover = model.generate_content("Following is the job description and key skills required for the job, prepare a cover letter for this job with the informations provided: "+ description1 + "Also make sure to not add any heading or title like cover letter or here is the cover letter etc, I just need the response to be direct. Additionally instead of giving experinece details yourself, leave spaces that I can fill like, [EXPERIENCE] or [NAME] etc.")
        skills_list = skills_list.text
        
        cover = cover.text
        
        inter_tips = model.generate_content("Following is the job description and key skills required for the job, prepare a list of interview tips for this job with the informations provided: "+ description1 + "Also make sure to not add any heading or title like interview tips or here is the interview tips etc, I just need the response to be direct.")
        inter_tips = inter_tips.text
        
        about_com1 = 'NILL' 
        about_com2 = 'NILL'
        try:
            about_com1 = INDUSTRYNAME #COMPANY NAME
        except NoSuchElementException:
            about_com1 = 'NILL'
        try:
            about_com2 = driver.find_element(By.XPATH,'//*[@id="salaryInfoAndJobType"]/span').text
        except NoSuchElementException:
            about_com2 = 'NILL'
            
        about_com = model.generate_content("Following are the company details, prepare a description on the company with the following information: \n Company Name- "+ about_com1 + "\nCompany Job Description- "+description1+ "\nSalary provided: "+about_com2+"\nAlso make sure to not add any heading or title like About company or here is the details on company etc, I just need the response to be direct.")
        about_com = about_com.text
        driver.quit()
        
    elif 'foundit' in link:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(link)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
        JOBHEADING = driver.find_element(By.XPATH, '//*[@id="jdSection"]/div[1]/div[1]/div[2]/div[1]/span').text
        INDUSTRYNAME = driver.find_element(By.XPATH, '//*[@id="jdSection"]/div[1]/div[1]/div[2]/div[2]/p').text
        EXPHEAD = driver.find_element(By.XPATH, '//*[@id="jobHighlight"]/div[1]/div/div[2]/div[2]').text
        LOCHEAD = driver.find_element(By.XPATH, '//*[@id="jobHighlight"]/div[1]/div/div[1]/div[2]').text
        try:
            APPLICANTS = driver.find_element(By.XPATH, '//*[@id="jobHighlight"]/div[1]/div/div[3]/span[3]').text
            if APPLICANTS == '':
                APPLICANTS = '0'
        except NoSuchElementException:
            APPLICANTS = '0'
        description1 = driver.find_element(By.XPATH, '//*[@id="jobDescription"]/div/div/p').text
        
        # Prompt for text generation
        response = model.generate_content("Following is a job description, simplify it, so that I can understand about the job more accurately in simple words: "+ description1 + "\n Also make sure to not add any heading or title like short description, I just need the response to be direct.")
        description = response.text
        
        skills_list = model.generate_content("Following is a job description, provide me the key skills mentioned in the content that a job applier should have. The key skills should be provided with a seperation using comma (,): "+ description1 + "\n Also make sure to not add any heading or title like key skills or skills etc, I just need the response to be direct.")
        
        cover = model.generate_content("Following is the job description and key skills required for the job, prepare a cover letter for this job with the informations provided: "+ description1 + "Also make sure to not add any heading or title like cover letter or here is the cover letter etc, I just need the response to be direct. Additionally instead of giving experinece details yourself, leave spaces that I can fill like, [EXPERIENCE] or [NAME] etc.")
        skills_list = skills_list.text
        
        cover = cover.text
        
        inter_tips = model.generate_content("Following is the job description and key skills required for the job, prepare a list of interview tips for this job with the informations provided: "+ description1 + "Also make sure to not add any heading or title like interview tips or here is the interview tips etc, I just need the response to be direct.")
        inter_tips = inter_tips.text
        
        about_com1 = 'NILL' 
        about_com2 = 'NILL'
        try:
            about_com1 = INDUSTRYNAME #COMPANY NAME
        except NoSuchElementException:
            about_com1 = 'NILL'
        try:
            about_com2 = driver.find_element(By.XPATH,'//*[@id="jobHighlight"]/div[1]/div/div[2]/div[5]').text
        except NoSuchElementException:
            about_com2 = 'NILL'
            
        about_com = model.generate_content("Following are the company details, prepare a description on the company with the following information: \n Company Name- "+ about_com1 + "\nCompany Job Description- "+description1+ "\nSalary provided: "+about_com2+"\nAlso make sure to not add any heading or title like About company or here is the details on company etc, I just need the response to be direct.")
        about_com = about_com.text
        driver.quit()
        
    elif 'naukri' in link:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(link)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
        JOBHEADING = driver.find_element(By.XPATH, '//*[@id="job_header"]/div[1]/div[1]/header/h1').text
        INDUSTRYNAME = driver.find_element(By.XPATH, '//*[@id="job_header"]/div[1]/div[1]/div/a').text
        EXPHEAD = driver.find_element(By.XPATH, '//*[@id="job_header"]/div[1]/div[2]/div[1]/div[1]/span').text
        LOCHEAD = driver.find_element(By.XPATH, '//*[@id="job_header"]/div[1]/div[2]/div[2]/span/a').text
        try:
            APPLICANTS = driver.find_element(By.XPATH, '//*[@id="job_header"]/div[2]/div[1]/span[3]/span').text
            if APPLICANTS == '':
                APPLICANTS = '0'
        except NoSuchElementException:
            APPLICANTS = '0'
        description1 = driver.find_element(By.XPATH, '//*[@id="root"]/div/main/div[1]/div[1]/section[2]/div[2]').text
        
        # Prompt for text generation
        response = model.generate_content("Following is a job description, simplify it, so that I can understand about the job more accurately in simple words: "+ description1 + "\n Also make sure to not add any heading or title like short description, I just need the response to be direct.")
        description = response.text
        
        skills_list = model.generate_content("Following is a job description, provide me the key skills mentioned in the content that a job applier should have. The key skills should be provided with a seperation using comma (,): "+ description1 + "\n Also make sure to not add any heading or title like key skills or skills etc, I just need the response to be direct.")
        
        cover = model.generate_content("Following is the job description and key skills required for the job, prepare a cover letter for this job with the informations provided: "+ description1 + "Also make sure to not add any heading or title like cover letter or here is the cover letter etc, I just need the response to be direct. Additionally instead of giving experinece details yourself, leave spaces that I can fill like, [EXPERIENCE] or [NAME] etc.")
        skills_list = skills_list.text
        
        cover = cover.text
        
        inter_tips = model.generate_content("Following is the job description and key skills required for the job, prepare a list of interview tips for this job with the informations provided: "+ description1 + "Also make sure to not add any heading or title like interview tips or here is the interview tips etc, I just need the response to be direct.")
        inter_tips = inter_tips.text
        
        about_com1 = 'NILL' 
        about_com2 = 'NILL'
        try:
            about_com1 = driver.find_element(By.XPATH, '//*[@id="root"]/div/main/div[1]/div[1]/section[3]/div').text #COMPANY NAME
        except NoSuchElementException:
            about_com1 = 'NILL'
        try:
            about_com2 = driver.find_element(By.XPATH,'//*[@id="job_header"]/div[1]/div[2]/div[1]/div[2]/span').text
        except NoSuchElementException:
            about_com2 = 'NILL'
            
        about_com = model.generate_content("Following are the company details, prepare a description on the company with the following information: \n Company Name- "+ about_com1 + "\nCompany Job Description- "+description1+ "\nSalary provided: "+about_com2+"\nAlso make sure to not add any heading or title like About company or here is the details on company etc, I just need the response to be direct.")
        about_com = about_com.text
        driver.quit()    
    
    elif 'glassdoor' in link:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(link)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
        JOBHEADING = driver.find_element(By.XPATH, '//*[@id="jd-job-title-1009182007037"]').text
        INDUSTRYNAME = driver.find_element(By.XPATH, '//*[@id="0"]/div/h4').text
        LOCHEAD = driver.find_element(By.XPATH, '//*[@id="app-navigation"]/div[2]/div/div[1]/div/div[1]/div/header/div[1]/div[2]').text
        APPLICANTS = 'No data!'
        description1 = driver.find_element(By.XPATH, '//*[@id="app-navigation"]/div[2]/div/div[1]/div/div[1]/div/section/div[2]/div[1]').text
        EXPHEAD = model.generate_content('In 2 words, tell me how much experince is mentioned to have for this job in the description: \n'+description1)
        EXPHEAD = EXPHEAD.text
        # Prompt for text generation
        
        response = model.generate_content("Following is a job description, simplify it, so that I can understand about the job more accurately in simple words: "+ description1 + "\n Also make sure to not add any heading or title like short description, I just need the response to be direct.")
        description = response.text
        
        skills_list = model.generate_content("Following is a job description, provide me the key skills mentioned in the content that a job applier should have. The key skills should be provided with a seperation using comma (,): "+ description1 + "\n Also make sure to not add any heading or title like key skills or skills etc, I just need the response to be direct.")
        
        cover = model.generate_content("Following is the job description and key skills required for the job, prepare a cover letter for this job with the informations provided: "+ description1 + "Also make sure to not add any heading or title like cover letter or here is the cover letter etc, I just need the response to be direct. Additionally instead of giving experinece details yourself, leave spaces that I can fill like, [EXPERIENCE] or [NAME] etc.")
        skills_list = skills_list.text
        
        cover = cover.text
        
        inter_tips = model.generate_content("Following is the job description and key skills required for the job, prepare a list of interview tips for this job with the informations provided: "+ description1 + "Also make sure to not add any heading or title like interview tips or here is the interview tips etc, I just need the response to be direct.")
        inter_tips = inter_tips.text
        
        about_com1 = 'NILL' 
        about_com2 = 'NILL'
        try:
            about_com1 = INDUSTRYNAME #COMPANY NAME
        except NoSuchElementException:
            about_com1 = 'NILL'
        try:
            about_com2 = driver.find_element(By.XPATH,'//*[@id="app-navigation"]/div[2]/div/div[1]/div/div[1]/div/section/section/div/div[1]/div[1]/div[2]').text
        except NoSuchElementException:
            about_com2 = 'NILL'
            
        about_com = model.generate_content("Following are the company details, prepare a description on the company with the following information: \n Company Name- "+ about_com1 + "\nCompany Job Description- "+description1+ "\nSalary provided: "+about_com2+"\nAlso make sure to not add any heading or title like About company or here is the details on company etc, I just need the response to be direct.")
        about_com = about_com.text
        driver.quit()   
        
    elif 'shine.com' in link:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(link)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
        JOBHEADING = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[1]/div[1]/div[2]/div/h1').text
        INDUSTRYNAME = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[1]/div[1]/div[2]/div/div[2]/span').text
        EXPHEAD = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[1]/div[1]/div[2]/div/div[3]/div[2]').text
        LOCHEAD = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[1]/div[1]/div[2]/div/div[3]/div[1]/a').text
        APPLICANTS = 'No data!'
        description1 = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[1]/div[3]').text
        
        # Prompt for text generation
        response = model.generate_content("Following is a job description, simplify it, so that I can understand about the job more accurately in simple words: "+ description1 + "\n Also make sure to not add any heading or title like short description, I just need the response to be direct.")
        description = response.text
        
        skills_list = driver.find_element(By.XPATH,'//*[@id="__next"]/div[1]/div/div/div[1]/div[4]/ul').text
        skills_list = model.generate_content("Following is a skills required for the job, provide me the key skills mentioned in the content that a job applier should have. The key skills should be provided with a seperation using comma (,): "+ skills_list + "\n Also make sure to not add any heading or title like key skills or skills etc, I just need the response to be direct.")
        
        cover = model.generate_content("Following is the job description and key skills required for the job, prepare a cover letter for this job with the informations provided: "+ description1 + "Also make sure to not add any heading or title like cover letter or here is the cover letter etc, I just need the response to be direct. Additionally instead of giving experinece details yourself, leave spaces that I can fill like, [EXPERIENCE] or [NAME] etc.")
        skills_list = skills_list.text
        
        cover = cover.text
        
        inter_tips = model.generate_content("Following is the job description and key skills required for the job, prepare a list of interview tips for this job with the informations provided: "+ description1 + "Also make sure to not add any heading or title like interview tips or here is the interview tips etc, I just need the response to be direct.")
        inter_tips = inter_tips.text
        
        about_com1 = 'NILL' 
        about_com2 = 'NILL'
        try:
            about_com1 = INDUSTRYNAME #COMPANY NAME
        except NoSuchElementException:
            about_com1 = 'NILL'
        try:
            about_com2 = driver.find_element(By.XPATH,'//*[@id="job_header"]/div[1]/div[2]/div[1]/div[2]/span').text
        except NoSuchElementException:
            about_com2 = 'NILL'
            
        about_com = model.generate_content("Following are the company details, prepare a description on the company with the following information: \n Company Name- "+ about_com1 + "\nCompany Job Description- "+description1+ "\nSalary provided: "+about_com2+"\nAlso make sure to not add any heading or title like About company or here is the details on company etc, I just need the response to be direct.")
        about_com = about_com.text
        driver.quit()  
        
    # After scraping the data
    data = {
        'JOBHEADING': JOBHEADING,
        'INDUSTRYNAME': INDUSTRYNAME,
        'EXPHEAD': EXPHEAD,
        'LOCHEAD': LOCHEAD,
        'APPLICANTS': APPLICANTS,
        'description': description,
        'skills_list': skills_list,
        'cover': cover,
        'inter_tips': inter_tips,
        'about_com': about_com
    }

    # Cache the data
    cache1[link] = {
        'data': data,
        'timestamp': time.time()
    }
    
    return render_template('redirect.html', **data)

cache = {}
MAX_CACHE_AGE_SECONDS = 86400 
def is_cache_valid(cache_key, timestamp):
    current_time = time.time()
    return (current_time - timestamp) < MAX_CACHE_AGE_SECONDS

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        job = request.form['job']
        location = request.form['location']
        exp = request.form['exp']
        worktype = request.form['worktype']
        experience = request.form['experience']
        cont = request.form['cont']
        
        
        linkedin_links = []
        indeed_links = []
        foundit_links = []
        naukri_links = []
        glassdoor_links = []
        shine_links = []
        TIMES_links = []
        
        cache_key = f"{job}_{location}_{exp}_{worktype}_{experience}_{cont}"
        if cache_key in cache and is_cache_valid(cache_key, cache[cache_key]['timestamp']):

            return render_template('result.html', **cache[cache_key])
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        
        #LINKEDIN
        driver.get('https://www.linkedin.com/jobs/search/?f_AL=true&f_E='+exp+'&f_WT='+worktype+'&keywords='+job+'&location='+location+'&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true&sortBy=R')
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        ul_element = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[2]/ul')
        a_tags = ul_element.find_elements(By.TAG_NAME, 'a')
        for a_tag in a_tags:
            href = a_tag.get_attribute('href')
            if href is not None and href.startswith('https://in.linkedin.com/jobs/view/'):
                linkedin_links.append(href)
        driver.quit()
        
        #INDEED
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        if cont == 'India':
            if worktype == '1':    
                if exp == '2' or exp == '3':
                    driver.get('https://in.indeed.com/jobs?q='+job+'&l=india&sc=0kf%3Ajt%28new_grad%29%3B&vjk=d6c8d73fdf09d1c2')
                elif exp == '4':
                    driver.get('https://in.indeed.com/jobs?q=MID_LEVEL+'+job+'&l=india&from=searchOnDesktopSerp&vjk=73ad0b80bd34783f')
                else:
                    driver.get('https://in.indeed.com/jobs?q=SENIOR_LEVEL+'+job+'&l=india&from=searchOnDesktopSerp&vjk=cf3aaad012121320')
            elif worktype == '2':
                if exp == '2' or exp == '3':
                    driver.get('https://in.indeed.com/jobs?q='+job+'&l=india&sc=0kf%3Aattr%28DSQF7%29jt%28new_grad%29%3B&vjk=d6c8d73fdf09d1c2')
                elif exp == '4':
                    driver.get('https://in.indeed.com/jobs?q=MID_LEVEL+'+job+'&l=india&sc=0kf%3Aattr%28DSQF7%29%3B&vjk=73ad0b80bd34783f')
                else:
                    driver.get('https://in.indeed.com/jobs?q=SENIOR_LEVEL+'+job+'&l=india&sc=0kf%3Aattr%28DSQF7%29%3B&vjk=cf3aaad012121320')
            else:
                if exp == '2' or exp == '3':
                    driver.get('https://in.indeed.com/jobs?q=Entry+Level+'+job+'&l=india&sc=0kf%3Aattr%28PAXZC%29%3B&vjk=6af2d42b35f771d1')
                elif exp == '4':
                    driver.get('https://in.indeed.com/jobs?q=MID+Level+'+job+'&l=india&sc=0kf%3Aattr%28PAXZC%29%3B&vjk=6af2d42b35f771d1')
                else:
                    driver.get('https://in.indeed.com/jobs?q=SENIOR+Level+'+job+'&l=india&sc=0kf%3Aattr%28PAXZC%29%3B&vjk=6af2d42b35f771d1')
        
        else:
            if worktype == '1':    
                if exp == '2' or exp == '3':
                    driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aexplvl%28ENTRY_LEVEL%29%3B&vjk=d594e92e41587b3d')
                elif exp == '4':
                    driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aexplvl%28MID_LEVEL%29%3B&vjk=80d8f8205c53b671')
                else:
                    driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aexplvl%28SENIOR_LEVEL%29%3B&vjk=2023c13cd2477e44')
            elif worktype == '2':
                if exp == '2' or exp == '3':
                    driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aattr%28DSQF7%29explvl%28ENTRY_LEVEL%29%3B&vjk=9eac3c1dd4df9074')
                elif exp == '4':
                    driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aattr%28DSQF7%29explvl%28MID_LEVEL%29%3B&vjk=80d8f8205c53b671')
                else:
                    driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aattr%28DSQF7%29explvl%28SENIOR_LEVEL%29%3B&vjk=72345ca4b4a0a23f')
            else:
                if exp == '2' or exp == '3':
                    driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aattr%28PAXZC%29explvl%28ENTRY_LEVEL%29%3B&vjk=d27890f0e3805994')
                elif exp == '4':
                    driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aattr%28PAXZC%29explvl%28MID_LEVEL%29%3B&vjk=2187dd820a19aebf')
                else:
                    driver.get('https://www.indeed.com/jobs?q='+job+'&l='+location+'&sc=0kf%3Aattr%28PAXZC%29explvl%28SENIOR_LEVEL%29%3B&vjk=72345ca4b4a0a23f')
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        # Find all 'a' tags dynamically
        li_index = 1
        while True:
            try:
                a_tag = driver.find_element(By.XPATH, f'/html/body/main/div/div[2]/div/div[5]/div/div[1]/div[5]/div/ul/li[{li_index}]/div/div/div/div/div/table/tbody/tr/td[1]/div[1]/h2/a')
                indeed_links.append(a_tag.get_attribute('href'))
                li_index += 1
            except NoSuchElementException:
                break

        # Close the driver
        driver.quit()
        
        # FOUND IT
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        if cont == 'India':
            driver.get('https://www.foundit.in/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
            for job_element in job_elements:
                job_title = job_element.text
                if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS', 'ROLES']:
                    foundit_links.append('https://www.foundit.in/srp/results?query=' + job_title + '&locations=' + location + '&experienceRanges=' + experience + '%7E' + experience + '&experience=' + experience)

            # Close the driver
            driver.quit()
        elif cont == 'Gulf':
            driver.get('https://www.founditgulf.com/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
            for job_element in job_elements:
                job_title = job_element.text
                if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                    foundit_links.append('https://www.founditgulf.com/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)

            # Close the driver
            driver.quit()
        elif cont == 'HongKong':
            driver.get('https://www.foundit.hk/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
            for job_element in job_elements:
                job_title = job_element.text
                if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                    foundit_links.append('https://www.foundit.hk/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)

            # Close the driver
            driver.quit()
        elif cont == 'Singapore':
            driver.get('https://www.foundit.sg/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
            for job_element in job_elements:
                job_title = job_element.text
                if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                    foundit_links.append('https://www.foundit.sg/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)

            # Close the driver
            driver.quit()
        elif cont == 'Philippines':
            driver.get('https://www.foundit.com.ph/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
            for job_element in job_elements:
                job_title = job_element.text
                if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                    foundit_links.append('https://www.foundit.com.ph/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)

            # Close the driver
            driver.quit()
        elif cont == 'Thailand':
            driver.get('https://www.monster.co.th/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
            for job_element in job_elements:
                job_title = job_element.text
                if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                    foundit_links.append('https://www.monster.co.th/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)

            # Close the driver
            driver.quit()
        elif cont == 'Malaysia':
            driver.get('https://www.foundit.my/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
            for job_element in job_elements:
                job_title = job_element.text
                if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                    foundit_links.append('https://www.foundit.my/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
            # Close the driver
            driver.quit()
        elif cont == 'Indonesia':
            driver.get('https://www.foundit.id/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
            for job_element in job_elements:
                job_title = job_element.text
                if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                    foundit_links.append('https://www.foundit.id/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)

            # Close the driver
            driver.quit()
        elif cont == 'Vietnam':
            driver.get('https://www.monster.com.vn/srp/results?query='+job+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            job_elements = driver.find_elements(By.CLASS_NAME, 'jobTitle')
            for job_element in job_elements:
                job_title = job_element.text
                if job_title not in ['JOB TYPE', 'INDUSTRY', 'FUNCTION', 'SKILLS', 'JOBS']:
                    foundit_links.append('https://www.monster.com.vn/srp/results?query='+job_title+'&locations='+location+'&experienceRanges='+experience+'%7E'+experience+'&experience='+experience)

            # Close the driver
            driver.quit()
        else:
            pass
   
        # NAUKRI
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        if cont == 'India':
            if worktype == '1':
                driver.get('https://www.naukri.com/'+job+'-jobs-in-'+location+'?k='+job+'&l='+location+'&experience='+experience+'&wfhType=0')
            elif worktype == '2':
                driver.get('https://www.naukri.com/'+job+'-jobs-in-'+location+'?k='+job+'&l='+location+'&experience='+experience+'&wfhType=2')
            else:
                driver.get('https://www.naukri.com/'+job+'-jobs-in-'+location+'?k='+job+'&l='+location+'&experience='+experience+'&wfhType=3')
            
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            a_tags = driver.find_elements(By.XPATH, './/a')    
            # Extract href attributes from the <a> tags and store them in href_links
            for a_tag in a_tags:
                href = a_tag.get_attribute('href')
                if href is not None and href.startswith('https://www.naukri.com/job-listings-'):
                    naukri_links.append(href)
                    
            
            driver.quit()
        else:
            pass
        
        # Glass Door
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        if worktype == '1':    
            if exp == '2' or exp == '3':
                driver.get('https://www.glassdoor.co.in/Job/'+location+'-'+job+'-jobs-SRCH_IL.0,6_IS4942_KO7,13.htm?seniorityType=entrylevel')
            elif exp == '4':
                driver.get('https://www.glassdoor.co.in/Job/'+location+'-'+job+'-jobs-SRCH_IL.0,6_IS4942_KO7,13.htm?seniorityType=midseniorlevel')
            else:
                pass
        else:
            if exp == '2' or exp == '3':
                driver.get('https://www.glassdoor.co.in/Job/'+location+'-'+job+'-jobs-SRCH_IL.0,6_IS4942_KO7,13.htm?seniorityType=entrylevel&remoteWorkType=1')
            elif exp == '4':
                driver.get('https://www.glassdoor.co.in/Job/'+location+'-'+job+'-jobs-SRCH_IL.0,6_IS4942_KO7,13.htm?seniorityType=midseniorlevel&remoteWorkType=1')
            else:
                pass
            
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        a_tags = driver.find_elements(By.XPATH, './/a')    
        # Extract href attributes from the <a> tags and store them in href_links
        for a_tag in a_tags:
            href = a_tag.get_attribute('href')
            if href is not None and href.startswith('https://www.glassdoor.co.in/job-listing/'):
                glassdoor_links.append(href)

        # Close the driver
        driver.quit()

        #SHINE
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        if cont == 'India':
            if worktype == '1':
                if exp == '2':
                    driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=1')
                elif exp == '3':
                    driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=2')
                elif exp == '4':
                    driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=4')
                else:
                    driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=5')
                
            else:
                if exp == '2':
                    driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=1&emp_type=4')
                elif exp == '3':
                    driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=2&emp_type=4')
                elif exp == '4':
                    driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=4&emp_type=4')
                else:
                    driver.get('https://www.shine.com/job-search/'+job+'-jobs-in-'+location+'?q='+job+'&loc='+location+'&fexp=5&emp_type=4')
            
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Find all 'a' tags dynamically
            li_index = 1
            while True:
                try:
                    a_tag = driver.find_element(By.XPATH, f'//*[@id="1"]/div[{li_index}]/div[1]/div[1]/meta[1]')
                    shine_links.append(a_tag.get_attribute('content'))
                    li_index += 1
                except NoSuchElementException:
                    break
                    
            
            driver.quit()
        else:
            pass
        
        #TIMES
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        if exp == '2':
            driver.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords='+job+'&txtLocation='+location+'&cboWorkExp1=0')
        elif exp == '3':
            driver.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords='+job+'&txtLocation='+location+'&cboWorkExp1=1')
        elif exp == '4':
            driver.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords='+job+'&txtLocation='+location+'&cboWorkExp1=3')
        elif exp == '5':
            driver.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords='+job+'&txtLocation='+location+'&cboWorkExp1=4')
        else:
            driver.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords='+job+'&txtLocation='+location+'&cboWorkExp1=5')
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        a_tags = driver.find_elements(By.XPATH, './/a')    
        # Extract href attributes from the <a> tags and store them in href_links
        for a_tag in a_tags:
            href = a_tag.get_attribute('href')
            if href is not None and href.startswith('https://www.timesjobs.com/job-detail/'):
                TIMES_links.append(href)
        
        
        driver.quit()
        
        foundit_links = set(foundit_links)
        TIMES_links = set(TIMES_links)
        shine_links = set(shine_links)
        glassdoor_links = set(glassdoor_links)
        naukri_links = set(naukri_links)
        indeed_links = set(indeed_links)
        linkedin_links = set(linkedin_links)
        
        cache[cache_key] = {
        'linkedin_links': linkedin_links,
        'indeed_links': indeed_links,
        'foundit_links': foundit_links,
        'naukri_links': naukri_links,
        'glassdoor_links': glassdoor_links,
        'shine_links': shine_links,
        'TIMES_links': TIMES_links,
        'job': job,
        'location': location,
        'timestamp': time.time()  # Add current timestamp
        }

        
        return render_template('result.html', **cache[cache_key])

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
