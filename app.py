import pandas as pd
import streamlit as st
import plotly.express as px
px.defaults.template = "plotly_white"

st.set_page_config(page_title="Grade Dashboard", layout="wide")

st.title("Grade Dashboard")
uploaded_file = st.sidebar.file_uploader("Upload grades file", type=["xlsx"])

if uploaded_file is None:
    st.info("Upload a grades.xlsx file to view the dashboard.")
    st.stop()

grades = pd.read_excel(uploaded_file)
st.sidebar.success("File uploaded successfully")

#MISSING COLUMN VALIDATION BLOCK
required_columns = ["StudentID", "StudentName", "Subject", "Quiz1", "Quiz2", "Attendance", "Exam"]
missing_columns = [col for col in required_columns if col not in grades.columns]

if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.stop()


#NUMERIC COLUMN VALIDATION
numeric_columns = ["Quiz1", "Quiz2", "Attendance", "Exam"]

for col in numeric_columns:
    grades[col] = pd.to_numeric(grades[col], errors="coerce")

if grades[numeric_columns].isna().any().any():
    st.error("Some score fields are missing or not numeric. Please check Quiz1, Quiz2, Attendance, and Exam.")
    st.stop()

#SCORE RANGE VALIDATION

invalid_scores = ((grades[numeric_columns] < 0) | (grades[numeric_columns] > 100)).any().any()

if invalid_scores:
    st.error("Some score fields are outside the 0-100 range.")
    st.stop()

grades["QuizAverage"] = grades[["Quiz1", "Quiz2"]].mean(axis=1)
grades["FinalScore"] = (grades["QuizAverage"] * 0.30) + (grades["Attendance"] * 0.20) + (grades["Exam"] * 0.50)
grades["Result"] = grades["FinalScore"].apply(lambda score: "Pass" if score >= 80 else "Fail")

#DUPLICATE STUDENT ID VALIDATION
st.sidebar.subheader("Data Quality")

duplicate_rows = grades[grades.duplicated(subset="StudentID", keep=False)]

if not duplicate_rows.empty:
    st.sidebar.warning(f"Found {len(duplicate_rows)} rows with duplicate StudentID values.")
    with st.expander("View duplicate rows"):
        st.dataframe(duplicate_rows, use_container_width=True)    
else:
    st.sidebar.success("No duplicate StudentID records found.")


#GRADE BAND & RISK LEVEL

