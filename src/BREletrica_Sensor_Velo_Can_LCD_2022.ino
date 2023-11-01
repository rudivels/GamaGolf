/*
  Veiculo Eletrico BREletrico GamaGolfe 
  inicio  23/11/2017 para medir a temperatura e mostrar os dados no LCD 
  2018/02/05 - Upgrade para medicao de Corrente e Tensao
  2018/08/26 - Colocando o display no painel versao com Arduino Mega
             - Instalando medidor de velocidade no pino 2 (Interrupcao)
  2018/09/08 - Odometro para calibrar o velocimetro 
             - Gravacao em EEPROM
  2018/09/13 - Calibracao Odometro. 210-170=40 pulsos Distancia 8.3metros           
               1 pulso = 8.30 / 40 = 0,2075 metro
  2021/08/14 - Fazendo o teste com UNO LCD GPS e Radio LoRa no carro de Golfe
  2022/02/22 - Placa PCB BReletrico_nano_instrum_can_2022.sch
               Arduino Nano, INA219, MCP2551 CAN, Velocidade, Sensores hardwire programaveis
               ina219 OK
               Interrupcao D3 ok
               Entrada analógica A0 - A3 ok  
  2022/02/27 - Mandando Valor de Velocidade, Tensao via CAN
               A cada 5 decimos de segundos é mandando uma mensagem via CAN
  2022/02/28 - Can funcionou a 125kbps 
               Funcionou com o dicionario de dados BRELETmotorV2.dbc
               python3 -m cantools monitor -c can0 -B 125000 src/DBC/BRELETmotorV2.dbc
  2022/03/13 - Mostra corrente e tensão no LCD   
  2022/03/28 - Mandando tensao e corrente do INA219 pela porta CAN
  2022/08/25 - Curva de calibracao  Sensibilidade é 4mV/A do manual do sensor                          
               
  Pinos Arudino Nano  
  D2  Interrupcao CAN 
  D3  Sensor velocidade
  D4  Sensor on of 12V
  D5  Rele 

  D6  lcd_RW   
  D7  lcd_RST  
  D8  lcd_RS 
  D9  lcd_E    

  D10 CAN SS
  D11 CAN MOSI
  D12 CAN MISO
  D13 CAN SCK
  
  A4 SDA ina219 
  A5 SCL ina219

  A0 - entrada sensor de corrente bateria de tracao com LEM 
  A1
  A2
  A3
  A6 
  A7 - entrada tensao bateria de tracao com divisor de tensao

  LCD Based on Universal 8bit Graphics Library, http://code.google.com/p/u8glib/
  Copyright (c) 2012, olikraus@gmail.com
*/

#include "U8glib.h"
#include "MsTimer2.h"
#include <Wire.h>
#include <INA219.h>
#include <SPI.h>
#include <mcp2515.h>

INA219 monitor;
char versao[10]="26ago22"; //"27mar22";  //25ago22

const int velocidade_pin = 3;
int contador_pulsos=0;

int tempor_contador=0;
int tempor_can1=0;
int tempor_can2=2;
int tempor_can3=1;

int sensor_corrente_Pin = A0;
int sensor_tensao_Pin = A7;

/* pinos de display LCD */

#define  lcd_RW  6    // D6
#define  lcd_RST 7    // D7
#define  lcd_E   9    // D9
#define  lcd_RS  8    // D8 

U8GLIB_ST7920_128X64_4X u8g(lcd_E , lcd_RW, lcd_RS, lcd_RST );  // Enable, RW, RS, RESET   

int TensaoBat_Int; 
int CorrenteBat_Int; 

int Velocidade_Int;
int Odometro_Int;

int Tensao12v;
int Corrente12v;

char TensaoBat_Str[10];  
char CorrenteBat_Str[10]; 

char Tensao12vStr[10];
char Corrente12vStr[10];

char Velocidade_Str[10];
char Odometro_Str[10]; 

struct can_frame canMsg1;
MCP2515 mcp2515(10);

void le_sensores(void)
{
 float f;
 int x;  
 x = analogRead(sensor_tensao_Pin);
 f = (12.3*(5.0/1024.0)*x);   
 dtostrf(f, 4, 2, TensaoBat_Str);
 TensaoBat_Int=int(100*f);

 x = analogRead(sensor_corrente_Pin);
 f = (x-517)*(1250.0/1024.0);         // offset é 517     ganho = 4mv/A
 //f = ((5.0/1024.0)*x - 2.52)*250;   // offset é 2,52    ganho = 4mv/A
 dtostrf(f, 4, 2, CorrenteBat_Str); 
 CorrenteBat_Int=int(100*f);
}

void le_velocidade(void)
{
 dtostrf(Velocidade_Int, 4, 0, Velocidade_Str);
 dtostrf(Odometro_Int, 4, 0, Odometro_Str);
}

void le_ina219(void)
{
 float f; 
 f = monitor.busVoltage()+ 0.7;
 Tensao12v=int(f*100);
 dtostrf(f,4, 1, Tensao12vStr);
 f = monitor.shuntCurrent();
 Corrente12v=int(f*100);
 dtostrf(f,4, 2, Corrente12vStr);
}

void draw(void) {
 u8g.setFont(u8g_font_unifont);
 u8g.setScale2x2(); 
 u8g.drawStr( 0, 10 , "Vel="); u8g.drawStr(30, 10, Velocidade_Str);    
 u8g.undoScale();
 u8g.drawStr( 0, 36 , "Vf=     Vb=    ");  u8g.drawStr(24, 36, Tensao12vStr);  u8g.drawStr(88, 36, TensaoBat_Str); //Sensor_2_Str);
 u8g.drawStr( 0, 50 , "If=     Ib=    ");  u8g.drawStr(24, 50, Corrente12vStr);u8g.drawStr(88, 50, CorrenteBat_Str); //Sensor_1_Str); 
 u8g.drawStr( 0, 62 , "Od=       CAN= ");  u8g.drawStr(24, 62, Odometro_Str);
}

