# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width="40%" height="40%"></a>
</p>

<br>

# Assistente Cardiológico Inteligente e Conversacional – CardioIA (Fase 5)

## 👨‍🎓 Integrantes:
- <a href="https://www.linkedin.com/company/">Thiago Lima Bernardes</a>

## 👩‍🏫 Professores:

### Coordenador(a)
- <a href="https://www.linkedin.com/in/profandregodoi/">André Godoi</a>

### Tutor(a)
- <a href="https://www.linkedin.com/in/leoruiz197/">Leo Ruiz</a>

---

## 📜 Descrição do Projeto

Esta atividade da **Fase 5** dá continuidade ao projeto **CardioIA**, evoluindo o escopo da etapa anterior para a construção de um **Assistente Cardiológico Inteligente e Conversacional**.

O objetivo do protótipo é simular um atendimento inicial em saúde por meio de **linguagem natural**, organizando respostas de forma clara, estruturada e contextualizada, sem ultrapassar os limites técnicos e éticos de um sistema educacional.

A solução entregue foi organizada em duas partes complementares:

1. **Parte 1 – Assistente Conversacional com NLP**
   - modelagem do assistente no **IBM Watson Assistant**;
   - definição de **intents**, **entities** e **dialog nodes**;
   - integração com um **backend em Flask**;
   - registro das interações em **SQLite**;
   - suporte a operação real com Watson ou em **modo local de demonstração**.

2. **Parte 2 – Interface de Interação com o Usuário**
   - criação de uma interface simples em **React Native com Expo**;
   - envio de mensagens ao backend;
   - exibição das respostas do assistente;
   - reinício de sessão conversacional e verificação de saúde da API.

> O projeto é acadêmico e demonstrativo. Ele **não realiza diagnóstico**, **não substitui atendimento médico** e foi estruturado para apresentar um fluxo de orientação inicial segura ao paciente.

---

## 🎯 Objetivos Cobertos na Fase 5

- Simular um atendimento inicial em saúde com interação por **linguagem natural**.
- Estruturar um assistente conversacional no **IBM Watson Assistant**.
- Modelar intenções, entidades e respostas contextualizadas para o domínio cardiológico inicial.
- Integrar o fluxo conversacional a um backend simples em **Python/Flask**.
- Disponibilizar uma interface de uso simples para o paciente em **React Native**.
- Manter o comportamento do sistema funcional mesmo sem credenciais externas, por meio de um **stub local**.
- Demonstrar boas práticas de escopo, segurança e comunicação responsável em um contexto de saúde.

---

## 🧩 Tecnologias Utilizadas

**Backend**
- **Python 3.11+**
- **Flask**
- **Flask-Cors**
- **SQLite** para persistência local dos logs de conversa
- **python-dotenv** para configuração por variáveis de ambiente
- **IBM Watson Assistant (API v2)** para runtime conversacional

**Frontend Web de Apoio**
- **HTML5**, **CSS3** e **JavaScript**
- Template web simples para teste manual do backend

**Aplicação Mobile**
- **React Native**
- **Expo**
- Componentes nativos como `FlatList`, `TextInput`, `Pressable`, `SafeAreaView` e `KeyboardAvoidingView`

**Lógica Conversacional**
- **Intents** para identificação de intenção do usuário
- **Entities** para extração de elementos clínicos e contextuais
- **Dialog Nodes** para organização do fluxo
- **Fallback local** para demonstrações sem dependência obrigatória do serviço externo

---

## 🏗️ Fluxo Conversacional da Solução

### Visão Geral

O fluxo principal do projeto segue a lógica:

`USUÁRIO > INTERFACE (WEB/MOBILE) > BACKEND FLASK > WATSON ASSISTANT OU STUB LOCAL > RESPOSTA ESTRUTURADA > LOG EM SQLITE`

### Etapas do funcionamento

