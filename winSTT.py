# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.

# Fix: text vanishing, live transcription, live system audio transcription with diarization

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QSizePolicy, QWidget, QFrame, QLabel, QProgressBar, QCheckBox, QPushButton, QTextEdit, QMessageBox, QMainWindow, QGraphicsView, QComboBox, QApplication, QGraphicsOpacityEffect
from PyQt6.QtCore import pyqtSignal, QThread, QTimer, QPropertyAnimation, QTimer, QEasingCurve, Qt, QSequentialAnimationGroup
from PyQt6.QtGui import QAction, QIcon
import sys
import os
import keyboard
import onnxruntime as ort
from utils.transcribe import WhisperONNXTranscriber, VaDetector
from utils.listener import AudioToText
from logger import setup_logger

logger = setup_logger()

class VadWorker(QtCore.QObject):
    initialized = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.status = False
        
    def run(self):
        try:
            self.vad = VaDetector()
            self.initialized.emit()
            self.toggle_status()
        except Exception as e:
            self.error.emit(f"Failed to initialize VAD: {e}")
            logger.debug(f"Failed to initialize VAD: {e}")
            
    def toggle_status(self):
        self.status = True if self.status==False else False
        
class ModelWorker(QtCore.QObject):
    initialized = pyqtSignal()
    error = pyqtSignal(str)
    display_message_signal = QtCore.pyqtSignal(object, object, object, object, object)# txt=None, filename=None, percentage=None, hold=False, reset=None

    def __init__(self, quantization=None):
        super().__init__()
        self.quantization = quantization
        self.status=False

    def run(self):
        try:
            self.model = WhisperONNXTranscriber(q=self.quantization, display_message_signal=self.display_message_signal)
            self.initialized.emit()
            self.toggle_status()
        except Exception as e:
            self.error.emit(f"Failed to initialize model: {e}")
            logger.debug(f"Failed to initialize model: {e}")
            
    def toggle_status(self):
        self.status = True if self.status==False else False
        
class ListenerWorker(QtCore.QObject):
    transcription_ready = pyqtSignal(str)
    error = pyqtSignal(str)
    initialized = pyqtSignal(str)
    display_message_signal = QtCore.pyqtSignal(object, object, object, object, object)# txt=None, filename=None, percentage=None, hold=False, reset=None
    
    def __init__(self, model, vad):
        super().__init__()
        self.model = model
        self.vad = vad

    def run(self):
        try:
            self.listener = AudioToText(self.model, self.vad, error_callback=self.display_message_signal)
            self.listener.run()
            self.initialized.emit()
        except Exception as e:
            self.error.emit(f"Listener Error: {e}")
            logger.debug(f"Listener Error: {e}")
            
