# Grade Dashboard

A Streamlit dashboard for analyzing student grades from an uploaded Excel file.

## Features

- Upload `.xlsx` grade files
- View summary metrics
- Filter by subject
- Visualize subject performance
- View pass/fail and risk breakdowns
- Download filtered student results as CSV
- Download individual charts as PNG images using the Plotly toolbar

## Required Columns

The uploaded Excel file must include:

- StudentID
- StudentName
- Subject
- Quiz1
- Quiz2
- Attendance
- Exam