#---------------------------------------------------------------------------------------
# Name:        url_example.py
# Purpose:     Example of using the urllib module
#
# Author:      Jesse Morgan
#
# Created:     03/01/2026
# Licence:     None
# Note:        Be sure to run: pip install --upgrade certifi
#---------------------------------------------------------------------------------------
import urllib.request
import requests

def main():
    # Read from www.esri.com
    url = urllib.request.urlopen("https://www.esri.com/")
    html = url.read()
    print(html)

    # Download a zip file
    url = "https://opendata.toronto.ca/gcc/bikeways_wgs84.zip"
    file = "bikeways.zip"
    urllib.request.urlretrieve(url, file)

    # Read a Text file from a website
    url = "https://wordpress.org/plugins/readme.txt"
    content = urllib.request.urlopen(url)

    for line in content:
        print(line)

    # Use the request module to download a zip file
    try:
        filename = "bikeways2.zip"
        response = requests.get(url)
        response.raise_for_status() # Check if the download was successful (status code 200-299)

        # Write the content to a local file in binary write mode ('wb')
        with open(filename, "wb") as f:
            f.write(response.content)

        print(f"Successfully downloaded {filename}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
