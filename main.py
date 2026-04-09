// ===================== LIBRARIES =====================
#include <WiFi.h>
#include "DHT.h"
#include <WebServer.h>

// ===================== WIFI =====================
const char* ssid = "network";
const char* password = "1122334455";
WebServer server(80);

// ===================== DHT11 =====================
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ===================== RELAYS =====================
#define FAN_RELAY 27
#define SPRINKLER_RELAY 26
#define LDR_RELAY 25
#define MOTOR_RELAY 14
#define MOISTURE1_RELAY 15
#define MOISTURE2_RELAY 2
#define MOISTURE3_RELAY 5

// >>> ADDED EXTRA RELAY
#define EXTRA_RELAY 13
bool extraState = false;
String extraStatus = "OFF";

// ===================== PINS =====================
#define LDR_PIN 34
#define TRIG_PIN 32
#define ECHO_PIN 33
#define TANK_HEIGHT 25.0 // cm
#define MOISTURE1_PIN 35
#define MOISTURE2_PIN 36
#define MOISTURE3_PIN 39

// ===================== VARIABLES =====================
bool manualMode = false;
bool fanState = false;
bool sprinklerState = false;
bool lightManual = false;
bool lightState = false;
int ldrThreshold = 2000;
String lightStatus = "OFF";
bool motorManual = false;
bool motorState = false;
float waterLevelPercent = 0;
String motorStatus = "OFF";
bool moistureManual[3] = {false,false,false};
bool moistureState[3] = {false,false,false};
String moistureStatus[3] = {"OFF","OFF","OFF"};
unsigned long previousMillis = 0;
bool cycleState = false;
String systemStatus = "Normal";

// ===================== HELPER FUNCTIONS =====================
void setFan(bool state){
  fanState = state;
  digitalWrite(FAN_RELAY, state ? LOW : HIGH);
}
void setSprinkler(bool state){
  sprinklerState = state;
  digitalWrite(SPRINKLER_RELAY, state ? LOW : HIGH);
}
void setLight(bool state){
  lightState = state;
  digitalWrite(LDR_RELAY, state ? HIGH : LOW);
}
void setMotor(bool state){
  motorState = state;
  digitalWrite(MOTOR_RELAY, state ? LOW : HIGH);
}
void setMoisture(int index, bool state){
  moistureState[index] = state;
  if(index == 0) digitalWrite(MOISTURE1_RELAY, state ? LOW : HIGH);
  if(index == 1) digitalWrite(MOISTURE2_RELAY, state ? LOW : HIGH);
  if(index == 2) digitalWrite(MOISTURE3_RELAY, state ? LOW : HIGH);
}

// >>> ADDED EXTRA RELAY FUNCTION
void setExtra(bool state){
  extraState = state;
  digitalWrite(EXTRA_RELAY, state ? LOW : HIGH);
  extraStatus = state ? "Manual ON" : "Manual OFF";
}

// ===================== MANUAL HANDLERS =====================
void handleManualFanOn(){ manualMode=true; setFan(true); systemStatus="Fan MANUAL ON"; server.sendHeader("Location","/"); server.send(303); }
void handleManualFanOff(){ manualMode=true; setFan(false); systemStatus="Fan MANUAL OFF"; server.sendHeader("Location","/"); server.send(303); }
void handleManualSprinklerOn(){ manualMode=true; setSprinkler(true); systemStatus="Sprinkler MANUAL ON"; server.sendHeader("Location","/"); server.send(303); }
void handleManualSprinklerOff(){ manualMode=true; setSprinkler(false); systemStatus="Sprinkler MANUAL OFF"; server.sendHeader("Location","/"); server.send(303); }
void handleAutoMode(){ manualMode=false; systemStatus="AUTO MODE Activated"; server.sendHeader("Location","/"); server.send(303); }

void handleLightOn(){ lightManual=true; setLight(true); lightStatus="Manual ON"; server.sendHeader("Location","/"); server.send(303); }
void handleLightOff(){ lightManual=true; setLight(false); lightStatus="Manual OFF"; server.sendHeader("Location","/"); server.send(303); }
void handleLightAuto(){ lightManual=false; lightStatus="AUTO MODE"; server.sendHeader("Location","/"); server.send(303); }

