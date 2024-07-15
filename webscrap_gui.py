import tkinter as tk
from tkinter import ttk
import csv
import requests
from bs4 import BeautifulSoup
import webbrowser
from ttkthemes import ThemedStyle

def get_url(pos, loc):
    pos = pos.replace(" ", "+")
    template = "https://in.indeed.com/jobs?q={}&l={}"
    url = template.format(pos, loc)
    return url

def get_job_details(card):
    title_element = card.find('h2', {'class': 'jobTitle'})
    title = title_element.text.strip() if title_element else 'N/A'

    company_element = card.find('span', {'class': 'css-63koeb'})
    company = company_element.text.strip() if company_element else 'N/A'

    location_element = card.find('div', {'data-testid': 'text-location'})
    location = location_element.text.strip() if location_element else 'N/A'

    job_link = "https://in.indeed.com" + card.find('a')['href']

    job = {
        'title': title,
        'company': company,
        'location': location,
        'job_link': job_link
    }
    return job

def scrape_jobs(position, location):
    url = get_url(position, location)
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all('div', 'job_seen_beacon')

    job_list = []

    for card in cards:
        job = get_job_details(card)
        job_list.append(job)

    # Construct filename based on position
    filename = f'{position.replace(" ", "_")}_jobs.csv'

    # Save data to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'company', 'location', 'job_link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for job in job_list:
            writer.writerow(job)

    print(f"Jobs scraped successfully and saved to '{filename}'.")
    
    return filename

def load_csv_data(filename):
    tree.delete(*tree.get_children())  # Clear existing data

    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title = row['title']
            company = row['company']
            location = row['location']
            job_link = row['job_link']
            tree.insert('', 'end', values=(title, company, location, job_link))

    tree.bind('<ButtonRelease-1>', lambda event: on_treeview_click(event, tree))

def scrape_and_load():
    position = position_entry.get()
    location = location_entry.get()

    if position and location:
        filename = scrape_jobs(position, location)
        load_csv_data(filename)

root = tk.Tk()
root.title("Job Scraper and Viewer")

style = ThemedStyle(root)
style.set_theme("plastik")

input_frame = ttk.Frame(root, padding=(500, 10))
input_frame.pack()

position_label = ttk.Label(input_frame, text="Position:")
position_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
position_entry = ttk.Entry(input_frame, width=30)
position_entry.grid(row=0, column=1, padx=10, pady=5)

location_label = ttk.Label(input_frame, text="Location:")
location_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
location_entry = ttk.Entry(input_frame, width=30)
location_entry.grid(row=1, column=1, padx=10, pady=5)

scrape_button = ttk.Button(input_frame, text="Scrape Jobs", command=scrape_and_load)
scrape_button.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky=tk.W + tk.E)
scrape_button.configure(style='Accent.TButton')

tree_frame = ttk.Frame(root)
tree_frame.pack(padx=20, pady=10, fill='both', expand=True)

tree = ttk.Treeview(tree_frame, columns=('Title', 'Company', 'Location', 'Job Link'), show='headings')
tree.heading('Title', text='Title')
tree.heading('Company', text='Company')
tree.heading('Location', text='Location')
tree.heading('Job Link', text='Job Link')

tree.column('Title', width=200, anchor=tk.CENTER)
tree.column('Company', width=150, anchor=tk.CENTER)
tree.column('Location', width=100, anchor=tk.CENTER)
tree.column('Job Link', width=150, anchor=tk.CENTER)

tree.pack(fill='both', expand=True)

root.mainloop()
