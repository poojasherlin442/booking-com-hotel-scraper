🏨 Hotel Price Monitoring Bot

A Python automation bot that searches hotels on Booking.com, extracts hotel details and images using Selenium, and sends personalized HTML emails with inline images to users.

📌 Features

🔍 Searches hotels on Booking.com by location

🏨 Extracts hotel details:

Hotel name

Check-in time

Check-out time

🖼️ Downloads hotel images automatically

📧 Sends HTML emails with inline hotel images

👥 Supports multiple users using Excel input

🧹 Automatically cleans up downloaded images after email is sent

🛠️ Tech Stack

Python

Selenium WebDriver

Pandas

Requests

SMTP (Gmail)

HTML Email (inline images using CID)

📂 Project Structure
hotel-price-monitoring-bot/
│
├── hotelbooking.py        # Main automation script
├── input_sample.xlsx     # Sample input file (no real data)
├── README.md              # Project documentation
├── .gitignore             # Ignored files (secrets, images, input)

📄 Input File Format

The script reads data from an Excel file (input.xlsx).

Columns required:

------------------------------
Location	|Price|	Email
Chennai 	|5000	|test@example.com


🚀 How It Works

Reads user input from Excel

Opens Booking.com using Selenium

Searches hotels for the given location

Opens hotel pages in new tabs

Extracts:

Hotel name

Check-in / Check-out times

Hotel image

Downloads hotel images

Sends a single HTML email with hotel details and images embedded

Cleans up downloaded images

📧 Email Preview (Conceptual)
Hotel 1
Check-in: From 2:00 PM
Check-out: Until 11:00 AM
[Hotel Image]

Hotel 2
Check-in: From 1:00 PM
Check-out: Until 12:00 PM
[Hotel Image]

Images appear inside the email body, not as attachments.
