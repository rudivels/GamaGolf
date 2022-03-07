# 1. Gama Golfe

link para arquivo original `Documentos/GitHub/GamaGolf`

O campus Gama tem a disposição um carro de golfe, que foi batizado com o nome de GamaGolge (GG). 
Este veículo está sendo usado para o uso dia-a-dia das atividades de transporte de material e de pessoas do campus Gama e também está sendo usado para pesquisas e experimentos de mobilidade elétrica.

![](fotos/IMG_3771.jpeg)

A figura a seguir mostra outra foto do GG.


![](fotos/IMG_3787.jpeg)

A primeira experiência foi uma pesquisa de trabalho de conclusão de curso de engenharia automotiva de implementar para transformar o carrinho de golfe num veículo elétrico híbrido série [1].

Um outro trabalho de conclusão de curso desenvolveu um computador de bordo para o GamaGolfe.


[1] Costa de Oliveira T. Estudo da tecnologia empregada em veículos elétricos com autonomia estendida: comparativo cxperimental com veiculos híbridos. Universidade de Brasília, 2018.


# 2. Plataforma de ensino e pesquisa

A grande vantagem do GamaGolfe é que tem uma estrutura de acionamento e controle bastante simplificado e accessível que permite que se possa usar o veículo como uma plataforma de ensino e pesquisa. 

O sistema de acionamento e controle de movimentação é bastante simples com um controlador de motor de corrente conínua com um banco de bateria de 48Vcc. 


![](fotos/IMG_3783.jpeg)

Além disso, o GG tem uma sistema de sinalização bastante simples, com sinalização de setas e iluminação.
A versão original do GG tem somente um sistema de indicação de carga de bateria, sem sistema BMS, indicação de tensão e corrente, ou carga da bateria.

![](fotos/IMG_3775.jpeg)



O banco de baterias é formado por 4 baterias de automotiva  de 100Ah.

![](fotos/IMG_3770.jpeg)


# 3. Proposta de arquitetura

Dessa forma se propõe as seguintes funções ou possibilidades:

* funcionalidade de carregar a bateria de forma inteligente com medição do consumo de energia e calculo de estado de carag;
* funcionalidade de de monitorar a corrente e a tensão da bateria, com calculo de energia consumida;
* monitorar a velocidade de deslocamento e outros sinais cruziais do GG;
* funcionalidade de registrar o percurso do veículo por meio de GPS;
* visualisar todos os variaveis do veículo por meio de um servidor SCADA em tempo real;
* criar estratégias para viabilizar a movimentação autônoma do GG;


Estrutura para implementar essas funcionalidades será composto pelos seguintes módulos de hardware e software: 

* Módulo de instrumentação; 
* Computador de bordo Pocket Beagle om rede CAN;
* Módulo de sinalização;
* Módulo BMS;
* Servidor SCADA;
* Módulo de direção e aceleração assistida;


## 3.1. Módulo de instrumentação 

O módulo de instrumentação é formado por uma placa de instrumentação com o seguinte esquema.

![](figuras/Esquema_Mod_instrumentacao2.jpg)

Essa placa de controle tem as seguintes funcionalidades :

* Sensor de velocidade
* Sensor de tensão da bateria de 12Volts
* Sensor de tensão do banco de bateria de 48Volts
* Sensor de corrente do banco de bateria
* Display LCD de 128x64
* Interface CAN

A placa tem mais funcionalidades e pode ser programada para ler mais sensores. A figura a seguir mostra a placa de instrumentação sendo testado na bancada.

 
![](fotos/foto_placa_instrum_lcd.jpg) 

### 3.1.1. Módulo de instrumentação 
 
O sensor de velocidade é implementado por meio de um sensor indutivo de aproximação montada no cubo da roda dianteira, onde a cada volta o sensor pega 4 pulsos.

![](fotos/sensor_velocidade.jpg)

O sensor indutivo aparentemente é da configuração PNP com a seguinte pinagem

| cor | função |
|-----|--------|
| marron | alimentação 12Vdc |
| preto  | sinal (deve ligar um resistor 10K para negativa ) |
| azul   | negativa |

O display do módulo de instrumentação mostra no lado direito do painel são mostrados as variáveis elétricas, tensão e corrente da bateria, enquanto no lado esquerda são mostrados os valores de velocidade, odômetro e outras variaveis do veículo.

### 3.1.1 Calibragem do sensor de velocidade

Numa primeira calibragem, a circumferência da roda, ou a distância de uma volta completa da roda é de 99 cm. Numa volta completa o sensor gera 4 pulsos.



## 3.2. Computador de bordo OBC

O diagrama de blocos do computador de bordo é dado a seguir.

![](figuras/Diagrama_BBB_can_GPS.jpg)

O computador de bordo tem a seguinte disponibilidade.

* GPS para pegar os coordenados geográficos
* Interface CAN
* Painel com chaves e leds
* Banco de dados para armazenar os dados
* Acesso por meio de rede Wifi

O OBC é implementado com o BeagleBone Black (BBB). A configuração é a mesma usado pelo OBC do BR800 que pode ser visto no [link](https://github.com/Tecnomobele-FGA/Computador-de-bordo).
A diferença é que no caso do GG é preciso ter a opção de um monitor com interface HDMI e por isso se escolheu o BBB. 

![](fotos/Foto_BBB_bateria.jpg)

Os pinos usados são:

| Beagle  | uso             | pinos | 
|:--------|:---------------:|:-----:|
| CAN 0   | Barramento CAN  | P1 - 26,28 |
| UART 4  | Serial GPS      | P2 - 5,7   | 
| Battery | Litium 18650    | conector batteria TP5,TP6,TP7,TP8 | 
| GPIO    | Chaves para GND | P2 - 2,4   | 
| AIN0    | Monitorar a tensão Vcc | P1 - 19 |

A montagem do OBC será no painel frontal e o esquema a seguir mostra uma opção de montagem.

![](figuras/Esquema_Montagem_OBC_Instrumtacao.jpg)


![](fotos/Foto_painel_mod_instrum_GamaGolfe.jpg)


## 3.3. Módulo de sinalização

O sistema de sinalização de setas e iluminação

![](fotos/IMG_3780.jpeg)


