import time
from multiprocessing import Process

import requests
from bs4 import BeautifulSoup

TIME_OUT = 2

def parser():
    response = requests.get("https://www.bileter.ru/afisha/building/teatr_dojdey.html")
    soup = BeautifulSoup(response.text, "html.parser")
    performance_divs = soup.find_all(
        name="div", attrs={"class": "building-schedule-item hasTickets"}
    )
    performance_divs.extend(
        soup.find_all(
            name="div",
            attrs={
                "class": "building-schedule-item building-schedule-item-hidden hasTickets"
            },
        )
    )
    for performance in performance_divs:
        date_div = performance.find(name="div", attrs={"class": "building-schedule-item-date-col"})
        date_date = date_div.find(name="div", attrs={"class": "schedule-date_date"}).text.strip()
        date_month = date_div.find(name="div", attrs={"class": "schedule-date_month"}).text.strip()
        date_day = date_div.find(name="div", attrs={"class": "schedule-date_day"}).text.strip()
        date_time = performance.find(name="div", attrs={"class": "building-schedule-session-time"}).text.strip()
        name = performance.find(name="span", attrs={"class": "show-link-title"}).text.strip()
        date_string = f"{date_day} - {date_date} {date_month}"
        print(date_string, date_time, name)

        is_has_ticket_divs = performance.find_all(name="div", attrs={"class": "building-schedule-item-ticket-col"})
        for div in is_has_ticket_divs:
            is_has_ticket = div.find(name="a", attrs={"class": "item"})
            if is_has_ticket:
                price = div.find(name="div", attrs={"class": "price"}).text.strip()
                ticket_count = div.find(name="div", attrs={"class": "ticket-count"}).find(name="span").text.strip()
                ticket_count_text = f"В наличии {ticket_count} билетов"
                link = is_has_ticket.get("href")
                link_text = f"https://www.bileter.ru{link}"
                print(price, ticket_count_text, link_text)


def loop_parser():
    while True:
        parser()
        time.sleep(TIME_OUT)


def main():
    process = Process(target=loop_parser)
    # start the child process
    process.start()

if __name__ == "__main__":
    main()