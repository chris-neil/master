import requests
import csv
import datetime
import time
import os.path 
import json
import packaging   # pip install packaging
import urllib.parse     #pip install urllib.parse
import xlsxwriter   #pip install xlsxwriter

# References
APPLICATION="a"
OPERATINGSYSTEM="o"
HARDWARE="h"
PRODUCTLIST="Python/test_data/productlist.csv"
FILENAME="Python/test_data/cves.xlsx"
MAXRETRIES=3   # Number of retry attempts for network requests

# Define a product class to hold product information
class product:
    def __init__(self, manufacturer, software, type, version):
        self.manufacturer = manufacturer
        self.software = software
        self.type = type
        self.version = version
        
    # Construct the CPE string according to the CPE 2.3 specification
    def cpe_string(self):
        return f"cpe:2.3:{self.type}:{self.manufacturer}:{self.software}:{self.version}:*:*:*:*:*:*:*"

# Define a function to query the NVD api for CPEs and CVEs
def query_nvd(url, context, retries):

    # We will make retry attempts in case of network issues or rate limiting
    for attempt in range(retries):
        try:
            # Fetch the data from the NVD API
            resp = requests.get(url)
            resp_json = resp.json()

            # Check if we got any results but continue if not
            total_results = resp_json['totalResults']

            if total_results == 0:
                print(f'No results found for {context}')
                return None

            return resp_json

        except requests.RequestException as e:
            if resp.status_code == 429:  # Rate limit exceeded, backing off according to NVD API guidelines
                print(f"Rate limit exceeded, retrying in 30 seconds...")
                time.sleep(30)
                continue
            else:
                print(f"Error querying NVD API for {context}: {resp.status_code} - {resp.reason}. Retrying {retries - attempt - 1} more times...")
                time.sleep(1)
                continue

    print(f"Failed to fetch data from NVD for {context} after {retries} attempts.")
    return None

# Set the CVE search parameters
max_results = 2000     # Maximum number of results per query, set to 1 for testing, Maximum is 2000
#exact_cpe = True   # Functionality removed
search_days = 90    # set to 0 for full search, or set number of days to limit the search

# Calculate the date range
mod_end = datetime.datetime.now()
mod_start = datetime.datetime.now() - datetime.timedelta(days=search_days)

# Declare and initialize the product list and table data arrays
product_list = []
cpe_list = []
table_data = []

# Check for a cpe list file first
#if os.path.isfile(CPELIST):

    # Open the CSV file for reading
#    csv_reader = csv.reader(open(CPELIST, 'r', newline=''))

    # Import each line into a new product object and append to list
#    for row in csv_reader:
#        new_cpe = row[0]
#        cpe_list.append(new_cpe)

#else:

# Check if the product list file exists
if not os.path.isfile(PRODUCTLIST):
    exit(f"Product list file '{PRODUCTLIST}' not found. Please create it with the required product information.")

# Open the CSV file for reading
csv_reader = csv.reader(open(PRODUCTLIST, 'r', newline=''))

# Import each line and convert if necessary to append to list
for row in csv_reader:
    if row[0].startswith('cpe:2.3'):
        # If the row starts with 'cpe:2.3', treat it as a CPE formatted string
        cpe_string = row[0]
    
    else:
        #else, treat it as a product entry with manufacturer, software, type, and version and construct a CPE string
        new_product = product(row[0], row[1], row[2], row[3])
        cpe_string = new_product.cpe_string()

    product_list.append(cpe_string)
    
# Loop through each product in the list
for cpe_string in product_list:

    # Encode the CPE string for use in the URL querystring
    cpe_match_str = urllib.parse.quote_plus(cpe_string)

    cpe_url=f"https://services.nvd.nist.gov/rest/json/cpes/2.0/?cpeMatchString={cpe_match_str}"
    #print(cpe_url)

    cpe_results = query_nvd(cpe_url, f"{cpe_string}", MAXRETRIES)

    # If we got results, we will now extract the CPE names
    if cpe_results is not None and 'products' in cpe_results:

        for cpe in cpe_results['products']:
            # Append the CPE name to the list
            cpe_list.append(cpe['cpe']['cpeName'])

