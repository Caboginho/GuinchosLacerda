from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
from classes.bancodados import BancoDados
from classes.googledrivesheets import GoogleDriveSheets
import os

# Importar blueprints
from routes.routes_guinchos import guinchos_bp
from routes.routes_servicos_guincho import servicos_guincho_bp
from routes.routes_transacoes import transacoes_bp
from routes.routes_usuario import usuario_bp
from routes.routes_anexos import anexos_bp
from routes.routes_main import main_bp

class App:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = '8e2aeaf562ce59676d8ed677f7e88935acc3fe44'
        self.google = GoogleDriveSheets(r"classes\lacerdaguinchos-8e2aeaf562ce.json")
        self.banco = BancoDados()
        self.configurar_rotas()
        self.registrar_blueprints()
        self.configurar_uploads()

    def configurar_uploads(self):
        self.app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'statics')

    def configurar_rotas(self):
        @self.app.route('/statics/<path:filename>')
        def static_files(filename):
            return send_from_directory(self.app.config['UPLOAD_FOLDER'], filename)

    def registrar_blueprints(self):
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(usuario_bp)
        self.app.register_blueprint(guinchos_bp)
        self.app.register_blueprint(servicos_guincho_bp)
        
        self.app.register_blueprint(transacoes_bp)
        self.app.register_blueprint(anexos_bp)
        

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    app = App()
    app.run()
