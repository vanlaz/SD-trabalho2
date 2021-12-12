from flask import Flask, jsonify
from flask_sse import sse
from flask_cors import CORS
from flask_restful import Resource, Api
from datetime import datetime
from helper import get_data

app = Flask(__name__)
api = Api(app)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

CORS(app)


@app.route('/')
def index():
    # apenas mantendo a rota / do projeto de exemplo
    return jsonify(get_data())


class Servidor(Resource):
    motoristas = []
    passageiras = []
    procura_por_passageiras = []
    procura_por_motoristas = []


class CadastroUsuaria(Servidor):
    def post(self, nome, telefone, tp_user):
        if tp_user == '1':
            id_user = (len(Servidor.motoristas) + 1)
            Servidor.motoristas.append([id_user, nome, telefone])
            return id_user
        else:
            id_user = (len(Servidor.passageiras) + 1)
            Servidor.passageiras.append([id_user, nome, telefone])
            return id_user


class ConsultaViagensDaUsuaria(Servidor):
    def get(self, id_user, tp_user):
        viagens_da_usuaria = []
        if tp_user == '1':
            lista_de_viagens = Servidor.procura_por_passageiras
        else:
            lista_de_viagens = Servidor.procura_por_motoristas
        for viagem in lista_de_viagens:
            # posição 1 pq essa lista possui o id da corrida na posição 0
            if str(viagem[1]) == id_user:
                viagens_da_usuaria.append(viagem)
        return viagens_da_usuaria


class ConsultaViagens(Servidor):
    def consulta_usuaria(self, id_user, tp_user):
        if tp_user == '1':
            lista_de_usuarias = Servidor.passageiras
        else:
            lista_de_usuarias = Servidor.motoristas
        for usuaria in lista_de_usuarias:
            if str(usuaria[0]) == id_user:
                return usuaria

    def get(self, origem, destino, data, tp_user):
        lista_compativeis = []
        if tp_user == '1':
            lista_de_viagens = Servidor.procura_por_motoristas
        else:
            lista_de_viagens = Servidor.procura_por_passageiras
        for viagens in lista_de_viagens:
            if viagens[2] == origem and viagens[3] == destino and viagens[4] == data:
                usuaria_compativel = self.consulta_usuaria(viagens[1], tp_user)
                lista_compativeis.append([usuaria_compativel, viagens])
        return lista_compativeis


def checa_correspondencia_com_passageira():
    infos_passageira = []
    qtd_viagens = len(Servidor.procura_por_passageiras) - 1
    for i in Servidor.procura_por_motoristas:
        if (Servidor.procura_por_passageiras[qtd_viagens][4] == i[4]
                and Servidor.procura_por_passageiras[qtd_viagens][3] == i[3]
                and Servidor.procura_por_passageiras[qtd_viagens][2] == i[2]):
            for usuaria in Servidor.motoristas:
                if str(usuaria[0]) == Servidor.procura_por_passageiras[qtd_viagens][1]:
                    # nome e telefone
                    infos_passageira.append([usuaria[1], usuaria[2]])
                    print(infos_passageira)
    if infos_passageira:
        server_side_event(infos_passageira, i[1] + '0')


class InteresseEmPassageira(Servidor):
    def post(self, id_user, origem, destino, data):
        id_corrida = str(datetime.now()).replace(":", "").replace("-", "").replace(".", "").replace(" ", "")
        Servidor.procura_por_passageiras.append([id_corrida, id_user, origem, destino, data])
        checa_correspondencia_com_passageira()
        return Servidor.procura_por_passageiras


def checa_correspondencia_com_motorista():
    infos_motorista = []
    qtd_viagens = len(Servidor.procura_por_motoristas) - 1
    for i in Servidor.procura_por_passageiras:
        if (Servidor.procura_por_motoristas[qtd_viagens][4] == i[4]
                and Servidor.procura_por_motoristas[qtd_viagens][3] == i[3]
                and Servidor.procura_por_motoristas[qtd_viagens][2] == i[2]):
            for usuaria in Servidor.passageiras:
                if str(usuaria[0]) == Servidor.procura_por_motoristas[qtd_viagens][1]:
                    # nome e telefone
                    infos_motorista.append([usuaria[1], usuaria[2]])
    if infos_motorista:
        server_side_event(infos_motorista, i[1] + '1')


class InteresseEmMotorista(Servidor):
    def post(self, id_user, origem, destino, data):
        id_corrida = str(datetime.now()).replace(":", "").replace("-", "").replace(".", "").replace(" ", "")
        Servidor.procura_por_motoristas.append([id_corrida, id_user, origem, destino, data])
        checa_correspondencia_com_motorista()
        return Servidor.procura_por_motoristas


class RemoveInteresseEmPassageira(Servidor):
    def delete(self, id_corrida):
        for i in range(0, len(Servidor.procura_por_passageiras)):
            if Servidor.procura_por_passageiras[i][0] == id_corrida:
                Servidor.procura_por_passageiras.pop(i)
                return Servidor.procura_por_passageiras


class RemoveInteresseEmMotorista(Servidor):
    def delete(self, id_corrida):
        for i in range(0, len(Servidor.procura_por_motoristas)):
            if Servidor.procura_por_motoristas[i][0] == id_corrida:
                Servidor.procura_por_motoristas.pop(i)
                return Servidor.procura_por_motoristas


class TamanhoLista(Servidor):
    def get(self, tp_user):
        if tp_user == '0':
            lista_de_viagens = Servidor.procura_por_motoristas
        else:
            lista_de_viagens = Servidor.procura_por_passageiras
        return len(lista_de_viagens) + 1


def server_side_event(lista, id):
    """ Function to publish server side event """
    with app.app_context():
        sse.publish(lista, type='publish', channel=str(id))
        print(sse.redis)


api.add_resource(CadastroUsuaria, '/servidor/cadastro/<nome>/<telefone>/<tp_user>')
api.add_resource(ConsultaViagensDaUsuaria, '/servidor/consulta/viagens/<id_user>/<tp_user>')
api.add_resource(ConsultaViagens, '/servidor/consulta/<origem>/<destino>/<data>/<tp_user>')
api.add_resource(InteresseEmPassageira, '/servidor/interesse/passageira/<id_user>/<origem>/<destino>/<data>')
api.add_resource(InteresseEmMotorista, '/servidor/interesse/motorista/<id_user>/<origem>/<destino>/<data>')
api.add_resource(RemoveInteresseEmPassageira, '/servidor/remove/interesse/passageira/<id_corrida>')
api.add_resource(RemoveInteresseEmMotorista, '/servidor/remove/interesse/motorista/<id_corrida>')
api.add_resource(TamanhoLista, '/servidor/tamanho/lista/<tp_user>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
