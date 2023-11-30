def collect_car_pages(bs):
    pages_links = bs.findAll('div', {'class':'active mui-style-14y9di7'})
    car_pages = []

    for pages in pages_links:
        car_page = pages.a.get("href")
        car_pages.append(car_page)

    return car_pages
