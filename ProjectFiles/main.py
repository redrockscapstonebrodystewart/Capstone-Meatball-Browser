# '''
# Brody Stewart
# Red Rocks Community College
# Secure Software Engineering
# Capstone Project: Meatball Browser
# Simple web-browser program that displays some of the knowledge I've gained throughout my tenure at
# Red Rocks Community College. This includes a tabbed window system, a bookmark system and other small features.
# Capstone released on May 6th, 2023.
# '''

import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *


class Browser(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Browser, self).__init__(*args, **kwargs)

        # Establish Tabbed Window
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

        # Status Bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Bookmarks Array setup for later incorporation
        bookmarks = ["Empty"] * 10
        bookmark_btns = [None] * 10

        # Navigation Portion, establishes essential navigation QActions.
        nav_tab = QToolBar("Navigation")
        nav_tab.setIconSize(QSize(16, 16))
        self.addToolBar(nav_tab)

        back_button = QAction(QIcon(os.path.join('images', 'back_arrow.png')), "Back", self)
        back_button.setStatusTip("Back")
        back_button.triggered.connect(lambda: self.tabs.currentWidget().back())
        nav_tab.addAction(back_button)

        next_button = QAction(QIcon(os.path.join('images', 'forward_arrow.png')), "Forward", self)
        next_button.setStatusTip("Forward")
        next_button.triggered.connect(lambda: self.tabs.currentWidget().forward())
        nav_tab.addAction(next_button)

        refresh_button = QAction(QIcon(os.path.join('images', 'reload.png')), "Reload", self)
        refresh_button.setStatusTip("Reload page")
        refresh_button.triggered.connect(lambda: self.tabs.currentWidget().reload())
        nav_tab.addAction(refresh_button)

        home_btn = QAction(QIcon(os.path.join('images', 'home.png')), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        nav_tab.addAction(home_btn)
        nav_tab.addSeparator()

        # Https Icon to display if it's a safe url
        self.safe_display = QLabel()
        self.safe_display.setPixmap(QPixmap(os.path.join('images', 'lock.png')))
        nav_tab.addWidget(self.safe_display)

        # Stop loading button
        stop_button = QAction(QIcon(os.path.join('images', 'circle_x.png')), "Stop", self)
        stop_button.setStatusTip("Stop loading current page")
        stop_button.triggered.connect(lambda: self.tabs.currentWidget().stop())
        nav_tab.addAction(stop_button)

        # File menu for basic file and tab navigation, such as creating new tabs and opening files.
        file_menu = self.menuBar().addMenu("&File")

        new_tab_button = QAction(QIcon(os.path.join('images', 'plus_sign.png')), "New Tab", self)
        new_tab_button.setStatusTip("Open a new tab")
        new_tab_button.triggered.connect(lambda _: self.add_new_tab())
        file_menu.addAction(new_tab_button)

        print_button = QAction(QIcon(os.path.join('images', 'printer.png')), "Print...", self)
        print_button.setStatusTip("Print current page")
        print_button.triggered.connect(self.print_page)
        file_menu.addAction(print_button)

        # Bookmarks menu, which holds all bookmark navigation and buttons
        bookmark_menu = self.menuBar().addMenu("&Bookmarks")

        save_bm_action = QAction(QIcon(os.path.join('images', 'save.png')), "Save Bookmark", self)
        save_bm_action.setStatusTip("Save a bookmark [Up to 10]")  # Hungry!
        save_bm_action.triggered.connect(lambda: self.save_bookmark(bookmarks, bookmark_btns))
        bookmark_menu.addAction(save_bm_action)

        remove_bm_action = QAction(QIcon(os.path.join('images', 'circle_x.png')), "Remove Bookmark", self)
        remove_bm_action.setStatusTip("Remove a bookmark")
        remove_bm_action.triggered.connect(lambda: self.rem_bookmark(bookmarks, bookmark_btns))
        bookmark_menu.addAction(remove_bm_action)

        # Url on enter navigation
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_tab.addWidget(self.url_bar)

        # Load the bookmarks for display
        self.load_bookmarks(bookmarks)
        self.create_bookmarks(bookmark_menu, bookmark_btns)
        self.display_bookmarks(bookmarks, bookmark_btns)

        # New tab started on Google, then open as a maximized window and set title and icon.
        self.add_new_tab(QUrl('http://www.google.com'), 'Google')
        self.showMaximized()
        self.setWindowTitle("Meatball Browser")
        self.setWindowIcon(QIcon(os.path.join('images', 'browser_icon.png')))

    # Creates the bookmark buttons for display
    def create_bookmarks(self, bookmark_menu, bookmark_btns):
        count = 0
        while count < 10:
            bm = QAction(QIcon(os.path.join('images', 'open.png')), 'Empty', self)
            bm.setStatusTip('Empty')
            bookmark_menu.addAction(bm)
            bookmark_btns[count] = bm
            count = count + 1

    # Read the bookmarks file and add each eligible item to the bookmark array.
    def load_bookmarks(self, bookmarks):
        bookmark_file = open("bookmarks.txt", 'r')
        count = 0
        clear_mode = False
        while count < 10:
            line = bookmark_file.readline()
            if not line or line.find("#") == -1:
                clear_mode = True
            if clear_mode:
                bookmarks[count] = "Empty"
            else:
                bookmarks[count] = line
            count = count + 1
        bookmark_file.close()

    # For fixing lambda scope issues
    def bookmark_action(self, x):
        return lambda: self.open_bookmark(x)

    # Read through the array and display each eligible bookmark item as a button.
    def display_bookmarks(self, bookmarks, bookmark_btns):
        count = 0
        clear_mode = False
        while count < 10:
            x = bookmarks[count]
            btn = bookmark_btns[count]
            if x == "Empty":
                clear_mode = True
            if clear_mode:
                title = "Empty"
                url = "Empty"
            else:
                title = x[0:x.find('#')]
                url = x[x.find('#') + 1:-1]
                btn.triggered.connect(self.bookmark_action(url))
            btn.setText(title)
            btn.setStatusTip(url)
            count = count + 1

    # Function to open clicked bookmark buttons.
    def open_bookmark(self, url):
        if url.find("://") >= 0:
            self.tabs.currentWidget().setUrl(QUrl(url))
        else:
            print("Broken link")

    # Function to remove a bookmark from the browser, array and bookmarks file.
    def rem_bookmark(self, bookmarks, bookmark_btns):
        url = self.url_bar.text()
        count = 0
        while count < 10:
            x = bookmarks[count].find(url)
            if x > -1:
                with open('bookmarks.txt', 'r') as fr:
                    lines = fr.readlines()
                    ptr = 1
                    with open('bookmarks.txt', 'w') as fw:
                        for line in lines:
                            if ptr != count + 1:
                                fw.write(line)
                            ptr += 1
                self.load_bookmarks(bookmarks)
                self.display_bookmarks(bookmarks, bookmark_btns)
                break
            count = count + 1

    # Function to save a bookmark, turning it into a button and saving the information to the bookmark file.
    def save_bookmark(self, bookmarks, bookmark_btns):
        if bookmarks[9] != "Empty":
            return
        title = self.tabs.currentWidget().page().title()
        url = self.url_bar.text()
        bookmark_file = open("bookmarks.txt", 'a')
        bookmark_file.write(title + "#" + url + "\n")
        bookmark_file.close()
        self.load_bookmarks(bookmarks)
        self.display_bookmarks(bookmarks, bookmark_btns)

    # Function to add a new tab to the browser.
    def add_new_tab(self, url=None, label="Blank"):
        if url is None:
            # Default to google
            url = QUrl('https://www.google.com')
        browser = QWebEngineView()
        browser.setUrl(url)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_url_bar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))

    # Add a new tab when double-clicking the tab bar.
    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    # Change tab
    def current_tab_changed(self):
        qurl = self.tabs.currentWidget().url()
        self.update_url_bar(qurl, self.tabs.currentWidget())

    # Close a tab when user presses the x button.
    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    # Basic printing function for printing a web-page.
    def print_page(self):
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(self.browser.print_)
        dlg.exec_()

    # Easy navigation function
    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

    # Navigates browser window to new url if it seems like an url entry. if not, automatically searches it on Google.
    # Also updates things to url-style if they look like an incomplete url.
    def navigate_to_url(self):
        url = self.url_bar.text()
        if url.find('https://') == -1:
            if 0 < url.find('.') < len(url) - 1:
                url = "https://" + url
            else:
                url = "https://www.google.com/search?q=" + url
        self.tabs.currentWidget().setUrl(QUrl(url))

    # Update url bar to match new webpage and security
    def update_url_bar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        if q.scheme() == 'https':
            # Secure
            self.safe_display.setPixmap(QPixmap(os.path.join('images', 'lock.png')))
        else:
            # Insecure
            self.safe_display.setPixmap(QPixmap(os.path.join('images', 'open_lock.png')))
        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)


app = QApplication(sys.argv)
app.setApplicationName("Meatball Browser")
window = Browser()
app.exec_()
