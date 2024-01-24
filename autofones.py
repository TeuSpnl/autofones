from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# Create a new instance of the Edge driver
driver = webdriver.Edge()

# Loop through IP addresses from 192.168.254.201 to 192.168.254.225
for i in range(202, 226):
    ip_address = f"192.168.254.{i}"

    # Open a new tab
    driver.execute_script("window.open('about:blank', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])

    # Navigate to the IP address
    driver.get(f"http://{ip_address}/")

    # Check the response
    if "couldn't find" in driver.page_source:
        # Close the tab if the response indicates the page couldn't be found
        driver.close()
        
    if "Erro de privacidade" in driver.page_source:
        # Continue loading the page if the response indicates it's not safe
        pass
    elif "login" in driver.page_source and "password" in driver.page_source:
        # Fill in the login and password fields with "admin" if prompted
        username_field = driver.find_element_by_name("username")
        password_field = driver.find_element_by_name("password")
        username_field.send_keys("admin")
        password_field.send_keys("admin")
        password_field.send_keys(Keys.RETURN)

    # Print the title and URL of the current tab
    print('Título:', driver.title)
    print('URL:', driver.current_url)

# Close the browser
driver.quit()
