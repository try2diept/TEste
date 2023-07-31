import mysql.connector
from decimal import Decimal, ROUND_HALF_UP

class Account:
    connection_settings = {
        "host": "localhost",
        "user": "Tobi",
        "database": "esxlegacy_b28433",
    }

    def __init__(self, account_number, account_holder, initial_balance=0):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = Decimal(str(initial_balance))
        self.transaction_history = []

    @classmethod
    def from_database(cls, account_data):
        account = cls(*account_data)
        return account

    @classmethod
    def connect_to_database(cls):
        return mysql.connector.connect(**cls.connection_settings)

    def deposit(self, amount):
        amount = Decimal(str(amount))
        if amount > 0:
            self.balance += amount
            self.transaction_history.append(f"Foi depositado {amount} €")
            self.save()
            return True
        return False

    def withdrawal(self, amount):
        amount = Decimal(str(amount))
        if 0 < amount <= self.balance and amount <= 500 and amount <= 2500 - self.total_withdrawal_today():
            self.balance -= amount
            self.transaction_history.append(f"Levantado {amount} €")
            self.save()
            return True
        return False

    def transfer(self, recipient_account, amount):
        amount = Decimal(str(amount))
        if self.withdrawal(amount):
            recipient_account.deposit(amount)
            self.transaction_history.append(f"Transferido {amount} € para a conta: {recipient_account.account_number}")
            self.save()
            return True
        return False

    @staticmethod
    def connect_database():
        return mysql.connector.connect(
            host="localhost",
            user="Tobi",
            database="esxlegacy_b28433",
        )

    @staticmethod
    def load_account(account_number):
        connection = Account.connect_database()
        cursor = connection.cursor()
        query = "SELECT * FROM accounts WHERE account_number = %s"
        cursor.execute(query, (account_number,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            return Account(*result)
        return None

    def save(self):
        connection = Account.connect_database()
        cursor = connection.cursor()
        query = "UPDATE accounts SET balance = %s WHERE account_number = %s"
        values = (self.balance, self.account_number)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

    def total_withdrawal_today(self):
        today_withdrawal = sum(
            amount for _, amount in self.transaction_history if "Levantado" in _
        )
        return today_withdrawal

    def get_statement(self):
        return self.transaction_history

class ATM:
    def __init__(self):
        self.accounts = {}

    def create_account(self, account_number, account_holder, initial_balance=0):
        if account_number not in self.accounts:
            new_account = Account(account_number, account_holder, initial_balance)
            self.accounts[account_number] = new_account
            new_account.save()
        return new_account

    def select_account(self, account_number):
        return self.accounts.get(account_number, None)

    def main_menu(self):
        print("Bem-vindo à Caixa Geral de Depósitos")
        while True:
            account_number = input("Insira o Nº da sua Conta: ")
            account = self.select_account(account_number)
            if account:
                self.account_menu(account)
            else:
                print("Conta não encontrada, tente novamente!")

    def account_menu(self, account):
        print(f"Bem-vindo, {account.account_holder}!")
        while True:
            print("\n1. Depositar\n2. Levantar\n3. Transferir\n4. Extrato Bancário\n5. Sair")
            choice = input("Escolha uma opção (1/2/3/4/5): ")

            if choice == "1":
                amount = Decimal(input("Selecione uma quantidade para depositar: "))
                if account.deposit(amount):
                    print(f"Depositado {amount} €. Novo Balanço: {account.balance} €")
                else:
                    print("Quantidade Inválida, Por favor tente novamente")

            elif choice == "2":
                amount = Decimal(input("Insira uma quantia para levantar: "))
                if account.withdrawal(amount):
                    print(f"Retirou {amount} € da sua conta. Novo balanço: {account.balance} €")
                else:
                    print("Quantia inválida ou limite alcançado")

            elif choice == "3":
                recipient_account_number = input("Insira o Nº da conta que deseja depositar dinheiro: ")
                recipient_account = self.select_account(recipient_account_number)
                if recipient_account:
                    amount = Decimal(input("Insira a quantia a transferir: "))
                    if account.transfer(recipient_account, amount):
                        print(f"Transferido {amount} € para a conta {recipient_account_number}, Novo balanço: {account.balance} €")
                    else:
                        print("Falha na transferência")
                else:
                    print("Conta não encontrada, verifique as credenciais")

            elif choice == "4":
                statement = account.get_statement()
                print("\nExtrato Bancário")
                for transaction in statement:
                    print(transaction)

            elif choice == "5":
                print("Obrigado e volte sempre")
                return

            else:
                print("Escolha Inválida, escolha novamente")

    def load_accounts(self):
        connection = Account.connect_to_database()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM accounts")
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        for account_data in result:
            account = Account.from_database(account_data)
            self.accounts[account.account_number] = account

if __name__ == "__main__":
    atm = ATM()
    atm.load_accounts()

    atm.main_menu()