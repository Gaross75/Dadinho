🤖 Dadinho Lite: Bot Espectador IA (Edição "Sobrevivência")

Um bot co-host autônomo com Inteligência Artificial de Visão Computacional, otimizado ao extremo para rodar em hardwares antigos e com pouca memória RAM (Ex: Intel Core i3 de 3ª Geração + 6GB RAM).

🌟 O Desafio e a Solução

Rodar IAs de visão (como LLaVA ou GPT-4V) exige muita memória de vídeo e processamento. O desafio deste projeto foi fazer um bot "assistir" a uma live no YouTube, entender o que está acontecendo na tela e comentar no chat rodando 100% localmente em um notebook de 2012.

Para alcançar isso sem causar o travamento (crash) do sistema operativo, o Dadinho Lite utiliza uma arquitetura de extração de performance:

Micro-Modelo de Visão: Em vez de usar modelos gigantes, utilizamos o Moondream (via Ollama), que possui apenas 1.8 bilhões de parâmetros e consome menos de 1.5GB de RAM.

Compressão Severa em Tempo Real: O bot tira um print da tela, mas antes de enviar para a IA, ele espreme a imagem para uma resolução minúscula (400x400) com 40% de qualidade. A IA ainda consegue entender as formas, mas o peso cai de megabytes para poucos kilobytes, aliviando a CPU.

Ciclo de Respiração (Cooldown): Para evitar o superaquecimento de processadores dual-core, o bot tem pausas programadas de 60 segundos entre análises, permitindo que o uso da CPU volte a 0%.

Coleta de Lixo Forçada: Uso do gc.collect() do Python a cada ciclo para garantir que a RAM de 6GB nunca chegue no limite.

🛠️ Tecnologias Utilizadas

Linguagem: Python 3

Interface Gráfica: tkinter (Leve e nativa)

Automação Web: undetected_chromedriver, selenium

Processamento de Imagem: Pillow (Otimização e redimensionamento)

IA Local: Ollama + Modelo Visual Moondream

📦 Instalação e Configuração

1. Requisitos do Sistema

Windows 10/11 com Memória Virtual (Paginação) ativada.

Pelo menos 6GB de RAM.

Ollama instalado.

2. Baixando as Dependências

No seu terminal (CMD), instale os pacotes necessários:

pip install undetected-chromedriver setuptools google-genai pillow requests


3. Baixando a Inteligência Artificial (Moondream)

Ainda no terminal, baixe o micro-modelo de visão. Ele é bem leve (menos de 2GB):

ollama run moondream


🕹️ Como Usar (Leia com Atenção!)

Execute o arquivo live_bot.py.

Insira o link da live do YouTube.

Escolha o modo IA Local (Moondream).

Clique em Iniciar. O Chrome irá abrir.

A REGRA DE OURO: Assim que o vídeo da live carregar no navegador do bot, altere a qualidade do vídeo do YouTube para 144p imediatamente.

Por quê? Renderizar vídeos em 1080p usa muita CPU. Em 144p, o navegador não pesa nada, permitindo que seu processador foque 100% na Inteligência Artificial.

Faça o login na sua conta do YouTube (apenas na primeira vez).

⚠️ Limitações Conhecidas

Tempo de Resposta: Em processadores antigos (ex: i3-3110M), o bot pode levar de 30 a 90 segundos para formular uma frase após capturar a imagem. Isso é normal e esperado.

O bot é configurado via prompt interno para nunca usar emojis e se limitar a 170 caracteres, evitando travar a caixa de chat do YouTube via injeção de JavaScript.

🤝 Contribuições

Sinta-se livre para clonar, modificar e melhorar. Se você conseguir otimizar esse código para rodar em um hardware ainda mais fraco (ex: 4GB de RAM), abra um Pull Request!