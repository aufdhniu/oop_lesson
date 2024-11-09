import csv
import os


class Table:
    def __init__(self, table_name, data):
        self.table_name = table_name
        self.data = data

    def filter(self, condition):
        return [row for row in self.data if condition(row)]

    def aggregate(self, aggregation_function, aggregation_key):
        try:
            values = [float(row[aggregation_key]) for row in self.data if
                      aggregation_key in row and row[aggregation_key] and row[aggregation_key].replace('.', '', 1).isdigit()]
            return aggregation_function(values) if values else None
        except ValueError:
            print(f"Error: Non-numeric value encountered in '{aggregation_key}' column.")
            return None

    def __str__(self):
        return f"Table({self.table_name}): {len(self.data)} rows"


class TableDB:
    def __init__(self):
        self.tables = {}

    def insert(self, table_name, data):
        self.tables[table_name] = Table(table_name, data)

    def search(self, table_name):
        return self.tables.get(table_name, None)


# Load data from CSV files
def load_csv(file_path):
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        print(f"Error: File not found at path '{file_path}'. Please check the file location.")
        return []
    except Exception as e:
        print(f"An error occurred while reading '{file_path}': {e}")
        return []


# Determine the directory where the script is located
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Construct file paths
cities_file = os.path.join(__location__, 'Cities.csv')
countries_file = os.path.join(__location__, 'Countries.csv')

# Load data
cities_data = load_csv(cities_file)
countries_data = load_csv(countries_file)

# Check if data loaded successfully
if not cities_data or not countries_data:
    print("Error: Failed to load data. Exiting script.")
    exit(1)

# Initialize TableDB and insert data
db = TableDB()
db.insert("Cities", cities_data)
db.insert("Countries", countries_data)

# Get cities table
cities_table = db.search("Cities")

if not cities_table:
    print("Error: 'Cities' table not found in the database.")
    exit(1)


# Helper functions to calculate average, minimum, and maximum
def average(values):
    return sum(values) / len(values) if values else None


def minimum(values):
    return min(values) if values else None


def maximum(values):
    return max(values) if values else None


# Helper function to get average temperature for cities in a specific country
def average_temperature_for_country(country_name):
    country_cities = cities_table.filter(lambda x: x['country'] == country_name)
    if country_cities:
        avg_temp = Table(f"{country_name}_Cities", country_cities).aggregate(average, 'temperature')
        print(f"Average temperature for cities in {country_name}: {avg_temp}")
    else:
        print(f"No cities found in {country_name}.")


# Helper function to get min or max temperature for cities in a specific country
def min_max_temperature_for_country(country_name, temperature_function):
    country_cities = cities_table.filter(lambda x: x['country'] == country_name)
    if country_cities:
        temp = Table(f"{country_name}_Cities", country_cities).aggregate(temperature_function, 'temperature')
        print(f"{temperature_function.__name__.capitalize()} temperature for cities in {country_name}: {temp}")
    else:
        print(f"No cities found in {country_name}.")


# Average temperature for cities in Italy
average_temperature_for_country("Italy")

# Average temperature for cities in Sweden
average_temperature_for_country("Sweden")

# Minimum temperature for cities in Italy
min_max_temperature_for_country("Italy", minimum)

# Maximum temperature for cities in Sweden
min_max_temperature_for_country("Sweden", maximum)

print()

# Additional test case: Min and max latitude for cities in every country
countries = set(city['country'] for city in cities_data)
for country in countries:
    country_cities = cities_table.filter(lambda x: x['country'] == country)
    if country_cities:
        try:
            latitudes = [float(city['latitude']) for city in country_cities if city['latitude'] and city['latitude'].replace('.', '', 1).isdigit()]
            if latitudes:
                min_latitude = min(latitudes)
                max_latitude = max(latitudes)
                print(f"{country}: Min Latitude = {min_latitude}, Max Latitude = {max_latitude}")
            else:
                print(f"{country}: No valid latitude data.")
        except ValueError:
            print(f"{country}: Error converting latitude to float.")
    else:
        print(f"{country}: No cities found.")
