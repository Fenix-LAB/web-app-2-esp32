#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>  // Necesitamos esta librería para crear el cuerpo JSON

const char* ssid = "TuWiFi";           // Reemplaza con tu red WiFi
const char* password = "TuContraseña"; // Reemplaza con tu contraseña WiFi

const String serverUrl = "https://hjt2crgsem.us-east-1.awsapprunner.com/api/recive-data"; // Cambia a la URL de tu servidor FastAPI

void setup() {
    Serial.begin(115200);
    Serial.println("\n[ESP32] Iniciando...");

    // Conectar a WiFi
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

    // Hacer la solicitud POST
    sendPostRequest("Encender LED");
}

void loop() {
    // Aquí puedes agregar más lógica si es necesario
}

void sendPostRequest(const String& message) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;

        // Configurar la URL
        http.begin(serverUrl); // Inicia la conexión HTTP
        http.addHeader("Content-Type", "application/json");  // Establece el tipo de contenido a JSON

        // Crear el objeto JSON con el campo 'data'
        StaticJsonDocument<200> doc;
        doc["data"] = message; // El dato que deseas enviar

        // Serializar el objeto JSON en una cadena
        String jsonBody;
        serializeJson(doc, jsonBody);

        // Enviar la solicitud POST con el cuerpo JSON
        Serial.println("[HTTP] Enviando solicitud POST...");
        int httpResponseCode = http.POST(jsonBody);  // Enviar el JSON en el cuerpo

        // Verificar la respuesta
        if (httpResponseCode > 0) {
            Serial.printf("[HTTP] Respuesta del servidor: %d\n", httpResponseCode);
            String payload = http.getString();
            Serial.println("[HTTP] Respuesta: " + payload);
        } else {
            Serial.printf("[HTTP] Error al hacer la solicitud POST: %d\n", httpResponseCode);
        }

        // Cerrar la conexión
        http.end();
    } else {
        Serial.println("[WiFi] No hay conexión a la red WiFi.");
    }
}