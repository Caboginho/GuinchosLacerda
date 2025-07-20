from flask                          import Flask, send_from_directory
from classes.bancodados             import BancoDados
from classes.googledrivesheets      import GoogleDriveSheets
import os

# Importar blueprints
from routes.routes_guinchos         import guinchos_bp
from routes.routes_servicos_guincho import servicos_guincho_bp
from routes.routes_transacoes       import transacoes_bp
from routes.routes_usuarios         import usuarios_bp  # Corrigido import
from routes.routes_financeiro       import financeiro_bp
from routes.routes_main             import main_bp
from routes.routes_admin            import admin_bp
from routes.routes_sec              import sec_bp

class App:
    #construtor
    def __init__(self):
    #variáveis privadas
        self.app = Flask(__name__)  # Removido os parênteses extras de __name__
        self.app.secret_key = '8e2aeaf562ce59676d8ed677f7e88935acc3fe44'
        self.google = GoogleDriveSheets(r"classes\lacerdaguinchos-8e2aeaf562ce.json")
        self.banco = BancoDados()
        self.configurar_rotas()
        self.registrar_blueprints()
        self.configurar_uploads()
    #metodos
    def configurar_uploads(self):
        self.app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'statics')

    def configurar_rotas(self):
        @self.app.route('/statics/<path:filename>')
        def static_files(filename):
            return send_from_directory(self.app.config['UPLOAD_FOLDER'], filename)

    def registrar_blueprints(self):
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(admin_bp, url_prefix='/admin')
        self.app.register_blueprint(sec_bp, url_prefix='/sec')
        self.app.register_blueprint(usuarios_bp)
        self.app.register_blueprint(guinchos_bp)
        self.app.register_blueprint(servicos_guincho_bp)
        self.app.register_blueprint(transacoes_bp)
        self.app.register_blueprint(financeiro_bp, url_prefix='/financeiro')
        
    def run(self):
        self.app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    app = App()
    app.run()

