import tkinter as tk
from tkinter import ttk
import csv
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Global variables for position and location entries
position_entry = None
location_entry = None

def scrape_jobs(position, location):
    options = Options()
    #options.add_argument("--headless")  # Uncomment to run Chrome in headless mode

    # Path to chromedriver.exe
    driver_path = r'chromedriver.exe'
    service = Service(driver_path)

    # Specify Chrome binary location (optional)
    options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'  # Adjust as per your Chrome installation path

    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = f"https://in.indeed.com/jobs?q={position}&l={location}"
        driver.get(url)

        # Wait until the job cards are loaded
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "mosaic-provider-jobcards")))

        # Get the HTML content after the page has fully loaded
        html_content = driver.page_source

        # Save the HTML content to a file
        with open("indeed_jobs.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        print("HTML content extracted successfully.")

        # Parse HTML and load data into Treeview
        filename = "indeed_jobs.html"
        csv_filename = parse_html(filename)
        load_csv_data(csv_filename, tree)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        driver.quit()

def parse_html(filename):
    with open(filename, 'r', encoding='utf-8') as html_file:
        soup = BeautifulSoup(html_file, 'html.parser')

    cards = soup.find_all('div', 'job_seen_beacon')

    job_list = []

    for card in cards:
        title_element = card.find('h2', {'class': 'jobTitle'})
        title = title_element.text.strip() if title_element else 'N/A'

        # Updated selector for the company element
        company_element = card.find('span', {'data-testid': 'company-name'})
        company = company_element.text.strip() if company_element else 'N/A'

        # Updated selector for the location element
        location_element = card.find('div', {'data-testid': 'text-location'})
        location = location_element.text.strip() if location_element else 'N/A'

        job_link = "https://in.indeed.com" + card.find('a')['href']

        job = {
            'title': title,
            'company': company,
            'location': location,
            'job_link': job_link
        }
        job_list.append(job)

    # Construct filename based on position (you might want to change this logic)
    csv_filename = 'jobs.csv'

    # Save data to CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'company', 'location', 'job_link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for job in job_list:
            writer.writerow(job)

    print(f"Jobs extracted successfully from '{filename}' and saved to '{csv_filename}'.")

    return csv_filename


def load_csv_data(filename, tree):
    tree.delete(*tree.get_children())  # Clear existing data

    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title = row['title']
            company = row['company']
            location = row['location']
            job_link = row['job_link']
            tree.insert('', 'end', values=(title, company, location, job_link))

    # Bind click event to open job link in browser
    tree.bind('<ButtonRelease-1>', lambda event: on_treeview_click(event, tree))


def on_treeview_click(event, tree):
    # Get the selected row
    selected_item = tree.focus()
    if not selected_item:
        return
    
    # Get the values for the selected row
    item_values = tree.item(selected_item, 'values')
    
    # The "Job Link" column is the last column, so the index is 3
    job_link = item_values[3] if len(item_values) > 3 else None
    
    if job_link:
        # Open the job link in the default browser
        webbrowser.open_new(job_link)


def scrape_and_load():
    global position_entry, location_entry

    position = position_entry.get()
    location = location_entry.get()

    if position and location:
        scrape_jobs(position, location)

def show():
    global position_entry, location_entry

    root = tk.Tk()
    root.title("Job Viewer")

    # Input Frame
    input_frame = ttk.Frame(root, padding=(20, 10))
    input_frame.pack()

    # Position and Location inputs
    position_label = ttk.Label(input_frame, text="Position:")
    position_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    position_entry = ttk.Entry(input_frame, width=30)
    position_entry.grid(row=0, column=1, padx=10, pady=5)

    location_label = ttk.Label(input_frame, text="Location:")
    location_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    location_entry = ttk.Entry(input_frame, width=30)
    location_entry.grid(row=1, column=1, padx=10, pady=5)

    # Scrape button
    scrape_button = ttk.Button(input_frame, text="Scrape HTML Content", command=scrape_and_load)
    scrape_button.grid(row=2, column=0, columnspan=2, pady=10)

    # Treeview for displaying jobs
    tree_frame = ttk.Frame(root)
    tree_frame.pack(padx=20, pady=10, fill='both', expand=True)

    global tree  # Make 'tree' global so that it can be accessed in load_csv_data function
    tree = ttk.Treeview(tree_frame, columns=('Title', 'Company', 'Location', 'Job Link'), show='headings')
    tree.heading('Title', text='Title')
    tree.heading('Company', text='Company')
    tree.heading('Location', text='Location')
    tree.heading('Job Link', text='Job Link')
    tree.pack(fill='both', expand=True)

    root.mainloop()

if __name__ == "__main__":
    show()
