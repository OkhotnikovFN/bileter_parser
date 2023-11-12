import time
import tkinter as tk
from multiprocessing import Process

import requests
from bs4 import BeautifulSoup

TIME_OUT = 2
TARGET_LINK = "https://www.bileter.ru/afisha/building/teatr_dojdey.html"
ENABLED = True
PROCESS = None


def parse():
    target_link_str = target_link.get() or TARGET_LINK
    response = requests.get(target_link_str)
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
        date_div = performance.find(
            name="div", attrs={"class": "building-schedule-item-date-col"}
        )
        date_date = date_div.find(
            name="div", attrs={"class": "schedule-date_date"}
        ).text.strip()
        date_month = date_div.find(
            name="div", attrs={"class": "schedule-date_month"}
        ).text.strip()
        date_day = date_div.find(
            name="div", attrs={"class": "schedule-date_day"}
        ).text.strip()
        date_time = performance.find(
            name="div", attrs={"class": "building-schedule-session-time"}
        ).text.strip()
        name = performance.find(
            name="span", attrs={"class": "show-link-title"}
        ).text.strip()
        date_string = f"{date_day} - {date_date} {date_month}"

        is_has_ticket_divs = performance.find_all(
            name="div", attrs={"class": "building-schedule-item-ticket-col"}
        )
        for div in is_has_ticket_divs:
            is_has_ticket = div.find(name="a", attrs={"class": "item"})
            if is_has_ticket:
                price = div.find(name="div", attrs={"class": "price"}).text.strip()
                ticket_count = (
                    div.find(name="div", attrs={"class": "ticket-count"})
                    .find(name="span")
                    .text.strip()
                )
                ticket_count_text = f"В наличии {ticket_count} билетов"
                link = is_has_ticket.get("href")
                link_text = f"https://www.bileter.ru{link}"
                print(date_string, date_time, name)
                print(price, ticket_count_text, link_text)


def loop_parser():
    while True:
        parse()
        time_out = max(int(time_out_entry.get()), TIME_OUT)
        time.sleep(time_out)


def threaded_loop_parse(
    event,
):
    global PROCESS
    if PROCESS is None:
        PROCESS = Process(
            target=loop_parser,
        )
        PROCESS.start()


def threaded_loop_parse_stop(
    event,
):
    global PROCESS
    if PROCESS:
        PROCESS.kill()
        PROCESS = None


def exit_program(
    event,
):
    global PROCESS
    if PROCESS:
        PROCESS.kill()
    exit(1)


# window = tk.Tk(screenName="Загрузить с YouTube")
window = tk.Tk()

exit_button = tk.Button(
    text="Выход",
    width=10,
    height=2,
    bg="grey",
    fg="black",
)
exit_button.pack()
exit_button.bind("<Button-1>", func=exit_program)


start_button = tk.Button(
    text="Старт",
    width=10,
    height=2,
    bg="grey",
    fg="black",
)
start_button.pack()
start_button.bind("<Button-1>", func=threaded_loop_parse)

stop_button = tk.Button(
    text="Стоп",
    width=10,
    height=2,
    bg="grey",
    fg="black",
)
stop_button.pack()
stop_button.bind("<Button-1>", func=threaded_loop_parse_stop)


link_label = tk.Label(text="Ссылка")
link_label.pack()
target_link = tk.Entry(fg="black", bg="white", width=50)
target_link.insert(0, TARGET_LINK)
target_link.pack()

time_out_label = tk.Label(text="Частота парсинга (не чаще 1 раз в минуту)")
time_out_label.pack()
time_out_entry = tk.Entry(fg="black", bg="white", width=50)
time_out_entry.insert(0, str(TIME_OUT))
time_out_entry.pack()


window.mainloop()
