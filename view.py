import urllib.request
import re, sys
import pickle, math
from tkinter import *

class View:
	def __init__(self):
		self.root = Tk()
		self.root.title("Информационный поиск")
		self.root.geometry('640x480')

		self.ent = Entry(self.root, width=50, bd=3)
		self.but = Button(self.root, text="Поиск")
		self.scr = Scrollbar(self.root)
		self.mylist = Listbox(self.root, bd=0, yscrollcommand = self.scr.set, )
		self.lbl = Label(self.root, text="habrahabr", 
			bg="white", fg="blue", width=9)

		self.lbl.grid(row=0, column=0)
		self.ent.grid(row=0, column=1)
		self.but.grid(row=0, column=2)


		self.but.bind("<Button-1>", self.printer)
		self.ent.bind("<Return>", self.printer)

		self.root.mainloop()



	def DeleteListbox(self) :
		items = self.mylist.size()
		pos = 0

		for i in range(0, items) :
			idx = int(i) - pos
			self.mylist.delete(idx, idx)
			pos = pos + 1



	def printer(self, event):

		self.DeleteListbox()

		self.scr.pack(side=RIGHT, fill=Y)

		data = self.ent.get()

		if len(data) == 0 :
			self.mylist.insert(END, "Пустой запрос")

		else:
			for x in range(0, 100):
				self.mylist.insert(END, "This is line number " + str(x) + " " + str(data))

		self.mylist.place(x=0, y=30, width=625, height=450)
		self.scr.config(command=self.mylist.yview)

		items = self.mylist.size()

		print(items)




def test():
    obj = View()



test()



