from selenium.webdriver import Edge
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By

import base64

# Set some configurations to the browser
opts = Options()
opts.headless = True  # Set te browser to headless mode
opts.add_argument("--ignore-certificate-errors")  # Ignore certificate errors
opts.add_argument("--ignore-ssl-errors")  # Ignore SSL errors
assert opts.headless  # Guarantee that the browser is headless

# Create a new instance of the Edge driver
driver = Edge(options=opts)

# Set the login credentials as headers to the bwoser – This skips the pop up login page
driver.execute_cdp_cmd("Network.enable", {})
credentials = base64.b64encode("admin:admin".encode()).decode()
headers = {'headers': {'authorization': 'Basic ' + credentials}}
driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', headers)

url = 'http://192.168.253.210/'  # Testing -- To delete

# Set the timeout for a page load
driver.set_page_load_timeout(2)


def opening_page(url='http://192.168.253.212'):
    """ Tries to open the page and log in. If it fails, it tries the next page.

    Args:
        url (str, optional): _description_. Defaults to 'http://admin:admin@192.168.253.212'.
    """
    try:
        # Open a new tab
        driver.execute_script("window.open('about:blank', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])

        # Open the browser and navigate to the page
        driver.get(url)

    # If the page takes more than 2 seconds to load, tries the next link. If some another error occurs, quits the browser.
    except (WebDriverException, TimeoutException) as e:
        if "net::ERR_CONNECTION_TIMED_OUT" in str(e):
            print("Connection timed out. Retrying...")
            opening_page()
        else:
            print(e)
            driver.quit()

    except Exception as e:
        print(e)
        driver.close()

    # If the page loads, it logs in
    loging_in(driver)


def loging_in(driver):

    # If the certificate error appear, it solves it
    if "Erro de privacidade" in driver.page_source or "Privacy error" in driver.page_source:
        # Find the hidden anchor element
        continue_button = driver.find_element("id", "proceed-link")

        # Execute a click event on the element using JavaScript
        driver.execute_script("arguments[0].click();", continue_button)


opening_page()


# # Loop through IP addresses from 192.168.254.201 to 192.168.254.225
# for i in range(202, 226):
#     ip_address = f"192.168.254.{i}"


#     # Navigate to the IP address
#     driver.get(f"http://{ip_address}/")

#     # Check the response
#     if "couldn't find" in driver.page_source:
#         # Close the tab if the response indicates the page couldn't be found
#         driver.close()

#     if "Erro de privacidade" in driver.page_source:
#         # Continue loading the page if the response indicates it's not safe
#         pass
#     elif "login" in driver.page_source and "password" in driver.page_source:

#     # Print the title and URL of the current tab
#     print('Título:', driver.title)
#     print('URL:', driver.current_url)

# Close the browser
driver.quit()
