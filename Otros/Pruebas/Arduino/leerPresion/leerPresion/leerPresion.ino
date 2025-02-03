// HX710B Weighing Sensor Example Code for Arduino UNO
#define DOUT  3
#define PD_SCK  2

void setup() {
  Serial.begin(9600);
  pinMode(PD_SCK, OUTPUT);
  pinMode(DOUT, INPUT);
}

void loop() {
  long weight = readWeight();
  Serial.print("Weight: ");
  Serial.println(weight);
  delay(2000);
}

long readWeight() {
  long count;
  unsigned char i;
  pinMode(DOUT, INPUT);
  
  while(digitalRead(DOUT));
  
  count=0;
  pinMode(PD_SCK, OUTPUT);
  for(i=0;i<24;i++) {
    digitalWrite(PD_SCK, HIGH);
    count=count<<1;
    digitalWrite(PD_SCK, LOW);
    if(digitalRead(DOUT))
      count++;
  }
  digitalWrite(PD_SCK, HIGH);
  count ^= 0x800000;
  digitalWrite(PD_SCK, LOW);
  return(count);
}