void handleMotorOn(){ motorManual=true; setMotor(true); motorStatus="Manual ON"; server.sendHeader("Location","/"); server.send(303); }
void handleMotorOff(){ motorManual=true; setMotor(false); motorStatus="Manual OFF"; server.sendHeader("Location","/"); server.send(303); }
void handleMotorAuto(){ motorManual=false; server.sendHeader("Location","/"); server.send(303); }

void handleMoisture1On(){ moistureManual[0]=true; setMoisture(0,true); moistureStatus[0]="Manual ON"; server.sendHeader("Location","/"); server.send(303); }
void handleMoisture1Off(){ moistureManual[0]=true; setMoisture(0,false); moistureStatus[0]="Manual OFF"; server.sendHeader("Location","/"); server.send(303); }
void handleMoisture1Auto(){ moistureManual[0]=false; server.sendHeader("Location","/"); server.send(303); }

void handleMoisture2On(){ moistureManual[1]=true; setMoisture(1,true); moistureStatus[1]="Manual ON"; server.sendHeader("Location","/"); server.send(303); }
void handleMoisture2Off(){ moistureManual[1]=true; setMoisture(1,false); moistureStatus[1]="Manual OFF"; server.sendHeader("Location","/"); server.send(303); }
void handleMoisture2Auto(){ moistureManual[1]=false; server.sendHeader("Location","/"); server.send(303); }

void handleMoisture3On(){ moistureManual[2]=true; setMoisture(2,true); moistureStatus[2]="Manual ON"; server.sendHeader("Location","/"); server.send(303); }
void handleMoisture3Off(){ moistureManual[2]=true; setMoisture(2,false); moistureStatus[2]="Manual OFF"; server.sendHeader("Location","/"); server.send(303); }
void handleMoisture3Auto(){ moistureManual[2]=false; server.sendHeader("Location","/"); server.send(303); }

// >>> EXTRA RELAY HANDLERS
void handleExtraOn(){ setExtra(true); server.sendHeader("Location","/"); server.send(303); }
void handleExtraOff(){ setExtra(false); server.sendHeader("Location","/"); server.send(303); }

