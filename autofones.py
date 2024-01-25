from selenium.webdriver import Edge
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException

# Set the browser as headless
opts = Options()
opts.headless = True
assert opts.headless  # Guarantee that the browser is headless

# Create a new instance of the Edge driver
driver = Edge(options=opts)


def opening_page(url = 'http://192.168.254.212'):
    time_limit = 2
    
    try:
        wait = WebDriverWait(driver, time_limit)
        
        # Open the browser and navigate to the page
        driver.get(url)
        
        wait.until(lambda driver: driver.find_element_by_id("proceed-link"))

    # If the page takes more than 2 seconds to load, close the browser
    except WebDriverException as wde or TimeoutException as te:
        if "net::ERR_CONNECTION_TIMED_OUT" in str(wde):
            opening_page()
        else:
            print(wde)
            driver.quit()

    except Exception as e:
        print(e)
        driver.close()

    loging_in()


def loging_in():
    if "Erro de privacidade" in driver.page_source:
        # Find the hidden anchor element
        continue_button = driver.find_element("id", "proceed-link")

        # Execute a click event on the element using JavaScript
        driver.execute_script("arguments[0].click();", continue_button)


opening_page()


# # Loop through IP addresses from 192.168.254.201 to 192.168.254.225
# for i in range(202, 226):
#     ip_address = f"192.168.254.{i}"

#     # Open a new tab
#     driver.execute_script("window.open('about:blank', '_blank');")
#     driver.switch_to.window(driver.window_handles[-1])

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
#         # Fill in the login and password fields with "admin" if prompted
#         username_field = driver.find_element_by_name("username")
#         password_field = driver.find_element_by_name("password")
#         username_field.send_keys("admin")
#         password_field.send_keys("admin")
#         password_field.send_keys(Keys.RETURN)

#     # Print the title and URL of the current tab
#     print('Título:', driver.title)
#     print('URL:', driver.current_url)

# Close the browser
driver.quit()
