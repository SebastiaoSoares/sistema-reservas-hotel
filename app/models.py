"""
Definição das classes principais do sistema de reservas de hotel.
"""

class Person:
    """
    Classe base que representa uma Pessoa e serve como superclasse para Hospede.
    """
    pass

class Guest(Person):
    """
    Classe Hospede, herda de Pessoa e armazena o histórico associado a ele.
    """
    pass

class Room:
    """
    Dados referentes aos quartos do hotel.
    """
    pass

class Reservation:
    """
    Representa o contrato de locação entre um Hospede e um Quarto.
    """
    pass

class Additional:
    """
    Representa um item de consumo ou serviço extra lançado na conta.
    """
    pass

class Payment:
    """
    Representa uma transação financeira para abater o custo da Reserva.
    """
    pass
