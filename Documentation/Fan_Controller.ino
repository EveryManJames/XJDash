/*************************************************** 
  This is a library for our I2C LED Backpacks

  Designed specifically to work with the Adafruit LED 7-Segment backpacks 
  ----> http://www.adafruit.com/products/881
  ----> http://www.adafruit.com/products/880
  ----> http://www.adafruit.com/products/879
  ----> http://www.adafruit.com/products/878

  These displays use I2C to communicate, 2 pins are required to 
  interface. There are multiple selectable I2C addresses. For backpacks
  with 2 Address Select pins: 0x70, 0x71, 0x72 or 0x73. For backpacks
  with 3 Address Select pins: 0x70 thru 0x77

  Adafruit invests time and resources providing this open source code, 
  please support Adafruit and open-source hardware by purchasing 
  products from Adafruit!

  Written by Limor Fried/Ladyada for Adafruit Industries.  
  BSD license, all text above must be included in any redistribution
  
******************************************************
  Arduino powered Automotive Fan Controller v1, 5/23/17
  
  3 Speed Fan Controller Code with:
  - 4 Digit Adafruit Seven Segment i2c backback display
  - 2 Button control
  - 1 common Annode, tri-color LED indicator
  - 97+ Jeep Cherokee XJ Thermostat housing Temperature Sender reading w/ 5k Resistor and 5v
  - 3 Transistor outputs to ground Fan Relay Coils
  - 1 A/C voltage input

  Additional Code written by Nick Risley 
  NickInTimeDesign, 2017
 ****************************************************/

#include <Wire.h> // Enable this line if using Arduino Uno, Mega, etc.
#include <Adafruit_GFX.h>
#include "Adafruit_LEDBackpack.h"

#include <EEPROM.h>

Adafruit_7segment matrix = Adafruit_7segment();

//arduino pin decleration
const byte fan1Pin = 3;
const byte fan2Pin = 4;
const byte fan3Pin = 5;
const byte acPin = 6;

const byte swSel = 8;//adjust key
const byte swAdv = 12;//advance key

const byte tempPin = A0; //analog input

const byte redPin = 9; //tri color led pins
const byte bluePin = 10;
const byte greenPin = 11;
const byte ledPin = 13;//onboard led


int blah = 0;
byte mode = 0;
int temp = 0;
int temperature = 0;
double alogTemp = 0;//just for accuracy giggles
int lightSensor = 0;

byte menu = 0;

byte tempFlag = 0;
const byte none = 0;
const byte ac = 1;
const byte low = 2;
const byte med = 3;
const byte high = 4;

bool lowFlag = false;
bool medFlag = false;
bool highFlag = false;
bool advPressed = false;//debounce
bool selPressed = false;
bool indicatorFlag = true;//shows sketch is running

//fun fact, the GFX library won't print bytes
int lowOn = 220;
int lowOff = 210;
int medOn = 225;
int medOff = 215;
int highOn = 230;
int highOff = 220;

//EEPROM Address decleration
const byte EElowOn = 1;
const byte EElowOff = 2;
const byte EEmedOn = 3;
const byte EEmedOff = 4;
const byte EEhighOn = 5;
const byte EEhighOff = 6;

//averaging stuff
byte advance = 0;
const byte averageTotal = 50; //this changes the amount of averaging
int tempArray[51]; //this MUST equal averageTotal
long tempSum = 0; //bigger to hold the total sum, left signed to allow negitives, make sure this doesn't overflow from above

//screen dimming
bool dimFlag = false;
byte advance2 = 0;
const byte averageTotal2 = 32; //this changes the amount of averaging
int dimArray[33]; //this MUST equal averageTotal
unsigned long dimSum = 0; //bigger to hold the total sum
int brightness = 0;
unsigned long prevTime2 = 0;
const int updateTime2 = 50; //in milliseconds

//timing stuff
unsigned long currentTime = 0;
unsigned long prevTime = 0;
const int updateTime = 250; //in milliseconds