// ===================== WEB PAGE =====================
void handleRoot(){
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    int ldrValue = analogRead(LDR_PIN);

    // --- ultrasonic ---
    digitalWrite(TRIG_PIN,LOW); delayMicroseconds(2);
    digitalWrite(TRIG_PIN,HIGH); delayMicroseconds(10);
    digitalWrite(TRIG_PIN,LOW);

    long duration = pulseIn(ECHO_PIN,HIGH);
    float distance = duration * 0.034 / 2;
    if(distance > TANK_HEIGHT) distance = TANK_HEIGHT;

    waterLevelPercent = ((TANK_HEIGHT - distance) / TANK_HEIGHT) * 100;

    // AUTO MOTOR LOGIC
    if(!motorManual){
      if(!motorState && waterLevelPercent < 50){
        setMotor(true);
        motorStatus="AUTO ON";
      }
      else if(motorState && waterLevelPercent >= 90){
        setMotor(false);
        motorStatus="AUTO OFF";
      }
    }
    else motorStatus = motorState ? "Manual ON" : "Manual OFF";

    // LDR AUTO
    if(!lightManual){
      setLight((ldrValue < ldrThreshold));
      lightStatus = lightState ? "AUTO: Dark → ON" : "AUTO: Light → OFF";
    }

    int moistureValue[3];
    moistureValue[0]=analogRead(MOISTURE1_PIN);
    moistureValue[1]=analogRead(MOISTURE2_PIN);
    moistureValue[2]=analogRead(MOISTURE3_PIN);

    for(int i=0; i<3; i++){
      if(!moistureManual[i]){
        if(moistureValue[i] > 2000){
          setMoisture(i,true);
          moistureStatus[i]="AUTO ON (Dry)";
        }
        else{
          setMoisture(i,false);
          moistureStatus[i]="AUTO OFF (Wet)";
        }
      }
    }

    // ===================== WEBPAGE =====================
    String page="<html><head><meta http-equiv='refresh' content='2'/><style>";
    page+="body{font-family:Arial;text-align:center;background:#eef2f3;}";
    page+=".box{background:white;padding:20px;margin:auto;margin-top:30px;width:60%;border-radius:15px;box-shadow:0 0 10px #777;}";
    page+="table{width:100%;font-size:20px;border-collapse:collapse;}";
    page+="th,td{padding:12px;border:1px solid #888;}th{background:#333;color:white;}";
    page+="button{padding:10px 20px;font-size:18px;margin:10px;border-radius:10px;}</style></head><body>";

    // ---------------- DHT BOX ----------------
    page+="<div class='box'><h2>DHT11 Readings</h2>";
    page+="<table><tr><th>Parameter</th><th>Value</th></tr>";
    page+="<tr><td>Temperature</td><td>"+String(t)+" °C</td></tr>";
    page+="<tr><td>Humidity</td><td>"+String(h)+"%</td></tr>";
    page+="<tr><td>Fan</td><td>"+String(fanState?"ON":"OFF")+"</td></tr>";
    page+="<tr><td>Sprinkler</td><td>"+String(sprinklerState?"ON":"OFF")+"</td></tr>";
    page+="<tr><td>System Mode</td><td>"+systemStatus+"</td></tr></table>";
    page+="<a href='/fanon'><button>Fan ON</button></a>";
    page+="<a href='/fanoff'><button>Fan OFF</button></a><br>";
    page+="<a href='/sprinkleron'><button>Sprinkler ON</button></a>";
    page+="<a href='/sprinkleroff'><button>Sprinkler OFF</button></a><br>";
    page+="<a href='/auto'><button>AUTO MODE</button></a></div>";

    // ---------------- LDR ----------------
    page+="<div class='box'><h2>LDR Light</h2>";
    page+="<table><tr><th>LDR Value</th><th>Status</th></tr>";
    page+="<tr><td>"+String(ldrValue)+"</td><td>"+lightStatus+"</td></tr></table>";
    page+="<a href='/lighton'><button>Light OFF</button></a>";
    page+="<a href='/lightoff'><button>Light ON</button></a><br>";
    page+="<a href='/lightauto'><button>LIGHT AUTO</button></a></div>";

    // ---------------- Tank ----------------
    page+="<div class='box'><h2>Water Tank</h2>";
    page+="<table><tr><th>Water Level</th><th>Status</th></tr>";
    page+="<tr><td>"+String(waterLevelPercent)+" %</td><td>"+motorStatus+"</td></tr></table>";
    page+="<a href='/motoron'><button>Motor ON</button></a>";
    page+="<a href='/motoroff'><button>Motor OFF</button></a><br>";
    page+="<a href='/motorauto'><button>MOTOR AUTO</button></a></div>";

    // ---------------- Moisture ----------------
    page+="<div class='box'><h2>Soil Moisture</h2>";
    page+="<table><tr><th>Sensor</th><th>Value</th><th>Status</th></tr>";
    for(int i=0;i<3;i++){
      page+="<tr><td>Moisture "+String(i+1)+"</td><td>"+String(moistureValue[i])+"</td><td>"+moistureStatus[i]+"</td></tr>";
    }
    page+="</table>";
    page+="<a href='/moisture1on'><button>M1 ON</button></a>";
    page+="<a href='/moisture1off'><button>M1 OFF</button></a>";
    page+="<a href='/moisture1auto'><button>M1 AUTO</button></a><br>";
    page+="<a href='/moisture2on'><button>M2 ON</button></a>";
    page+="<a href='/moisture2off'><button>M2 OFF</button></a>";
    page+="<a href='/moisture2auto'><button>M2 AUTO</button></a><br>";
    page+="<a href='/moisture3on'><button>M3 ON</button></a>";
    page+="<a href='/moisture3off'><button>M3 OFF</button></a>";
    page+="<a href='/moisture3auto'><button>M3 AUTO</button></a></div>";

    // >>> EXTRA RELAY SECTION
    page+="<div class='box'><h2>Extra Manual Relay</h2>";
    page+="<table><tr><th>Status</th></tr>";
    page+="<tr><td>"+extraStatus+"</td></tr></table>";
    page+="<a href='/extraon'><button>Extra ON</button></a>";
    page+="<a href='/extraoff'><button>Extra OFF</button></a>";
    page+="</div>";

    page+="</body></html>";
    server.send(200,"text/html",page);
}