# If we have a CPE list, we will now look for CVEs
if len(cpe_list) == 0:
    exit("No CPEs found. Please check your product list or CPE list file.")
    
# For each matching CPE we will now look for CVEs
for cpe in cpe_list:

    # Encode the CPE name and date range for use in the CVE querystring
    cpe_name_str = urllib.parse.quote_plus(cpe)
    mod_end_str = urllib.parse.quote_plus(mod_end.strftime("%Y-%m-%dT%H:%M:%S"))
    mod_start_str = urllib.parse.quote_plus(mod_start.strftime("%Y-%m-%dT%H:%M:%S"))
    
    if search_days > 0:    
        cve_url=f"https://services.nvd.nist.gov/rest/json/cves/2.0/?cpeName={cpe_name_str}&lastModStartDate={mod_start_str}&lastModEndDate={mod_end_str}&resultsPerPage={max_results}"
    else:
        cve_url=f"https://services.nvd.nist.gov/rest/json/cves/2.0/?cpeName={cpe_name_str}&resultsPerPage={max_results}"

    print(cve_url)

    cve_results = query_nvd(cve_url, cpe, MAXRETRIES)

    # If we got results, we will now extract the CPE matches
    if cve_results is not None and 'vulnerabilities' in cve_results:

        # Saving json results to a file for debugging purposes
