from time import sleep
import tkinter as tk
import pyautogui as ptgui
import base64

from selenium.webdriver import Edge
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Set some configurations to the browser
opts = Options()
opts.headless = True  # Set te browser to headless mode
opts.add_argument("--ignore-certificate-errors")  # Ignore certificate errors
opts.add_argument("--ignore-ssl-errors")  # Ignore SSL errors
assert opts.headless  # Guarantee that the browser is headless

# Create a new instance of the Edge driver
driver = Edge(options=opts)

# url = 'http://192.168.253.210/'  # Testing -- To delete

# Set the timeout for a page load
driver.set_page_load_timeout(2)


def opening_page(start=12):
    """ Tries to open the page and log in. If it fails, it tries the next page.

    Args:
        url (int, optional): _description_. Defaults to 12.
    """
    url = f"http://192.168.253.2{start:02d}/"

    try:
        # Set the login credentials as headers to the bwoser – This skips the pop up login page
        driver.execute_cdp_cmd("Network.enable", {})
        credentials = base64.b64encode("admin:admin".encode()).decode()
        headers = {'headers': {'authorization': 'Basic ' + credentials}}
        driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', headers)

        # Open the browser and navigate to the page
        driver.get(url)

    # If the page takes more than 2 seconds to load, tries the next link. If some another error occurs, quits the browser.
    except (WebDriverException, TimeoutException) as e:
        print(f"\nTimeout error. Trying next: \n\n\
                \n############################### \
                \n############################### \
                \n############################### \
                \n###############################\n")
        if start <= 25:
            opening_page(start + 1)
        else:
            driver.quit()
            quit()

    except Exception as e:
        print(f"\n\nUNKNOWN ERROR: \n\n{e} \
                  \n############################### \
                  \n############################### \
                  \n############################### \
                  \n###############################\n")
        driver.quit()
        quit()

    # If the certificate error appear, it solves it
    try:
        if "Erro de privacidade" in driver.page_source or "Privacy error" in driver.page_source:
            privacy_fix(driver)

    except Exception as e:
        print(f"\nPrivacy error: {e}")

    # It waits for the page to load and then changes the DNS settings
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "label_operation_time"))
        )

        if element:
            wan(start)

    except TimeoutException as e:
        print(f"\n\nTimeout. Trying next: \n\n \
                  \n############################### \
                  \n############################### \
                  \n############################### \
                  \n###############################\n")
        opening_page(start + 1)

    while start <= 25:
        opening_page(start)
        start += 1


def restart():
    driver.find_element("id", "linkMenuRestart").click()
    sleep(.5)
    driver.find_element("id", "resetSystem").click()
    alert = driver.switch_to.alert
    alert.accept()
    try:
        print(f"\nAlert text: {alert.text} \
                  \n############################### \
                  \n############################### \
                  \n############################### \
                  \n###############################\n")
    except Exception as e:
        print(f"\nMaybe there's no alert text.")


def privacy_fix(driver):
    """Pass through the privacy error page.

    Args:
        driver (webdriver): _description_
    """
    # Find the hidden anchor element
    continue_button = driver.find_element("id", "proceed-link")

    # Execute a click event on the element using JavaScript
    driver.execute_script("arguments[0].click();", continue_button)


def wan(i):
    # Open the IP settings page
    driver.find_element("id", "linkMenuNetwork").click()
    sleep(.2)
    driver.find_element("id", "linkMenuNetworkWan").click()

    # Wait until the input with id "ETHAddressIP" is not empty
    try:
        element = WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element_value((By.ID, "ETHAddressIP"), "")
        )

        if not element:
            print("timeout")
            opening_page(i + 1)

    except TimeoutException as e:
        print(f"\n\nTimeout. Trying next: \n\n \
                  \n############################### \
                  \n############################### \
                  \n############################### \
                  \n###############################\n")
        opening_page(i + 1)

    change_ip(i)
    change_dns()

    # Save the changes and restart the phone
    sleep(.5)
    driver.find_element("id", "saveButton").click()
    sleep(1)
    restart()


def change_ip(i):

    ip_value = f"192.168.253.2{i}"
    mask_value = "255.255.255.0"
    gateway_value = "192.168.253.254"

    # Upadate the IP settings and save
    ip = driver.find_element("id", "ETHAddressIP")
    mask = driver.find_element("id", "ETHNetMask")
    gateway = driver.find_element("id", "ETHDefGateway")
    sleep(.55)
    ip.clear()
    mask.clear()
    gateway.clear()
    ip.send_keys(ip_value)
    mask.send_keys(mask_value)
    gateway.send_keys(gateway_value)


def change_dns():
    """Change the DNS settings of the phone.
    """

    # ptgui.prompt(text='Insira o DNS primário', title='DNS primário' , default='')
    # ptgui.prompt(text='Insira o DNS secundários', title='DNS secundário' , default='')
    # DNS_screen = tk.Tk()
    # DNS_screen.title("DNS changer")
    # DNS_screen.geometry("500x350")

    # DNS_screen.mainloop()
    DNSprima = "1.1.1.1"
    DNSsecun = "1.0.0.1"

    # Upadate the DNS settings and save
    primary = driver.find_element("id", "ETHPriDNS")
    secondary = driver.find_element("id", "ETHSecDNS")
    sleep(.25)
    primary.clear()
    secondary.clear()
    primary.send_keys(DNSprima)
    secondary.send_keys(DNSsecun)


opening_page(1)


# # Loop through IP addresses from 192.168.254.201 to 192.168.254.225


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
