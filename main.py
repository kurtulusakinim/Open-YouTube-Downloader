import sys
from PyQt5.QtCore import QThread
from pytube import YouTube
from pytube import Playlist
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QAction
from PyQt5.QtGui import QMovie, QPixmap, QImage, QTextCursor
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
import urllib
import os
import subprocess



class VideoDetailThread(QThread):
    ytdetailsignal = pyqtSignal(str, dict, bytes, list)
    ytexception =pyqtSignal(str)

    def __init__(self):
        super(VideoDetailThread, self).__init__()
        self.yt_url = ""
        self.yt_title = ""
        self.yt_thumbnail = ""
        self.yt_resolutions = []
        self.yt_sizesdict = {}

    @pyqtSlot(str, bytes)
    def run(self):
        try:
            self.getvideodetails(self.yt_url)
            self.ytdetailsignal.emit(self.yt_title, self.yt_sizesdict, self.yt_thumbnail, self.yt_resolutions)
        except:
            self.ytexception.emit("error")
            

    def getvideodetails(self, url):
        welcome.console.append("<font color='black'>Getting video details... </font>")
        yt = YouTube(url)
        self.yt_title = yt.title
        thumbnailurl = yt.thumbnail_url.replace('sddefault.jpg', 'mqdefault.jpg')
        self.yt_thumbnail = urllib.request.urlopen(thumbnailurl).read()

        streams = yt.streams
        audiobyte =  yt.streams.filter(only_audio=True).first().filesize


        self.yt_resolutions = []
        for i in streams.filter(type = "video", adaptive = True):
            if i.resolution not in self.yt_resolutions:
                self.yt_resolutions.append(i.resolution)

        filesizes = []

        for i in self.yt_resolutions:	
            videobyte = streams.filter(type = "video", adaptive = True, resolution = i).first().filesize	
            filesizemb = round((audiobyte + videobyte) /1000000, 2)	
            filesizes.append(str(filesizemb))	
        self.yt_sizesdict = {}	
        self.yt_sizesdict = dict(zip(self.yt_resolutions, filesizes))

    

class DownloadVideoThread(QThread):
    ytdownloadsignal= pyqtSignal(float)
    filesize = 0

    def __init__(self):
        super(DownloadVideoThread, self).__init__()
        self.yt_url = ""
        self.yt_quality = ""
        self.yt_urls = []

    @pyqtSlot(str)
    def run(self):
        if welcome.multipleselect == False:
            self.videodownload(self.yt_url, self.yt_quality)
        else:
            self.multipledownload(self.yt_urls, self.yt_quality)

    def videodownload(self, url, quality):

        yt = YouTube(url)
        yt.register_on_progress_callback(self.progress_bar)
        path = os.getcwd()
        titulo=yt.title
        unwantedstrings = ["?", "!", "|", "\\", "/", "*", ":", "<", ">", '"']
        for i in unwantedstrings:
            titulo = titulo.replace(i, "")

# Video and Audio - Download
        audiotitulo = yt.streams.filter(only_audio=True).first()
        if welcome.checkBox.isChecked():
            welcome.console.append("<font color='black'>****************************************************</font>")
            welcome.console.append("<font color='black'>Starting to download audio</font>")
            welcome.console.append("<font color='black'>****************************************************</font>")
            audio = yt.streams.get_audio_only()
            self.filesize = audio.filesize
            audio.download(path+'\\videos\\'+titulo,filename=titulo)
            audiodirect =  path + "\\videos\\" + titulo + "\\" + titulo
            welcome.console.append("<font color='green'>Audio downloaded</font>")
            welcome.console.append("<font color='black'>Converting audio file to mp3... </font>")
            
            newfile =  path + "\\videos\\" + titulo + "\\" + titulo + ".mp3"
            command = 'ffmpeg -y -i ' + '"' + audiodirect + '"' + ' "' + newfile + '"'
        

            subprocess.call(command, shell=True)
            os.system('del ' + '"' + audiodirect + '"')
            welcome.console.insertHtml("<font color='green'>Done!</font>")
            

        else:
            welcome.console.append("<font color='black'>****************************************************</font>")
            welcome.console.append("<font color='black'>Starting to download video</font>")
            welcome.console.append("<font color='black'>Selected quality: </font>" + quality)
            welcome.console.append("<font color='black'>****************************************************</font>")
            videotitulo = yt.streams.filter(type = "video", adaptive = True, resolution = quality).first()

            self.filesize = videotitulo.filesize

            yt.streams.get_audio_only().download(path+'\\videos\\'+titulo,filename=titulo+'audio')

            welcome.console.append("<font color='green'>Audio downloaded</font>")
    
            yt.streams.filter(type = "video", adaptive = True, resolution = quality).first().download(path+'\\videos\\'+titulo,filename=titulo+'video')

            welcome.console.append("<font color='green'>Video downloaded</font>")
