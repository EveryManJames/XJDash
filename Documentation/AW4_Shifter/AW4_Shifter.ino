/*
 * Arduino Powered AW-4 Automatic Transmission Manual Shifting Code for Jeep or Similar.
 * 
 * !WARNING! PLEASE BE CAREFUL WITH THIS CODE. You are trusting your transmission's life to a little box and some homemade code so triple check everything!
 * I am not responsible for how this code is used, and will not be liable if you blow up your rig so consider this your warning!
 * 
 * 
 * This code reads 4 or 2 digital inputs from a joystick or switches and will then select and hold a specific gear
 * by outputting to a 2 CH relay box to control the Transmission Solenoids. The Current Gear is also displayed on a 7-segment display for viewing.
 *
 *
 * Each switch is connected to a seperate arduino pin to be digitally read. The Internal Pull-up resistors are turned on to bring the pin high. 
 * One end of the switch goes to the pin, the other to ground. When the switch is pressed, current will go to ground and the pin will read LOW.
 * If you find the switches are prone to interference or not working over long distance, plop in a 1k Resistor from 5v to the pin for a stronger Pull-up.
 * 
 * Each Relay Coil is connected to a seperate arduino pin to be digitally written. The Arduino pins don't have the power to energize a real relay coil,
 * so getting an arduino compatible relay board is recommended. Otherwise, you can use an NPN transitor to switch the relay coil while keeping the arduino safe.
 * 
 * 12v will go to the common pin of the relay, and the transmission solenoid will be connected to the Normally Open Contact. 
 * That way when the relay coil is powered, the contact will close and the solenoid will recieve 12v, which will shift it.
 * 
 * For best results driving the 7-Segment display, it is recommened that each pin is given it's own resistor. 
 * If you don't care about differing brightness, then 1 resitor on the common annode/common cathod pin can also work.
 * 
 * 
 * Sequetial Shift code has also been added if you only want a 2 button input system. 
 * Comment out the system that won't be used so they don't conflict with each other.
 * 
 * 
 * Written By: Nick Risley
 * NicknTimeDesign, 2018
 * 
 * 2/25/18 - Added Sequential Shifting Code
 */
 
// library used to convert display numbers into the proper 7-segment pins
#include <SegmentDisplay.h>

//the 7-segment pins must be mapped so the code knows how to talk to the screen since we are not multiplexing this 
                  //7-Seg pins 4,  5,  8,  7,  9, 10,  2,  3 
SegmentDisplay segmentDisplay(A1, A0, 12, A4, 11, 10, A3, A2);
                  //7-Seg pins E,  D,  C, DP,  B,  A,  F,  G 
                  
//we will assign the arduino digital pins a variable for easier reference
//set these to whatever pins you would like to use

//for complelte manual control
const byte firstGearPin   = 4;
const byte secondGearPin  = 12;
const byte thirdGearPin   = 6;
const byte fourthGearPin  = 8;

//for sequential shifitng control
const byte upShiftPin     = 4;
const byte downShiftPin   = 12;

//for solenoid outputs
const byte solenoidOnePin = 5;
const byte solenoidTwoPin = 13;

//these variables will store the digital read state, set High because inverse logic with pullups
byte firstGearButton  = HIGH;
byte secondGearButton = HIGH;
byte thirdGearButton  = HIGH;
byte fourthGearButton = HIGH;

byte upShiftButton    = HIGH;
byte downShiftButton  = HIGH;

//this is our flag varaible to store the currently selected gear, notice it is set to start in 4th untill modified
byte currentGear      = 4;

//these variables are just shortcuts, makes the code easier to read
const byte firstGear  = 1;
const byte secondGear = 2;
const byte thirdGear  = 3;
const byte fourthGear = 4;

//variables to be used with the averaging code if sequential shift is used
const byte averagingTotal = 5; //amount of averaging, this must be a const so arrays can use it.

byte upShiftArray[averagingTotal] = {1, 1, 1, 1, 1}; //This is an array. It's size must be declared so we set it equal to the const variable above
byte upShiftAVG; //This is the final value

byte downShiftArray[averagingTotal] = {1, 1, 1, 1, 1}; //The array is filled with 1 so it doesn't initially downshift
byte downShiftAVG;

bool shiftFlag; //boolean variable, just true or false.

void setup() {
  // put your setup code here, to run once:

//define the state of the pins, the pullup brings the pin HIGH, 
//so that way connecting the switch to ground will bring it LOW

//comment out the pins not needed
pinMode(firstGearPin, INPUT_PULLUP);
pinMode(secondGearPin, INPUT_PULLUP);
pinMode(thirdGearPin, INPUT_PULLUP);
pinMode(fourthGearPin, INPUT_PULLUP);

/*
pinMode(upShiftPin, INPUT_PULLUP);
pinMode(downShiftPin, INPUT_PULLUP);
*/

pinMode(solenoidOnePin, OUTPUT);
pinMode(solenoidTwoPin, OUTPUT);

//Serial.begin(56700); //for Debug
}

