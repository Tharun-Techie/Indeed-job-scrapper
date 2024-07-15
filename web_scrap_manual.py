import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def get_url(pos, loc):
    pos = pos.replace(" ", "+")
    template = "https://in.indeed.com/jobs?q={}&l={}"
    url = template.format(pos, loc)
    return url

# def get_job_details(card):
#     # Extract job title
#     title_element = card.find('h2', 'jobTitle')
#     title = title_element.text.strip() if title_element else 'N/A'

#     # Extract company name
#     company_element = card.find('span', {'class': 'css-63koeb'})
#     company = company_element.text.strip() if company_element else 'N/A'

#     # Extract location
#     location_element = card.find('div', {'data-testid': 'text-location'})
#     location = location_element.text.strip() if location_element else 'N/A'

#     # Extract job posting timestamp
#     posted_element = card.find('span', {'data-testid': 'myJobsStateDate'})
#     posted = posted_element.text.strip().split(' • ')[-1] if posted_element else 'N/A'

#     # Extract job summary
#     summary_element = card.find('div', {'class': 'job-snippet'})
#     summary = summary_element.text.strip() if summary_element else 'N/A'

#     # Extract job link
#     job_link = "https://in.indeed.com" + card.find('a')['href']

#     job = {
#         'title': title,
#         'company': company,
#         'location': location,
#         'posted': posted,
#         'summary': summary,
#         'job_link': job_link
#     }
#     return job

def get_job_details(card):
    title_element = card.find('h2', {'class': 'jobTitle'})
    title = title_element.text.strip() if title_element else 'N/A'

    company_element = card.find('span', {'class': 'css-63koeb'})
    company = company_element.text.strip() if company_element else 'N/A'

    location_element = card.find('div', {'data-testid': 'text-location'})
    location = location_element.text.strip() if location_element else 'N/A'

    posted_element = card.find('span', {'class': 'date'})
    posted = posted_element.text.strip() if posted_element else 'N/A'

    summary_element = card.find('div', {'class': 'job-snippet'})
    summary = summary_element.text.strip() if summary_element else 'N/A'

    job_link = "https://in.indeed.com" + card.find('a')['href']

    job = {
        'title': title,
        'company': company,
        'location': location,
        'posted': posted,
        'summary': summary,
        'job_link': job_link
    }
    return job

def main():
    posi = input("Enter role")
    loc = input("Enter Location")
    url = get_url(posi, loc)
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all('div', 'job_seen_beacon')

    job_list = []

    for card in cards:
        job = get_job_details(card)
        job_list.append(job)

    # Save data to a CSV file
    pos = posi.replace(' ','_')
    filename = f'{pos}.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'company', 'location', 'posted', 'summary', 'job_link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for job in job_list:
            writer.writerow(job)

    print(f"Jobs scraped successfully and saved to '{filename}'.")

if __name__ == "__main__":
    main()
