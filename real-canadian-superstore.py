# selenium allows us to interact with HTML elements, such as clicking on a page using automation; in this case we will use it for specifying location on the Costco website
from selenium import webdriver
# to let us type stuff from our code we need to import Keys:
from selenium.webdriver.common.keys import Keys
# selenium module that lets us make the web driver wait until a certain condition is met (browser is loaded enough)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# deal with elements not being present on page:
from selenium.common.exceptions import NoSuchElementException    

import pandas as pd 

# must specify where the web driver is located and create a variable that will call on the web driver for chrome
path = "/Applications/chromedriver101" 
driver = webdriver.Chrome(path)
# to make code easier to read, create variable for the url you want to use
url = "https://www.realcanadiansuperstore.ca/"

# specifying which costco CSV product list to get:
costco_path = '/Users/anjawu/Code/costco-deal-hunter/Coupons/editted/strippedbrand-costco-couponsMay30.csv'
costco_df = pd.read_csv(costco_path)

# Taking a column from Costco products and creating a list to iterate through
costco_products_list = costco_df['Product'].tolist()
costco_brand_list = costco_df['Brand'].tolist()
costco_price_list = costco_df['New Price'].tolist()

# Creating list to store all items to look for in the RCS website 
search_list = costco_products_list

# initializing final product list of comparable RCS items to Costco items
products_list = []

# to pull open the webpage:
driver.get(url)
wait = WebDriverWait(driver, 10)

# navigating RCS's webpage to select ON as region for flyer.
driver.implicitly_wait(10)
select_province = driver.find_element(By.XPATH, '//button[text()="Ontario"]').click()


try:
	# Waiting for page to load enough to get a search bar
	rcs_search = driver.find_element_by_xpath('//input[@class="search-input__input"]')

	for i, item in enumerate(search_list):
		# Clear search bar
		wait.until(
			EC.presence_of_element_located((By.XPATH, '//input[@class="search-input__input"]'))
		).clear()

		# Entering word into search bar
		wait.until(
			EC.presence_of_element_located((By.XPATH, '//input[@class="search-input__input"]'))
		).send_keys(item)

		# Hitting enter once search word has been entered
		wait.until(
			EC.presence_of_element_located((By.XPATH, '//input[@class="search-input__input"]'))
		).send_keys(Keys.RETURN)

		# Not all items have a search result, so we must try and check for NoSuchElementExceptions; return False if there is a search result present.
		try:
			driver.find_element_by_class_name("search-no-results__section-title")
			no_result = True
		except NoSuchElementException:
			no_result = False


		if no_result:
			i +=1
			# print(f'no result{i}')
			continue
		else:
			i

		# Waiting for page to load with search results
		product_detail = wait.until(
			EC.presence_of_element_located((By.XPATH, "//*[@id='odd']/div/div/div[3]"))
		)

		# Not all items have a brand, so we must try and check for NoSuchElementExceptions to get a product brand; return False if there is none.
		try:
			product_detail.find_element_by_class_name("product-name__item--brand")
			find_product_brand = True
		except NoSuchElementException:
			find_product_brand = False

		# If there is a product brand then we want to get the text from the element, otherwise return none.
		if find_product_brand: 
			product_brand = product_detail.find_element_by_class_name("product-name__item--brand").text
		else:
			product_brand = None

		# Get the product name and price per each item
		product_name = product_detail.find_element_by_class_name("product-name__item--name").text
		product_price = product_detail.find_element_by_class_name("price__value").text

		# Not all items have a unit price, so we must try and check for NoSuchElementExceptions to get a unit price; return False if there is none.
		try:
			product_detail.find_element_by_class_name("comparison-price-list__item__price__value")
			find_unit_price = True
		except NoSuchElementException:
			find_unit_price = False
		
		# If there is a unit price, we want to store the unit price per unit measurements, otherwise return none.
		if find_unit_price: 
			product_unit_price = product_detail.find_element_by_class_name("comparison-price-list__item__price__value").text
			product_unit = product_detail.find_element_by_class_name("comparison-price-list__item__price__unit").text
		else:
			product_unit_price = None	
			product_unit = None
	
		print(f'brand: {product_brand}, item: {product_name}, price: {product_price}, unit: {product_unit_price}{product_unit}')

		# creating dictionary to be able to append once, as opposed to for each data point pulled
		data = {
			'Costco-Brand' : costco_brand_list[i],
			'Costco-Item' : item,
			'Costco-Price' : costco_price_list[i],
			'RCS-Brand' : product_brand,
 			'RCS-Item' : product_name,
			'RCS-Price' : product_price,
			'RCS-Unit Price' : product_unit_price,
			'RCS-Unit Measure' : product_unit,
		}

		# appending each dictionary entry to our list
		products_list.append(data)

finally:
	driver.quit()

products = pd.DataFrame(products_list)

products.to_csv('/Users/anjawu/Code/real-canadian-superstore/CSVs/strippedbrand-rcss_costco_May30.csv')