void loop() {
  // put your main code here, to run repeatedly:
  
//segmentDisplay.testDisplay(); //to debug 7-segment display

//manual shifting code ********************************************************************************************************************

//read the state of the pushbutton values
  fourthGearButton = digitalRead(fourthGearPin);
  thirdGearButton  = digitalRead(thirdGearPin);
  secondGearButton = digitalRead(secondGearPin);
  firstGearButton  = digitalRead(firstGearPin);
  
//IF statements to trigger the current gear flag variable
//The order matters, if multiple pins are detected, the higher gear is choosen for safety.
//since these are all If statements that save to a flag variable, if no buttons are pushed it will still stay in the last selected gear.
//notice the IF statement is looking for a LOW condition since we are using pull-up resistors and grounding the switched when they are pushed.
  if (firstGearButton == LOW)
    currentGear = firstGear;

  if (secondGearButton == LOW)
    currentGear = secondGear;
    
  if (thirdGearButton == LOW)
    currentGear = thirdGear;
    
  if (fourthGearButton == LOW)
    currentGear = fourthGear;

  //Debug code
    /*
    Serial.print(currentGear);
    Serial.print("G ");
    Serial.print(firstGearButton);
    Serial.print("b1 ");
    Serial.print(secondGearButton);
    Serial.print("b2 ");
    Serial.print(thirdGearButton);
    Serial.print("b3 ");
    Serial.print(fourthGearButton);
    Serial.println("b4"); 
    */
//sequential shifting code ********************************************************************************************************************
/*
//So this get's a bit more complicated because now accuracy matters and noise or glitches need to be properly filtered out for stable opperation.

//read the state of the pushbutton values
  downShiftButton = digitalRead(downShiftPin);
  upShiftButton   = digitalRead(upShiftPin);

//Averaging functions to filter out button noise, see actual code below
  upShiftAVG   = averageInputValue (upShiftButton, upShiftArray);
  downShiftAVG = averageInputValue (downShiftButton, downShiftArray);

//modify the current gear, but only once!
  if (upShiftAVG == LOW && shiftFlag == false && currentGear < 4){
    ++currentGear;    //since we are using the acutal gear numbers, simple addition or subtraction is fine
    shiftFlag = true; //this variable will keep the code from re shifting every loop
  }
  if (downShiftAVG == LOW && shiftFlag == false && currentGear > 1){
    --currentGear; 
    shiftFlag = true; 
  }
  if (upShiftAVG == HIGH && downShiftAVG == HIGH)
    shiftFlag = false; //reset the variable if neither button is pressed

  delay(10); //this is included so that an average is spaced over a longer and set time period. That fastest you can push a button is only like 60ms anyway.
  
  //Debug code
    /* 
    Serial.print(currentGear);
    Serial.print("G ");
    Serial.print(upShiftButton);
    Serial.print("U ");
    Serial.print(upShiftAVG);
    Serial.print("UA ");
    Serial.print(downShiftButton);
    Serial.print("D ");
    Serial.print(downShiftAVG);
    Serial.println("DA");
    */ 
      
//actual shifting code ********************************************************************************************************************

//The AW-4 Shift Table is as follows:
// First  = S1 On,  S2 Off 
// Second = S1 On,  S2 On
// Third  = S1 Off, S2 On
// Fourth = S1 Off, S2 Off

//Switch Case to trigger the solenoids based on current gear flag variable
    switch (currentGear)
    {
      case firstGear: 
        digitalWrite(solenoidOnePin, LOW);
        digitalWrite(solenoidTwoPin, HIGH);
        segmentDisplay.displayHex(1, false); //the false turns the decimal off
      break;
      case secondGear:
        digitalWrite(solenoidOnePin, LOW);
        digitalWrite(solenoidTwoPin, LOW);
        segmentDisplay.displayHex(2, false);
      case thirdGear:
        digitalWrite(solenoidOnePin, HIGH);
        digitalWrite(solenoidTwoPin, LOW);
        segmentDisplay.displayHex(3, false);
      case fourthGear: 
        digitalWrite(solenoidOnePin, HIGH);
        digitalWrite(solenoidTwoPin, HIGH);
        segmentDisplay.displayHex(4, false);
      break;
      default: //failsafe that will shift into 4th if code goofs 
        digitalWrite(solenoidOnePin, HIGH);
        digitalWrite(solenoidTwoPin, HIGH);
        segmentDisplay.displayHex(4, false);
      break;
    }//switch case closing curly    

}//Loop closing curly

//function used to do averaging while keeping the above code cleaner
byte averageInputValue(byte buttonInput, byte Array[averagingTotal])
{
    int sum = 0;                            //these variables only exisit in here and dissapeard afterwards, tidier code
    static byte arrayCounter;               //global variable would reset so we'll do it this way
    //fun fact, this value updates each time the function is called, and it's called twice in each loop which sounds like it would skip. 
    //But surprisingly each seperate array is still flushed in the same amount of loops, the numbers just count out of order. 
                    
    ++arrayCounter;                         //simple counter to update array position by 1
    if (arrayCounter >= averagingTotal)  
      arrayCounter = 0;                     //reset if too big
    
    Array[arrayCounter] = buttonInput;      //add current reading to selected array spot, together with the counter variable 
                                            //this will only replace the oldest value each loop with the newest
  
    for (byte count = 0; count < averagingTotal; count++){ //for loop to do automated repetitive summing
      sum += Array[count]; //clever code that adds the 2 values together without needed to retype it
    }
  
    return sum / averagingTotal;//Divide to get an Average for the final reading and spit it out
}

