import ftplib
import os

from model.process.ProcessCommand import ProcessCommand

def walk_dir(f, dirpath, filename):
    original_dir = f.pwd()
    try:
        f.cwd(dirpath)
        if dirpath.startswith("/"):
            create_folder(dirpath[1:])
    except ftplib.error_perm:
        if dirpath.startswith("/"):
            download_file(f,dirpath[1:],filename)
        return  

    names = f.nlst()
    for name in names:
        walk_dir(f, dirpath + '/' + name, name)
    f.cwd(original_dir)  

def download_file(f,dirpath,filename):
    dir_model= os.path.join(os.path.dirname(__file__), dirpath)
    file = open(dir_model, 'wb')
    f.retrbinary('RETR ' + filename, file.write)
    file.close()

def create_folder(dirpath):
    dir_model= os.path.join(os.path.dirname(__file__), dirpath)
    if not os.path.exists(dir_model):
        os.mkdir(dir_model)

def update(process: ProcessCommand, orch_ip, ftp_port, usr, psw):
    print(os.path.dirname(__file__))
    ftp = ftplib.FTP()
    try:
        ftp.connect(orch_ip, ftp_port)
        ftp.login(usr, psw)
        process.update_log("FTP Connection Success", True)
    except:
        process.update_log("FTP Connection Failed",True)
        return True

    data = []
    ftp.dir(data.append)

    dir =os.path.dirname(__file__)
    if not os.path.exists(dir):
        os.mkdir(dir)
    process.update_log("Init pull files",True)
    try:
        walk_dir(ftp, "","")
        process.update_log("Finished pull files", True)
    except:
        process.update_log("Fail pull files", True)
        return True

    ftp.quit()
