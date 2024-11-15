const int redPin = 2;  
const int bluePin = 3;  
int redState = 0;
int blueState = 0;

void setup() {
  Serial.begin(115200);  
  pinMode(redPin, INPUT_PULLUP);
  pinMode(bluePin, INPUT_PULLUP);
}


void loop() {
  // put your main code here, to run repe atedly:
  redState = digitalRead(redPin);
  blueState = digitalRead(bluePin);
  if (redState == LOW) {
    Serial.println("red");
    delay(200);  // Petit délai pour éviter les rebonds
    Serial.println("gray");
  }

  if (blueState == LOW) {
    Serial.println("blue");
    delay(200);  // Petit délai pour éviter les rebonds
    Serial.println("gray");
  }
  // if data is available to read
  // if (Serial.available()>0){
  //   char data= Serial.read();

  // }
}