#        with open(f"Python/test_data/cve_results_{cpe.replace(':', '_').replace('*', '')}.json", 'w') as f:
#            json.dump(cve_results, f, indent=4)   

        for cve in cve_results['vulnerabilities']:

            #find our cpe match
            for cpeMatch in cve['cve']['configurations'][0]['nodes'][0]['cpeMatch']:

                if cpeMatch['criteria'].split('*',1)[0] in cpe:

                    from packaging.version import Version
                    cpe_version = cpe.split(':')[5]  # Extract the version from the CPE string for comparison
                    
                    # To avoid possible duplicates where multiple versions are included in the CPE
                    if ('versionStartIncluding' in cpeMatch and 'versionEndExcluding' in cpeMatch) and \
                        (Version(cpe_version) < Version(cpeMatch['versionStartIncluding']) or Version(cpe_version) >= Version(cpeMatch['versionEndExcluding'])):

                        # Skip this CPE match as it does not match the version criteria
                        continue    
                    
                    # To avoid further duplicates where multiple cpe matches are included in the CVE
                    elif ('versionStartIncluding' not in cpeMatch or 'versionEndExcluding' not in cpeMatch) and \
                        (cpe.split('*',1)[0] not in cpeMatch['criteria']):

                         # Skip this CPE match as it does not match the cpe criteria completely
                        continue 
                    else:

                        id= cve['cve']['id'] if 'id' in cve['cve'] else 'N/A'
                        cpeSearch = cpe
                        sourceIdentifier = cve['cve']['sourceIdentifier'] if 'sourceIdentifier' in cve['cve'] else 'N/A'
                        published = cve['cve']['published'] if 'published' in cve['cve'] else 'N/A'
                        lastModified = cve['cve']['lastModified'] if 'lastModified' in cve['cve'] else 'N/A'
                        vulnStatus = cve['cve']['vulnStatus'] if 'vulnStatus' in cve['cve'] else 'N/A'
                        descriptions = cve['cve']['descriptions'] if 'descriptions' in cve['cve'] else [{'value': 'N/A'}]

                        if 'cvssMetricV31' in cve['cve']['metrics']:
                            version = "3.1"
                            source= cve['cve']['metrics']['cvssMetricV31'][0]['source'] if 'cvssMetricV31' in cve['cve']['metrics'] else 'N/A'
                            baseScore = cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['baseScore'] if 'cvssMetricV31' in cve['cve']['metrics'] else 'N/A'
                            baseSeverity = cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['baseSeverity'] if 'cvssMetricV31' in cve['cve']['metrics'] else 'N/A'
                            attackVector = cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['attackVector'] if 'cvssMetricV31' in cve['cve']['metrics'] else 'N/A'
                            privilegesRequired = cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['privilegesRequired'] if 'cvssMetricV31' in cve['cve']['metrics'] else 'N/A'
                            userInteraction = cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['userInteraction'] if 'cvssMetricV31' in cve['cve']['metrics'] else 'N/A'
                            confidentialityImpact = cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['confidentialityImpact'] if 'cvssMetricV31' in cve['cve']['metrics'] else 'N/A'
                            integrityImpact = cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['integrityImpact'] if 'cvssMetricV31' in cve['cve']['metrics'] else 'N/A'
                            availabilityImpact = cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['availabilityImpact'] if 'cvssMetricV31' in cve['cve']['metrics'] else 'N/A'
                            exploitabilityScore = cve['cve']['metrics']['cvssMetricV31'][0]['exploitabilityScore'] if 'cvssMetricV31' in cve['cve']['metrics'] else 'N/A'
                            impactScore = cve['cve']['metrics']['cvssMetricV31'][0]['impactScore'] if 'cvssMetricV31' in cve['cve']['metrics'] else 'N/A'

                        elif 'cvssMetricV30' in cve['cve']['metrics']:
                            version = "3.0"
                            source = cve['cve']['metrics']['cvssMetricV30'][0]['source'] if 'cvssMetricV30' in cve['cve']['metrics'] else 'N/A'
                            baseScore = cve['cve']['metrics']['cvssMetricV30'][0]['cvssData']['baseScore'] if 'cvssMetricV30' in cve['cve']['metrics'] else 'N/A'
                            baseSeverity = cve['cve']['metrics']['cvssMetricV30'][0]['cvssData']['baseSeverity'] if 'cvssMetricV30' in cve['cve']['metrics'] else 'N/A'
                            attackVector = cve['cve']['metrics']['cvssMetricV30'][0]['cvssData']['attackVector'] if 'cvssMetricV30' in cve['cve']['metrics'] else 'N/A'
                            privilegesRequired = cve['cve']['metrics']['cvssMetricV30'][0]['cvssData']['privilegesRequired'] if 'cvssMetricV30' in cve['cve']['metrics'] else 'N/A'
                            userInteraction = cve['cve']['metrics']['cvssMetricV30'][0]['cvssData']['userInteraction'] if 'cvssMetricV30' in cve['cve']['metrics'] else 'N/A'
                            confidentialityImpact = cve['cve']['metrics']['cvssMetricV30'][0]['cvssData']['confidentialityImpact'] if 'cvssMetricV30' in cve['cve']['metrics'] else 'N/A'
                            integrityImpact = cve['cve']['metrics']['cvssMetricV30'][0]['cvssData']['integrityImpact'] if 'cvssMetricV30' in cve['cve']['metrics'] else 'N/A'
                            availabilityImpact = cve['cve']['metrics']['cvssMetricV30'][0]['cvssData']['availabilityImpact'] if 'cvssMetricV30' in cve['cve']['metrics'] else 'N/A'
                            exploitabilityScore = cve['cve']['metrics']['cvssMetricV30'][0]['exploitabilityScore'] if 'cvssMetricV30' in cve['cve']['metrics'] else 'N/A'
                            impactScore = cve['cve']['metrics']['cvssMetricV30'][0]['impactScore'] if 'cvssMetricV30' in cve['cve']['metrics'] else 'N/A'

                        else:
                            version = "2.0"
                            source= cve['cve']['metrics']['cvssMetricV2'][0]['source'] if 'cvssMetricV2' in cve['cve']['metrics'] else 'N/A'
                            baseScore = cve['cve']['metrics']['cvssMetricV2'][0]['cvssData']['baseScore'] if 'cvssMetricV2' in cve['cve']['metrics'] else 'N/A'
                            baseSeverity = cve['cve']['metrics']['cvssMetricV2'][0]['baseSeverity'] if 'cvssMetricV2' in cve['cve']['metrics'] else 'N/A'
                            attackVector = cve['cve']['metrics']['cvssMetricV2'][0]['cvssData']['accessVector'] if 'cvssMetricV2' in cve['cve']['metrics'] else 'N/A'
                            privilegesRequired = cve['cve']['metrics']['cvssMetricV2'][0]['cvssData']['authentication'] if 'cvssMetricV2' in cve['cve']['metrics'] else 'N/A'
                            userInteraction = cve['cve']['metrics']['cvssMetricV2'][0]['userInteractionRequired'] if 'cvssMetricV2' in cve['cve']['metrics'] else 'N/A'
                            confidentialityImpact = cve['cve']['metrics']['cvssMetricV2'][0]['cvssData']['confidentialityImpact'] if 'cvssMetricV2' in cve['cve']['metrics'] else 'N/A'
                            integrityImpact = cve['cve']['metrics']['cvssMetricV2'][0]['cvssData']['integrityImpact'] if 'cvssMetricV2' in cve['cve']['metrics'] else 'N/A'
                            availabilityImpact = cve['cve']['metrics']['cvssMetricV2'][0]['cvssData']['availabilityImpact'] if 'cvssMetricV2' in cve['cve']['metrics'] else 'N/A'
                            exploitabilityScore = cve['cve']['metrics']['cvssMetricV2'][0]['exploitabilityScore'] if 'cvssMetricV2' in cve['cve']['metrics'] else 'N/A'
                            impactScore = cve['cve']['metrics']['cvssMetricV2'][0]['impactScore'] if 'cvssMetricV2' in cve['cve']['metrics'] else 'N/A'                            

                        weaknesses = cve['cve']['weaknesses'] if 'weaknesses' in cve['cve'] else [{'description': [{'value': 'N/A'}]}]
                        vulnerable = cpeMatch['vulnerable'] if 'vulnerable' in cpeMatch else 'N/A'
                        criteria = cpeMatch['criteria'] if 'criteria' in cpeMatch else 'N/A'    
                        versionStartIncluding = cpeMatch['versionStartIncluding'] if 'versionStartIncluding' in cpeMatch else 'N/A'
                        versionEndExcluding = cpeMatch['versionEndExcluding'] if 'versionEndExcluding' in cpeMatch else 'N/A'
                                                                        
                        # Append this CVE information to the table data
                        table_data.append([id,
                                        cpeSearch,
                                        sourceIdentifier,
                                        published,
                                        lastModified,
                                        vulnStatus,
                                        descriptions[0]['value'],
                                        version,
                                        source,
                                        baseScore,
                                        baseSeverity,
                                        attackVector,
                                        privilegesRequired,
                                        userInteraction,
                                        confidentialityImpact,
                                        integrityImpact,
                                        availabilityImpact,
                                        exploitabilityScore,
                                        impactScore,
                                        weaknesses[0]['description'][0]['value'],
                                        vulnerable,
                                        criteria,
                                        versionStartIncluding,
                                        versionEndExcluding
                                        ])

                                           