void setup() {

//declare pins
  analogWrite(redPin, 255);
  analogWrite(greenPin, 255);
  analogWrite(bluePin, 255);
  
  pinMode(fan1Pin, OUTPUT);
  pinMode(fan2Pin, OUTPUT);
  pinMode(fan3Pin, OUTPUT);
  pinMode(acPin, INPUT_PULLUP);
  
  pinMode(swAdv, INPUT_PULLUP);
  pinMode(swSel, INPUT_PULLUP);

  pinMode(ledPin, OUTPUT);

  //upload the matrix....I mean, start the screen..
  matrix.begin(0x70);
  //matrix.setBrightness(6); //0-15

//initial EEPROM set
  if (EEPROM.read(EElowOff) == 255){
    EEPROM.update(EElowOn, lowOn);
    EEPROM.update(EElowOff, lowOff);
    EEPROM.update(EEmedOn, medOn);
    EEPROM.update(EEmedOff, medOff);
    EEPROM.update(EEhighOn, highOn);
    EEPROM.update(EEhighOff, highOff);
  }

//bring EEPROM values into local variables 
  lowOn = EEPROM.read(EElowOn);
  lowOff = EEPROM.read(EElowOff);
  medOn = EEPROM.read(EEmedOn);
  medOn = EEPROM.read(EEmedOn);
  highOn = EEPROM.read(EEhighOn);
  highOn = EEPROM.read(EEhighOn);

//fill averaging array with current reading
  alogTemp = analogRead(A0);

  if (alogTemp < 26)//cut off for glitchy readings
    temp = -40;   
  else if (alogTemp < 200) // low curve
    temp = 40 * log(alogTemp) - 163; 
  else if (alogTemp > 700) // high curve
    temp = 0.001 * pow(alogTemp, 2) - 1.27 * alogTemp + 546;//545   
  else //(alogTemp >= 205 && alogTemp <= 684) middle line
    temp = 0.19 * alogTemp + 12;

  for (advance = 0; advance < averageTotal; advance++){
    tempArray[advance] = temp;
  }
}

