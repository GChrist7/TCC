#include "Adafruit_VL53L0X.h"
#include <PubSubClient.h>
#include <WiFi.h>
#include <ESP32Servo.h>


Servo myservo;

const char *WIFI_SSID = "GOHAN-2.4";

const char *MQTT_SERVER = "test.mosquitto.org";
const uint16_t MQTT_PORT = 1883;

char SendUp[10];
char SendDown[10];

float offset;


WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

float Filter[200]; //Filtro para a média

typedef struct {
  float up[4];   //Medida de up para 5, 6, 7, 8
  float down[4]; //Medida de down para 5, 6, 7, 8
} General_Cycle;

General_Cycle Cycle[3];//

Adafruit_VL53L0X lox = Adafruit_VL53L0X();

/*void CallbackMqtt(char* topic, byte* payload,unsigned int length){
  Serial.print("ReceivedMessage!");
}*/

void SetupMqtt(){
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  //mqttClient.setCallback(CallbackMqtt);
}

void ConnectToWiFi(){
  Serial.print("Connecting to WiFi ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, "bch080363");

  while (WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(500);
  }
  Serial.print("\nConnected to ");
  Serial.println(WIFI_SSID);
}

void ConnectToMqtt(){
  Serial.println("Connecting to MQTT Broker...");
  while (!mqttClient.connected()) {
    char clientId[100] = "\0";
    sprintf(clientId, "ESP32Client-12345");

    Serial.println(clientId);

    if (mqttClient.connect(clientId)){
      Serial.println("Connected to MQTT broker.");
    }
  }
}

void init_cycles(){
  int i, j;
  for(i=0 ; i<3 ; i++){
    for(j=0 ; j<4 ; j++){
      Cycle[i].up[j] = 0;
      Cycle[i].down[j] = 0;
    }
  }
}

void print_cycle(int num){
  while (!mqttClient.connected()){
    ConnectToMqtt();
  }
  int force;  
  for(int i=0 ; i<4 ; i++){
    force = i + 5;          
    Serial.print("Up "); Serial.print(force); Serial.print("kgf = "); Serial.print(Cycle[num].up[i]);
    dtostrf(Cycle[num].up[i], 2, 2, SendUp);
    mqttClient.publish("Unifesp-ICT MQTT Topic I4O592", SendUp);
    Serial.print("                      ");
    Serial.print("Down "); Serial.print(force); Serial.print("kgf = "); Serial.println(Cycle[num].down[i]);
    dtostrf(Cycle[num].down[i], 2, 2, SendDown);
    mqttClient.publish("Unifesp-ICT MQTT Topic I4O592", SendDown);
  }        
}

float get_measure(){
  int i = 0;
  while(1){
    VL53L0X_RangingMeasurementData_t measure;
    lox.rangingTest(&measure, false); // Pega a medida e armazena na estrutura measure
    if (measure.RangeStatus != 4) {  // Checa se a medida está dentro do limite do sensor
      Filter[i] = (float)measure.RangeMilliMeter; // Armazena a medida obtida 
      i++;
      //return Filter[0];
    }
    // Após 10 medidas, a média móvel entre elas é feita e o valor medido naquele ciclo é armazenado   
    if(i == 200){
      float avg_measure = 0;
      int j;
      for(j=0 ; j<200 ; j++){
        avg_measure = avg_measure + Filter[j];
        delay(10);
      }
      avg_measure = avg_measure / 200;
      return avg_measure;
    }
  }
}

//Função para mover o Servo gradualmente até a força desejada
void Move_Servo(int pos_atual, int pos_final){
  int i;
  if(pos_final > pos_atual){
    for(i=pos_atual ; i<=pos_final ; i++){
      myservo.write(i);
      delay(100);
    }
  }
  else{
    for(i=pos_atual ; i>=pos_final ; i--){
      myservo.write(i);
      delay(500);
    }
  }
}

void Move_Servo_Up(int force){
  if(force == 0)
    Move_Servo(90, 80);
  if(force == 1)
    Move_Servo(90, 78);
  if(force == 2)
    Move_Servo(90, 76);
  if(force == 3)
    Move_Servo(90, 74);
}

void Move_Servo_Down(int force){
  if(force == 0)
    Move_Servo(90, 100);
  if(force == 1)
    Move_Servo(90, 102);
  if(force == 2)
    Move_Servo(90, 104);
  if(force == 3)
    Move_Servo(90, 106);
}

void do_cycle1(){
  int i;
  delay(500);
  for(i=0 ; i<4 ; i++){
    Move_Servo_Down(i); 
    delay(500);
    Cycle[0].down[i] = offset - get_measure();
    myservo.write(90);
    delay(500);
  }
  myservo.write(90);
  delay(1000);
  //offset = get_measure();
  delay(500);
  for(i=0 ; i<4 ; i++){
    Move_Servo_Up(i);
    delay(500);
    Cycle[0].up[i] = get_measure() - offset;     
    myservo.write(90);
    delay(500);   
  }
  myservo.write(91);
  print_cycle(0);      
}

void setup() {
  Serial.begin(115200);
  Serial.println("Starting...");

  // wait until serial port opens for native USB devices
  
  while (! Serial) {
    delay(1);
  }
  
  Serial.println("Adafruit VL53L0X test");
  while (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X"));
    //while(!lox.begin());
  }
  // power 
  Serial.println(("VL53L0X API Simple Ranging example\n\n")); 

  ConnectToWiFi();
  SetupMqtt();

  Serial.println("Initiailizing");

  myservo.attach(13);
  //myservo.write(0);
  myservo.write(90);

  offset = get_measure();

  Serial.print("offset set as: ");
  Serial.print(offset);
  Serial.println(" mm");

  Serial.println("Initializing cycle");

  init_cycles(); 

  do_cycle1();   
}


void loop() {

}