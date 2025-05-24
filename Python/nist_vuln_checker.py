import requests
import datetime
import urllib.parse

# Constants
APPLICATION="a"
OPERATINGSYSTEM="o"
HARDWARE="h"

# Define a product class to hold product information
class product:
  def __init__(self, manufacturer, software, type, version):
    self.manufacturer = manufacturer
    self.software = software
    self.type = type
    self.version = version

# Set the CVE search parameters
mod_end = datetime.datetime.now()
mod_start = datetime.datetime.now() - datetime.timedelta(days=120)
max_results = 2

# Create a list of products to check for vulnerabilities
productlist = [product("solarwinds","orion_platform",APPLICATION,"2024"),
               product("fortinet","fortios",OPERATINGSYSTEM,"7.2.7"),
               product("checkpoint","security_gateway",APPLICATION,"r81.10"),
               product("checkpoint","security_gateway",APPLICATION,"r81.20"),
               product("checkpoint","ssl_network_extender",APPLICATION,"r81.10"),
               product("checkpoint","ssl_network_extender",APPLICATION,"r81.20"),
               product("checkpoint","ipsec_vpn",APPLICATION,"r81.20"),
               product("checkpoint","ipsec_vpn",APPLICATION,"r81.10"),
               product("checkpoint","ipsec_vpn",APPLICATION,"r81.20"),
               product("checkpoint","management_server",APPLICATION,"r81.10"),
               product("checkpoint","management_server",APPLICATION,"r81.20"),
               product("checkpoint","smart_console",APPLICATION,"r81.10"),
               product("checkpoint","smart_console",APPLICATION,"r81.20"),
               product("checkpoint","secureclient_ng",APPLICATION,"r81"),
               product("checkpoint","gaia_portal",APPLICATION,"r81.10"),
               product("checkpoint","gaia_portal",APPLICATION,"r81.20"),
               product("checkpoint","ssl_network_extender",APPLICATION,"r81.10"),
               product("checkpoint","ssl_network_extender",APPLICATION,"r81.20"),
               product("checkpoint","gaia_os",OPERATINGSYSTEM,"r81.10"),
               product("checkpoint","gaia_os",OPERATINGSYSTEM,"r81.20"),
               product("checkpoint","multi-domain_management_firmware",OPERATINGSYSTEM,"r81"),
               product("checkpoint","quantum_security_management_firmware",OPERATINGSYSTEM,"r81")]

for product in productlist:

    cpe_string = "cpe:2.3:" + \
        product.type + ":" + \
        product.manufacturer + ":" + \
        product.software + ":" + \
        product.version + ":*:*:*:*:*:*:*"
 
    print(f"CPE String: {cpe_string}")
    
    # Encode the CPE string for use in the URL
    cpe_match_str = urllib.parse.quote_plus(cpe_string)

    cpe_url=f"https://services.nvd.nist.gov/rest/json/cpes/2.0/?cpeMatchString={cpe_match_str}"
    #print(cpe_url)

    try:
        resp = requests.get(cpe_url)
        resp_json = resp.json()

        total_results=resp_json['totalResults']

        if total_results == 0:
            print(f'No entry found for {product.manufacturer} {product.software} ({product.type}) version {product.version}')
            continue
            
    except:
        print('failed to fetch from nvd: ' + str(resp.status_code) + ' ' + resp.reason)
        continue
    
    for cpe in resp_json['products']:
       
        print(f"{cpe['cpe']['cpeName']}")
        
        cpe_name_str = urllib.parse.quote_plus(cpe['cpe']['cpeName'])
        mod_end_str = urllib.parse.quote_plus(mod_end.strftime("%Y-%m-%dT%H:%M:%S"))
        mod_start_str = urllib.parse.quote_plus(mod_start.strftime("%Y-%m-%dT%H:%M:%S"))
        
        cve_url=f"https://services.nvd.nist.gov/rest/json/cves/2.0/?cpeName={cpe_name_str}&lastModStartDate={mod_start_str}&lastModEndDate={mod_end_str}&resultsPerPage={max_results}"
        #print(cve_url)

        try:
            resp = requests.get(cve_url)
            resp_json = resp.json()

            total_results=resp_json['totalResults']

            if total_results == 0:
                print(f'No vulnerabilities found for {cpe["cpe"]["cpeName"]}')
                continue
            
            if total_results > max_results:
                print(f'There are {str(total_results)} results, we scanned only the first {str(max_results)} ')

        except:
            print('failed to fetch from nvd: ' + str(resp.status_code) + ' ' + resp.reason)
            continue

        for cve in resp_json['vulnerabilities']:

            print(f"{cve['cve']['id']}")
            
            #print(f"{cve['cve']['id']}: \
            #    {cve['cve']['metrics']['cvssMetricV31'][0]['source']} - \
            #    {cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['baseScore']} - \
            #    {cve['cve']['descriptions'][0]['value']}")





