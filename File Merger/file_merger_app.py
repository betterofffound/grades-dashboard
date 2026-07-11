import pandas as pd
import streamlit as st

st.set_page_config(page_title="Excel File Merger",layout="wide")
st.title("Excel File Merger")

uploaded_files = st.sidebar.file_uploader(
    "Upload xlsx file(s)",
    type=["xlsx"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("Upload the xlsx file/s to view the consolidated data")
    st.stop()

reference_columns = None
dataframes = []

for file in uploaded_files:
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip().str.lower()

    if reference_columns is None:
        reference_columns = set(df.columns)
    else:
        current_columns = set(df.columns)
        if current_columns != reference_columns:
            missing = [col for col in reference_columns if col not in current_columns]
            extra = [col for col in current_columns if col not in reference_columns]
            st.error(
                f"{file.name} has mismatched headers."
                f"Mismatch: {', '.join(missing)if missing else 'None'} |"
                f"Extra: {','.join(extra) if extra else 'None'}"
            )
            st.stop()
            
    dataframes.append(df)

merged_df = pd.concat(dataframes, ignore_index=True)
merged_df = merged_df.dropna(how="all")
merged_df.columns = merged_df.columns.str.strip()


no_of_rows_collected = merged_df.shape[0]
no_of_columns_collected = merged_df.shape[1]


#DUPLICATE ORDER VALIDATION
duplicates= merged_df[merged_df.duplicated(keep=False)].reset_index()
no_of_duplicates = len(duplicates)

if not duplicates.empty:
    st.sidebar.warning(f"Found {len(duplicates)} duplicate rows.")
    with st.expander("View Duplicate records:"):
         st.dataframe(duplicates,width="stretch")
else:
    st.sidebar.success("No duplicates found!")


summary_tab, table_tab = st.tabs(["Summary", "Merged Data Results"])

with summary_tab:
    st.subheader("Summary")
    st.caption("Overview based on the merged data results.")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total No. of Rows Collected",no_of_rows_collected)
    col2.metric("Total No. of Columns",no_of_columns_collected)
    col3.metric("Total No. of Duplicate Rows",no_of_duplicates)
st.divider()     


with table_tab:

    st.markdown("##### Merged Data")
    st.dataframe(merged_df)

    download_merged_data = merged_df
    csv = download_merged_data.to_csv(index=False)

    st.download_button(
        label="Download Merged Data Results",
        data=csv,
        file_name="Merged Data Results.csv",
        mime="text/csv"
    )