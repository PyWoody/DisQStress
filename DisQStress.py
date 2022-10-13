import random
import threading
import time

from functools import partial

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDial,
    QVBoxLayout,
    QWidget,
)


class StressTest(QWidget):

    run = Signal(partial)

    def __init__(self, *, rows=15, columns=20, parent=None):
        super().__init__(parent)

        self.resize(100, 100)

        self.run.connect(self.run_func)

        self.lock = threading.Lock()
        self.threads = []
        self.__stop = False

        self.min_sleep, self.max_sleep = 1, 100
        self.rows, self.columns = rows, columns

        snake_btn = QPushButton('Snake')
        snake_btn.clicked.connect(partial(self.stop, False))
        snake_btn.clicked.connect(self.snake)
        wash_btn = QPushButton('Wash')
        wash_btn.clicked.connect(partial(self.stop, False))
        wash_btn.clicked.connect(self.wash)
        rain_btn = QPushButton('Rain')
        rain_btn.clicked.connect(partial(self.stop, False))
        rain_btn.clicked.connect(self.rain)
        talk_btn = QPushButton('Talk')
        talk_btn.clicked.connect(self.talk)

        action_btns_layout = QVBoxLayout()
        action_btns_layout.addWidget(snake_btn)
        action_btns_layout.addWidget(wash_btn)
        action_btns_layout.addWidget(rain_btn)
        action_btns_layout.addWidget(talk_btn)
        action_btns_group = QGroupBox()
        action_btns_group.setLayout(action_btns_layout)

        add_row_btn = QPushButton('Add Row')
        add_row_btn.clicked.connect(self.add_row)
        add_column_btn = QPushButton('Add Column')
        add_column_btn.clicked.connect(self.add_column)
        remove_row_btn = QPushButton('Remove Row')
        remove_row_btn.clicked.connect(self.remove_row)
        remove_column_btn = QPushButton('Remove Column')
        remove_column_btn.clicked.connect(self.remove_column)

        grid_btns_layout = QHBoxLayout()
        grid_btns_layout.addWidget(add_row_btn)
        grid_btns_layout.addWidget(add_column_btn)
        grid_btns_layout.addWidget(remove_row_btn)
        grid_btns_layout.addWidget(remove_column_btn)
        grid_btns_group = QGroupBox()
        grid_btns_group.setLayout(grid_btns_layout)

        self.speed_label = QLabel()
        speed_layout = QVBoxLayout()
        speed_dial = QDial()
        speed_dial.setRange(self.min_sleep, self.max_sleep)
        speed_dial.setSingleStep(1)
        speed_dial.setNotchesVisible(True)
        speed_dial.valueChanged.connect(self.update_speed)
        speed_dial.setValue(self.max_sleep)
        speed_dial.setValue(self.min_sleep)
        speed_layout.addWidget(speed_dial)
        speed_layout.addWidget(
            self.speed_label, alignment=Qt.AlignCenter | Qt.AlignTop
        )

        stop_btn = QPushButton('Stop')
        stop_btn.clicked.connect(partial(self.stop, True))
        reset_btn = QPushButton('Reset')
        reset_btn.clicked.connect(partial(self.stop, True))
        reset_btn.clicked.connect(self.reset_grid)

        process_btns_layout = QHBoxLayout()
        process_btns_layout.addWidget(stop_btn)
        process_btns_layout.addWidget(reset_btn)
        process_btns_group = QGroupBox()
        process_btns_group.setLayout(process_btns_layout)

        btn_layout = QVBoxLayout()
        btn_layout.addWidget(action_btns_group)
        btn_layout.addWidget(grid_btns_group)
        btn_layout.addWidget(process_btns_group)

        top_btn_layout = QHBoxLayout()
        top_btn_layout.addLayout(btn_layout)
        top_btn_layout.addLayout(speed_layout)

        self.status = QLabel()

        # Setup grid of labels
        self.grid = QGridLayout()
        self.grid_layout = QVBoxLayout()
        for row in range(self.rows):
            for column in range(self.columns):
                panel = GridPanel(row, column)
                panel.status.connect(self.update_status)
                panel.ephemeral_status.connect(
                    partial(self.update_status, ephemeral=True)
                )
                self.grid.addWidget(panel, row, column)
        self.grid_layout.addLayout(self.grid)
        self.snake_cells = [i for i in self.snaked_panels()]

        layout = QVBoxLayout()
        layout.addLayout(self.grid_layout)
        layout.setStretchFactor(self.grid_layout, 1)
        layout.addLayout(top_btn_layout)
        layout.addWidget(self.status, alignment=Qt.AlignLeft | Qt.AlignBottom)
        self.setLayout(layout)

    @Slot()
    def talk(self):
        msg = 'Bark!'
        if text := self.status.text():
            msg = f'{text} {msg}'
        self.update_status(msg, ephemeral=True)

    @Slot()
    def rain(self):
        if self.columns > 1 and self.rows > 2:
            for _ in range(3):
                t = threading.Thread(target=self.__rain)
                t.daemon = True
                t.start()
                self.threads.append(t)
        else:
            self.status.setText('Not enough rows or columns for rain!')

    def __rain(self):
        previous_column = -1
        while True:
            with self.lock:
                if self.columns < 3 or self.rows < 3:
                    return
                row = random.randint(1, self.rows - 2)
                column = random.randint(0, self.columns - 1)
                while column == previous_column:
                    column = random.randint(0, self.columns - 1)
            opacity = 0.1
            opacity_step = 1.0 / (self.rows - row)
            panels = []
            while row < self.rows:
                if self.columns < 3 or self.rows < 3:
                    return
                if self.__stop:
                    return
                style = f'background: rgba(16, 97, 227, {opacity:2f})'
                if panel := self.get_panel(row, column):
                    self.run.emit(partial(panel.setStyleSheet, style))
                    opacity += opacity_step
                    if opacity > 1.0:
                        opacity = 1.0
                    row += 1
                    panels.insert(0, panel)
                    time.sleep(self.sleep)
            time.sleep(random.randint(1, 20) / 10)
            self.reset_panels(panels)
            previous_column = column

    @Slot()
    def wash(self):
        t = threading.Thread(target=self.__wash)
        t.daemon = True
        t.start()
        self.threads.append(t)

    def __wash(self):
        previous_row = None
        previous_row_1 = None
        previous_row_2 = None
        while True:
            for row in range(self.rows):
                panels = []
                for column in range(self.columns):
                    if panel := self.get_panel(row, column):
                        panels.append(panel)
                if self.__stop:
                    return
                self.update_wash_row(panels)
                time.sleep(self.sleep)
                if previous_row:
                    self.update_wash_row(previous_row, opacity=.5)
                    time.sleep(self.sleep)
                    if previous_row_1:
                        self.update_wash_row(previous_row_1, opacity=.25)
                        time.sleep(self.sleep)
                        if previous_row_2:
                            self.reset_panels(previous_row_2)
                            time.sleep(self.sleep)
                    previous_row_2 = previous_row_1
                    previous_row_1 = previous_row
                    previous_row = panels
                else:
                    previous_row = panels

    def update_wash_row(self, panels, color=(16, 97, 227), opacity=1.0):
        color = ', '.join([str(i) for i in color])
        for panel in panels:
            self.run.emit(
                partial(panel.setFrameStyle, QFrame.WinPanel | QFrame.Raised)
            )
            self.run.emit(
                partial(
                    panel.setStyleSheet,
                    f'background: rgba({color}, {opacity:.2f})'
                )
            )

    @Slot()
    def snake(self):
        t = threading.Thread(target=self.__snake)
        t.daemon = True
        t.start()
        self.threads.append(t)

    def __snake(self):
        tail = 0
        head = 1
        snake_length = 5
        iteration = 0
        while True:
            if self.__stop:
                return
            panels = self.snake_cells[tail:head]
            if panels:
                panels.reverse()
                self.update_snake(panels, snake_length, iteration)
                if head >= snake_length:
                    tail += 1
                head += 1
                iteration += 1
                time.sleep(self.sleep)
            else:
                tail = 0
                head = 1
                iteration = 0

    def update_snake(self, panels, max_length, iteration, color=(16, 97, 227)):
        if self.__stop:
            return
        color = ', '.join([str(i) for i in color])
        opacity = 1.0
        opacity_step = 1.0 / len(panels)
        for panel in panels:
            self.run.emit(
                partial(panel.setFrameStyle, QFrame.WinPanel | QFrame.Raised)
            )
            self.run.emit(
                partial(
                    panel.setStyleSheet,
                    f'background: rgba({color}, {opacity:.2f})'
                )
            )
            opacity -= opacity_step
        if len(panels) >= max_length or iteration >= self.rows:
            self.run.emit(
                partial(
                    panels[-1].setFrameStyle, QFrame.WinPanel | QFrame.Raised
                )
            )
            self.run.emit(partial(panels[-1].setStyleSheet, ''))

    def reset_grid(self):
        for panel in self.panels():
            if panel.style():
                panel.setStyleSheet('')
                panel.setFrameStyle(QFrame.WinPanel | QFrame.Raised)

    def get_panel(self, row, column):
        if item := self.grid.itemAtPosition(row, column):
            panel = item.widget()
            if isinstance(panel, GridPanel):
                return panel

    def panels(self):
        for row in range(self.rows):
            for column in range(self.columns):
                if panel := self.get_panel(row, column):
                    yield panel

    def reset_panels(self, panels):
        for panel in panels:
            self.run.emit(
                partial(panel.setFrameStyle, QFrame.WinPanel | QFrame.Raised)
            )
            self.run.emit(partial(panel.setStyleSheet, ''))

    def snaked_panels(self):
        columns = list(range(self.columns))
        for row in range(self.rows):
            for column in columns:
                if panel := self.get_panel(row, column):
                    yield panel
            columns.reverse()

    @Slot()
    def add_row(self):
        with self.lock:
            for column in range(self.columns):
                panel = GridPanel(self.rows, column)
                panel.status.connect(self.update_status)
                panel.ephemeral_status.connect(
                    partial(self.update_status, ephemeral=True)
                )
                self.grid.addWidget(panel, self.rows, column)
            self.rows += 1
            self.layout()
        self.snake_cells = [i for i in self.snaked_panels()]

    @Slot()
    def add_column(self):
        with self.lock:
            for row in range(self.rows):
                panel = GridPanel(row, self.columns)
                panel.status.connect(self.update_status)
                panel.ephemeral_status.connect(
                    partial(self.update_status, ephemeral=True)
                )
                self.grid.addWidget(panel, row, self.columns)
            self.columns += 1
            self.layout()
        self.snake_cells = [i for i in self.snaked_panels()]

    @Slot()
    def remove_row(self):
        with self.lock:
            if self.rows > 1:
                self.rows -= 1
                for column in range(self.columns):
                    if item := self.grid.itemAtPosition(self.rows, column):
                        item.widget().setParent(None)
                self.layout()
        self.snake_cells = [i for i in self.snaked_panels()]

    @Slot()
    def remove_column(self):
        with self.lock:
            if self.columns > 1:
                self.columns -= 1
                for row in range(self.rows):
                    if item := self.grid.itemAtPosition(row, self.columns):
                        item.widget().setParent(None)
                self.layout()
        self.snake_cells = [i for i in self.snaked_panels()]

    @Slot(str)
    @Slot(partial)
    def update_status(self, status, ephemeral=False):
        self.status.setText(status)
        if ephemeral:
            QTimer.singleShot(1_000, partial(self.remove_status, status))

    @Slot(partial)
    def remove_status(self, status):
        if self.status.text() == status:
            self.status.setText('')

    @Slot(int)
    def update_speed(self, speed):
        sleep = (100 - speed) * .001
        self.sleep = sleep
        self.speed_label.setText(f'Sleep: {sleep:.2f}')

    @Slot(partial)
    def run_func(self, func):
        if not self.__stop:
            func()

    @Slot()
    def stop(self, val):
        if self.__stop != val:
            self.__stop = val

    def closeEvent(self, *args, **kwargs):
        self.__stop = True
        for t in self.threads:
            t.join()
        super().closeEvent(*args, **kwargs)


