# SISTEMA DE RESERVAS DE HOTEL

Este repositório contém o desenvolvimento do Projeto 1 da disciplina de Programação Orientada a Objetos (Engenharia de Software - UFCA), focado no Tema 8: Sistema de Reservas de Hotel.

## Descrição do Projeto

O projeto consiste em desenvolver um sistema de gerenciamento hoteleiro, na forma de uma API mínima. O sistema deve gerenciar o cadastro de hóspedes, o inventário de quartos e o ciclo completo de reservas, incluindo check-in, check-out, políticas de cancelamento e tarifas dinâmicas.

A persistência dos dados será realizada de forma simples, utilizando um banco de dados SQLite.

## Objetivo

O objetivo principal é aplicar os conceitos fundamentais de Programação Orientada a Objetos (POO) para modelar um problema de domínio real. O foco está na utilização correta de herança, encapsulamento, validações de dados e composição para criar um software coeso, manutenível e robusto.

## Definição da estrutura de classes (Modelagem OO)

### Classe: Pessoa

**Atributos:**
- nome: str
- documento: str
- email: str
- telefone: str

**Métodos:**
(nenhum método principal)

---

### Classe: Hospede (herda de Pessoa)

**Atributos:**
- historico_reservas: list

**Métodos:**
visualizar_historico()

---

### Classe: Quarto

**Atributos:**
- numero: int
- tipo: str
- capacidade: int
- tarifa_base: float
- status: str

**Métodos:**
- verificar_disponibilidade(data_inicio, data_fim)
- bloquear_para_manutencao()
- liberar_quarto()
- str()

---

### Classe: Reserva

**Atributos:**
- data_entrada: date
- data_saida: date
- status: str
- hospede: Hospede
- quarto: Quarto
- lista_adicionais: list
- lista_pagamentos: list

**Métodos:**
- calcular_total()
- confirmar()
- fazer_checkin()
- fazer_checkout()
- cancelar()
- len()

---

### Classe: Adicional

**Atributos:**
- descricao: str
- valor: float
- data_lancamento: datetime

**Métodos:**
(nenhum método principal)

---

### Classe: Pagamento

**Atributos:**
- valor: float
- forma_pagamento: str
- data: datetime

**Métodos:**
(nenhum método principal)

---