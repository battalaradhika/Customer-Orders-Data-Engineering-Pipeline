My Project Approach and Decisions

 1. About the Problem

In this project, I wanted to create a simple pipeline to process customer and order data using Python.

While working with data, some records may have missing or incorrect values. So, I worked on a pipeline that reads the data, checks it, processes valid records, and saves them in a database.

 2. Assumptions

Before starting the project, I considered a few things:

- Customer and order data would be available as input files.
- Some records might contain errors or invalid values.
- Invalid records should be kept separately.
- The project should run on my local system.
- I should be able to check whether the pipeline completed successfully.

 3. Technologies I Used

 Technology How I Used It 

 Python  To write the pipeline code. 
 Pandas  To work with customer and order data. 
 SQLite  To save the processed data. 
 Pytest To test different parts of the project. 
 Logging  To check the pipeline execution details. 

4. Why I Made These Choices

- **Data Validation:** I wanted to identify incorrect records before saving the data to the database. So, I kept rejected records separately.
- **SQLite:** I used SQLite because it was easy to set up and worked well for my local project.
- **Pipeline Steps:** I divided the work into different steps like ingestion, validation, transformation, loading, and reconciliation. This made the code easier for me to understand and manage.
- **Reconciliation:** I added this step to check whether the processed row count and revenue matched the expected values.

 5. Trade-offs

I chose SQLite because I did not need to install or manage a separate database server.

But I understand that SQLite may not be suitable for handling very large amounts of data or many users at the same time.

For a bigger project, I would consider using a database like SQLite.

 6. How I Tested the Project

I used Pytest to check whether the main functions were working correctly.

I wrote tests for:

- Data validation.
- Data transformation.
- Database operations.

After that, I ran the complete project using:

python main.py


I also ran the test cases using:


python -m pytest -v
```

7. Results I Got

In one successful run, I got the following output:

 Details  Result :
 Total Input Records : 500 
 Processed Records  :495 
 Rejected Records  :5 
 Pipeline Status : SUCCESS 
 Reconciliation : PASSED 

The expected and actual row counts were both 495. The expected revenue and actual revenue were also the same (701800.76).

This helped me check that the pipeline was processing the sample data correctly.

 8. Current Limitations

- I used generated sample data for this project.
- I tested the project on my local system.
- I have not deployed it to the cloud.
- I have not tested it with very large datasets.
- I used SQLite for database storage.

9. What I Would Like to Improve:

If I continue working on this project, I would like to:

- Try processing larger datasets.
- Learn to connect a cloud database.
- Add automatic pipeline scheduling.
- Improve error notifications and monitoring.