void loop() {

  if (indicatorFlag == true)
    digitalWrite(ledPin, HIGH);
  else digitalWrite(ledPin, LOW);
  
//Temperature sender calculations**************************************************

  currentTime = millis();
  if (currentTime > prevTime + updateTime){ //throttle read time to prevent jumpy readings
    alogTemp = analogRead(A0);
    prevTime = currentTime;

    indicatorFlag = !indicatorFlag;
  
  //alogTemp = (alogTemp * 5.0) / 1024.0;

  if (alogTemp < 26)//cut off for glitchy readings
    temp = -40;   
  else if (alogTemp < 200) // low curve
    temp = 40 * log(alogTemp) - 163; 
  else if (alogTemp > 700) // high curve
    temp = 0.001 * pow(alogTemp, 2) - 1.27 * alogTemp + 546;//545   
  else //(alogTemp >= 205 && alogTemp <= 684) middle line
    temp = 0.19 * alogTemp + 12;

//Averaging stuff

  ++advance;//simple counter to update array
  if (advance >= averageTotal)
    advance = 0; //reset

  tempArray[advance] = temp; //add current temp to array spot

  for (byte count = 0; count < averageTotal; count++){ //for loop to do summing
    if (count == 0)
      tempSum = 0;//resets number or bad things happen
    tempSum += tempArray[count];
  }

  temperature = tempSum / averageTotal;//final reading
  //temperature = temp;
  //temperature = tempArray[advance];
  }//end temp reading throttle

//Dimming Stuf***********************************************************************

  currentTime = millis();
  if (currentTime > prevTime2 + updateTime2){ //throttle read time to prevent jumpy readings
    prevTime2 = currentTime;
    lightSensor = analogRead(A2);
  
    ++advance2;//simple counter to update array
    if (advance2 >= averageTotal2)
      advance2 = 0; //reset
  
    dimArray[advance2] = lightSensor; //add current dim to array spot
  
    for (byte count2 = 0; count2 < averageTotal2; count2++){ //for loop to do summing
      if (count2 == 0)
        dimSum = 0;//resets number or bad things happen
      dimSum += dimArray[count2];
    }
  
    brightness = dimSum / averageTotal2;//final reading
  }

  if (brightness < 60 && dimFlag == false){ //brightness control
    dimFlag = true;
    matrix.setBrightness(0);//0-15
  }
  
  if (brightness > 100 && dimFlag == true){ //brightness control
    dimFlag = false;
    matrix.setBrightness(15);
  }
            
//Button Stuff***********************************************************************
  
  if (digitalRead(swAdv) == LOW){//button debounce
    if (advPressed == false){
      ++menu;
      advPressed = true;
    }
  }
  else advPressed = false;

  if (menu > 13) //menu reset
    menu = 0;

  if (digitalRead(swAdv) == LOW && digitalRead(swSel) == LOW)//hold both to go home
    menu = 0;
    
  switch (menu)//menu selection switch case******************************************
  {
    case 0:
      /*if (digitalRead(swSel) == LOW)
        ++temperature;
      if (digitalRead(swAdv) == LOW)
        --temperature;*/
      //matrix.print(brightness);  
      matrix.print(temperature);
      if (digitalRead(acPin) == LOW)//draw symbol if ac is active
        matrix.writeDigitRaw(0, 92);
      matrix.writeDisplay();
    break;
    case 1://manual control
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){//keeps from triggering if trying to go home
        if (selPressed == false){
          ++mode;
          selPressed = true;
        }
      }
      else selPressed = false;
      if (mode > 4)
          mode = 0;
        //++blah; 
      switch (mode)
        {
          case 0://auto
            //matrix.print(blah);
            //matrix.writeDigitRaw(0, blah);
            matrix.writeDigitRaw(0, 119);
            matrix.writeDigitRaw(1, 28);
            matrix.writeDigitRaw(3, 120);
            matrix.writeDigitRaw(4, 92);
            //A119 d94 E121 f113 G61? g111 h116 i6,48 L56 m4 o92 t120 u28 w4 J14,30 B127 b124 G125? c88 C57 H118 N55 U62 O63 n84 P115 -64 ?83
          break;
          case 1://off
            tempFlag = none;
            matrix.writeDigitRaw(0, 0);
            matrix.writeDigitRaw(1, 63);
            matrix.writeDigitRaw(3, 113);
            matrix.writeDigitRaw(4, 113);
          break;
          case 2://low
            matrix.writeDigitRaw(0, 56);
            matrix.writeDigitRaw(1, 92);
            matrix.writeDigitRaw(3, 6);//56
            matrix.writeDigitRaw(4, 62);
            tempFlag = low;
          break;
          case 3://med
            tempFlag = med;
            matrix.writeDigitRaw(0, 6);
            matrix.writeDigitRaw(1, 55);
            matrix.writeDigitRaw(3, 121);
            matrix.writeDigitRaw(4, 94);
          break;
          case 4://high
            tempFlag = high;
            matrix.writeDigitRaw(0, 118);
            matrix.writeDigitRaw(1, 6);
            matrix.writeDigitRaw(3, 111);
            matrix.writeDigitRaw(4, 116);
          break;
        }
      matrix.writeDisplay();
    break;
    case 2: //increase lowOn
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){
        if (selPressed == false){
          ++lowOn;
          selPressed = true;
        }
      }
      else selPressed = false;
      matrix.print(lowOn);  //dm71Nmbt
      matrix.writeDigitRaw(0, 10);
      matrix.writeDisplay();
      EEPROM.update(EElowOn, lowOn); 
    break;
    case 3: //decrease lowOn
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){
        if (selPressed == false){
          --lowOn;
          selPressed = true;
        }
      }
      else selPressed = false;
      matrix.print(lowOn);
      matrix.writeDigitRaw(0, 12);
      matrix.writeDisplay();
      EEPROM.update(EElowOn, lowOn);
    break;
    case 4: //increase lowOff
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){
        if (selPressed == false){
          ++lowOff;
          selPressed = true;
        }
      }
      else selPressed = false;
      matrix.print(lowOff);
      matrix.writeDigitRaw(0, 40);
      matrix.writeDisplay();
      EEPROM.update(EElowOff, lowOff);
    break;
    case 5: //decrease lowOff
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){
        if (selPressed == false){
          --lowOff;
          selPressed = true;
        }
      }
      else selPressed = false;
      matrix.print(lowOff);
      matrix.writeDigitRaw(0, 24);
      matrix.writeDisplay();
      EEPROM.update(EElowOff, lowOff);
    break;
    case 6: //increase medOn
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){
        if (selPressed == false){
          ++medOn;
          selPressed = true;
        }
      }
      else selPressed = false;
      matrix.print(medOn);
      matrix.writeDigitRaw(0, 66);//good
      matrix.writeDisplay();
      EEPROM.update(EEmedOn, medOn);
    break;
    case 7: //decrease medOn
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){
        if (selPressed == false){
          --medOn;
          selPressed = true;
        }
      }
      else selPressed = false;
      matrix.print(medOn);
      matrix.writeDigitRaw(0, 68);
      matrix.writeDisplay();
      EEPROM.update(EEmedOn, medOn);
    break;
    case 8: //increase medOff
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){
        if (selPressed == false){
          ++medOff;
          selPressed = true;
        }
      }
      else selPressed = false;
      matrix.print(medOff);
      matrix.writeDigitRaw(0, 96);
      matrix.writeDisplay();
      EEPROM.update(EEmedOff, medOff);
    break;
    case 9: //decrease medOff
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){
        if (selPressed == false){
          --medOff;
          selPressed = true;
        }
      }
      else selPressed = false;
      matrix.print(medOff);
      matrix.writeDigitRaw(0, 80);//decimal...
      matrix.writeDisplay();
      EEPROM.update(EEmedOff, medOff);
    break;
    case 10: //increase highOn
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){
        if (selPressed == false){
          ++highOn;
          selPressed = true;
        }
      }
      else selPressed = false;
      matrix.print(highOn);
      matrix.writeDigitRaw(0, 3);
      matrix.writeDisplay();
      EEPROM.update(EEhighOn, highOn);
    break;
    case 11: //increase highOn
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){
        if (selPressed == false){
          --highOn;
          selPressed = true;
        }
      }
      else selPressed = false;
      matrix.print(highOn);
      matrix.writeDigitRaw(0, 5);
      matrix.writeDisplay();
      EEPROM.update(EEhighOn, highOn);
    break;
    case 12: //increase highOff
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){
        if (selPressed == false){
          ++highOff;
          selPressed = true;
        }
      }
      else selPressed = false;
      matrix.print(highOff);
      matrix.writeDigitRaw(0, 33);
      matrix.writeDisplay();
      EEPROM.update(EEhighOff, highOff);
    break;
    case 13: //increase highOff
      if (digitalRead(swSel) == LOW && digitalRead(swAdv) == HIGH){
        if (selPressed == false){
          --highOff;
          selPressed = true;
        }
      }
      else selPressed = false;
      matrix.print(highOff);
      matrix.writeDigitRaw(0, 17);
      matrix.writeDisplay();
      EEPROM.update(EEhighOff, highOff);
    break;
  }

  if (mode == 0){//auto mode switching***************************************************
    tempFlag = none;
  
    if (digitalRead(acPin) == LOW)
      tempFlag = ac;
  
    
    if (lowFlag == false && temperature >= lowOn)
      lowFlag = true;
    if (lowFlag == true && temperature <= lowOff)
      lowFlag = false;
    if (lowFlag == true)
      tempFlag = low;
  
  
    if (medFlag == false && temperature >= medOn)
      medFlag = true;
    if (medFlag == true && temperature <= medOff)
      medFlag = false;
    if (medFlag == true)
      tempFlag = med;
  
  
    if (highFlag == false && temperature >= highOn)
      highFlag = true;
    if (highFlag == true && temperature <= highOff)
      highFlag = false;
    if (highFlag == true)
      tempFlag = high;
  }

  switch (tempFlag)//Fan and LED switching*******************************************************
  {
    case none:
      digitalWrite(fan1Pin, LOW);
      digitalWrite(fan2Pin, LOW);
      digitalWrite(fan3Pin, LOW);
      analogWrite(redPin, 255);
      analogWrite(greenPin, 255);
      analogWrite(bluePin, 255);
    break;
    case ac:
      digitalWrite(fan1Pin, HIGH);
      digitalWrite(fan2Pin, LOW);
      digitalWrite(fan3Pin, LOW);
      
      if (dimFlag == true){
        analogWrite(redPin, 255);
        analogWrite(greenPin, 254);
        analogWrite(bluePin, 253);
      }
      else{
        analogWrite(redPin, 255);
        analogWrite(greenPin, 251);
        analogWrite(bluePin, 245);
      }
    break;
    case low:
      digitalWrite(fan1Pin, LOW);
      digitalWrite(fan2Pin, HIGH);
      digitalWrite(fan3Pin, LOW);
      
      if (dimFlag == true){
        analogWrite(redPin, 255);
        analogWrite(greenPin, 253);
        analogWrite(bluePin, 255);
      }
      else{
        analogWrite(redPin, 255);
        analogWrite(greenPin, 245);
        analogWrite(bluePin, 255);
      }
    break;
    case med:
      digitalWrite(fan1Pin, HIGH);
      digitalWrite(fan2Pin, HIGH);
      digitalWrite(fan3Pin, LOW);
            
      if (dimFlag == true){
        analogWrite(redPin, 254);
        analogWrite(greenPin, 253);
        analogWrite(bluePin, 255);
      }
      else{
        analogWrite(redPin, 249);
        analogWrite(greenPin, 246);
        analogWrite(bluePin, 255);
      }
    break;
    case high:
      digitalWrite(fan1Pin, HIGH);
      digitalWrite(fan2Pin, LOW);
      digitalWrite(fan3Pin, HIGH);
            
      if (dimFlag == true){
        analogWrite(redPin, 254);
        analogWrite(greenPin, 255);
        analogWrite(bluePin, 255);
      }
      else{
        analogWrite(redPin, 245);
        analogWrite(greenPin, 255);
        analogWrite(bluePin, 255);
      }
    break;
  }
  //delay(10);
  /*if (tempFlag == true)
    digitalWrite(13, HIGH);
  else
    digitalWrite(13, LOW);*/
    
  /*// try to print a number thats too long
  matrix.print(10000, DEC);
  matrix.writeDisplay();
  delay(1000);

  // print a hex number
  matrix.print(0xBEEF, HEX);
  matrix.writeDisplay();
  delay(1000);

  // print a floating point 
  matrix.print(12.34);
  matrix.writeDisplay();
  delay(500);
  
  // print with print/println
  for (uint16_t counter = 0; counter < 9999; counter++) {
    matrix.println(counter);
    matrix.writeDisplay();
    delay(10);
  }

  // method #2 - draw each digit
  uint16_t blinkcounter = 0;
  boolean drawDots = false;
  for (uint16_t counter = 0; counter < 9999; counter ++) {
    matrix.writeDigitNum(0, (counter / 1000), drawDots);
    matrix.writeDigitNum(1, (counter / 100) % 10, drawDots);
    matrix.drawColon(drawDots);
    matrix.writeDigitNum(3, (counter / 10) % 10, drawDots);
    matrix.writeDigitNum(4, counter % 10, drawDots);
   
    blinkcounter+=50;
    if (blinkcounter < 500) {
      drawDots = false;
    } else if (blinkcounter < 1000) {
      drawDots = true;
    } else {
      blinkcounter = 0;
    }
    matrix.writeDisplay();
    delay(10);
  }*/
}