class Ui_MainWindow(object):
    
    def setupUi(self, MainWindow):
        
        self.script_path = (os.path.dirname(os.path.abspath(__file__)))
        # print(self.script_path)
        self.acc = "CUDAExecutionProvider" in ort.get_available_providers()
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.setFixedSize(400, 300)
        
        icon = QIcon(os.path.join(self.script_path, "./media/Windows 1 Theta.png"))
        MainWindow.setWindowIcon(icon)
        
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(46, 52, 64))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(20, 27, 31))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(46, 52, 64))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(20, 27, 31))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(20, 27, 31))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(20, 27, 31))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Window, brush)
        MainWindow.setPalette(palette)
        self.centralwidget = QWidget(parent=MainWindow)
        self.centralwidget.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.line = QFrame(parent=self.centralwidget)
        self.line.setStyleSheet("color: rgb(144, 164, 174);")
        self.line.setGeometry(QtCore.QRect(80, 190, 241, 20))
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.checkBox = QCheckBox(parent=self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(10, 269, 180, 31))
        font = QtGui.QFont()
        font.setFamily("Roboto")
        self.checkBox.setFont(font)
        self.checkBox.setAcceptDrops(True)
        self.checkBox.setObjectName("checkBox")
        self.checkBox.setStyleSheet("""QCheckBox {
                                    border-style: outset;
                                    border-radius: 3px;
                                    color: rgb(144, 164, 174);
                                }
                                QCheckBox::indicator {
                                    background-color: rgb(54, 71, 84);
                                    border-width: 1px;
                                    border-color: rgb(78, 106, 129);
                                }
                                QCheckBox::indicator:checked {
                                    background-color: rgb(20, 89, 134);
                                }
                                """)
        self.label = QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(262, 269, 161, 31))
        self.label.setStyleSheet("""QLabel {
                                    color: rgb(144, 164, 174);
                                }
                                """)
        font = QtGui.QFont()
        font.setFamily("Roboto")
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.WinSTT = QLabel(parent=self.centralwidget)
        self.WinSTT.setStyleSheet("""QLabel {
                                    color: rgb(144, 164, 174);
                                }
                                """)
        self.WinSTT.setGeometry(QtCore.QRect(150, 10, 131, 31))
        font = QtGui.QFont()
        font.setFamily("Codec Pro ExtraBold")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.WinSTT.setFont(font)
        self.WinSTT.setMouseTracking(True)
        self.WinSTT.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.WinSTT.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.WinSTT.setObjectName("WinSTT")
        self.label_3 = QLabel(parent=self.centralwidget)
        self.label_3.setStyleSheet("color: rgb(144, 164, 174);")
        self.label_3.setGeometry(QtCore.QRect(17, 200, 370, 50))
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Input")
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.progressBar = QProgressBar(parent=self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(60, 240, 290, 14))
        self.progressBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.progressBar.setStyleSheet("""
                                            QProgressBar {background-color: rgb(8, 11, 14);
                                            color: rgb(144, 164, 174);
                                            border-radius: 5px}
                                            """)
        font = QtGui.QFont()
        font.setFamily("Input")
        self.progressBar.setFont(font)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setVisible(False)
        self.graphicsView_2 = QGraphicsView(parent=self.centralwidget)
        self.graphicsView_2.setGeometry(QtCore.QRect(0, 270, 411, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(8, 11, 14))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(8, 11, 14))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(20, 27, 31))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Base, brush)
        self.graphicsView_2.setPalette(palette)
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.label_2 = QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(160, 10, 21, 21))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(os.path.join(self.script_path, "./media/Windows 1 Theta.png")))
        self.label_2.setScaledContents(True)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.pushButton = QPushButton(parent=self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(230, 70, 101, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setStyleSheet("QPushButton {background-color: rgb(54, 71, 84); color: rgb(144, 164, 174); border-style: outset;  border-radius: 3px; border-width: 1px; border-color: rgb(78, 106, 129)}")

        self.textEdit = QTextEdit(parent=self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(70, 70, 110, 31))
        self.textEdit.setLineWidth(0)
        self.textEdit.setText("right ctrl")
        self.textEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("Current Key")
        self.textEdit.setStyleSheet("""
                                    QTextEdit {background-color: rgb(54, 71, 84);
                                    color: rgb(144, 164, 174); border-style: outset;
                                    border-radius: 3px; border-width: 1px;
                                    border-color: rgb(78, 106, 129)}
                                    """)
        self.comboBox = QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(70, 140, 111, 31))
        self.comboBox.setObjectName("Model")
        self.comboBox.addItem("")
        self.comboBox.setStyleSheet("""
            QComboBox {
                background-color: rgb(54, 71, 84);
                color: rgb(144, 164, 174);
                placeholder-text-color: rgb(173, 190, 203);
                border-style: outset;
                border-radius: 3px;
                border-width: 1px;
                border-color: rgb(78, 106, 129);
                color: rgb(163, 190, 203);
            }

            QComboBox QAbstractItemView {
                background-color: rgb(8, 11, 14);
            }
        """)
        self.comboBox_2 = QComboBox(parent=self.centralwidget)
        self.comboBox_2.setGeometry(QtCore.QRect(230, 140, 101, 31))
        self.comboBox_2.setObjectName("Quantization")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setStyleSheet("""
            QComboBox {
                background-color: rgb(54, 71, 84);
                color: rgb(144, 164, 174);
                placeholder-text-color: rgb(173, 190, 203);
                border-style: outset;
                border-radius: 3px;
                border-width: 1px;
                border-color: rgb(78, 106, 129);
                color: rgb(163, 190, 203);
            }

            QComboBox QAbstractItemView {
                background-color: rgb(8, 11, 14);
            }
        """)
        self.label_4 = QLabel(parent=self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(360, 270, 31, 31))
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap(os.path.join(self.script_path, "./media/switch-on.png" if self.acc else "./media/switch-off.png")))
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")
        self.label_5 = QLabel(parent=self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(0, -5, 401, 51))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap(os.path.join(self.script_path,"./media/Untitled-1.png")))
        self.label_5.setScaledContents(True)
        self.label_5.setObjectName("label_5")
        self.label_5.raise_()
        self.graphicsView_2.raise_()
        self.line.raise_()
        self.checkBox.raise_()
        self.label.raise_()
        self.WinSTT.raise_()
        self.label_3.raise_()
        self.progressBar.raise_()
        self.label_2.raise_()
        self.pushButton.raise_()
        self.textEdit.raise_()
        self.comboBox.raise_()
        self.comboBox_2.raise_()
        self.label_4.raise_()
        self.logger = setup_logger()        
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "WinSTT"))
        self.checkBox.setText(_translate("MainWindow", "Recording sound (Drag/Drop)"))
        self.checkBox.setChecked(True)
        self.label.setText(_translate("MainWindow", "H/W Acceleration:"))
        self.WinSTT.setText(_translate("MainWindow", "STT"))
        self.label_3.setText(_translate("MainWindow", ""))
        self.pushButton.setText(_translate("MainWindow", "Change Rec Key"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Whisper-Turbo"))
        self.comboBox.setCurrentText("Whisper-Turbo") #! Change when adding new models
        self.comboBox.setEnabled(True if self.acc else False)
        self.comboBox_2.setItemText(0, _translate("MainWindow", "Full"))
        self.comboBox_2.setItemText(1, _translate("MainWindow", "quantized"))
        
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if self.record_key_toggle:
            if self.currently_hooked != None:
                keyboard.unhook_all()
                
            key_text = keyboard.read_event(suppress=True).name
            self.currently_hooked = key_text
            self.textEdit.setReadOnly(False)
            self.textEdit.setText(key_text)
            self.textEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.textEdit.setReadOnly(True)
            
        QWidget.keyPressEvent(self, event)
        
    # def vanish_text(self, fade_duration=3000):
    #     start_time = datetime.now()

    #     app = QApplication.instance()
    #     while datetime.now() - start_time < timedelta(milliseconds=fade_duration):
    #         app.processEvents()

    #         current_opacity = 1.0 - ((datetime.now() - start_time).total_seconds() / (fade_duration / 1000))
    #         self.label_3.setWindowOpacity(max(0, current_opacity))

    #     self.label_3.setText("")
    #     self.label_3.setWindowOpacity(1.0)
        
    def toggle_sound(self):
        if self.checkBox.isChecked():
            self.self.listener_worker.listener.start_sound = self.start_sound
        else:
            self.self.listener_worker.listener.start_sound = ""
            
    def dragEnterEvent(self, event):
        mime_data = event.mimeData()

        # Check if the dragged data contains URLs
        if mime_data.hasUrls():
            url = mime_data.urls()[0].toLocalFile()
            if os.path.splitext(url)[-1] in ['.mp3', '.wav']:
                event.acceptProposedAction()
            else:
                QMessageBox.warning(self, "Invalid File", "Please drop a .mp3 or .wav file.", QMessageBox.StandardButton.Ok)
                
    def dropEvent(self, event):
        mime_data = event.mimeData()

        # Check if the dragged data contains URLs
        if mime_data.hasUrls():
            url = mime_data.urls()[0]
            file_path = url.toLocalFile()
            self.start_sound = url
            self.listener_worker.listener.start_sound = self.start_sound
        
class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.start_sound = os.path.join(self.script_path, "./media/splash.mp3")
        self.currently_hooked = None
        self.record_key_toggle = False
        
        self.pushButton.clicked.connect(self.toggle_and_set)

        self.checkBox.clicked.connect(self.toggle_sound)
        
        self.timer= None
        
        self.minimize_counter = 0
        self.comboBox_2.setCurrentText("Full" if self.acc else "quantized")
        self.comboBox_2.currentIndexChanged.connect(self.init_workers_and_signals)
        self.comboBox.currentIndexChanged.connect(self.init_workers_and_signals)

        # Initialize threads
        self.vad_thread = QThread()
        self.model_thread = QThread()
        self.listener_thread = QThread()
        self.started_listener = False
        
        self.init_workers_and_signals()

        self.create_tray_icon()
        self.hide()
        self.minimize_counter = 0

    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("./media/Windows 1 Theta.png"))

        show_action = QAction("Show", self)
        close_action = QAction("Exit", self)
        show_action.triggered.connect(self.show_window)
        close_action.triggered.connect(self.close_app)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(close_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def close_app(self):
        self.tray_icon.hide()
        QtCore.QCoreApplication.quit()
        
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()

    def show_window(self):
        self.showNormal()
        self.activateWindow()
        
    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.WindowStateChange and self.isMinimized():
            # Override the close event to minimize to the system tray instead
            event.ignore() 
            self.hide()
            self.show_notification()
            
    def toggle_and_set(self):
        if not self.record_key_toggle:
            self.record_key_toggle = True
            self.pushButton.setText("Stop")
        else:
            self.record_key_toggle = False
            if self.currently_hooked != None:
                self.listener_worker.listener.set_record_key(self.currently_hooked)
            self.currently_hooked = None
            self.pushButton.setText("Record Key")
            
    def display_message(self, txt=None, filename=None, percentage=None, hold=None, reset=None):
        # Create opacity effects if they don't exist
        if not hasattr(self, 'label_opacity_effect'):
            self.label_opacity_effect = QGraphicsOpacityEffect(self.label_3)
            self.label_3.setGraphicsEffect(self.label_opacity_effect)
        
        if not hasattr(self, 'progress_opacity_effect'):
            self.progress_opacity_effect = QGraphicsOpacityEffect(self.progressBar)
            self.progressBar.setGraphicsEffect(self.progress_opacity_effect)

        # Handle text display
        if txt:
            # Reset opacity
            self.label_opacity_effect.setOpacity(1.0)
            self.label_3.setText(txt)

            # Create fade out animation
            fade_out = QPropertyAnimation(self.label_opacity_effect, b"opacity")
            fade_out.setDuration(3000)  # 3 second animation
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
            
            # Start fade out after 5 seconds
            QTimer.singleShot(5000, fade_out.start)
            
            # Clear text after animation
            fade_out.finished.connect(lambda: self.label_3.setText(""))
            
        elif filename:
            self.label_3.setText(f"Downloading {filename}...")
            self.label_opacity_effect.setOpacity(1.0)
        
        # Handle button states
        if hold:
            self.pushButton.setEnabled(False)
            self.textEdit.setEnabled(False)
            self.comboBox.setEnabled(False)
            self.comboBox_2.setEnabled(False)
        
        if reset:
            self.pushButton.setEnabled(True)
            self.textEdit.setEnabled(True)
            self.comboBox_2.setEnabled(True)
            
            # Create fade out animations for both elements
            fade_out_label = QPropertyAnimation(self.label_opacity_effect, b"opacity")
            fade_out_label.setDuration(3000)
            fade_out_label.setStartValue(1.0)
            fade_out_label.setEndValue(0.0)
            
            fade_out_progress = QPropertyAnimation(self.progress_opacity_effect, b"opacity")
            fade_out_progress.setDuration(3000)
            fade_out_progress.setStartValue(1.0)
            fade_out_progress.setEndValue(0.0)
            
            # Create animation group to run both animations together
            animation_group = QSequentialAnimationGroup()
            animation_group.addAnimation(fade_out_label)
            animation_group.addAnimation(fade_out_progress)
            
            # Start animations
            animation_group.start()
            
            # Clean up after animations complete
            def cleanup():
                self.label_3.setText("")
                self.progressBar.setVisible(False)
                self.progressBar.setProperty("value", 0)
            
            animation_group.finished.connect(cleanup)
        
        if percentage is not None:
            if not self.progressBar.isVisible():
                self.progressBar.setVisible(True)
                self.progress_opacity_effect.setOpacity(1.0)
            
            self.progressBar.setProperty("value", percentage)
            
            # If percentage reaches 100%, start fade out animation
            if percentage >= 100:
                QTimer.singleShot(1000, lambda: self.display_message(reset=True))
                
    def init_workers_and_signals(self):
        # Initialize VAD worker and thread
        if not hasattr(self, "vad_worker"):
            self.vad_worker = VadWorker()
            self.vad_worker.moveToThread(self.vad_thread)
            self.vad_worker.initialized.connect(lambda: self.display_message(txt="VAD Initialized"))
            self.vad_worker.initialized.connect(lambda: self.init_listener())
            self.vad_worker.error.connect(lambda error_message: self.display_message(txt=f"Error: {error_message}"))
            self.vad_thread.started.connect(self.vad_worker.run)
            self.vad_thread.start()

        # Initialize Model worker and thread
        if hasattr(self, "model_worker"):
            self.model_thread.quit()
            self.model_thread.wait()
            del self.model_worker
            del self.model_thread
            self.model_thread = QThread()
        self.model_worker = ModelWorker(self.comboBox_2.currentText())
        self.model_worker.moveToThread(self.model_thread)
        self.model_worker.display_message_signal.connect(lambda txt, filename, percentage, hold, reset: self.display_message(txt, filename, percentage, hold, reset))
        self.model_worker.initialized.connect(lambda: self.display_message(txt="Model Initialized"))
        self.model_worker.initialized.connect(lambda: self.init_listener())
        self.model_worker.error.connect(lambda error_message: self.display_message(txt=f"Error: {error_message}"))
        self.model_thread.started.connect(self.model_worker.run)
        self.model_thread.start()
        
    def init_listener(self):
        # Initialize Listener worker and thread
        if hasattr(self.model_worker, "model") and hasattr(self.vad_worker, "vad"):
            if not self.started_listener:
                self.started_listener = True
            if hasattr(self, "ListenerWorker"):
                self.listener_thread.quit()
                self.listener_thread.wait()
                del self.listener_worker
                del self.listener_thread
                self.listener_thread = QThread()
            self.listener_worker = ListenerWorker(self.model_worker.model, self.vad_worker.vad)
            self.listener_worker.moveToThread(self.listener_thread)
            self.listener_worker.transcription_ready.connect(self.handle_transcription)
            self.listener_worker.error.connect(lambda error_message: self.display_message(txt=f"Error: {error_message}"))
            self.listener_worker.initialized.connect(lambda: self.display_message(txt="Listener Initialized"))
            self.listener_worker.display_message_signal.connect(lambda txt, filename, percentage, hold, reset: self.display_message(txt, filename, percentage, hold, reset))
            self.listener_thread.started.connect(self.listener_worker.run)
            self.listener_thread.start()
            
    def handle_transcription(self, transcription):
        self.display_message(txt=f"{transcription}")
        
    def show_notification(self):
        self.minimize_counter +=1
    # Only show notification when the window is minimized the first time
        if self.minimize_counter == 1:
            self.tray_icon.showMessage(
                "App Minimized",
                "The app is minimized, and still running in the background. Right click on icon to exit",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            ) 

app = QApplication(sys.argv)
window = Window()
window.show()
app.exec()