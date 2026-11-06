# Customer-Orders-Data-Engineering-Pipeline
This project is about building a simple data pipeline using Python to process customer and order data.
The pipeline takes input data, checks for errors, cleans and transforms the data, and stores the processed records in an SQLite database.
I also added logging and testing to check whether each step of the pipeline is working properly.

Tools & Technologie

Python
Pandas
SQLite
Pytest
SQL
Loggin 

Project Files
main.py – Runs the complete pipeline.
config.py – Contains project settings and file paths.
data_generator.py – Generates sample customer and order data.
ingestion.py – Reads the input data.
validation.py – Checks data and identifies invalid records.
transformation.py – Cleans and transforms the data.
database.py – Creates tables and stores the data in SQLite.
monitoring.py – Tracks pipeline execution.
orchestration.py – Manages the pipeline steps.
test_database.py – Tests database operations.
test_transformation.py – Tests data transformation.
test_validation.py – Tests data validation.

How to Run

Clone the repository.

git clone YOUR_REPOSITORY_URL

Open the project folder.

cd customer-orders-data-pipeline

Create a virtual environment.
python -m venv venv

Install the required packages.

pip install -r requirements.txt

Run the project.
python main.py

Run Tests
python -m pytest -v

Sample Output
In one successful pipeline run:
Input Records: 500
Processed Records: 495
Rejected Records: 5
Pipeline Status: SUCCESS
Reconciliation Status: PASSED
The expected and actual row counts and revenue were matching.

What I Learned
How to build a data pipeline using Python.
How to clean and validate data.
How to work with SQLite databases.
How to handle invalid records.
How to use logging and Pytest.

Author
Radhika Battala
GitHub: battalaradhika
