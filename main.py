import threading
import time
import tkinter as tk
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup


class Parser:
    TIME_OUT = 60
    TARGET_LINK = "https://www.bileter.ru/afisha/building/teatr_dojdey.html"
    ENABLED = True
    PROCESS = None
    DATE_ENTRY_WIDTH = 50
    DATE_TIME_ENTRY_WIDTH = 10
    NAME_ENTRY_WIDTH = 30
    PRICE_ENTRY_WIDTH = 30
    TICKET_COUNT_TEXT_ENTRY_WIDTH = 30
    LINK_TEXT_ENTRY_WIDTH = 50

    def __init__(self):
        self.new_thread = None
        self.timeout = self.TIME_OUT

        self.window = tk.Tk()

        self._init_main_button()
        self._init_exit_button()
        self._init_target_link_entry()
        self._init_time_out_entry()
        self._init_results_labels()

        self.result_columns = []

    def _init_main_button(self) -> None:
        self.main_button = tk.Button(
            width=10,
            height=2,
            bg="grey",
            fg="black",
        )
        self.main_button.pack()
        self._resetbutton()

    def _init_exit_button(self) -> None:
        self.exit_button = tk.Button(
            text="Выход",
            width=10,
            height=2,
            bg="grey",
            fg="black",
        )
        self.exit_button.pack()
        self.exit_button.config(command=self.exit_program)

    def _init_target_link_entry(self) -> None:
        self.link_label = tk.Label(text="Ссылка")
        self.link_label.pack()
        self.target_link = tk.Entry(fg="black", bg="white", width=50)
        self.target_link.insert(0, self.TARGET_LINK)
        self.target_link.pack()

    def _init_time_out_entry(self) -> None:
        self.time_out_label = tk.Label(
            text="Частота парсинга, c (не чаще 1 раз в минуту)"
        )
        self.time_out_label.pack()
        self.time_out_entry = tk.Entry(fg="black", bg="white", width=50)
        self.time_out_entry.insert(0, str(self.TIME_OUT))
        self.time_out_entry.pack()

    def _init_results_labels(self) -> None:
        self.results_time_update_label = tk.Label(text="Время обновления")
        self.results_time_update_label.pack()
        self.results_time_update = tk.Entry(
            fg="black", bg="white", width=50, state=tk.DISABLED
        )
        self.results_time_update.pack()

        frame = tk.Frame()
        frame.pack()
        date_lable = tk.Label(
            frame,
            text="Дата",
            width=self.DATE_ENTRY_WIDTH,
        )
        date_lable.pack(side="left")
        date_time_lable = tk.Label(
            frame, text="Время", width=self.DATE_TIME_ENTRY_WIDTH
        )
        date_time_lable.pack(side="left")
        name_lable = tk.Label(frame, text="Название", width=self.NAME_ENTRY_WIDTH)
        name_lable.pack(side="left")
        price_lable = tk.Label(frame, text="Цена", width=self.PRICE_ENTRY_WIDTH)
        price_lable.pack(side="left")
        ticket_count_text_lable = tk.Label(
            frame, text="Количество", width=self.TICKET_COUNT_TEXT_ENTRY_WIDTH
        )
        ticket_count_text_lable.pack(side="left")
        link_text_lable = tk.Label(
            frame, text="Сысылка", width=self.LINK_TEXT_ENTRY_WIDTH
        )
        link_text_lable.pack(side="left")

    def start(self) -> None:
        self.window.mainloop()

    def exit_program(
        self,
    ) -> None:
        if self.new_thread:
            self.new_thread.join(timeout=0.01)
        exit(1)

    def _resetbutton(self) -> None:
        self.running = False
        self.main_button.config(text="Старт", command=self.start_thread)

    def start_thread(self) -> None:
        try:
            try:
                self.time_out = max(int(self.time_out_entry.get()), self.TIME_OUT)
            except ValueError:
                self.time_out_entry.config(bg="red")
                raise
            self.time_out_entry.config(bg="white")
            self.running = True
            self.new_thread = threading.Thread(target=self.loop_parse, daemon=True)
            self.new_thread.start()
        except Exception:
            return
        self.main_button.config(text="Стоп", command=self._resetbutton)

    def loop_parse(self) -> None:
        try:
            while self.running:
                self.parse()
                time.sleep(self.time_out)
        except RuntimeError:
            pass
        except Exception:
            self.results_time_update.config(state=tk.NORMAL)
            self.results_time_update.delete(0, len(self.results_time_update.get()))
            self.results_time_update.insert(
                0,
                "Что-то пошло не так",
            )
            self._resetbutton()

    def _make_response(self) -> str:
        target_link_str = self.target_link.get() or self.TARGET_LINK
        response = requests.get(target_link_str)
        response.raise_for_status()
        return response.text

    def _get_performance_divs(self) -> list:
        soup = BeautifulSoup(self._make_response(), "html.parser")
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
        return performance_divs

    def _clear_resul_columns(self) -> None:
        for column in self.result_columns:
            for entry in column:
                entry.destroy()
        self.result_columns = []

    def _parse_date(self, performance: BeautifulSoup) -> str:
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
        return f"{date_day} - {date_date} {date_month}"

    def _parse_date_time(self, performance: BeautifulSoup) -> str:
        return performance.find(
            name="div", attrs={"class": "building-schedule-session-time"}
        ).text.strip()

    def _parse_name(self, performance: BeautifulSoup) -> str:
        return performance.find(
            name="span", attrs={"class": "show-link-title"}
        ).text.strip()

    def _parse_div_with_tickets(self, performance: BeautifulSoup) -> list:
        return performance.find_all(
            name="div", attrs={"class": "building-schedule-item-ticket-col"}
        )

    def _parse_link_text(self, div: BeautifulSoup) -> Optional[str]:
        link_tag = div.find(name="a", attrs={"class": "item"})
        if link_tag:
            link = link_tag.get("href")
            return f"https://www.bileter.ru{link}"

    def _parse_price(self, div: BeautifulSoup) -> str:
        return div.find(name="div", attrs={"class": "price"}).text.strip()

    def _parse_ticket_count(self, div: BeautifulSoup) -> str:
        ticket_count = (
            div.find(name="div", attrs={"class": "ticket-count"})
            .find(name="span")
            .text.strip()
        )
        return f"В наличии {ticket_count} билетов"

    def _update_result_columns(self, performance, div):
        link_text = self._parse_link_text(div=div)
        if link_text:
            date_time = self._parse_date_time(performance=performance)
            name = self._parse_name(performance=performance)
            date_string = self._parse_date(performance=performance)
            price = self._parse_price(div=div)
            ticket_count = self._parse_ticket_count(div=div)
            frame = tk.Frame()
            date_entry = tk.Entry(
                frame, fg="black", bg="white", width=self.DATE_ENTRY_WIDTH
            )
            date_entry.insert(0, date_string)
            date_time_entry = tk.Entry(
                frame, fg="black", bg="white", width=self.DATE_TIME_ENTRY_WIDTH
            )
            date_time_entry.insert(0, date_time)
            name_entry = tk.Entry(
                frame, fg="black", bg="white", width=self.NAME_ENTRY_WIDTH
            )
            name_entry.insert(0, name)
            price_entry = tk.Entry(
                frame, fg="black", bg="white", width=self.PRICE_ENTRY_WIDTH
            )
            price_entry.insert(0, price)
            ticket_count_text_entry = tk.Entry(
                frame, fg="black", bg="white", width=self.TICKET_COUNT_TEXT_ENTRY_WIDTH
            )
            ticket_count_text_entry.insert(0, ticket_count)
            link_text_entry = tk.Entry(
                frame, fg="black", bg="white", width=self.LINK_TEXT_ENTRY_WIDTH
            )
            link_text_entry.insert(0, link_text)
            self.result_columns.append(
                [
                    frame,
                    date_entry,
                    date_time_entry,
                    name_entry,
                    price_entry,
                    ticket_count_text_entry,
                    link_text_entry,
                ]
            )

    def _paint_results(self):
        for column in self.result_columns:
            for i, entry in enumerate(column):
                side = "top" if i == 0 else "left"
                entry.pack(side=side)

        self.results_time_update.config(state=tk.NORMAL)
        self.results_time_update.delete(0, len(self.results_time_update.get()))
        self.results_time_update.insert(0, datetime.now().isoformat())
        self.results_time_update.config(state=tk.DISABLED)

    def parse(self) -> None:
        performance_divs = self._get_performance_divs()
        self._clear_resul_columns()

        for performance in performance_divs:
            ticket_divs = self._parse_div_with_tickets(performance=performance)

            for div in ticket_divs:
                self._update_result_columns(performance=performance, div=div)

        self._paint_results()


if __name__ == "__main__":
    parser = Parser()
    parser.start()
