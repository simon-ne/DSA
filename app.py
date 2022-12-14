import sys
import os
from time import ctime
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5 import uic

from lib.rsa import RSA
from lib.dsa import DSA
 
qtCreatorFile = os.path.join('ui', 'dsa.ui')
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

 
class MyApp(QMainWindow, Ui_MainWindow):
    file_path = None
    rsa = None

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.generateKeys.clicked.connect(self.generate_keys)
        self.saveKeys.clicked.connect(self.save_keys)
        self.loadPrivateKey.clicked.connect(self.load_private_key)
        self.loadPublicKey.clicked.connect(self.load_public_key)
        self.loadFile.clicked.connect(self.load_file)
        self.signFile.clicked.connect(self.sign_file)
        self.checkSignature.clicked.connect(self.check_signature)

    #-----------#
    #  HELPERS  #
    #-----------#
    def open_file_dialog(self, file_format = 'All Files (*)'):
        """Opens a file dialog where user can select a file to open.

        Args:
            file_format (str, optional): Which formats can user choose. Defaults to 'All Files (*)'.

        Returns:
            str: Path to the selected file. Returns None if no file was selected.
        """

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a file", "", file_format, options=options)

        if file_path:
            return file_path


    def save_file_dialog(self, file_format = 'All Files (*)'):
        """Opens a save file dialog where user can select where to save a file.

        Args:
            file_format (str, optional): Which formats can be the file saved in. Defaults to 'All Files (*)'.

        Returns:
            str: Path to a selected save location. Returns None if no location was selected.
        """

        options = QFileDialog.Options()
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", file_format, options=options)

        if path:
            return path


    def folder_dialog(self):
        """Opens a folder dialog where user can select a folder.

        Returns:
            str: Path to selected folder. Returns None if no folder was selected.
        """

        folder_path = QFileDialog.getExistingDirectory(self, 'Select directory')

        if folder_path:
            return folder_path
    

    def message_popup(self, text, title='Error'):
        """Opens an informative popup with defined text and title.

        Args:
            text (str): Text content of the popup.
            title (str, optional): Title of the popup. Defaults to 'Error'.
        """

        dlg = QMessageBox(self)
        dlg.setWindowTitle(title)
        dlg.setText(text)
        dlg.exec()



    #-----------#
    #  BUTTONS  #
    #-----------#
    def load_file(self):
        """Handles Load File button in UI, loads file and prints info about it in fileInfo input.
        """

        # Choose a file
        path = self.open_file_dialog('All Files (*)')

        # If closed the dialog
        if not path: return

        # Check if path is file
        if not os.path.isfile:
            self.message_popup('Only single files can be loaded, not folders.')
            return

        # Save path for signing or checking
        self.file_path = path

        # Get file informations for outputing
        file_info = {}
        file_info['File name'] = os.path.basename(path)
        file_info['File type'] = os.path.splitext(path)[-1]
        file_info['File location'] = path
        file_info['File size'] = str(round(os.stat(path).st_size/1024, 2)) + ' KB'
        file_info['Created'] = ctime(os.stat(path).st_ctime)
        file_info['Last modified'] = ctime(os.stat(path).st_mtime)
        file_info['Last accessed'] = ctime(os.stat(path).st_atime)

        file_info_out = ''
        for key, value in file_info.items():
            file_info_out += f"{key}: {value}\n"

        self.fileInfo.setText(file_info_out)

    
    def generate_keys(self):
        """Generates new RSA keys, prints it to privateKeyOut, publicKeyOut, pOut and qOut.
        """

        rsa = RSA()

        # Set keys to text fields
        self.privateKeyOut.setText(f"{rsa.private_key[0]}, {rsa.private_key[1]}")
        self.publicKeyOut.setText(f"{rsa.public_key[0]}, {rsa.public_key[1]}")

        # Set p and q to text fieds
        self.pOut.setText(str(rsa.primes['p']))
        self.qOut.setText(str(rsa.primes['q']))

        # Set object as class variable for saving keys
        self.rsa = rsa
    

    def save_keys(self):
        """Saves generated RSA keys to a location given from folder_dialog to .priv and .pub files.
        """

        # Check if rsa object exists
        if not self.rsa:
            self.message_popup('Only generated keys can be saved.')
            return

        # If text in inputs are different from generated keys in self.rsa
        if f"{self.rsa.private_key[0]}, {self.rsa.private_key[1]}" != self.privateKeyOut.text():
            self.message_popup('Only generated keys can be saved.')
            return
            
        if f"{self.rsa.public_key[0]}, {self.rsa.public_key[1]}" != self.publicKeyOut.text():
            self.message_popup('Only generated keys can be saved.')
            return
        
        # Get save location
        path = self.folder_dialog()

        # If not chosen any file
        if not path:
            return
        
        # Check if path is a folder
        if not os.path.isdir(path):
            self.message_popup('Save location must be a folder.')
            return
        try:
            self.rsa.generate_key_files(path)
        except:
            self.message_popup('Ooops, something went wrong while saving the keys.')
            return

    
    def load_private_key(self):
        """Loads private RSA key from .priv file and prints it in privateKeyOut field.
        """

        # Get priv key file location
        path = self.open_file_dialog('Private Key (*.priv);;All Files (*)')

        if not path: return

        # Check corret file format
        if os.path.splitext(path)[-1] != '.priv':
            self.message_popup('Private key can only be loaded from .priv file.')
            return

        # Open file and get content
        with open(path, 'r') as f:
            private_key_str = f.read().replace('RSA ', '')
        
        try:
            # Parse content
            part_1 = private_key_str.split(', ')[0][1:]
            part_2 = private_key_str.split(', ')[1][:-1]

            # Write priv key to text field
            self.privateKeyOut.setText(f"{part_1}, {part_2}")
        except:
            self.message_popup(f"Wrong key format in {path}")
            return

        # Remove p and q values since they would be misleading
        self.pOut.setText('')
        self.qOut.setText('')


    def load_public_key(self):
        """Loads public RSA key from .pub file and prints it in publicKeyOut field.
        """

        # Get priv key file location
        path = self.open_file_dialog('Public Key (*.pub);;All Files (*)')

        if not path: return

        # Check corret file format
        if os.path.splitext(path)[-1] != '.pub':
            self.message_popup('Public key can only be loaded from .pub file.')
            return

        # Open file and get content
        with open(path, 'r') as f:
            public_key_str = f.read().replace('RSA ', '')
        
        try:
            # Parse content
            part_1 = public_key_str.split(', ')[0][1:]
            part_2 = public_key_str.split(', ')[1][:-1]

            # Write priv key to text field
            self.publicKeyOut.setText(f"{part_1}, {part_2}")
        except:
            self.message_popup(f"Wrong key format in {path}")
            return
        
        # Remove p and q values since they would be misleading
        self.pOut.setText('')
        self.qOut.setText('')


    def sign_file(self):
        """Signs loaded file with dsa library and saves it to a location given by user with save_file_dialog.
        """

        # Check if file is loaded
        if self.file_path == None:
            self.message_popup('A file must be loaded before signing.')
            return

        # Where to save signed zip
        save_path = self.save_file_dialog('Zip File (*.zip);;All Files (*)')

        # Get private key from input
        private_key = self.privateKeyOut.text().split(', ')
        
        # Sign and generate zip to desired location
        dsa = DSA()
        try:
            dsa.sign(self.file_path, (int(private_key[0]), int(private_key[1])), save_path)
        except:
            self.message_popup('Ooops, Something went wrong when signing the file.')

        # Success popup
        self.message_popup(f"Successfuly signed file and saved to {save_path}", 'SUCCESS')


    def check_signature(self):
        """Checks if signature of loaded zip is valid with dsa lib and shows user validity status with message_popup.
        """

        # Check if file is loaded
        if not self.file_path:
            self.message_popup('A file must be loaded before signing.')
            return

        # Check if loaded file is zip
        if os.path.splitext(self.file_path)[-1] != '.zip':
            self.message_popup('Zip file must be loaded for sign check')
            return
        
        # Get private key from input
        public_key = self.publicKeyOut.text().split(', ')
        
        # Check zip
        dsa = DSA()
        try:
            success = dsa.check(self.file_path, (int(public_key[0]), int(public_key[1])))
        except:
            self.message_popup('Ooops, Something went wrong when checking the signature.')
            return
        
        # Success popup
        if success:
            self.message_popup('SUCCESS: SIGNATURE IS VALID', title='SUCCESS')
            return

        # Failure popup
        self.message_popup('FAILURE: SIGNATURE IS INVALID', title='FAILURE')
            
     
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
