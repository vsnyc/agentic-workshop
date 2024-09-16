import csv
import random
from datetime import date, timedelta
from faker import Faker

# Initialize Faker instance
fake = Faker()

# Define lists for company names and hobbies
company_names = [
    "TechGiant Inc.", "InnovaCorp", "SoftwareSolutions LLC", "CyberTech Ltd.", "DataMasters Inc.",
    "CodeWizards Co.", "TechMavericks LLC", "DigitalEdge Solutions", "TechTrend Group", "ByteCrafters Inc.",
    "CodeMasters Ltd.", "SoftwarePros LLC", "CyberSecure Solutions", "DataTech Corp.", "InnovatIQ Ltd.",
    "TechGalaxy Inc.", "CodeMasters Group", "SoftwareSolutions Pro", "DigitalEdge Innovations", "TechTrend Solutions",
    "ByteCrafters Group", "CyberSecure Corp.", "DataMasters Solutions", "CodeWizards Ltd.", "SoftwarePros Inc.",
    "TechMavericks Solutions", "DigitalEdge Pros", "InnovaCorp Ltd."
]

hobbies = [
    "Painting", "Basketball", "Photography", "Hiking", "Reading", "Cycling", "Baking", "Gardening", "Yoga",
    "Gaming", "Dancing", "Swimming", "Drawing", "Running", "Cooking", "Traveling", "Writing", "Fishing",
    "Camping", "Crafting", "Singing", "Playing Guitar", "Watching Movies", "Playing Video Games"
]

# Open a CSV file for writing
with open("data.csv", "w", newline="") as csvfile:
    fieldnames = ["First name", "Last name", "Joining Date", "Age", "Company Name", "Favorite Hobby"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write the header row
    writer.writeheader()

    # Generate 1000 records
    for _ in range(1000):
        first_name = fake.first_name()
        last_name = fake.last_name()
        joining_date = fake.date_between(date(2015, 1, 1), date(2021, 12, 31)).strftime("%Y-%m-%d")
        age = random.randint(21, 40)
        company_name = random.choice(company_names)
        favorite_hobby = random.choice(hobbies)

        writer.writerow({
            "First name": first_name,
            "Last name": last_name,
            "Joining Date": joining_date,
            "Age": age,
            "Company Name": company_name,
            "Favorite Hobby": favorite_hobby
        })

print("CSV file 'data.csv' has been generated with 1000 records.")
