from pathlib import Path
import pandas as pd
import os

#LOADING OF RAW DATA#
data_path = Path(__file__).resolve().parent /"employee_attendance_tracker_data.xlsx"
attendance= pd.read_excel(data_path)


#GROUPED DATA#
attendance["Date"] = pd.to_datetime(attendance["Date"],errors="coerce")
# attendance["Month"] = attendance["Date"].dt.to_period("M")
workdays = attendance["Date"].nunique()
no_of_duplicate_emp_id = attendance[attendance.duplicated(subset=["Employee ID","Date"],keep=False)]
attendance["Scheduled In"] = pd.to_datetime(attendance["Scheduled In"],format="%H:%M",errors="coerce")
attendance["Scheduled Out"] = pd.to_datetime(attendance["Scheduled Out"],format="%H:%M",errors="coerce")
attendance["Scheduled Hours"] = (attendance["Scheduled Out"] - attendance["Scheduled In"]).dt.total_seconds() / 3600
#TIME-BASED METRICS #
#Average Check-In Time 
attendance["Check In"] = pd.to_datetime(attendance["Check In"], format="%H:%M", errors="coerce")
attendance = attendance.dropna(subset=["Check In"])
average_check_in = attendance["Check In"].mean().strftime("%H:%M")
attendance["Check Out"] = pd.to_datetime(attendance["Check Out"],format="%H:%M",errors='coerce')
attendance = attendance.dropna(subset=["Check Out"])
average_check_out = attendance["Check Out"].mean().strftime("%H:%M")
total_hours_worked_jan2026 = attendance["Total Hours"].sum()
attendance["Undertime Hours"] = attendance["Scheduled Hours"] - attendance["Total Hours"]
attendance["Undertime Hours"] = attendance["Undertime Hours"].clip(lower=0)
missed_punch_ins_count = (
    (attendance["Status"] == "Present") &
    (attendance["Check In"].isna())
).sum()
missed_punch_outs_count=(
    (attendance["Status"] == "Present") &
    (attendance[["Check Out"]]).isna()
).sum()


# EMPLOYEE-LEVEL METRICS#
attendance["Attendance Credits"] = attendance["Status"].map({
    "Present": 1,
    "Late": 1,
    "Half Day": 0.5,
    "Absent": 0 
})
attendance_credits_per_employee = attendance.groupby("Employee ID")["Attendance Credits"].sum()
attendance_percentage_per_employee = (
    attendance_credits_per_employee / workdays * 100).round(2)
print(attendance_percentage_per_employee)
#VISUALIZATION#
average_hours_worked_per_day = attendance.groupby("Date")["Total Hours"].mean()

