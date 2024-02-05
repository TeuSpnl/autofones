from time import sleep
import tkinter as tk
import pyautogui as ptgui
import base64

from selenium.webdriver import Edge
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select


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


def print_timeout_trying_next(i):
    if i <= 25:
        print(f"\n\nTimeout. Trying next: \n\n \
                \n############################### \
                \n###############################\n")
        opening_page(i + 1)
    else:
        print(f"\n\nTimeout. Max tries. Shutting down: \n\n \
                \n############################### \
                \n###############################\n")
        driver.quit()
        quit()


def wait_presence(elemento, i, continua=0):
    # Waits for the page to load and then Open the IP settings page
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, f"{elemento}"))
        )

        if element:
            pass

    except TimeoutException as e:
        if continua == 1:
            print(f"\n\nFatal timeout error. Shutting Down. \n\n \
                    \n############################### \
                    \n###############################\n")
            driver.quit()

        else:
            print_timeout_trying_next(i)


def opening_page(start=12):
    """ Tries to open the page and log in. If it fails, it tries the next page.

    Args:
        url (int, optional): _description_. Defaults to 12.
    """
    url = f"http://182.17.2.2{start:02d}/"

    try:
        # Set the login credentials as headers to the bwoser – This skips the pop up login page
        driver.execute_cdp_cmd("Network.enable", {})
        credentials = base64.b64encode("admin:admin".encode()).decode()
        headers = {'headers': {'authorization': 'Basic ' + credentials}}
        driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', headers)

        # Open the browser and navigate to the page
        driver.get(url)
        sleep(.5)
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()

    # If the page takes more than 2 seconds to load, tries the next link. If some another error occurs, quits the browser.
    except (WebDriverException, TimeoutException) as e:
        print_timeout_trying_next(start)

    except Exception as e:
        print(f"\n\nUNKNOWN ERROR: \n\n{e} \
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
    wait_presence("label_operation_time", start)

    wan(start)

    while start <= 25:
        opening_page(start)
        start += 1


def restart():
    driver.find_element("id", "linkMenuRestart").click()
    wait_presence("resetSystem", 0, 1)
    driver.find_element("id", "resetSystem").click()
    alert = driver.switch_to.alert
    alert.accept()
    try:
        print(f"\nAlert text: {alert.text} \
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
    wait_presence("linkMenuNetwork", i)
    driver.find_element("id", "linkMenuNetwork").click()
    sleep(.2)
    driver.find_element("id", "linkMenuNetworkWan").click()

    # Wait until the input with id "ETHAddressIP" is not empty
    try:
        element = WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element_value((By.ID, "ETHAddressIP"), "")
        )

        if element:
            pass

    except TimeoutException as e:
        print_timeout_trying_next(i)

    # Put as DHCP
    sleep(.5)
    if not driver.find_element("id", "ETHActivateDHCPClient_static").is_selected():
        driver.find_element("id", "ETHActivateDHCPClient_static").click()

    change_ddos(i)

    # change_ip(i)
    # change_dns()

    # Save the changes and restart the phone
    sleep(.2)
    driver.find_element("id", "saveButton").click()
    restart()


def change_ip(i):

    ip_value = f"182.17.2.2{i:02d}"
    mask_value = "255.255.255.0"
    gateway_value = "182.17.2.254"

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


def change_ddos(i):
    # Change the tab to the advanced settings
    driver.find_element("id", "li_Avançado").click()

    # Waits for the page to load and then activate QoS settings
    wait_presence("enable_qos_layer_3", i, 1)

    # Activate the QoS settings
    if not driver.find_element("id", "enable_qos_layer_3").is_selected():
        driver.find_element("id", "enable_qos_layer_3").click()

    # Find the QoS type elements
    sip_element = driver.find_element("id", "sip_type")
    sip_select = Select(sip_element)
    rtp_element = driver.find_element("id", "rtp_type")
    rtp_select = Select(rtp_element)
    dados_element = driver.find_element("id", "data_type")
    dados_select = Select(dados_element)

    # Select the DSCP option for all the QoS types
    sip_select.select_by_visible_text("DSCP")
    rtp_select.select_by_visible_text("DSCP")
    dados_select.select_by_visible_text("DSCP")

    # Find the QoS value elements
    sip_value = driver.find_element("id", "sip_value")
    rtp_value = driver.find_element("id", "rtp_value")
    dados_value = driver.find_element("id", "data_type_value")

    # Clear the input fields and set the values
    sip_value.clear()
    rtp_value.clear()
    dados_value.clear()

    # Set the values as EF (Expedited Forwarding), or 46, for higher priority
    sip_value.send_keys("46")
    rtp_value.send_keys("46")
    dados_value.send_keys("46")


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
