#include <WiFi.h>
#include <WebSocketsClient.h>

const char* ssid = "TuWiFi";           // Reemplaza con tu red WiFi
const char* password = "TuContraseña"; // Reemplaza con tu contraseña WiFi

WebSocketsClient webSocket;

void webSocketEvent(WStype_t type, uint8_t *payload, size_t length) {
    switch (type) {
        case WStype_CONNECTED:
            Serial.println("[WebSocket] Conectado al servidor!");
            break;
        
        case WStype_DISCONNECTED:
            Serial.println("[WebSocket] Desconectado del servidor!");
            break;
        
        case WStype_TEXT:
            Serial.printf("[WebSocket] Mensaje recibido: %s\n", payload);
            if (strcmp((char*)payload, "Encender LED") == 0) {
                Serial.println("[ESP32] Encendiendo LED...");
                digitalWrite(2, HIGH);  // Enciende el LED en el pin 2
            } else if (strcmp((char*)payload, "Apagar LED") == 0) {
                Serial.println("[ESP32] Apagando LED...");
                digitalWrite(2, LOW);  // Apaga el LED en el pin 2
            } else {
                Serial.println("[ESP32] Mensaje no reconocido.");
            }
            break;
        
        default:
            Serial.printf("[WebSocket] Evento desconocido: %d\n", type);
            break;
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("\n[ESP32] Iniciando...");

    // Conectar a WiFi
    Serial.println("[WiFi] Conectando...");
    WiFi.begin(ssid, password);
    int intentos = 0;

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
        intentos++;
        if (intentos > 20) {  // Si después de 20 intentos no conecta, reiniciar ESP32
            Serial.println("\n[WiFi] No se pudo conectar. Reiniciando...");
            ESP.restart();
        }
    }
    Serial.println("\n[WiFi] Conectado con éxito!");
    Serial.print("[WiFi] Dirección IP: ");
    Serial.println(WiFi.localIP());

    // Configurar WebSocket
    Serial.println("[WebSocket] Conectando...");
    webSocket.begin("https://hjt2crgsem.us-east-1.awsapprunner.com", 8080, "/ws"); // Asegúrate de usar el dominio correcto
    webSocket.onEvent(webSocketEvent);

    // Configurar el pin del LED
    pinMode(2, OUTPUT);
    digitalWrite(2, LOW);  // Apagar LED al inicio
}

void loop() {
    webSocket.loop();  // Mantiene la conexión WebSocket activa
}
