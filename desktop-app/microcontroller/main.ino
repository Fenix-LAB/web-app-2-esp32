// Codigo para el microcontrolador (leer y enviar datos por serial)

// Librerias
// #include <Tus librearias>

// Constantes
// #define TUS_CONSTANTES

// Para lograr una buena comunicacion con el microcontrolador, se usara millis()
unsigned long tiempo1, tiempo2;
unsigned long t1 = 0, t2 = 2000;

int ps1, ps2, ps3, ms1, ms2, ms3;

void setup() {
  // Inicializacion
  Serial.begin(9600);
  
  // PinModes
    // pinMode(13, OUTPUT);
}

void loop() {

  /*
  Vi que millis es una buena opcion para leer y enviar datos por serial
  Se puede usar un contador para enviar datos cada cierto tiempo
  Se puede usar un contador para leer datos cada cierto tiempo
  Favor de revisar si funciona bien

  
  */

  tiempo1 = millis(); // Se lee el tiempo actual
  tiempo2 = millis(); // Se lee el tiempo actual

  // Envio de datos Esto es un ejemplo
  sp1 = digitalRead(2);
  sp2 = digitalRead(3);
  sp3 = digitalRead(4);
  sm1 = analogRead(A0);
  sm2 = analogRead(A1);
  sm3 = analogRead(A2);

  /* 
  Aqui va tu codigo para leer los sensores y enviar los datos por serial
  Solo es un ejemplo lo que esta arriba
  
  
  
  */




  if (tiempo1 - t1 >= t2) { // if (tiempo1 - t1 >= 200) { // Se envian datos cada 200ms
    // Envio de datos generar formato: psa:1,psb:1,psc:1,msa:1,msb:1,msc:1
    Serial.print("psa:", ps1, ",psb:", ps2, ",psc:", ps3, ",msa:", ms1, ",msb:", ms2, ",msc:", ms3);
    t1 = tiempo1; // Se actualiza el tiempo
  }

  // Lectura de datos
  if (Serial.available() > 0) {
    // Se lee el dato
    char dato = Serial.readString();

    // Casting char to int
    int angulo = dato.toInt();
    // Se realiza una accion con el angulo recibido




    /*
    Aqui va tu codigo para mover el motor o lo que sea
    
    
    */

}

}