import os
import pandas as pd
import pysolr
import plotly.express as px
import matplotlib.pyplot as plt


# Function to create a Solr collection
def createCollection(p_collection_name):
    os.system(f"solr create -c {p_collection_name}")


# Function to index employee data into Solr, excluding a specific column
def indexData(p_collection_name, p_exclude_column):
    # Load employee data
    data = pd.read_csv(r'C:\Users\T460S\Downloads\archive\Employee Sample Data 1.csv', encoding='windows-1252')

    # Drop the excluded column
    if p_exclude_column in data.columns:
        data = data.drop(columns=[p_exclude_column])

    # Convert to JSON format for indexing
    solr_data = data.to_dict(orient='records')

    # Connect to Solr
    solr = pysolr.Solr(f'http://localhost:8983/solr/{p_collection_name}', always_commit=True)

    # Index data
    solr.add(solr_data)


# Function to search within a Solr collection by a specified column and value
def searchByColumn(p_collection_name, p_column_name, p_column_value, plot_results=False):
    solr = pysolr.Solr(f'http://localhost:8983/solr/{p_collection_name}', always_commit=True)
    query = f'{p_column_name}:{p_column_value}'
    results = solr.search(query)

    data = []
    for result in results:
        print(result)
        data.append(result)

    # Plot the results if requested
    if plot_results:
        df = pd.DataFrame(data)
        if not df.empty:
            # Use 'Full_Name' for employee names in the x-axis
            fig = px.bar(df, x='Full_Name', y=p_column_name, title=f"{p_column_value} in {p_column_name}")
            fig.show()


# Function to get the total number of employees in a Solr collection
def getEmpCount(p_collection_name):
    solr = pysolr.Solr(f'http://localhost:8983/solr/{p_collection_name}', always_commit=True)
    results = solr.search('*:*')
    print(f'Total employee count: {results.hits}')
    return results.hits


# Function to delete an employee from a Solr collection by employee ID
def delEmpById(p_collection_name, p_employee_id):
    solr = pysolr.Solr(f'http://localhost:8983/solr/{p_collection_name}', always_commit=True)
    solr.delete(id=p_employee_id)
    print(f'Employee {p_employee_id} deleted.')


# Function to retrieve and plot department facets from a Solr collection
def getDepFacet(p_collection_name, plot_facet=False):
    solr = pysolr.Solr(f'http://localhost:8983/solr/{p_collection_name}', always_commit=True)
    facet_query = {'facet': 'true', 'facet.field': 'Department'}
    results = solr.search('*:*', **facet_query)

    facets = results.facets['facet_fields']['Department']
    departments = facets[::2]  # Department names
    counts = facets[1::2]      # Employee counts

    print('Department Facet Counts:')
    for dep, count in zip(departments, counts):
        print(f'{dep}: {count}')

    # Plot the facet result if requested
    if plot_facet:
        if departments and counts:
            fig = px.bar(x=departments, y=counts, labels={'x': 'Department', 'y': 'Count'},
                         title='Employee Count by Department')
            fig.show()


# ---- Example Usage ----
v_nameCollection = 'Hash_Gogulakkannan'  # Using your name
v_phoneCollection = 'Hash_1234'  # Using the last 4 digits of your phone number

# 1. Create collections
createCollection(v_nameCollection)
createCollection(v_phoneCollection)

# 2. Get initial employee count
getEmpCount(v_nameCollection)

# 3. Index data excluding certain columns
indexData(v_nameCollection, 'Department')
indexData(v_phoneCollection, 'Gender')

# 4. Delete an employee by ID
delEmpById(v_nameCollection, 'E02003')

# 5. Get employee count after deletion
getEmpCount(v_nameCollection)

# 6. Search by column with results and optional plot
searchByColumn(v_nameCollection, 'Department', 'IT')
searchByColumn(v_nameCollection, 'Gender', 'Male')
searchByColumn(v_phoneCollection, 'Department', 'IT', plot_results=True)

# 7. Get department facet and plot
getDepFacet(v_nameCollection)
getDepFacet(v_phoneCollection, plot_facet=True)
