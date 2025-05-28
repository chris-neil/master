import requests
import csv
import datetime
import time
import os.path
import urllib.parse
import xlsxwriter

# References
APPLICATION="a"
OPERATINGSYSTEM="o"
HARDWARE="h"
PRODUCTLIST="Python/test_data/productlist.csv"
FILENAME="Python/test_data/cves.xlsx"
RETRIES=3

# Define a product class to hold product information
class product:
  def __init__(self, manufacturer, software, type, version):
    self.manufacturer = manufacturer
    self.software = software
    self.type = type
    self.version = version

# Set the CVE search parameters
max_results = 10
exact_cpe = True
search_days = 120

# Calculate the date range
mod_end = datetime.datetime.now()
mod_start = datetime.datetime.now() - datetime.timedelta(days=search_days)

# Declare and initialize the product list and table data arrays
product_list = []
table_data = []

# Check if the product list file exists
if not os.path.isfile(PRODUCTLIST):
    exit(f"Product list file '{PRODUCTLIST}' not found. Please create it with the required product information.")

# Open the CSV file for reading
csv_reader = csv.reader(open(PRODUCTLIST, 'r', newline=''))

# Import each line into a new product object and append to list
for row in csv_reader:
    new_product = product(row[0], row[1], row[2], row[3])
    product_list.append(new_product)

# Loop through each product in the list
for product_entry in product_list:

    if exact_cpe:

        # Construct the CPE string according to the CPE 2.3 specification
        cpe_string = "cpe:2.3:" + \
            product_entry.type + ":" + \
            product_entry.manufacturer + ":" + \
            product_entry.software + ":" + \
            product_entry.version + ":*:*:*:*:*:*:*"
    
        #print(f"CPE String: {cpe_string}")
        
        # Encode the CPE string for use in the URL querystring
        cpe_match_str = urllib.parse.quote_plus(cpe_string)

        cpe_url=f"https://services.nvd.nist.gov/rest/json/cpes/2.0/?cpeMatchString={cpe_match_str}"
        #print(cpe_url)

    else:
        # Conduct a loose search for the product
        cpe_url = f"https://services.nvd.nist.gov/rest/json/cpes/2.0/?keyword={urllib.parse.quote_plus(product_entry.manufacturer)}&keyword={urllib.parse.quote_plus(product_entry.software)}&keyword={urllib.parse.quote_plus(product_entry.version)}"   


    # We will make retry attempts in case of network issues or rate limiting
    for attempt in range(RETRIES):
        try:
            # Fetch the CPE data from the NVD API
            resp = requests.get(cpe_url)
            resp_json = resp.json()

            # Check if we got any results but continue if not
            total_results=resp_json['totalResults']

            if total_results == 0:
                print(f'No product entry found for {product_entry.manufacturer} {product_entry.software} ({product_entry.type}) version {product_entry.version}')

            break

        except:

            # Search for a too many requests error and sleep according to NIST guidelines
            if resp.status_code == 429:
                print(f"Rate limit exceeded, retrying in 30 seconds...")
                time.sleep(30)
                continue
            else:
                # Print any other kind of error
                print('Failed to fetch from nvd with error: ' + str(resp.status_code) + ' ' + resp.reason)
                continue

    else:
        # If we reach here, it means we exhausted all retries without success
        print(f"Failed to fetch CPE data after {RETRIES} attempts.")
        break

    # For each matching CPE we will now look for CVEs
    for cpe in resp_json['products']:

        print(f"{cpe['cpe']['cpeName']}")

        # Encode the CPE name and date range for use in the CVE querystring
        cpe_name_str = urllib.parse.quote_plus(cpe['cpe']['cpeName'])
        mod_end_str = urllib.parse.quote_plus(mod_end.strftime("%Y-%m-%dT%H:%M:%S"))
        mod_start_str = urllib.parse.quote_plus(mod_start.strftime("%Y-%m-%dT%H:%M:%S"))
        
        cve_url=f"https://services.nvd.nist.gov/rest/json/cves/2.0/?cpeName={cpe_name_str}&lastModStartDate={mod_start_str}&lastModEndDate={mod_end_str}&resultsPerPage={max_results}"
        print(cve_url)

        # We will make retry attempts in case of network issues or rate limiting
        for attempt in range(RETRIES):
            try:
                # Fetch the CVE data from the NVD API
                resp = requests.get(cve_url)
                resp_json = resp.json()

                # Check if we got any results but continue if not
                total_results=resp_json['totalResults']

                if total_results == 0:
                    print(f'No vulnerabilities found for {cpe["cpe"]["cpeName"]}')
                
                # Notify if there were more results to retrieve 
                if total_results > max_results:
                    print(f'There are {str(total_results)} results, we scanned only the first {str(max_results)} ')
                break

            except:
                # Search for a too many requests error and sleep according to NIST guidelines
                if resp.status_code == 429:
                    print(f"Rate limit exceeded, retrying in 30 seconds...")
                    time.sleep(30)
                    continue
                else:
                    # Print any other kind of error
                    print('Failed to fetch from nvd with error: ' + str(resp.status_code) + ' ' + resp.reason)
                    continue
        else:
            # If we reach here, it means we exhausted all retries without success
            print(f"Failed to fetch CVE data after {RETRIES} attempts.")
            break           

        for cve in resp_json['vulnerabilities']:

            #find our cpe match
            for cpeMatch in cve['cve']['configurations'][0]['nodes'][0]['cpeMatch']:
                
                if cpeMatch['criteria'].split('*',1)[0] in cpe['cpe']['cpeName']:

                    # Append this CVE information to the table data
                    table_data.append([cve['cve']['id'],
                                    cve['cve']['sourceIdentifier'],
                                    cve['cve']['published'],
                                    cve['cve']['lastModified'],
                                    cve['cve']['vulnStatus'],
                                    cve['cve']['descriptions'][0]['value'],
                                    cve['cve']['metrics']['cvssMetricV31'][0]['source'],
                                    cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['baseScore'],
                                    cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['baseSeverity'],
                                    cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['attackVector'],
                                    cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['privilegesRequired'],
                                    cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['userInteraction'],
                                    cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['confidentialityImpact'],
                                    cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['integrityImpact'],
                                    cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['availabilityImpact'],
                                    cve['cve']['metrics']['cvssMetricV31'][0]['exploitabilityScore'],
                                    cve['cve']['metrics']['cvssMetricV31'][0]['impactScore'],
                                    cve['cve']['weaknesses'][0]['description'][0]['value'],
                                    cpeMatch['vulnerable'],
                                    cpeMatch['criteria']
                                    ])

