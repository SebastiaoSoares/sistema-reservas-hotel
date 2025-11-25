# SISTEMA DE RESERVAS DE HOTEL

Este repositório contém o desenvolvimento do Projeto 1 da disciplina de Programação Orientada a Objetos (Engenharia de Software - UFCA), focado no Tema 8: Sistema de Reservas de Hotel.

## Descrição do Projeto

O projeto consiste em desenvolver um sistema de gerenciamento hoteleiro, na forma de uma API mínima. O sistema deve gerenciar o cadastro de hóspedes, o inventário de quartos e o ciclo completo de reservas, incluindo check-in, check-out, políticas de cancelamento e tarifas dinâmicas.

A persistência dos dados será realizada de forma simples, utilizando um banco de dados SQLite.

## Objetivo

O objetivo principal é aplicar os conceitos fundamentais de Programação Orientada a Objetos (POO) para modelar um problema de domínio real. O foco está na utilização correta de herança, encapsulamento, validações de dados e composição para criar um software coeso, manutenível e robusto.

## Definição da estrutura de classes (Modelagem OO)

### Classe: Person
Classe base que representa uma pessoa no sistema.

**Atributos:**
- `name`: str
- `email`: str
- `phone`: str
- `documents`: List[Document]

**Métodos:**
- `add_document(type_doc, number)`: Adiciona um documento à lista.
- `__str__()`: Retorna o nome da pessoa.

---

### Classe: Document
Representa um documento de identificação.

**Atributos:**
- `doc_type`: TypeDocument (Enum: CPF, PASSPORT)
- `number`: str

**Métodos:**
- `__str__()`: Formata o número e tipo do documento para exibição.

---

### Classe: Guest (Herda de Person)
Representa o hóspede e seu histórico.

**Atributos:**
- `history`: List[Reservation] (Lista de reservas passadas e atuais)

**Métodos:**
- Herda todos os métodos de `Person`.

---

### Classe: Room
Representa um quarto do hotel com validação de dados de capacidade e tarifa.

**Atributos:**
- `number`: int
- `type`: TypeRoom (Enum: SIMPLE, DOUBLE, LUXURY)
- `capacity`: int (Validado via property: deve ser >= 1)
- `basic_fare`: float (Validado via property: deve ser > 0)
- `status`: StatusRoom (Enum: AVAILABLE, OCCUPIED, MAINTENANCE, BLOCKED)

**Métodos:**
- `__str__()`: Retorna detalhes formatados do quarto.
- `__lt__(other)`: Permite ordenação de quartos baseada no tipo e depois no número.

---

### Classe: Reservation
Representa o contrato de locação entre um Hospede e um Quarto.

**Atributos:**
- `guest`: Guest
- `room`: Room
- `check_in`: date
- `check_out`: date
- `n_guests`: int (Validado para não exceder a capacidade do quarto)
- `status`: StatusReservation (Enum: PENDING, CONFIRMED, etc.)
- `payments`: List[Payment]
- `additionals`: List[Additional]

**Métodos:**
- `__len__()`: Retorna o número de diárias (calculado pela diferença de datas).
- `__eq__(other)`: Verifica igualdade de reservas baseada no número do quarto e datas.
- `__str__()`: Retorna um resumo textual da reserva.

---

### Classe: Additional
Representa um item de consumo ou serviço extra.

**Atributos:**
- `description`: str
- `value`: float

---

### Classe: Payment
Representa uma transação financeira associada à reserva.

**Atributos:**
- `method`: str
- `value`: float
- `date`: date (Define automaticamente a data atual na criação)

---

### Enums

- **TypeRoom:** SIMPLE, DOUBLE, LUXURY.
- **StatusRoom:** AVAILABLE, OCCUPIED, MAINTENANCE, BLOCKED.
- **StatusReservation:** PENDING, CONFIRMED, CHECKIN, CHECKOUT, CANCELED, NO_SHOW.
- **TypeDocument:** CPF, PASSPORT.

---