void inicia_lcd(void)
{
 if ( u8g.getMode() == U8G_MODE_R3G3B2 ) {
    u8g.setColorIndex(255);     // white
 }
  else if ( u8g.getMode() == U8G_MODE_GRAY2BIT ) {
    u8g.setColorIndex(3);         // max intensity
  }
   else if ( u8g.getMode() == U8G_MODE_BW ) {
    u8g.setColorIndex(1);         // pixel on
  }
  else if ( u8g.getMode() == U8G_MODE_HICOLOR ) {
    u8g.setHiColorByRGB(255,255,255);
 }
}

void setup(void) { 
  pinMode(velocidade_pin,INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(velocidade_pin), conta_pulsos, CHANGE);  
  MsTimer2::set(100, BaseDeTempo); // dezimo segundos
  MsTimer2::start();
  monitor.begin();
  /* Iinicializa lcd */
  inicia_lcd(); 
  delay(1000); 
  u8g.firstPage();
  do {
    u8g.setFont(u8g_font_unifont);
    u8g.drawStr(20, 20, "BREletrico");      
    u8g.drawStr(30, 54, versao);
  } while (u8g.nextPage());
  Serial.begin(9600);
  Serial.print("BREletrico ");
  Serial.print(versao);
  mcp2515.reset();
  mcp2515.setBitrate(CAN_125KBPS,MCP_8MHZ);
  mcp2515.setNormalMode(); 
  delay(1000);
}

void conta_pulsos() {
  contador_pulsos++;
  Odometro_Int++;
}

void BaseDeTempo(void)
{
 /*medidido velocidade - desabilitado para fazer uma simulação */
 tempor_contador++;
 tempor_can1++;
 tempor_can2++;
 tempor_can3++; 
 if (tempor_contador==10)
 {
  Velocidade_Int=contador_pulsos;
  contador_pulsos=0;
  tempor_contador=0;
  // Velocidade_Int++;  // testando debug
 } 
}

//unsigned char tp=0;

void loop(void) {
 char c;
 le_sensores();
 le_velocidade();
 le_ina219();
 /* imprimindo no LCD */
 u8g.firstPage();  
 do {
      draw();   
 } while( u8g.nextPage() );
 /* Fim impressao LCD */
 if (tempor_can1 >= 5)
 {
  tempor_can1=0;
  canMsg1.can_id = 0x10FEBF90 | CAN_EFF_FLAG;  //  2432614288 testando com 0x90FEBF90 tambem funcionou
  canMsg1.can_dlc = 8;
  canMsg1.data[0] = (Velocidade_Int & 0x00FF); //  (Velocidade_Int & 0x00FF);
  canMsg1.data[1] = (Velocidade_Int >> 8) & 0x00FF; //(Velocidade_Int >> 8) & 0x00FF;
  canMsg1.data[2] = 0xFF;  
  canMsg1.data[3] = 0xFF;  
  canMsg1.data[4] = 0xFF;   
  canMsg1.data[5] = 0xFF;  
  canMsg1.data[6] = 0xFF; 
  canMsg1.data[7] = 0xFF;
  mcp2515.sendMessage(&canMsg1);
 } 
 if (tempor_can2 >= 5)
 {
  tempor_can2=0;
  //Voltage_Int=Sensor_1_Int;
  //Current_Int=Sensor_2_Int;
  canMsg1.can_id = 0x10088A9E | CAN_EFF_FLAG; // 2416478878
  canMsg1.can_dlc = 8;
  canMsg1.data[0] = (TensaoBat_Int & 0x00FF);  
  canMsg1.data[1] = (TensaoBat_Int >> 8) & 0x00FF;
  canMsg1.data[2] = (CorrenteBat_Int & 0x00FF); 
  canMsg1.data[3] = (CorrenteBat_Int >> 8) & 0x00FF;  
  canMsg1.data[4] = 0xFF;  // temperatura 8 bits
  canMsg1.data[5] = 0xFF;  // 0-forward, 1-backward, 2-brake, 3-stop, 6-ready
  canMsg1.data[6] = 0xFF; 
  canMsg1.data[7] = 0xFF;
  mcp2515.sendMessage(&canMsg1);
  //Serial.write("message sent");
 }
 if (tempor_can3 >= 5)
 {
  tempor_can3=0;
  canMsg1.can_id = 0x100A8A9E | CAN_EFF_FLAG; //  PGN Proprio Rudi
  canMsg1.can_dlc = 8;
  canMsg1.data[0] = (Tensao12v & 0x00FF);  
  canMsg1.data[1] = (Tensao12v >> 8) & 0x00FF;
  canMsg1.data[2] = (Corrente12v & 0x00FF); 
  canMsg1.data[3] = (Corrente12v >> 8) & 0x00FF;  
  canMsg1.data[4] = 0xFF;   
  canMsg1.data[5] = 0xFF;   
  canMsg1.data[6] = 0xFF; 
  canMsg1.data[7] = 0xFF;
  mcp2515.sendMessage(&canMsg1);
 }
 if (Serial.available() > 0) 
 {
  c = Serial.read();
  switch(c)
  {
    case 'V': Serial.println(Velocidade_Int); break; // Serial.write("V"); break;
    case 'F': Serial.println(Tensao12vStr);   break; //Serial.write("F"); break;
    case '1': Serial.println(TensaoBat_Str);   break; //Serial.write("1"); break;
    case '2': Serial.println(CorrenteBat_Str);   break; //Serial.write("2"); break;                           
    default:  Serial.write(c); 
  }   
 }
}
