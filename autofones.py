import os
from time import sleep
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
# Remove unecessary warning on terminal
opts.add_experimental_option('excludeSwitches', ['enable-logging'])
assert opts.headless  # Guarantee that the browser is headless

# Create a new instance of the Edge driver
driver = Edge(options=opts)

# Set the timeout for a page load to 2 secs
driver.set_page_load_timeout(2)

# Set the login credentials as headers to the browser – This skips the pop up login page
driver.execute_cdp_cmd("Network.enable", {})
credentials = base64.b64encode("admin:admin".encode()).decode()
headers = {'headers': {'authorization': 'Basic ' + credentials}}
driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', headers)


def log(i, type=0):
    """   Gera um arquivo txt mostrando a mensagem que o programa passou na chamada    """

    try:
        # Abre o arquivo pra editá-lo
        log = open(
            f"ips.txt", 'at+', encoding='utf-8')

    except (FileNotFoundError):  # Tenta criar o arquivo caso ele não exista
        try:
            log = open(
                f"ips.txt", 'at', encoding='utf-8')

        except Exception as e:
            print(f"Erro ao criar txt do log!\nErro: {e.__class__}")

    except Exception as e:
        print(text=f"Erro ao criar log!\nErro: {e.__class__}")

    # Writes the message according to its purpose
    if type == 0:
        log.write(f"Não abriu o 192.168.254.2{i:02d}\n\n")
    elif type == 1:
        log.write(f"192.168.254.2{i:02d} em conversação\n\n")
    else:
        pass

    log.close()


def print_timeout_trying_next(i):
    """Prints a message and tries the next page. If the i value is higher than 25, quits the program.

    Args:
        i (int): Final number of the phone
    """
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


def wait(element, i, type=0, continua=0):
    """Waits for the element to be in the page. If it takes too long, tries the next page, or stops the program.

    Args:
        element (String): The id of the element to wait for.
        i (int): The final number of the phone
        type (int): The type of search to be done. 0 for presence, 1 for not empty text.
        continua (int, optional): When the program shouldn't continue to run when this error happens, set this to 1. Defaults to 0.
    """
    try:
        result = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, f"{element}"))
        )

        # If the type is 1, waits for the element to have a non empty text
        if type == 1:
            result = WebDriverWait(driver, 5).until(
                lambda driver: driver.find_element(
                    By.ID, f"{element}").get_attribute("value") != ""
            )

        if result:
            pass

    except TimeoutException:
        if continua == 1:
            print(f"\n\nFatal timeout error. Shutting Down. \n\n \
                    \n############################### \
                    \n###############################\n")
            driver.quit()
            quit()

        else:
            print_timeout_trying_next(i)

    except Exception as e:
        print(f"\n\nFatal wait unknown error. Shutting Down: \n\n{e} \
                  \n############################### \
                  \n###############################\n")
        driver.quit()
        quit()


def opening_page(start=12):
    """ Tries to open the page and log in. If it fails, it tries the next page.

    Args:
        start (int, optional): The end of the ip, that's equal to the 2 last numbers of the phone. Defaults to 12.
    """
    url = f"http://192.168.254.2{start:02d}/"

    try:
        # Open the browser and navigate to the page
        driver.get(url)
        
        # Refresh to make sure the auth popup goes away
        driver.set_page_load_timeout(10)
        driver.refresh()
        driver.set_page_load_timeout(2)

    # If the page takes more than 2 seconds to load, tries the next link. If some another error occurs, quits the browser.
    except (WebDriverException, TimeoutException) as e:
        log(start)
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

    # It waits for the page to load to make the changes
    wait("label_operation_time", start, 0)

    # wan(start)
    account(start)
    restart()

    while start <= 25:
        start += 1
        opening_page(start)


def restart():
    # Open the restart menu
    driver.find_element("id", "linkMenuRestart").click()

    # Wait for the element "resetSystem" to appear
    wait("resetSystem", 0, 0, 1)

    # Click on the button to restart the phone
    driver.find_element("id", "resetSystem").click()

    # Accepts the alert to restart the phone
    alert = driver.switch_to.alert
    alert.accept()

    # Tries to print the alert text – often doen't work and it's just a debuging thing
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
    # Open the Wan settings page
    driver.find_element("id", "linkMenuNetwork").click()
    sleep(.2)
    driver.find_element("id", "linkMenuNetworkWan").click()

    # Wait until the input with id "ETHAddressIP" is not empty
    wait("ETHAddressIP", i, 1)

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
    wait("enable_qos_layer_3", i, 0, 1)

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


def account(i):
    # Click on the account settings
    driver.find_element("id", "linkMenuAccount").click()

    # Wait until the input with id "line_caller_name" is not empty
    wait("line_caller_name", i, 1)

    outbounds()
    # account_adv_settings(i)

    # Save new configs
    driver.find_element("id", "saveButton").click()

    # If the telephone being used, it registers and move on
    answer = driver.find_element(By.CLASS_NAME, "ng-binding")
    sleep(.1)
    if "Em conversação" in answer.text:
        log(i, 1)


def outbounds():
    Add_Fst_Sip = driver.find_element("id", "outbound_proxy_ip")
    
    Add_Fst_Sip.clear()
    
    Add_Fst_Sip.send_keys("187.50.251.28")
    
        
    # Find the input for the Secondary SIP settings
    Sec_Sip = driver.find_element("id", "sip_server2")
    Sec_Port_Sip = driver.find_element("id", "sip_server_port2")

    # Clear the input field of the secondary SIP settings
    Sec_Sip.clear()
    Sec_Port_Sip.clear()

    # Unselect the option to the outbound proxy
    if driver.find_element("id", "outbound_proxy2").is_selected():
        driver.find_element("id", "outbound_proxy2").click()


def account_adv_settings(i):
    # Click on advanced settings
    driver.find_element("id", "li_Avançado").click()

    # Wait until the input with id "register_time" is not empty
    wait("register_time", i, 1)

    # Find the input for the Min and Max RTP ports
    MinRtpPort = driver.find_element("id", "MinPortRTP")
    MaxRtpPort = driver.find_element("id", "MaxPortRTP")

    # Clear the input fields
    MinRtpPort.clear()
    MaxRtpPort.clear()

    # Set the values for the Min and Max RTP ports
    MinRtpPort.send_keys("16384")
    MaxRtpPort.send_keys("65535")


# Delete the log to start a new one
try:
    os.remove('ips.txt')
    print("ips.txt apagado com sucesso\n\
            \n############################### \
            \n###############################\n")
except Exception as e:
    pass

opening_page(1)

# Close the browser
driver.quit()
