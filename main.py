import threading
import time
import tkinter as tk

import requests
from bs4 import BeautifulSoup


class Parser:
    TIME_OUT = 2
    TARGET_LINK = "https://www.bileter.ru/afisha/building/teatr_dojdey.html"
    ENABLED = True
    PROCESS = None

    def __init__(self):
        self.window = tk.Tk()

        self.main_button = tk.Button(
            width=10,
            height=2,
            bg="grey",
            fg="black",
        )
        self.main_button.pack()
        self._resetbutton()

        self.exit_button = tk.Button(
            text="Выход",
            width=10,
            height=2,
            bg="grey",
            fg="black",
        )
        self.exit_button.pack()
        self.exit_button.config(command=self.exit_program)

        self.link_label = tk.Label(text="Ссылка")
        self.link_label.pack()
        self.target_link = tk.Entry(fg="black", bg="white", width=50)
        self.target_link.insert(0, self.TARGET_LINK)
        self.target_link.pack()

        self.time_out_label = tk.Label(text="Частота парсинга (не чаще 1 раз в минуту)")
        self.time_out_label.pack()
        self.time_out_entry = tk.Entry(fg="black", bg="white", width=50)
        self.time_out_entry.insert(0, str(self.TIME_OUT))
        self.time_out_entry.pack()

        self.results_label = tk.Label(text="Результат")
        self.results_label.pack()
        self.results_label_list_box = tk.Listbox()
        self.results_label_list_box.pack()

        self.window.mainloop()

    def exit_program(
        self,
    ):
        exit(1)

    def _resetbutton(self):
        self.running = False
        self.main_button.config(text="Старт", command=self.start_thread)

    def start_thread(self):
        self.running = True
        newthread = threading.Thread(target=self.loop_parse)
        newthread.start()
        self.main_button.config(text="Стоп", command=self._resetbutton)

    def loop_parse(self):
        time_out = max(int(self.time_out_entry.get()), self.TIME_OUT)
        while self.running:
            self.parse()
            time.sleep(time_out)

    def parse(self):
        target_link_str = self.target_link.get() or self.TARGET_LINK
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
            for i, div in enumerate(is_has_ticket_divs, start=1):
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

                    self.results_label_list_box.insert(
                        i,
                        f"{date_string} {date_time} {name} {price} {ticket_count_text} {link_text}",
                    )
                    print(self.results_label_list_box.get(1))


Parser()