// ===================== SETUP =====================
void setup(){
  Serial.begin(115200);
  dht.begin();

  pinMode(FAN_RELAY,OUTPUT);
  pinMode(SPRINKLER_RELAY,OUTPUT);
  pinMode(LDR_RELAY,OUTPUT);
  pinMode(MOTOR_RELAY,OUTPUT);
  pinMode(MOISTURE1_RELAY,OUTPUT);
  pinMode(MOISTURE2_RELAY,OUTPUT);
  pinMode(MOISTURE3_RELAY,OUTPUT);

  pinMode(TRIG_PIN,OUTPUT);
  pinMode(ECHO_PIN,INPUT);

  // >>> Extra relay setup
  pinMode(EXTRA_RELAY, OUTPUT);
  setExtra(false);

  setFan(false);
  setSprinkler(false);
  setLight(false);
  setMotor(false);
  setMoisture(0,false);
  setMoisture(1,false);
  setMoisture(2,false);

  WiFi.begin(ssid,password);
  Serial.print("Connecting");
  while(WiFi.status()!=WL_CONNECTED){
    delay(400);
    Serial.print(".");
  }
  Serial.println("\nConnected! IP:");
  Serial.println(WiFi.localIP());

  server.on("/",handleRoot);

  server.on("/fanon",handleManualFanOn);
  server.on("/fanoff",handleManualFanOff);

  server.on("/sprinkleron",handleManualSprinklerOn);
  server.on("/sprinkleroff",handleManualSprinklerOff);

  server.on("/auto",handleAutoMode);

  server.on("/lighton",handleLightOn);
  server.on("/lightoff",handleLightOff);
  server.on("/lightauto",handleLightAuto);

  server.on("/motoron",handleMotorOn);
  server.on("/motoroff",handleMotorOff);
  server.on("/motorauto",handleMotorAuto);

  server.on("/moisture1on",handleMoisture1On);
  server.on("/moisture1off",handleMoisture1Off);
  server.on("/moisture1auto",handleMoisture1Auto);

  server.on("/moisture2on",handleMoisture2On);
  server.on("/moisture2off",handleMoisture2Off);
  server.on("/moisture2auto",handleMoisture2Auto);

  server.on("/moisture3on",handleMoisture3On);
  server.on("/moisture3off",handleMoisture3Off);
  server.on("/moisture3auto",handleMoisture3Auto);

  // >>> Extra relay routes
  server.on("/extraon", handleExtraOn);
  server.on("/extraoff", handleExtraOff);

  server.begin();
}

// ===================== LOOP =====================
void loop(){
  server.handleClient();

  float t = dht.readTemperature();
  int ldrValue = analogRead(LDR_PIN);

  unsigned long currentMillis = millis();

  // AUTO FAN & SPRINKLER
  if(!manualMode){
    if(t <= 28){
      setFan(false);
      setSprinkler(false);
      systemStatus = "Normal Mode: Fan OFF, Sprinkler OFF";
    }
    else if(t > 28 && t <= 32){
      systemStatus = "Fan Cycling (30s ON / 30s OFF)";
      if(currentMillis - previousMillis >= 30000){
        cycleState = !cycleState;
        previousMillis = currentMillis;
      }
      setFan(cycleState);
      setSprinkler(false);
    }
    else if(t > 32){
      systemStatus = "Sprinkler Cycling (30s ON / 30s OFF)";
      if(currentMillis - previousMillis >= 30000){
        cycleState = !cycleState;
        previousMillis = currentMillis;
      }
      setSprinkler(cycleState);
      setFan(false);
    }
  }

  // LDR AUTO
  if(!lightManual)
    setLight((ldrValue < ldrThreshold));

  // TANK MOTOR AUTO
  digitalWrite(TRIG_PIN,LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN,HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN,LOW);

  long duration = pulseIn(ECHO_PIN,HIGH);
  float distance = duration * 0.034 / 2;
  if(distance > TANK_HEIGHT) distance = TANK_HEIGHT;

  waterLevelPercent = ((TANK_HEIGHT - distance) / TANK_HEIGHT) * 100;

  if(!motorManual){
    if(!motorState && waterLevelPercent < 50){
      setMotor(true);
      motorStatus="AUTO ON";
    }
    else if(motorState && waterLevelPercent >= 90){
      setMotor(false);
      motorStatus="AUTO OFF";
    }
  }

  // Moisture AUTO
  int moistureValue[3] = {
    analogRead(MOISTURE1_PIN),
    analogRead(MOISTURE2_PIN),
    analogRead(MOISTURE3_PIN)
  };

  for(int i=0;i<3;i++){
    if(!moistureManual[i]){
      if(moistureValue[i] > 2000){
        setMoisture(i,true);
        moistureStatus[i]="AUTO ON (Dry)";
      } else {
        setMoisture(i,false);
        moistureStatus[i]="AUTO OFF (Wet)";
      }
    }
  }

  delay(200);
}
