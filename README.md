# Projeto: Sistema Distribuído de Troca de Mensagens (BBS/IRC Simplificado)

Este projeto implementa um sistema de troca de mensagens instantâneas simplificado, utilizando ZeroMQ para comunicação assíncrona em uma arquitetura distribuída.

## ⚙️ Arquitetura e Tecnologia

O projeto segue um padrão de microserviços e utiliza tecnologias padronizadas:

* **Comunicação:** **ZeroMQ** (Padrões REQ-REP e PUB-SUB).
* **Containerização:** **Docker** para isolamento e testes.
* **Desenvolvimento:** Mínimo de **3 linguagens de programação** diferentes.
* **Controle de Versão:** **Git** (Utilização de branches isoladas para cada parte e merge na `main` ao final).

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

➡️ Exemplo de Requisição (Login):

```json
{
  "service": "login",
  "data": {
    "user": "nome de usuário",
    "timestamp": "[gerado no envio da mensagem]"
  }
}

➡️ Exemplo de Resposta (Login):

{
  "service": "login",
  "data":{
    "status": "sucesso"/"erro",
    "timestamp": "[gerado no envio da mensagem]",
    "description": "[caso a mensagem seja de erro]"
  }
}
