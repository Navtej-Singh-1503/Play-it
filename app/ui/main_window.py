    def _show_liked(self): self._library_page("Liked Songs",self.db.liked())
    def _show_history(self): self._library_page("History",self.db.history())
    def _library_page(self,title,songs):
        w,l=self._page(title); self._list(l,"",songs); self.content.addWidget(w); self.content.setCurrentWidget(w)
    def _show_playlists(self):
        w,l=self._page("Playlists"); create=QPushButton("＋ Create playlist",objectName="primary"); create.clicked.connect(self._create_playlist); l.addWidget(create); self.playlist_list=QListWidget(); l.addWidget(self.playlist_list); self._refresh_playlists(); self.content.addWidget(w); self.content.setCurrentWidget(w)
    def _refresh_playlists(self):
        if not hasattr(self,"playlist_list"):return
        self.playlist_list.clear()
        for p in self.db.playlists():
            i=QListWidgetItem(p["name"]); i.setData(Qt.UserRole,p); self.playlist_list.addItem(i)
        self.playlist_list.itemDoubleClicked.connect(lambda i:self._open_playlist(i.data(Qt.UserRole)))
    def _create_playlist(self):
        name,ok=QInputDialog.getText(self,"Create playlist","Name:");
        if ok and name.strip(): self.db.create_playlist(name); self._refresh_playlists()
    def _open_playlist(self,p):
        songs=self.db.playlist_songs(p["id"]); w,l=self._page(p["name"]); self._list(l,"",songs); self.content.addWidget(w); self.content.setCurrentWidget(w)
    def _show_downloads(self): self._library_page("Downloads",[])
    def _show_settings(self):
        w,l=self._page("Settings"); path=QLineEdit(self.settings.get("download_location","")); choose=QPushButton("Choose folder"); choose.clicked.connect(lambda:self._choose(path)); row=QHBoxLayout(); row.addWidget(path); row.addWidget(choose); l.addWidget(QLabel("Download location")); l.addLayout(row); save=QPushButton("Save settings",objectName="primary"); save.clicked.connect(lambda:(self.settings.update(download_location=path.text(),volume=self.volume.value()/100),save_settings(self.settings),self.statusBar().showMessage("Settings saved",3000))); l.addWidget(save); clear=QPushButton("Clear history"); clear.clicked.connect(lambda:(self.db.clear_history(),self.statusBar().showMessage("History cleared",3000))); l.addWidget(clear); l.addWidget(QLabel("About\nPLAY-IT is a lightweight local music player. Playback streams are not saved automatically.",objectName="muted")); l.addStretch(); self.content.addWidget(w); self.content.setCurrentWidget(w)
    def _choose(self,edit):
        p=QFileDialog.getExistingDirectory(self,"Download folder",edit.text());
        if p:edit.setText(p)
    def _show_queue(self):
        w,l=self._page("Queue"); self._list(l,"",self.queue); self.content.addWidget(w); self.content.setCurrentWidget(w)
    def _play_song(self,song):
        if not song.get("video_id"):return
        self.current=song; self.db.add_history(song); self.now.setText(f"{song.get('title')}\n{song.get('artist')}"); self.play.setText("⏳"); self._run(lambda:stream_url(song["video_id"]),self._stream_ready)
    def _stream_ready(self,url): self.player.setSource(QUrl(url)); self.player.play(); self.play.setText("Ⅱ"); self.like.setText("♥" if self.db.is_liked(self.current["video_id"]) else "♡")
    def _toggle(self):
        if self.player.playbackState()==QMediaPlayer.PlayingState:self.player.pause(); self.play.setText("▶")
        elif self.player.source().isValid():self.player.play(); self.play.setText("Ⅱ")
    def _next(self):
        if self.queue:
            self._play_song(self.queue.pop(0))
    def _previous(self): self.player.setPosition(0); self.player.play()
    def _position(self,p): self.progress.blockSignals(True); self.progress.setValue(p); self.progress.blockSignals(False); self.elapsed.setText(fmt(p))
    def _media_status(self,s):
        if s==QMediaPlayer.EndOfMedia:self._next()
        if s==QMediaPlayer.InvalidMedia:self.statusBar().showMessage("Playback failed",5000); self.play.setText("▶")
    def _like(self):
        if self.current:self.like.setText("♥" if self.db.toggle_like(self.current) else "♡")
    def _download(self):
        if not self.current:return
        folder=self.settings.get("download_location",str(Path.home()/"Downloads")) if False else self.settings.get("download_location","")
        folder=QFileDialog.getExistingDirectory(self,"Save download",folder)
        if not folder:return
        self.statusBar().showMessage("Downloading (only because you requested it)...")
        self._run(lambda:download(self.current["video_id"],folder),lambda _:self.statusBar().showMessage("Download complete",5000))

def run():
    app=QApplication([]); win=MainWindow(); win.show(); app.exec()