# Merge Video and Audio
            videodirect = path + "\\videos\\" + titulo + "\\" + titulo + "video"
            audiodirect = path + "\\videos\\" + titulo + "\\" + titulo + "audio"
            newfile = path + "\\videos\\" + titulo + "\\" + titulo + ".mp4"

            command = 'ffmpeg -y -i ' + '"' + videodirect + '"' +  ' -i ' + '"' + audiodirect +  '"' + " -c copy " + '"' +newfile + '"'

            subprocess.call(command, shell=True)

            welcome.console.append("<font color='green'>Merged video and audio</font>")

            os.system('del ' + '"' + videodirect + '"' + ' &  del ' + '"' + audiodirect + '"' )

            welcome.console.append("<font color='black'>Useless files deleted</font>")
            welcome.console.append("<font color='green'>DONE!</font>")
    
    def multipledownload(self, urls, quality):
        welcome.lineEdit.setEnabled(False)
        welcome.qualitycombobox.addItem(quality)
        welcome.qualitycombobox.setCurrentText(quality)
        welcome.qualitycombobox.setEnabled(False)
        welcome.console.append("<font color='black'>****************************************************</font>")
        welcome.console.append("<font color='black'>Starting to download playlist...</font>")
        welcome.console.append("<font color='black'>Selected quality: </font>" + quality)
        welcome.console.append("<font color='black'>****************************************************</font>")

        count = 0
        for url in urls:
            count += 1

            welcome.lineEdit.setText(url)
            try:
                yt = YouTube(url)
            except:
                welcome.console.append("<font color='black'>Error! Video not found. Scanning next video... </font>" + str(count)+ "/" + str(len(urls)))
                welcome.multipleselect = False
                welcome.lineEdit.setEnabled(True)
                welcome.qualitycombobox.setEnabled(True)
                continue
            yt.register_on_progress_callback(self.progress_bar)

            path = os.getcwd()
            titulo=yt.title
        
            welcome.console.append("<font color='black'>****************************************************</font>")
            welcome.console.append("<font color='black'>Next video found! </font>"+ str(count)+ "/" + str(len(urls)))
            welcome.console.append("<font color='black'>Video title: </font>" + titulo)
            unwantedstrings = ["?", "!", "|", "\\", "/", "*", ":", "<", ">", '"']
            for i in unwantedstrings:
                titulo = titulo.replace(i, "")

            welcome.label_4.setText(titulo)

            thumbnailurl = yt.thumbnail_url.replace('sddefault.jpg', 'mqdefault.jpg')
            thumbnailscrap = urllib.request.urlopen(thumbnailurl).read()
            thumbnail = QImage()
            thumbnail.loadFromData(thumbnailscrap)
            welcome.thumbnail.setPixmap(QPixmap(thumbnail))

            

            if welcome.checkBox.isChecked():
                welcome.console.append("<font color='black'>****************************************************</font>")
                welcome.console.append("<font color='black'>Starting to download audio</font>")
                welcome.console.append("<font color='black'>****************************************************</font>")
                audio = yt.streams.get_audio_only()
                self.filesize = audio.filesize
                audio.download(path+'\\videos\\'+titulo,filename=titulo)
                audiodirect = path + "\\videos\\" + titulo + "\\" + titulo
                welcome.console.append("<font color='green'>Audio downloaded</font>")
                welcome.console.append("<font color='black'>Converting audio file to mp3... </font>")

                newfile =  path + "\\videos\\" + titulo + "\\" + titulo + ".mp3"

                command = 'ffmpeg -y -i ' + '"' + audiodirect + '"' + ' "' + newfile + '"'
                subprocess.call(command, shell=True)
                os.system('del ' + '"' + audiodirect + '"')

                welcome.console.insertHtml("<font color='green'>Done!</font>")

            
            else:
                audiotitulo = yt.streams.get_audio_only()
                audiosize = audiotitulo.filesize

                if quality == "BEST":
                    videotitulo = yt.streams.filter(type = "video", adaptive = True).first()
                else:
                    videotitulo = yt.streams.filter(type = "video", adaptive = True, resolution = quality).first()
            
            

                if videotitulo:
                    welcome.console.append("<font color='green'>Selected quality: </font>" + videotitulo.resolution)
                    self.filesize = videotitulo.filesize

                    filesizemb = round((audiosize + self.filesize) /1000000, 2)
                    welcome.label_6.setText(str(filesizemb) + " MB")

                    videotitulo.download(path+'\\videos\\'+titulo,filename=titulo+'video')
                    welcome.console.append("<font color='green'>Video downloaded</font>")
        
                else:
                    yt_resolutions = []
                    for i in yt.streams.filter(type = "video", adaptive = True, mime_type = "video/mp4"):
                        if i.resolution not in yt_resolutions:
                            yt_resolutions.append(i.resolution)
             
                    videotitulo = yt.streams.filter(type = "video", adaptive = True, mime_type = "video/mp4", resolution = max(yt_resolutions)).first()
                    welcome.console.append("<font color='green'>Selected quality: </font>" + max(yt_resolutions))
                    self.filesize = videotitulo.filesize
                    videotitulo.download(path+'\\videos\\'+titulo,filename=titulo+'video')
                    welcome.console.append("<font color='green'>Video downloaded</font>")
                        
                audiotitulo.download(path+'\\videos\\'+titulo,filename=titulo+'audio')
                welcome.console.append("<font color='green'>Audio downloaded</font>")

                videodirect = path + "\\videos\\" + titulo + "\\" + titulo + "video"
                audiodirect = path + "\\videos\\" + titulo + "\\" + titulo + "audio"
                newfile = path + "\\videos\\" + titulo + "\\" + titulo + ".mp4"

                command = 'ffmpeg -y -i ' + '"' + videodirect + '"' +  ' -i ' + '"' + audiodirect + '"' + " -c copy " + '"' +newfile + '"'
                subprocess.call(command, shell=True)

                welcome.console.append("<font color='green'>Merged video and audio</font>")

                os.system('del ' + '"' + videodirect + '"' + ' &  del ' + '"' + audiodirect + '"' )
                welcome.console.append("<font color='black'>Useless files deleted</font>")
                welcome.console.append("<font color='green'>DONE!</font>")

        welcome.multipleselect = False
        welcome.lineEdit.setEnabled(True)
        welcome.qualitycombobox.setEnabled(True)
        welcome.lineEdit.clear()


    def progress_bar(self, chunk, file_handle, bytes_remaining):
        remaining = (100 * bytes_remaining) / self.filesize
        step = 100 - int(remaining)
        self.ytdownloadsignal.emit(step)