def grade_band(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    else:
        return "D/F"

def risk_level(row):
    if row["FinalScore"] < 75:
        return "High Risk"
    elif row["Attendance"] < 85:
        return "Attendance Risk"
    elif row["FinalScore"] < 80:
        return "Watchlist"
    else:
        return "On Track"
grades["Grade Band"] = grades["FinalScore"].apply(grade_band)
grades["Risk Level"] = grades.apply(risk_level,axis=1)

selected_subject = st.sidebar.selectbox("Subject", ["All"] + sorted(grades["Subject"].unique()))
# creates a dropdown filter in the left sidebar of your Streamlit app.

if selected_subject == "All":
    filtered_grades = grades
else:
    filtered_grades = grades[grades["Subject"] == selected_subject]

st.caption(f"Current filter: {selected_subject}")

total_students = filtered_grades["StudentID"].nunique()
average_score = filtered_grades["FinalScore"].mean()
pass_rate = ((filtered_grades["Result"] == "Pass").sum() / total_students) * 100
at_risk_students =((filtered_grades["Risk Level"].eq("Watchlist")) | (filtered_grades["Risk Level"].eq("High Risk")) | (filtered_grades["Risk Level"].eq("Attendance Risk"))).sum()


summary_tab, charts_tab, table_tab = st.tabs(["Summary", "Charts", "Student Results"])

with summary_tab:
    st.subheader("Summary")
    st.caption(f"Showing results for: {selected_subject}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", total_students)   
    col2.metric("Average Final Score", round(average_score, 2))
    col3.metric("Pass Rate", f"{pass_rate:.2f}%")
    col4.metric("At Risk Students", at_risk_students)

#VISUALS

with charts_tab:
    st.subheader("Subject Performance")
    students_per_subject = filtered_grades.groupby("Subject")["StudentID"].nunique().reset_index(name="Students")
    fig_students = px.bar(
        students_per_subject,
        x="Subject",
        y="Students",
        title="Number of Students per Subject",
        text="Students" ,
        color_discrete_sequence=["#2563EB"]
    )   
    fig_students.update_traces(textposition="outside")
    fig_students.update_layout(
        height=420,
        showlegend=False,
        yaxis_title="Students",
        xaxis_title=None
    )
    chart_col1, chart_col2 = st.columns(2)
    chart_col1.plotly_chart(fig_students, use_container_width=True)
    average_score_per_subject = filtered_grades.groupby("Subject")["FinalScore"].mean().round(2).reset_index()
    fig_average_score = px.bar(
        average_score_per_subject,
        x="Subject",
        y="FinalScore",
        title="Average Final Score per Subject",
        text="FinalScore",
        color_discrete_sequence=["#16A34A"]
    )
    fig_average_score.update_traces(textposition="outside")
    fig_average_score.update_layout(
        height=420,
        showlegend=False,
        yaxis_title="Average Final Score",
        xaxis_title=None
    )
    chart_col2.plotly_chart(fig_average_score, use_container_width=True)
    
    st.subheader("Student Outcomes")
    pass_fail_counts = filtered_grades["Result"].value_counts().reset_index()
    fig_pass_fail = px.pie(
    pass_fail_counts,
    names="Result",
    values="count",
    title="Pass vs. Fail",
    color="Result",
    color_discrete_map={
        "Pass": "green",
        "Fail": "red",
    }
    )
    fig_pass_fail.update_traces(textinfo="label+percent+value")
    fig_pass_fail.update_layout(
        height = 420,
        legend_title_text = "Result"
    )
    chart_col3, chart_col4 = st.columns(2)

    chart_col3.plotly_chart(fig_pass_fail, use_container_width=True)

    risk_level_count = filtered_grades["Risk Level"].value_counts().reset_index()
    fig_risk_level_count = px.bar(
    risk_level_count,
    x = "Risk Level",
    y = "count",
    title="Student by Risk Level",
    text="count",
    color="Risk Level",
    color_discrete_map={
        "On Track": "green",
        "Watchlist": "orange",
        "Attendance Risk": "gold",
        "High Risk": "red",
    },
    )
    fig_risk_level_count.update_traces(textposition="outside")
    fig_risk_level_count.update_layout(
        height = 420,
        showlegend = False,
        yaxis_title = "Students",
        xaxis_title = None
    )
    chart_col4.plotly_chart(fig_risk_level_count, use_container_width=True)


with table_tab:
    st.subheader("Student Results")
    display_columns = [
    "StudentID",
    "StudentName",
    "Subject",
    "QuizAverage",
    "FinalScore",
    "Result",
    "Grade Band",
    "Risk Level",
    ]

    styled_table = (
    filtered_grades[display_columns]
    .sort_values("FinalScore", ascending=False)
    .style
    .map(
        lambda value: (
            "background-color: #ffcccc" if value == "High Risk"
            else "background-color: #fff3cd" if value in ["Watchlist", "Attendance Risk"]
            else ""
        ),
        subset=["Risk Level"]
        )
    )
    #apply styling to chosen subset
    st.dataframe(styled_table, use_container_width=True)

    download_subject = selected_subject.replace(" ", "_").lower()
    csv = filtered_grades[display_columns].to_csv(index=False)

    st.download_button(
    label="Download Student Results",
    data=csv,
    file_name=f"student_results_{download_subject}.csv",
    mime="text/csv"
    )
