import socket
import pickle

class ClienteRPC:
    def __init__(self, host="localhost", porta=5000):
        self.host = host
        self.porta = porta

    def chamar_metodo(self, metodo, parametros):
        """Envia uma solicitação RPC ao servidor."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
                cliente.connect((self.host, self.porta))
                requisicao = {"metodo": metodo, "parametros": parametros}
                cliente.send(pickle.dumps(requisicao))

                try:
                    resposta = pickle.loads(cliente.recv(1024))
                    return resposta
                except (pickle.UnpicklingError, AttributeError) as e:
                    return {"status": "erro", "mensagem": f"Erro ao decodificar resposta do servidor: {e}"}
        except ConnectionRefusedError:
            return {"status": "erro", "mensagem": "Não foi possível conectar ao servidor"}
        except Exception as e:
            return {"status": "erro", "mensagem": f"Erro inesperado: {e}"}

if __name__ == "__main__":
    cliente = ClienteRPC()
    operacoes = {
        1: "somar",
        2: "subtrair",
        3: "multiplicar",
        4: "dividir",
        5: "potencia",
        6: "raiz_quadrada"
    }

    while True:
        try:
            # Entrada do primeiro número
            numero1 = float(input("Digite o primeiro número: ").strip())

            # Exibir opções para o usuário
            print("\nEscolha a operação:")
            for chave, valor in operacoes.items():
                print(f"{chave} - {valor.replace('_', ' ').capitalize()}")

            escolha = int(input("Digite o número correspondente à operação: ").strip())
            operacao = operacoes.get(escolha)

            if not operacao:
                print("Erro: Operação inválida.")
                continue

            # Configurar os parâmetros conforme a operação
            if operacao == "raiz_quadrada":
                parametros = [numero1]
            elif operacao == "potencia":
                numero2 = float(input("Digite o segundo número (expoente): ").strip())
                parametros = [numero1, numero2]
            elif operacao in ["somar", "subtrair", "multiplicar", "dividir"]:
                numero2 = float(input("Digite o segundo número: ").strip())
                parametros = [numero1, numero2]
            else:
                print("Erro: Operação não reconhecida.")
                continue

            # Chamar o método e exibir a resposta
            resposta = cliente.chamar_metodo(operacao, parametros)

            if resposta["status"] == "sucesso":
                print(f"\nResultado: {resposta['resultado']}")
            else:
                print(f"\nErro: {resposta['mensagem']}")

        except ValueError:
            print("Erro: Por favor, insira valores numéricos válidos.")
        except KeyboardInterrupt:
            print("\nCliente encerrado pelo usuário.")
            break

        # Opção de continuar ou sair
        continuar = input("\nDeseja realizar outra operação? (s/n): ").strip().lower()
        if continuar != 's':
            print("Cliente Encerrado!")
            break