class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super(YouTubeDownloader, self).__init__()
        loadUi("youtubedownloader.ui", self)

        self.multiple = MultipleDownloader()

        self.about = AboutPage()
        
        self.ytdetail = VideoDetailThread()

        self.sizesdict = {}

        self.ytdetail.ytdetailsignal.connect(self.showdetails)
        self.ytdetail.ytexception.connect(self.geterror)
        self.downloadbutton.setEnabled(False)

        self.videodownload = DownloadVideoThread()
        self.videodownload.ytdownloadsignal.connect(self.processdownload)

        self.multipleselect = False
        self.console.ensureCursorVisible()

        self.aboutaction = QAction("About")
        self.menubar.addAction(self.aboutaction)

        self.aboutaction.triggered.connect(self.openaboutpage)



        self.show()

    def openaboutpage(self):
        self.about.show()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        self.progressBar.setValue(0) 
        clipboard = QApplication.clipboard()
        self.lineEdit.clear()
        self.lineEdit.setText(clipboard.text())


    @pyqtSlot(str)
    def on_lineEdit_textChanged(self):
        if self.lineEdit.text():
            if self.multipleselect == False:
                self.console.clear()
                self.progressBar.setValue(0)
                self.downloadbutton.setEnabled(False)
                self.qualitycombobox.clear()
                self.label_4.clear()
                self.label_6.clear()
                loading_gif = QMovie(self.resource_path("loading.gif"))
                self.thumbnail.setMovie(loading_gif)
                loading_gif.start()

                self.ytdetail.yt_url = self.lineEdit.text()
                self.ytdetail.start()
            else:
                loading_gif = QMovie(self.resource_path("loading.gif"))
                self.thumbnail.setMovie(loading_gif)
                loading_gif.start()

    @pyqtSlot(str)
    def on_qualitycombobox_currentTextChanged(self):
        quality = self.qualitycombobox.currentText()
        if quality:	
            try:	
                self.label_6.setText(self.sizesdict[quality] + " MB")	
            except:	
                pass

    @pyqtSlot()
    def on_downloadbutton_clicked(self):
        self.videodownload.yt_url = self.ytdetail.yt_url
        self.videodownload.yt_quality = self.qualitycombobox.currentText()
        self.videodownload.start()

    @pyqtSlot()
    def on_multiplebutton_clicked(self):
        self.multiple.textEdit.clear()
        self.multiple.checkBox.setChecked(False)
        self.multiple.show()


    @pyqtSlot()
    def on_console_textChanged(self):
        self.console.moveCursor(QTextCursor.End)

    @pyqtSlot(int)
    def on_checkBox_stateChanged(self):
        if self.checkBox.isChecked():
            self.qualitycombobox.setEnabled(False)
            self.label_6.setVisible(False)
            self.downloadbutton.setText("Download Audio!")
        else:
            self.qualitycombobox.setEnabled(True)
            self.label_6.setVisible(True)
            self.downloadbutton.setText("Download!")
            

    def showdetails(self, yt_title, yt_sizesdict, yt_thumbnail, yt_resolutions):
        self.sizesdict = yt_sizesdict
        self.qualitycombobox.addItems(yt_resolutions)
        if len(yt_title) > 40:
            self.label_4.setText(yt_title[:41] + "...")
        else:
            self.label_4.setText(yt_title)
        self.label_6.setText(list(yt_sizesdict.values())[0] +" MB")
        self.setthumbnail(yt_thumbnail)
        self.downloadbutton.setEnabled(True)
        self.console.insertHtml('<font color="green">DONE!</font>')

    def setthumbnail(self, thumbnailurl):
        thumbnail = QImage()
        thumbnail.loadFromData(thumbnailurl)
        self.thumbnail.setPixmap(QPixmap(thumbnail))

    def geterror(self, error):
        pass

    def processdownload(self, download):
        self.progressBar.setValue(download)



class MultipleDownloader(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("multipledownloader.ui", self)
        self.setWindowModality(Qt.ApplicationModal)

    @pyqtSlot()
    def on_pastebutton_clicked(self):
        clipboard = QApplication.clipboard()
        self.textEdit.append(clipboard.text())

    @pyqtSlot()
    def on_clearbutton_clicked(self):
        self.textEdit.clear()
    
    @pyqtSlot()
    def on_scrapbutton_clicked(self):
        clipboard = QApplication.clipboard()
        try:
            p = Playlist(clipboard.text())
            for url in p.video_urls:
                self.textEdit.append(url)
        except:
            pass

    @pyqtSlot()
    def on_downloadallbutton_clicked(self):
        self.close()
        if self.checkBox.isChecked():
            welcome.checkBox.setChecked(True)
        else:
            welcome.checkBox.setChecked(False)

        urls = self.textEdit.toPlainText().split("\n")
        welcome.videodownload.yt_urls = urls
        welcome.videodownload.yt_quality = self.comboBox.currentText()

        welcome.multipleselect = True
        welcome.videodownload.start()
        

class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("aboutpage.ui", self)
        self.setWindowModality(Qt.ApplicationModal)


# main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome = YouTubeDownloader()
    sys.exit(app.exec_())
