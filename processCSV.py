import pandas as pd
import os
import csv




def write_to_csv(file_name, column_data):
    """
    Writes data to a CSV file, updating it immediately. Creates the file if it doesn't exist.
    Strings are enclosed in double quotes, and double quotes in strings are escaped properly.

    Args:
        file_name (str): The name of the CSV file.
        column_data (dict): A dictionary where keys are column names and values are the corresponding data to write.
    """
    # Check if the file exists
    file_exists = os.path.isfile(file_name)

    # Open the file in append mode
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(
            file,
            fieldnames=column_data.keys(),
            quotechar='"',
            quoting=csv.QUOTE_NONNUMERIC  # Enclose all non-numeric fields in double quotes
        )

        # Write the header if the file is new
        if not file_exists:
            writer.writeheader()

        # Write the data row
        writer.writerow(column_data)


class processCSV:
    def __init__(self, file_path):
        self.file_path = file_path

        # Determine the path for the processed CSV
        self.processed_file_path = file_path.replace('.csv', '_processed.csv')

        # Check if the processed file already exists
        if os.path.exists(self.processed_file_path):
            print(f"Processed file found: {self.processed_file_path}")
            self.df = pd.read_csv(self.processed_file_path)
        else:
            print(f"No processed file found. Using original file: {file_path}")
            self.df = pd.read_csv(file_path)

        # Add the "processed" column if it doesn't already exist
        if 'processed' not in self.df.columns:
            self.df['processed'] = False

    def distinct_values(self, column_name):
        """
        Get the distinct values from the specified column.

        :param column_name: Column to get distinct values from
        :return: List of distinct values
        """
        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

        return self.df[column_name].unique()
    

    def filter_by_column(self, column_name, filter_value):
        """
        Filter the DataFrame by the specified column and value.

        :param column_name: Column to filter by
        :param filter_value: Value to filter for
        :return: Filtered DataFrame
        """
        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")
        
        filtered_df = self.df[self.df[column_name] == filter_value]
        return filtered_df


if __name__ == "__main__":
    CSV_processor = processCSV('allplaces.csv')

    listNames = CSV_processor.distinct_values('ListName')

    for listName in listNames:
        
        print(f"Processing list: {listName}")
        
        filtered_df = CSV_processor.filter_by_column('ListName', listName)
        
        for index, row in filtered_df.iterrows():
            place_name = row['name']
            place_address = row['address']
            print(f" - Place name: {place_name} - {place_address}")
    

