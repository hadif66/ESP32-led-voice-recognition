
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

const char* ssid = "your-wifi-ssid";
const char* password = "your-wifi-pass";

WebServer server(80);

// LED pins and states
const int ledPins[] = {15, 2, 4, 5, 18};
int ledStates[] = {0, 0, 0, 0, 0}; // All LEDs off

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi!");
  Serial.println(WiFi.localIP());

  for (int i = 0; i < 5; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }

  server.on("/control", HTTP_POST, handleControl);
  server.begin();
}

void handleControl() {
  String body = server.arg("plain"); // Read POST body
  Serial.println("Received command: " + body);

  // Parse JSON command
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, body);
  String action = doc["action"];
  int count = doc["count"];

  if (action == "turn_on") {
    for (int i = 0; i < count && i < 5; i++) {
      digitalWrite(ledPins[i], HIGH);
      ledStates[i] = 1;
    }
  } else if (action == "turn_off") {
    for (int i = 0; i < count && i < 5; i++) {
      digitalWrite(ledPins[i], LOW);
      ledStates[i] = 0;
    }
  }

  server.send(200, "application/json", "{\"status\":\"success\"}");
}

void loop() {
  server.handleClient();
}

