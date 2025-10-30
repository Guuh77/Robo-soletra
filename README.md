Resumidamente, as pastas mais importantes é dics, Robo e dup.
 
dics é a pasta onde esta alguns dicionarios antigos.
dup foi uma pasta usada para juntas varios dicionario e remover palavras duplicadas.
e o Robo é a alma do projeto
 
nele contem tres robos, um simples e com um tempo de execução longo por ultilizar o Selenium para inputar as palavras chamado robo_soletra.py. Outro uma versao muito mais avançado do robo_soletra.py
basicamente ele usa Selenium para muitas coisas dentro da pagina, o nosso alicerce, mas o grande incremento dele é usar javascript para deixe o input das palavras ultra rapido. o robo_soletra_ultimate.py por exemplo,
possui um p/s(palavras por segundo) de 20 a 22. Ja o outro, é uma versao experimental que na teoria era para usar machine learning para criar um arquivo csv só com os acertos da primeira execução, tornando a proxima execuçao quase ultrassônica,
ja que ele inputa entre 30 a 35p/s, que dependendo do dia, pode resolver o soletra em menos de 2 segundos. Nos dias com mais palavras, a ideia é que os ultimates, terminem o desafio com menos de 60 segundos,
ja o simples por exemplo terminaria entre 5 a 10 minutos. Alem dos ultimates serem ultra rapidos, tambem sao mega confiaveis, ja que no simples, a chance dele inputar duas ou mais palavras antes de confirmar é gigante, o que é quase nula nos ultimates ja que o javascript torna tudo muito rapido e responsivo.
Tem tambem o robo_soletra_ml_funcional, onde o machine learning esta funcionando, lembre-se de sempre apagar o historico a cada dia ja que as palavras mudam.
