import socket
import pickle
from threading import Thread
import math

class Calculadora:
    """Classe que encapsula as operações matemáticas."""
    @staticmethod
    def somar(a, b):
        return a + b

    @staticmethod
    def subtrair(a, b):
        return a - b

    @staticmethod
    def multiplicar(a, b):
        return a * b

    @staticmethod
    def dividir(a, b):
        if b == 0:
            raise ValueError("Divisão por zero não é permitida.")
        return a / b

    @staticmethod
    def potencia(base, expoente):
        return math.pow(base, expoente)

    @staticmethod
    def raiz_quadrada(a):
        if a < 0:
            raise ValueError("Raiz quadrada de número negativo não é permitida.")
        return math.sqrt(a)

class ServidorRPC:
    def __init__(self, host="localhost", porta=5000):
        self.host = host
        self.porta = porta
        self.metodos_rpc = {}  # Dicionário de métodos disponíveis

    def registrar_metodo(self, nome, func):
        """Registra um método RPC."""
        self.metodos_rpc[nome] = func

    def handle_client(self, conn, addr):
        print(f"Conexão de {addr}")
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print(f"Conexão encerrada por {addr}")
                    break

                try:
                    request = pickle.loads(data)
                    metodo = request.get("metodo")
                    parametros = request.get("parametros", [])
                    
                    if metodo in self.metodos_rpc:
                        try:
                            resultado = self.metodos_rpc[metodo](*parametros)
                            response = {"status": "sucesso", "resultado": resultado}
                        except Exception as e:
                            response = {"status": "erro", "mensagem": f"Erro na execução do método: {e}"}
                    else:
                        response = {"status": "erro", "mensagem": "Método não encontrado"}
                except (pickle.UnpicklingError, AttributeError) as e:
                    response = {"status": "erro", "mensagem": f"Erro ao decodificar a solicitação: {e}"}

                conn.send(pickle.dumps(response))

            except ConnectionResetError:
                print(f"Conexão perdida com {addr}")
                break
            except Exception as e:
                print(f"Erro inesperado com {addr}: {e}")
                break
        conn.close()

    def iniciar(self):
        """Inicia o servidor para escutar conexões."""
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind((self.host, self.porta))
        servidor.listen(5)
        print(f"Servidor iniciado em {self.host}:{self.porta}")
        while True:
            try:
                conn, addr = servidor.accept()
                thread = Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
            except KeyboardInterrupt:
                print("Servidor encerrado.")
                break
            except Exception as e:
                print(f"Erro ao aceitar conexões: {e}")

if __name__ == "__main__":
    servidor = ServidorRPC()
    calculadora = Calculadora()

    # Registrando os métodos da calculadora
    servidor.registrar_metodo("somar", calculadora.somar)
    servidor.registrar_metodo("subtrair", calculadora.subtrair)
    servidor.registrar_metodo("multiplicar", calculadora.multiplicar)
    servidor.registrar_metodo("dividir", calculadora.dividir)
    servidor.registrar_metodo("potencia", calculadora.potencia)
    servidor.registrar_metodo("raiz_quadrada", calculadora.raiz_quadrada)

    servidor.iniciar()