# Having completed loops the table_data should contain all found CVEs

# Calculate the range for the table in the Excel file based on the number of entries and columns required
#print(f"Length: {len(table_data)}, width: {chr(len(table_data[0]) + 96) if table_data else 0}")

if len(table_data) == 0:
    exit("No CVEs found for the provided CPEs.")
       
table_range = "A1:" + chr(len(table_data[0]) + 96).upper() + str(1+len(table_data))

# If the file already exists, delete it to avoid appending to an old file
if os.path.isfile(FILENAME):
    os.remove(FILENAME)
    print(f"Deleted existing file ready for new data: {FILENAME}")
    
# Create a new Excel file and add a worksheet
workbook = xlsxwriter.Workbook(FILENAME)
worksheet = workbook.add_worksheet()

# Write table data and headers to the worksheet in a table format
print(f"Writing {len(table_data)} entries to {FILENAME}...")
worksheet.add_table(table_range, {'data': table_data, 'columns': [{'header': 'id'},
                                                            {'header': 'configurations.cpeSearch'},
                                                            {'header': 'sourceIdentifier'},
                                                            {'header': 'published'},
                                                            {'header': 'lastModified'},
                                                            {'header': 'vulnStatus'},
                                                            {'header': 'description'},
                                                            {'header': 'configurations.version'},
                                                            {'header': 'cvss.source'},
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
                                                            {'header': 'configurations.criteria'},
                                                            {'header': 'configurations.versionStartIncluding'},
                                                            {'header': 'configurations.versionEndExcluding'}
                                                            ]})

# Close and save the workbook
workbook.close()