1. O usuário envia uma mensagem pela interface web ou pelo app mobile.
2. O backend recebe a mensagem no endpoint `POST /api/chat`.
3. Se as credenciais do **IBM Watson Assistant** estiverem configuradas, a mensagem é enviada à API do serviço.
4. Caso contrário, o sistema ativa um **modo local de demonstração**, com respostas acadêmicas previamente estruturadas.
5. O backend interpreta a resposta, extrai:
   - texto final da resposta;
   - intenção principal identificada;
   - entidades reconhecidas;
   - nível de urgência inferido.
6. A conversa é registrada em **SQLite** para fins de auditoria e demonstração.
7. A resposta é devolvida ao usuário na interface.

### Situações contempladas no fluxo

O assistente cobre cenários como:
- saudação e apresentação do escopo;
- triagem inicial de sintomas;
- identificação de sinais de urgência;
- orientação sobre pressão arterial;
- explicação de exames cardíacos;
- orientações sobre medicamentos;
- preparo para consulta;
- hábitos saudáveis;
- tratamento de mensagens fora do escopo.

---

## 🤖 Modelagem do Assistente no Watson Assistant

### Intents implementadas
- `saudacao`
- `emergencia`
- `informar_sintoma`
- `informar_pressao`
- `explicar_exame`
- `medicamentos`
- `preparo_consulta`
- `habitos_saudaveis`
- `agradecimento`
- `despedida`

### Entities implementadas
- `sintoma`
- `exame`
- `pressao_estado`
- `habito`

### Exemplos de elementos reconhecidos
- sintomas: dor no peito, palpitação, tontura, falta de ar, desmaio;
- exames: eletrocardiograma, ecocardiograma, Holter, MAPA, raio-X de tórax;
- estados de pressão: alta, baixa, normal.

### Regras importantes do assistente
1. Mensagens com **dor no peito**, **falta de ar** ou **desmaio** são tratadas com prioridade mais alta.
2. O sistema evita linguagem de diagnóstico definitivo.
3. O assistente orienta o usuário a procurar atendimento imediato nos cenários de urgência.
4. Quando o usuário faz perguntas genéricas, o fluxo tenta redirecionar para temas cobertos.
5. O backend classifica a urgência em níveis como `alta`, `moderada` e `baixa` para enriquecer a resposta da interface.

---

## 🔌 Principais Endpoints da API

### Backend principal
- `GET /` – interface web simples para testes manuais
- `GET /api/health` – verifica se o backend está online e se o Watson está configurado
- `POST /api/chat` – envia uma mensagem ao assistente e recebe a resposta estruturada
- `POST /api/reset` – reinicia a sessão atual do assistente
- `GET /api/history` – lista histórico recente das interações registradas

### Resposta típica do endpoint `/api/chat`
A resposta do backend inclui campos como:
- `response`
- `top_intent`
- `entities`
- `urgency_level`
- `source`

Isso permite que a interface apresente não apenas o texto retornado, mas também metadados úteis para demonstração acadêmica.

---

## 📱 Interface de Interação com o Usuário

A Parte 2 do projeto entrega uma aplicação **React Native** simples, com foco na demonstração do fluxo conversacional.

### Funcionalidades implementadas
- campo para digitação da mensagem do usuário;
- envio da mensagem ao backend;
- renderização das respostas do assistente em formato de chat;
- chips com exemplos rápidos de pergunta;
- botão para reiniciar a conversa;
- checagem de disponibilidade do backend com `GET /api/health`;
- configuração da URL da API por variável de ambiente.

### Integração com o backend
A aplicação mobile consome os endpoints:
- `/api/chat`
- `/api/reset`
- `/api/health`

A URL do backend é configurada por:
- `EXPO_PUBLIC_API_URL`

Isso facilita testes em:
- emulador Android;
- simulador iOS;
- dispositivo físico na rede local.

---

## 🗂️ Estrutura do Repositório

```text
CardioIA_Fase5/
  assets/
    logo-fiap.png
  config/
    ThiagoBernardes_rm560085_watson_assistant_export.json
  docs/
    ThiagoBernardes_rm560085_Relatorio_CardioIA_Fase5.docx
  mobile-react-native/
    App.js
    README.md
    app.json
    babel.config.js
    package.json
    .env.example
    src/
      components/
        Composer.js
        MessageBubble.js
      config/
        api.js
      services/
        chatApi.js
  templates/
    index.html
  .env.example
  app.py
  requirements.txt
  README.md
```

