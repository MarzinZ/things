#!/usr/bin/env python
#coding=utf8

"""Usage:
         things.py
         things.py all
         things.py clear
         things.py <thing>
         things.py done <num>
         things.py hasDone <num>
         things.py rm <num>
"""

import sqlite3
import sys
from os import path
from docopt import docopt
from datetime import datetime
from uuid import uuid4

class TermColor:
    RED = "\033[91m"
    GREEN = "\033[92m"
    BOLD = "\033[1m"
    END = "\033[0m"

class TermSign:
    CHECK = u"\u2714".encode("utf8")
    START = u"\u2731".encode("utf8")
    BALLOTBOXWITHCHECK = u"\u2611".encode("utf8")
    BALLOTBOX = u"\u2610".encode("utf8")


class Thing(object):
    def __init__(self, token, name, time, hasDone=0):
        self.token = token
        self.name = name
        self.time = time
        self.hasDone = hasDone

class ToDo(object):
    def __init__(self, db_file="todo.db"):
        self.db_file = db_file
        self.todos = []
        self.db = sqlite3.connect(db_file)
        self.cur = self.db.cursor()
        try:
            with self.db:
                self.cur.execute('''CREATE TABLE IF NOT EXISTS
                            todolist(token TEXT PRIMARY KEY, name TEXT, time TEXT, 
                                    hasDone INTEGER)''')
            with self.db:
                self.cur.execute('''SELECT * FROM todolist''')
                for info in self.cur:
                    t = Thing(*info)
                    self.todos.append(t)

        except sqlite3.DatabaseError as err:
            sys.stderr.write(str(err)+"\n")

    def add(self, thing):
        token = thing.token
        name = thing.name
        time = thing.time
        hasDone = thing.hasDone
        try:
            with self.db:
                self.cur.execute('''INSERT INTO todolist VALUES(?, ?, ?, ?)''', 
                    (token, name, time, hasDone))
                self.todos.append(thing)
        except sqlite3.DatabaseError as err:
            sys.stderr.write("ERROR add: " + str(err)+"\n")

    def done(self, index):
        token = self.todos[index-1].token
        try:
            with self.db:
                self.cur.execute('''UPDATE todolist SET hasDone = ? WHERE token = ?''',
                    (1, token))
                self.todos[index-1].hasDone = 1
        except sqlite3.DatabaseError as err:
            sys.stderr.write("ERROR done: " + str(err)+"\n")

    def remove(self, index):
        token = self.todos[index-1].token
        try:
            with self.db:
                self.cur.execute('''DELETE FROM todolist WHERE token = ?''',
                    (token,))
            del self.todos[index-1]
        except sqlite3.DatabaseError as err:
            sys.stderr.write("ERROR remove" + str(err)+"\n")

    def clear(self):
        try:
            with self.db:
                self.cur.execute('''DROP TABLE todolist''')
                del self.todos[:]
        except sqlite3.DatabaseError as err:
            sys.stderr.write("ERROR clear" + str(err)+"\n")

    def print_todo(self):
        print
        # print "{0}  TO-DO-List  {0}".format("*"*32)
        for index, thing in enumerate(self.todos):
            if thing.hasDone == 0:
                print TermColor.RED + TermSign.START + TermColor.END,
                print " {0}. {1}\t\t {2}".format(index+1, thing.name, thing.time)
        print

    def print_all(self):
        print
        # print "{0}  Archieve-List  {0}".format("*"*32)
        for index, thing in enumerate(self.todos):
            if thing.hasDone == 0:
                print TermColor.RED + TermSign.START + TermColor.END,
            else:
                print TermColor.GREEN + TermSign.CHECK + TermColor.END,
            print " {0}. {1}\t\t {2}".format(index+1, thing.name, thing.time)
        print

def main():
    parser = docopt(__doc__)
    td = ToDo()
    try:
        if parser["rm"]:
            td.remove(int(parser["<num>"]))
        elif parser["clear"]:
            td.clear()
        elif parser["done"]:
            td.done(int(parser["<num>"]))
        elif parser["hasDone"]:
            td.hasDone(int(parser["<num>"]))
        elif parser["<thing>"]:
            token = uuid4().bytes.encode("base64")
            time = datetime.now().strftime("%Y-%m-%d %H:%M")
            thing = Thing(token, parser["<thing>"], time)
            td.add(thing)

        if parser["all"]:
            td.print_all()
        else:
            td.print_todo()
    except IndexError:
        sys.stderr.write("Index is out of range, please retry...\n")
    except ValueError as err:
        sys.stderr.write("Parse Parameter Wrong, {}, please retry...".format(err))

if __name__ == "__main__":
    main()