class GridPanel(QLabel):

    status = Signal(str)
    ephemeral_status = Signal(str)

    def __init__(self, row, column, *, parent=None, f=Qt.WindowFlags()):
        super().__init__(parent, f)
        self.row = row
        self.column = column
        self.setFrameStyle(QFrame.WinPanel | QFrame.Raised)
        self.clicked = False

    def mousePressEvent(self, event):
        self.status.emit(
            f'Clicking on Row: {self.row + 1} | Column: {self.column}'
        )
        self.clicked = True

    def mouseReleaseEvent(self, event):
        self.status.emit(
            f'Clicked on Row: {self.row + 1} | Column: {self.column}'
        )

    def enterEvent(self, event):
        self.status.emit(
            f'Hovering on Row: {self.row + 1} | Column: {self.column}'
        )
        self.toggle_on()

    def leaveEvent(self, event):
        self.ephemeral_status.emit(
            f'Hovered on Row: {self.row + 1} | Column: {self.column}'
        )
        if self.clicked:
            self.clicked = False
        else:
            self.toggle_off()

    def toggle_on(self, color='#FF5733'):
        if not self.styleSheet():
            self.setFrameStyle(QFrame.WinPanel | QFrame.Sunken)
            self.setStyleSheet(f'background: {color}')

    def toggle_off(self):
        if self.styleSheet():
            self.setFrameStyle(QFrame.WinPanel | QFrame.Raised)
            self.setStyleSheet('')


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = StressTest()
    window.show()
    sys.exit(app.exec())
