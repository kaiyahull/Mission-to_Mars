# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Set up executable path
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    
    news_title, news_paragraph = mars_news(browser)
    hemisphere_image_urls = hemi_data(browser)
 

    # Run all scraping funtions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_motified": dt.datetime.now(),
        "hemispheres": hemisphere_image_urls,
        
    }

    browser.quit()
    return data

def mars_news(browser):    
    # Visit the mars masa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Set up HTML parser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
  
    except AttributeError:
        return None, None

    return news_title, news_p

def hemi_data(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    html = browser.html
    hemi_soup = soup(html, 'html.parser')

    hemisphere_image_urls = []
    hemispheres = {}
    hemi_link= hemi_soup.find_all('div', class_="description")

    try:
        for x in hemi_link:
            link = x.find('a', class_="itemLink product-item")
            img_link = link['href']
            link_url=f'{url}{img_link}'
            browser.visit(link_url)
            html_2 = browser.html
            h_soup = soup(html_2, 'html.parser')
            full_image = h_soup.find('div', class_='downloads')
            full_image = full_image.find_all('a', target="_blank")[0]['href']
            hemi_url = f'{url}{full_image}'
            img_title = h_soup.find('h2', class_='title').get_text()
            hemispheres["img_url"] = hemi_url
            hemispheres["img_title"] = img_title
            hemisphere_image_urls.append(hemispheres)
            hemispheres={}

    except AttributeError:
        return None

    return hemisphere_image_urls


# ### JPL Space Images Featured Image


# Visit URL
def featured_image(browser):
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None


    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url
 

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=["Description", "Mars", "Earth"]
    df.set_index("Description", inplace=True)

    classes='table table-striped table-bordered table-hover'
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes=classes)




# classes="table table-striped"
if __name__ == "__main__":
    # If running as a script, print scraped data
    print(scrape_all())


