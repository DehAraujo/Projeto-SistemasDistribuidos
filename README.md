# Projeto: Sistema Distribuído de Troca de Mensagens (BBS/IRC Simplificado)

Este projeto implementa um sistema de troca de mensagens instantâneas simplificado, inspirado nos modelos BBS e IRC, utilizando arquitetura de sistemas distribuídos.
O desenvolvimento é dividido em partes, com foco inicial nos padrões **Request-Reply (REQ-REP)** e, posteriormente, em **Publisher-Subscriber (PUB-SUB)** do ZeroMQ para comunicação assíncrona.

---

## ⚙️ Arquitetura e Tecnologia

O projeto segue um padrão de microserviços e utiliza tecnologias padronizadas:

* **Comunicação:** **ZeroMQ** (Biblioteca de mensagens distribuídas).
* **Containerização:** **Docker** para isolamento e facilidade de testes.
* **Linguagens:** O projeto será desenvolvido em, no mínimo, **3 linguagens de programação** diferentes.
* **Controle de Versão:** **Git** (utilizando branches separadas para cada parte e merge na `main` ao final).

---

## [PARTE 1] Implementação: Request-Reply (REQ-REP)

A primeira fase estabelece o fluxo de comunicação e o registro inicial no servidor.

### 1. Funcionalidades Implementadas

| Serviço | Descrição |
| :--- | :--- |
| `login` | Permite o cadastro do usuário (somente nome). |
| `users` | Retorna a lista de todos os usuários cadastrados. |
| `channel` | Permite a criação de um novo canal de mensagens (se não existir). |
| `channels` | Retorna a lista de todos os canais disponíveis. |

### 2. Formato de Mensagens (JSON)

As trocas de mensagens seguem o padrão REQ-REP e são formatadas em JSON.
<img width="565" height="347" alt="image" src="https://github.com/user-attachments/assets/96f1ff40-a85c-4e0e-85d2-c07ff191197f" />


### ➡️ Exemplo de Requisição (Login):

#### Exemplo de Comunicação (Login REQ/REP)

Este bloco demonstra o formato JSON esperado para a requisição de Login enviada pelo Cliente e a resposta de sucesso ou erro retornada pelo Servidor.
O fluxo de comunicação utiliza o padrão REQ-REP.

---

#### **CLIENTE -> SERVIDOR: REQUISIÇÃO (`REQ: login`)**

<img width="657" height="244" alt="image" src="https://github.com/user-attachments/assets/e3eecea7-6eda-4ea8-8b1a-2c5cbd9a9d2e" />
<img width="722" height="298" alt="image" src="https://github.com/user-attachments/assets/459db7ca-9ca1-4f7c-9503-eb9103df0912" />
<img width="735" height="312" alt="image" src="https://github.com/user-attachments/assets/96f996b2-dce9-4b1f-9759-e055f846a3ba" />




