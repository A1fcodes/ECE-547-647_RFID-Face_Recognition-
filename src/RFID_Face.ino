#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9
#define GREEN_LED_PIN 7
#define RED_LED_PIN 6

MFRC522 rfid(SS_PIN, RST_PIN);
byte authorizedUID[4] = {0x34, 0x5D, 0x19, 0x5};

bool faceVerified = false;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();

  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);

  digitalWrite(GREEN_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);  // OFF by default

  Serial.println("System ready: waiting for face scan...");
}

void loop() {
  // Handle face recognition input from Python
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();  // Remove any \r or whitespace

    if (input == "face_ok") {
      faceVerified = true;
      Serial.println("✅ Face recognized. Waiting for RFID...");
    } else if (input == "face_fail") {
      Serial.println("❌ Face not recognized.");
      flashRedLED();
    }
  }

  if (faceVerified) {
    if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
      bool rfidMatch = true;
      for (byte i = 0; i < 4; i++) {
        if (rfid.uid.uidByte[i] != authorizedUID[i]) {
          rfidMatch = false;
        }
      }

      if (rfidMatch) {
        Serial.println("✅ RFID matched. Access granted.");
        digitalWrite(GREEN_LED_PIN, HIGH);
        Serial.println("rfid_ok");  // Signal to Python
        delay(3000);
        digitalWrite(GREEN_LED_PIN, LOW);
        
      } else {
        Serial.println("❌ RFID unauthorized.");
        flashRedLED();
      }

      faceVerified = false;
      rfid.PICC_HaltA();
      rfid.PCD_StopCrypto1();
    }
  }
}

void flashRedLED() {
  digitalWrite(RED_LED_PIN, HIGH);
  delay(2000);  // Red LED on for 2 seconds
  digitalWrite(RED_LED_PIN, LOW);
}
