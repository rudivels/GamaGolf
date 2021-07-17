# 1. Gama Golfe
O campus Gama tem a disposição um carro de golfe, que foi batizado com o nome de GamaGolge (GG). 
Este veículo está sendo usado para o uso dia-a-dia das atividades de transporte de material e de pessoas do campus Gama e também está sendo usado para pesquisas e experimentos de mobilidade elétrica.

![](fotos/IMG_3771.jpeg)

A figura a seguir mostra outra foto do GG.


![](fotos/IMG_3787.jpeg)

A primeira experiência foi uma pesquisa de trabalho de conclusão de curso de engenharia automotiva de implementar para transformar o varrinho de golfe num veículo elétrico híbrido série.

Um outro trabalho de conclusão de curso desenvolveu um computador de bordo para o GamaGolfe.



# 2. Plataforma de ensino e pesquisa

A grande vantagem do GamaGolfe é que tem uma estrutura de acionamento e controle bastante simplificado e accessível que permite que se possa usar o veículo como uma plataforma de ensino e pesquisa. 

O sistema de acionamento e controle de movimentação é bastante simples com um controlador de motor de corrente conínua com um banco de bateria de 48Vcc. 


![](fotos/IMG_3783.jpeg)

Além disso, o GG tem uma sistema de sinalização bastante simples, com sinalização de setas e iluminação.
A versão original do GG tem somente um sistema de indicação de carga de bateria, sem sistema BMS, indicação de tensão e corrente, ou carga da bateria.

![](fotos/IMG_3775.jpeg)


# 3. Proposta de arquitetura**

Dessa forma se propõe as seguintes funções ou possibilidades:

* Módulo de carga de bateria inteligente com medição do consumo de energia;
* Módulo de monitoração de corrente e tensão da bateria, com calculo de energia consumido;
* Módulo instrumentação para montorar a velocidade de deslocamento e monitaramento de outros sinais cruziais do GG;
* Módulo GPS para registrar o percurso do veículo
* Módulo Scada num servidor para registrar os diversos variáveis do GG em tempo real;
* Estratégias para viabilizar a movimentação autônoma do GG;


Estrutura composto por 

* Computador de bordo Pocket Beagle om rede CAN;
* Módulo de sinalazação; 
* Módulo de instrumentação;
* Módulo BMS
* Scada de monitoramemte;
* Módulo de direção e aceleração assistida;





## 3.1. Banco de baterias

O banco de baterias é formado por 4 baterias de automotiva  de 100Ah.

![](fotos/IMG_3770.jpeg)

## 3.2. Módulo de sinalização

O sistema de sinalização de setas e iluminação

![](fotos/IMG_3780.jpeg)