---

## ▶️ Instruções de Execução

### 1) Backend Flask
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app run --host 0.0.0.0 --port 5000
```

Teste de saúde:
```bash
curl http://127.0.0.1:5000/api/health
```

### 2) Configurar variáveis do backend
Copie o arquivo `.env.example` para `.env` e preencha, se desejar usar o Watson Assistant:

- `WA_API_KEY`
- `WA_URL`
- `WA_ASSISTANT_ID`
- `WA_VERSION`

Caso essas credenciais não sejam informadas, o sistema poderá operar com:
- `USE_LOCAL_STUB=true`

### 3) Executar a interface web simples
Após subir o Flask, acesse:
- `http://127.0.0.1:5000/`

### 4) Executar a aplicação React Native
```bash
cd mobile-react-native
npm install
npx expo start
```

### 5) Configurar a URL da API no app mobile
Copie `mobile-react-native/.env.example` para `.env` e ajuste:

```env
EXPO_PUBLIC_API_URL=http://192.168.0.10:5000
```

Exemplos de uso:
- **Android Emulator**: `http://10.0.2.2:5000`
- **iOS Simulator**: `http://127.0.0.1:5000`
- **Dispositivo físico**: IP local da máquina hospedeira

---

## 💬 Exemplos de Perguntas ao Assistente

- “Estou com palpitação.”
- “Minha pressão está alta.”
- “O que é ecocardiograma?”
- “Como me preparo para a consulta?”
- “Estou com dor no peito e falta de ar.”

---

## 🔐 Segurança, Ética e Escopo de Uso

- o projeto utiliza um **fluxo acadêmico e demonstrativo**;
- não fornece **diagnóstico médico**;
- não substitui consulta, exame ou atendimento profissional;
- orienta o usuário a buscar atendimento imediato diante de sinais de urgência;
- mantém os registros localmente em **SQLite** para fins de demonstração;
- permite uso do **Watson Assistant** ou de um **stub local**, reduzindo dependência externa em ambiente acadêmico.

Em um cenário real, seria necessário ampliar controles de:
- autenticação;
- proteção de dados sensíveis;
- rastreabilidade clínica;
- LGPD;
- revisão médica e governança de conteúdo.

---

## 🔄 Continuidade do Projeto CardioIA

A **Fase 4** concentrou-se em um assistente cardiológico com **visão computacional**, treinado para interpretar imagens médicas simuladas por meio de **CNNs** e **Transfer Learning**.

Na **Fase 5**, o projeto avança para uma camada de **interação conversacional**, permitindo que o paciente:
- envie mensagens em linguagem natural;
- receba orientações iniciais organizadas;
- compreenda sintomas, exames e preparo para consulta em linguagem mais acessível.

Assim, o CardioIA passa a combinar duas frentes conceituais do projeto acadêmico:
- **análise computacional de imagens**;
- **atendimento conversacional inteligente**.

---

## 🗃 Histórico de Lançamentos

- **0.2.0 – Fase 5**:
  - modelagem do assistente no IBM Watson Assistant;
  - backend Flask com integração à API do Watson;
  - fallback local para demonstração sem credenciais externas;
  - persistência de logs em SQLite;
  - interface web simples;
  - aplicação React Native integrada ao backend.

- **0.1.0 – Fase 4**:
  - pipeline de pré-processamento de imagens médicas;
  - treinamento de CNN simples e modelo com Transfer Learning;
  - avaliação por acurácia, matriz de confusão, precisão, recall e F1-score;
  - protótipo interativo em notebook para análise de imagens.

---

## 📋 Licença / Modelo

Este README foi adaptado para o projeto **CardioIA – Fase 5** com base no modelo estrutural FIAP fornecido como referência, preservando a organização em descrição, objetivos, arquitetura, estrutura do repositório, instruções de execução, segurança e histórico de lançamentos.
