#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore


class TabSwitch(QtGui.QTabWidget):

    def __init__(self):
        super(TabSwitch, self).__init__()
        self.altkey = False
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 600, 600)
        self.setWindowTitle('TabSwitch')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.initTabs()
        QtGui.QShortcut(QtGui.QKeySequence("Alt+Q"),
                        self, self.goTabBackward)
        QtGui.QShortcut(QtGui.QKeySequence("Alt+W"),
                        self, self.goTabForward)
        self.show()

    def initTabs(self):
        self.tab1 = QtGui.QWidget()
        self.addTab(self.tab1, "Tab 1")
        text = QtGui.QTextEdit(self.tab1)
        text.setHtml("Das ist Tab 1")

        self.tab2 = QtGui.QWidget()
        self.addTab(self.tab2, "Tab 2")
        text = QtGui.QTextEdit(self.tab2)
        text.setHtml("Das ist Tab 2")

        self.tab3 = QtGui.QWidget()
        self.addTab(self.tab3, "Tab 3")
        text = QtGui.QTextEdit(self.tab3)
        text.setHtml("Das ist Tab 3")

        self.tab4 = QtGui.QWidget()
        self.addTab(self.tab4, "Tab 4")
        text = QtGui.QTextEdit(self.tab4)
        text.setHtml("Das ist Tab 4")

        self.tab5 = QtGui.QWidget()
        self.addTab(self.tab5, "Tab 5")
        text = QtGui.QTextEdit(self.tab5)
        text.setHtml("Das ist Tab 5")

    def keyPressEvent(self, event):
        """
        key = event.key()
        #print key
        if key == QtCore.Qt.Key_Alt:
            self.altkey = True
        elif key == QtCore.Qt.Key_Q:
            if self.altkey:
                print "Alt + Q!!!"
                self.goTabBackward()

        elif key == QtCore.Qt.Key_W:
            if self.altkey:
                print "Alt + W!!!"
                self.goTabForward()
        """

    def keyReleaseEvent(self, event):
        """
        key = event.key()
        if key == QtCore.Qt.Key_Alt:
            self.altkey = False
        """

    def goTabForward(self):
        next = self.currentIndex() + 1
        if next > (self.count() - 1):
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(next)

    def goTabBackward(self):
        last = self.currentIndex() - 1
        if last < 0:
            self.setCurrentIndex(self.count()-1)
        else:
            self.setCurrentIndex(last)


def main():
    app = QtGui.QApplication(sys.argv)
    switch = TabSwitch()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()