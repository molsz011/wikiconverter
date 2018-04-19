from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import sys
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import exc
from mediawiki_functions import *
from tiki_functions import *
from jamwiki_functions import *
from wacko_functions import *
from wikka_functions import *

class WikiGUI(Frame):
    def __init__(self):
        super().__init__()

        self.master.title("Wiki Converter")
        self.pack(fill=BOTH, expand=True)

        self.frame1 = Frame(self)
        self.frame1.pack(fill=X)

        self.lbl1 = Label(self.frame1, text="Admin username", width=15)
        self.lbl1.pack(side=LEFT, padx=5, pady=5)

        self.admin = Entry(self.frame1)
        self.admin.pack(fill=X, padx=5, expand=True)

        self.frame2 = Frame(self)
        self.frame2.pack(fill=X)

        self.lbl2 = Label(self.frame2, text="Password", width=15)
        self.lbl2.pack(side=LEFT, padx=5, pady=5)

        self.pwd = Entry(self.frame2)
        self.pwd.pack(fill=X, padx=5, expand=True)

        self.frame3 = Frame(self)
        self.frame3.pack(fill=X)

        self.lbl3 = Label(self.frame3, text="Hostname", width=15)
        self.lbl3.pack(side=LEFT, padx=5, pady=5)

        self.host = Entry(self.frame3)
        self.host.pack(fill=X, padx=5, expand=True)
        self.host.insert(END, 'localhost')

        self.frame4 = Frame(self)
        self.frame4.pack(fill=X)

        self.lbl4 = Label(self.frame4, text="Port", width=15)
        self.lbl4.pack(side=LEFT, padx=5, pady=5)

        self.port = Entry(self.frame4)
        self.port.pack(fill=X, padx=5, expand=True)
        self.port.insert(END, '3306')

        self.frame8 = Frame(self)
        self.frame8.pack(fill=X)

        self.lbl8 = Label(self.frame8, text="Source Wiki", width=15)
        self.lbl8.pack(side=LEFT, padx=5, pady=5)

        self.srcwiki = StringVar()
        self.srcwiki.set('MediaWiki')
        self.src = OptionMenu(self.frame8, self.srcwiki, 'MediaWiki','TikiWiki','JamWiki','WackoWiki','WikkaWiki')
        self.src.pack(fill=X, padx=5, expand=True)

        self.frame5 = Frame(self)
        self.frame5.pack(fill=X)

        self.lbl5 = Label(self.frame5, text="Source DB name", width=15)
        self.lbl5.pack(side=LEFT, padx=5, pady=5)

        self.srcname = Entry(self.frame5)
        self.srcname.pack(fill=X, padx=5, expand=True)

        self.frame10 = Frame(self)
        self.frame10.pack(fill=X)

        self.srcpath_ = StringVar()
        self.lbl10 = Label(self.frame10, text="Src. media directory", width=15)
        self.lbl10.pack(side=LEFT, padx=5, pady=5)

        self.srcpathen = Entry(self.frame10, textvariable=self.srcpath_)
        self.srcpathen.pack(padx=5, side=LEFT, ipadx=12)

        self.srcpathb = Button(self.frame10, text='Browse...', command=self.getsrcpath)
        self.srcpathb.pack(padx=5, side=LEFT)

        # if self.srcwiki.get() == 'WikkaWiki':
        #     self.srcpathen.config(state=DISABLED)
        #     self.srcpathb.config(state=DISABLED)

        self.frame7 = Frame(self)
        self.frame7.pack(fill=X)

        self.lbl7 = Label(self.frame7, text="Destination Wiki", width=15)
        self.lbl7.pack(side=LEFT, padx=5, pady=5)

        self.destwiki = StringVar()
        self.destwiki.set('TikiWiki')
        self.dest = OptionMenu(self.frame7, self.destwiki, 'MediaWiki','TikiWiki','JamWiki','WackoWiki','WikkaWiki')
        self.dest.pack(fill=X, padx=5, expand=True)

        self.frame6 = Frame(self)
        self.frame6.pack(fill=X)

        self.lbl6 = Label(self.frame6, text="Destination DB name", width=15)
        self.lbl6.pack(side=LEFT, padx=5, pady=5)

        self.destname = Entry(self.frame6)
        self.destname.pack(fill=X, padx=5, expand=True)

        self.frame11 = Frame(self)
        self.frame11.pack(fill=X)

        self.destpath_ = StringVar()
        self.lbl11 = Label(self.frame11, text="Dest. media directory", width=15)
        self.lbl11.pack(padx=5, side=LEFT)

        self.destpathen = Entry(self.frame11, textvariable=self.destpath_)
        self.destpathen.pack(padx=5, side=LEFT, ipadx=12)
        # self.destpathen.cget('state')

        self.destpathb = Button(self.frame11, text='Browse...', command=self.getdestpath)
        self.destpathb.pack(padx=5, side=LEFT)
        # self.destpathb.cget('state')
        #
        # if self.destwiki.get() == 'WikkaWiki':
        #     self.destpathen.config(state=DISABLED)
        #     self.destpathb.config(state=DISABLED)

        self.frame9 = Frame(self)
        self.frame9.pack(fill=X)

        self.commitbutton = Button(self.frame9, text="Proceed", command=self.submit)
        self.commitbutton.pack(side=BOTTOM, fill=X, ipadx=30, padx=5, pady=10)

        # self.testbutton = Button(self.frame9, text="Test", command=self.test)
        # self.testbutton.pack(side=RIGHT, fill=X, ipadx=15, padx=5)


    def test(self):
        print(self.admin.get())
        print(self.pwd.get())
        print(self.host.get())
        print(self.port.get())
        print(self.srcwiki.get())
        print(self.srcname.get())
        print(self.srcpath_.get())
        print(self.destwiki.get())
        print(self.destname.get())
        print(self.destpath_.get())
        print('mysql://' + self.admin.get() + ':' + self.pwd.get() + '@' + self.host.get() + ':' + \
                      self.port.get() + '/' + self.srcname.get())
        print('mysql://' + self.admin.get() + ':' + self.pwd.get() + '@' + self.host.get() + ':' + \
                       self.port.get() + '/' + self.destname.get())

    def submit(self):
        src_connect = 'mysql://' + self.admin.get() + ':' + self.pwd.get() + '@' + self.host.get() + ':' + \
                      self.port.get() + '/' + self.srcname.get()
        dest_connect = 'mysql://' + self.admin.get() + ':' + self.pwd.get() + '@' + self.host.get() + ':' + \
                       self.port.get() + '/' + self.destname.get()
        try:
            Base = automap_base()
            engine = create_engine(src_connect, echo=True)
            Base.prepare(engine, reflect=True)
            session = Session(engine)
        except exc.OperationalError:
            # print('Cannot connect to the source database.')
            messagebox.showerror('Error', 'Cannot connect to the source database.')
            return


        try:
            Base2 = automap_base()
            engine2 = create_engine(dest_connect, echo=True)
            Base2.prepare(engine2, reflect=True)
            session2 = Session(engine2)
        except exc.OperationalError:
            # print('Cannot connect to the destination database.')
            messagebox.showerror('Error', 'Cannot connect to the destination database.')
            return

        session.flush()
        session2.flush()
        src = self.srcwiki.get()
        dest = self.destwiki.get()
        srcpath = self.srcpath_.get()
        destpath = self.destpath_.get()
        print(src)
        print(dest)
        if src == 'MediaWiki':
            dicts = mediawiki_pages_to_dict(session, Base)
            files = mediawiki_img_to_dict(session, Base, srcpath)
        elif src == 'TikiWiki':
            dicts = tiki_pages_to_dict(session, Base)
            files = tiki_img_to_dict(session, Base, srcpath)
        elif src == 'JamWiki':
            dicts = jam_pages_to_dict(session, Base)
            files = jamwiki_img_to_dict(session, Base, srcpath)
        elif src == 'WackoWiki':
            dicts = wacko_pages_to_dict(session, Base)
            files = wacko_img_to_dict(session, Base, srcpath)
        elif src == 'WikkaWiki':
            dicts = wikka_pages_to_dict(session, Base)
            files = wikka_img_to_dict(srcpath)
        else:
            messagebox.showerror('Error', 'Invalid source Wiki.')
            return

        if dest == 'MediaWiki':
            mediawiki_dict_to_pages(session2, Base2, dicts)
            mediawiki_dict_to_files(session2, Base2, destpath, files)
        elif dest == 'TikiWiki':
            tiki_dict_to_files(session2, Base2, destpath, files)
            tiki_dict_to_pages(session2, Base2, dicts)
        elif dest == 'JamWiki':
            jamwiki_dict_to_pages(session2, Base2, dicts)
            jamwiki_dict_to_files(session2, Base2, destpath, files)
        elif dest == 'WackoWiki':
            wacko_dict_to_pages(session2, Base2, dicts)
            wacko_dict_to_files(session2, Base2, destpath, files)
        elif dest == 'WikkaWiki':
            wikka_dict_to_pages(session2, Base2, dicts)
            wikka_dict_to_files(destpath, files)
        else:
            messagebox.showerror('Error', 'Invalid destination Wiki.')
            return
        session.expire_all()
        session2.expire_all()
        messagebox.showinfo('Success!', 'Database has been successfully imported.')

    def getsrcpath(self):
        srcfilename = filedialog.askdirectory()
        self.srcpath_.set(srcfilename)

    def getdestpath(self):
        destfilename = filedialog.askdirectory()
        self.destpath_.set(destfilename)


def main():
    root = Tk()
    root.geometry("350x350+300+300")
    app = WikiGUI()
    root.resizable(width=False, height=False)
    root.mainloop()


if __name__ == '__main__':
    main()