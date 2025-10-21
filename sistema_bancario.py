
# retorno e forma definidda pelo desenvolvedor
clientes = {}
contas = {}
conta = 0
mensagens = [""]
from datetime import datetime
import csv
from pathlib import Path

BASE = Path(__file__).parent
def datar_extrato(funcao):
    def envelope(*args, **kwargs):
        print("\n")
        print("="*100)
        print("Data Extrato", datetime.strftime(datetime.now(), "%d/%m/%Y - %H:%M"))
        return funcao(*args, **kwargs)

    return envelope

def escrever_log(funcao):
    def envelope(*args, **kwargs):
        print("escrever log")
        with open(f'{BASE}/logs.csv', mode="a", newline="", encoding="utf-8") as log:
            escritor = csv.writer(log)
            if log.tell()==0:
                escritor.writerow(["data_hora","operacao"])
            escritor.writerow([datetime.strftime(datetime.now(), "%d/%m/%Y - %H:%M:%S"), funcao.__name__])
        return funcao(*args, **kwargs)
    return envelope

@escrever_log
def sacar(*, valor, cpf, conta): # sugestao retorno saldo, extrato
    saldo =  contas[cpf]["Contas"][conta]["saldo"]
    extrato = contas[cpf]["Contas"] [conta]["extrato"]

    if valor > 0 and valor <= saldo:
        saldo =  contas[cpf]["Contas"][conta]["saldo"] - valor
        lancar_no_extrato = f"{'(D) ----- - R$':<15} {valor:<15.2f}".center(30)
        extrato += f"\n{lancar_no_extrato}"
        contas[cpf]["Contas"][conta] = {"saldo":saldo, "extrato": extrato }
        mensagens.append(f"Saque efetuado com sucesso")

    else:
        mensagens.append("Saldo insuficiente para o valor do saque!!!")
    
   

@escrever_log
def depositar(valor, cpf, conta,/): # sugestao retorno saldo, extrato
   
    # Linha a ser incluída no extrato
    lancar_no_extrato = f"{'(C) ----- + R$':<15} {valor:<15.2f}".center(30)
    
    saldo = contas[cpf]["Contas"][conta]["saldo"] + valor
    extrato = contas[cpf]["Contas"] [conta]["extrato"]

    extrato += f"\n{lancar_no_extrato}"
    contas[cpf]["Contas"][conta] = {"saldo":saldo, "extrato": extrato }

@escrever_log
@datar_extrato  
def exibir_extrato(cpf, /, *, conta):
    extrato = contas[cpf]["Contas"][conta]["extrato"]
    saldo = contas[cpf]["Contas"][conta]["saldo"]
    print(f"Saldo: R$ {saldo:.2f}")
    print(f"Extrato: {extrato}")
 
@escrever_log
def criar_cliente(nome, data_nascimento, cpf, endereco): # nao pode cadastrar dois clientes com mesmo cpf 
    print('\n')
                                                     # endereço: Avenida 100, nº 1071 - Brazão - Orlândia/SP
    if cpf not in clientes:
        clientes[cpf] = {"nome": nome, "data_nascimento": data_nascimento,"endereco": endereco} 
        mensagens.append(f"Cliente de CPF {cpf} cadastrado com sucesso!")

    else:
        mensagens.append(f"Cliente de CPF {cpf} já possui cadastro!")


@escrever_log
def criar_conta(cpf, conta): # Agencia, Número da Conta, Usuário, Agencia 0001, Conta Sequencial 1, 2, 3 ... 
                  # Usuário pode ter mais de uma conta, mas a conta só pode ter um usuário
    print('\n')

    if cpf in clientes:
        agencia = "0001"

        if cpf not in contas:
            contas[cpf] = {"Agencia":agencia, "Contas": {} }

        contas[cpf]["Contas"][conta] = {"saldo": 0, "extrato":''}
        mensagens.append(f"Conta nº {conta} vinculada com sucesso ao CPF {cpf}!")
        
    else:
        mensagens.append("\033[31m É necessário ser cliente para abrir conta! \nUse a opção ===> [1] para cadastrar o cliente!\033[0m")    

@escrever_log
def listar_clientes():
    print('\n')
    numero_clientes = 0

    if clientes:
        print(f"{'CPF CLIENTE':<15} | {'NOME CLIENTE':<30}")

        for cpf, dados in clientes.items():
            print(f"{cpf:<15} | {dados["nome"]:<30}")
            numero_clientes += 1
        mensagens.append(f"{numero_clientes} clientes listados com sucesso!")
        
    else:
        mensagens.append("A lista de clientes está vazia!")

@escrever_log
def listar_contas_cliente(cpf):
    contas_cliente = contas[cpf]["Contas"].keys()

    for k in contas_cliente:
        print(f"Conta nº: {k}")
    
while True:
    menu = f"""
====================================================================================
    Menu

    [1] :===> Cadastrar Cliente
    [2] :===> Listar Clientes
    [3] :===> Abrir Conta
    [4] :===> Operação Conta
    [5] :===> Exibir Extrato
   
    [0] :===> Sair

    Mensagens: {logs[-1]}
====================================================================================
"""
    print(menu)
    opcao = input("Entre com uma das opções desejadas conforme menu: ")

    if opcao == "1":
        nome = input("Nome do Cliente: ")
        data_nascimento = input("Data de Nascimento: ")
        cpf = input("CPF: ")
        endereco = input("Endereço: ")
        criar_cliente(nome, data_nascimento, cpf, endereco)
        print(clientes)

    elif opcao == "2":
        listar_clientes()

    elif opcao == "3":
        conta += 1
        cpf = input("CPF do Cliente: ")
        criar_conta(cpf, conta)

    elif opcao == "4":
        cpf = input("Digite o CPF do cliente: ")

        if cpf in contas:
            listar_contas_cliente(cpf)
            conta = int(input("Digite a Conta de Operação: "))
            print("\n\033[34m Tipo de Operação: \n D - Depósito, \n S - Saque\033[0m\n")
            tipo_operacao = input("Digite a Operação: ").upper()
            valor = float(input("Digite o Valor da Operação: "))

            if tipo_operacao == 'D':
                depositar(valor, cpf, conta)
                logs.append(f"Depósito efetuado com sucesso!")
                exibir_extrato(cpf, conta = conta)

            elif tipo_operacao == 'S':
                sacar(valor=valor, cpf=cpf, conta=conta)
                exibir_extrato(cpf, conta = conta)

            else:
                logs.append(f"Opção '{tipo_operacao}' Inválida!")
        else:
            logs.append(f"Cliente de CPF {cpf} não localizado!")
        
    elif opcao == "5":
        cpf = input("Digite o CPF do cliente: ")

        if cpf in contas:
            listar_contas_cliente(cpf)
            conta = int(input("Nº da Conta: "))
            exibir_extrato(cpf, conta=conta)
            
        else:
            logs.append(f"Cliente de CPF {cpf} não localizado!")

    elif opcao == "0":
        break

    else:
        print("Opção inválida!!")
    

    