# Having completed loops the table_data should contain all found CVEs

# Define the range for the table in the Excel file
table_range = "A1:T" + str(1+len(table_data))

# If the file already exists, delete it to avoid appending to an old file
if os.path.isfile(FILENAME):
    os.remove(FILENAME)
    print(f"Deleted existing file ready for new data: {FILENAME}")
    
# Create a new Excel file and add a worksheet
workbook = xlsxwriter.Workbook(FILENAME)
worksheet = workbook.add_worksheet()


print(f"Writing {len(table_data)} entries to {FILENAME}...")
worksheet.add_table(table_range, {'data': table_data, 'columns': [{'header': 'id'},
                                                            {'header': 'sourceIdentifier'},
                                                            {'header': 'published'},
                                                            {'header': 'lastModified'},
                                                            {'header': 'vulnStatus'},
                                                            {'header': 'description'},
                                                            {'header': 'cvss.baseScore'},
                                                            {'header': 'cvss.baseSeverity'},
                                                            {'header': 'cvss.attackVector'},
                                                            {'header': 'cvss.privilegesRequired'},
                                                            {'header': 'cvss.userInteraction'},
                                                            {'header': 'cvss.confidentialityImpact'},
                                                            {'header': 'cvss.integrityImpact'},
                                                            {'header': 'cvss.availabilityImpact'},
                                                            {'header': 'cvss.exploitabilityScore'},
                                                            {'header': 'cvss.impactScore'},
                                                            {'header': 'weakness.description'},
                                                            {'header': 'configurations.vulnerable'},
                                                            {'header': 'configurations.criteria'}
                                                            ]})

# Close and save the workbook
workbook.close()






