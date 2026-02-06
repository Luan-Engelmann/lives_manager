📊 Lives Manager (Gerenciador de Lives)

A solução completa para gerir as suas transmissões.

O Lives Manager é uma aplicação web robusta desenvolvida para auxiliar streamers a gerir, registar e analisar as métricas das suas transmissões em múltiplas plataformas. Com uma interface moderna e intuitiva, permite o controlo total dos seus dados pós-live.

🚀 Funcionalidades Principais

📡 Gestão Multiplataforma

🟣 Twitch

Registo detalhado com validação inteligente de moeda (USD/BRL).

Controlo de média de visualizações e novos inscritos.

Máscaras de input automáticas.

🔴 YouTube

Métricas específicas como Picos Simultâneos e Likes.

Cálculo de médias e registo de horários.

🟢 Kick

Suporte completo com identidade visual personalizada (Tema Verde).

Campos adaptados para a realidade da plataforma.

🎨 Interface do Usuário (UI/UX)

🌓 Modo Escuro/Claro: Alternância de tema fluida com persistência de preferência (salvo no navegador).

📱 Design Responsivo: Formulários adaptados para funcionar perfeitamente em Desktop e Mobile.

✨ Identidade Visual: Suporte total para Logo do canal e Favicon personalizados via URL externa.

⚙️ Tratamento de Dados & Backend

Sanitização de Moeda: Campos monetários formatam automaticamente enquanto o utilizador digita (ex: R$ 1.250,00) e são salvos como float (ex: 1250.00) no banco de dados.

Suporte a Decimais: Médias de visualização aceitam valores quebrados (ex: 3,4).

Inputs Inteligentes: Seletores nativos de Data e Hora.

📂 Exportação

Relatórios CSV: Botões dedicados para descarregar todos os registos de cada plataforma em formato .csv (compatível com Excel e Google Sheets).

🛠️ Stack Tecnológico

Área

Tecnologia

Descrição

Backend



Linguagem base do projeto.

Framework



Framework web de alta performance.

Servidor



Servidor ASGI.

Database



Banco de dados relacional leve e nativo.

Frontend



Estrutura semântica e Jinja2 Templates.

📂 Estrutura do Projeto

lives_manager/
│
├── static/              # Arquivos estáticos
│   └── LOGO 3.jpeg      # (Opcional) Logo local
│
├── templates/           # O coração do Frontend
│   ├── index.html            # Dashboard Principal
│   ├── cadastro_twitch.html  # Módulo Twitch
│   ├── cadastro_youtube.html # Módulo YouTube
│   └── cadastro_kick.html    # Módulo Kick
│
├── main.py              # Cérebro da aplicação (Rotas, DB, Lógica)
├── lives.db             # Banco de dados (Gerado automaticamente)
└── requirements.txt     # Dependências do Python


⚡ Guia de Instalação

Siga os passos abaixo para rodar o projeto na sua máquina.

1. Clonar o repositório

git clone [https://github.com/SEU-USUARIO/lives-manager.git](https://github.com/SEU-USUARIO/lives-manager.git)
cd lives-manager


2. Instalar dependências

# Opção A: Usando requirements.txt
pip install -r requirements.txt

# Opção B: Manualmente
python -m pip install fastapi "uvicorn[standard]" jinja2 python-multipart


3. Rodar a aplicação

python -m uvicorn main:app --reload


4. Acessar

Abra o seu navegador favorito e acesse:

https://www.google.com/search?q=http://127.0.0.1:8000

📝 Notas da Versão 2.1

⚠️ Atualização Crítica: Se está a atualizar de uma versão anterior, siga estes passos:

Delete o arquivo antigo lives.db.

Reinicie o servidor.

O sistema recriará o banco de dados automaticamente com as novas colunas REAL (para decimais) e os novos campos do YouTube.

🤝 Contribuição

Contribuições são muito bem-vindas!

Faça um Fork do projeto.

Crie uma Branch para a sua Feature (git checkout -b feature/NovaFeature).

Faça o Commit (git commit -m 'Adicionando nova feature').

Faça o Push (git push origin feature/NovaFeature).

Abra um Pull Request.

📄 Licença

Este projeto está sob a licença MIT.

<div align="center">
<sub>Desenvolvido com 💜 por <b>LuanTech</b>.</sub>
</div>
