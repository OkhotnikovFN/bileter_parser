import threading
import time
import tkinter as tk

import requests
from bs4 import BeautifulSoup


class Parser:
    TIME_OUT = 60
    TARGET_LINK = "https://www.bileter.ru/afisha/building/teatr_dojdey.html"
    ENABLED = True
    PROCESS = None

    def __init__(self):
        self.new_thread = None
        self.timeout = self.TIME_OUT
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
        self.results_label_list_box = tk.Listbox(width=200)
        self.results_label_list_box.pack()

        self.window.mainloop()

    def exit_program(
        self,
    ):
        if self.new_thread:
            self.new_thread.join(timeout=0.01)
        exit(1)

    def _resetbutton(self):
        self.running = False
        self.main_button.config(text="Старт", command=self.start_thread)

    def start_thread(self):
        try:
            try:
                self.time_out = max(int(self.time_out_entry.get()), self.TIME_OUT)
            except ValueError:
                self.time_out_entry.delete(0, len(self.time_out_entry.get()))
                self.time_out_entry.insert(0, "неверный формат числа")
                raise
            self.running = True
            self.new_thread = threading.Thread(target=self.loop_parse, daemon=True)
            self.new_thread.start()
        except Exception:
            return
        self.main_button.config(text="Стоп", command=self._resetbutton)

    def loop_parse(self):
        try:
            while self.running:
                self.parse()
                time.sleep(self.time_out)
        except RuntimeError:
            pass
        except Exception:
            self.results_label_list_box.insert(
                self.results_label_list_box.size(),
                "Что-то пошло не так",
            )
            self._resetbutton()

    def parse(self):
        self.results_label_list_box.delete(0, self.results_label_list_box.size())
        target_link_str = self.target_link.get() or self.TARGET_LINK
        response = requests.get(target_link_str)
        response.raise_for_status()
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
            for i, div in enumerate(is_has_ticket_divs):
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

                    self.results_label_list_box.insert(
                        i,
                        f"{date_string:^50} {date_time:^10} | {name:^50} | {price:^50} | {ticket_count_text:^50} | {link_text:^60}",
                    )


Parser()
